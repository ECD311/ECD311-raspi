import serial
import csv
import os
import glob
import ast
from paramiko import SSHClient
from pyscp import SCPClient
import cachetools
from pyowm import owm
import sys
from suncalc import get_position, get_times
from datetime import datetime, timedelta
import math
try:
	import conf
except:
	sys.stderr.write("ERR: conf.py not found")
	sys.exit(1)

owm = owm.OWM(conf.owm_api_key)
mgr = owm.weather_manager()

global rx_datetime_first


@cachetools.cached(cache=cachetools.TTLCache(ttl=60*5))  # 5 minute cache
def get_weather():
     return mgr.weather_at_place(conf.place).weather.detailed_status


def get_current_position():  # ['azimuth': azimuth, 'altitude': altitude]
    return get_position(datetime.utcnow(), conf.suncalc_lon, conf.suncalc_lat)


def get_suntimes(): # need to figure out conversion to compatible timestamp for arduino
    times = get_times(datetime.utcnow(), conf.suncalc_lon, conf.suncalc_lat)
    return (times['sunrise'] - timedelta(hours=conf.datetime_offset), times['sunset'] - timedelta(hours=conf.datetime_offset))


def rx_data(writer):
    print("rx\n")

    dict = ast.literal_eval(ser.readline().rstrip().decode("utf-8"))
    if firstrun:
        rx_datetime_first = dict['Date_Time']
        firstrun = 0

    outdoor_conditions = get_weather()
    dict["outdoor_conditions"] = outdoor_conditions
    writer.writerow(dict)


port = "/dev/ttyACM0"  # placeholder, switch w actual serial port; use env var?
baud = 115200


header = ['Date_Time', 'System_Status', 'Solar_Panel_Voltage', 'Solar_Panel_Current', 'Solar_Panel_Power', 'Battery_One_Voltage', 'Battery_Two_Voltage', 'Battery_Total_Voltage', 'Battery_Total_Current', 'Battery_Total_Power', 'Load_Voltage', 'Load_Current', 'Load_Power', 'Inverter_Voltage', 'Inverter_Current', 'Inverter_Power', 'Motor_One_Voltage', 'Motor_One_Current', 'Motor_One_Power',
          'Motor_Two_Voltage', 'Motor_Two_Current', 'Motor_Two_Power', 'Five_Volt_Voltage', 'Five_Volt_Current', 'Five_Volt_Power', 'Windspeed', 'Outdoor_Temp', 'Outdoor_Humidity', 'System_Temp', 'System_Humidity', 'Azimuth_Reading', 'Azimuth_Command', 'Azimuth_Motor_Mode', 'Azimuth_Motor_Status', 'Elevation_Reading', 'Elevation_Command', 'Elevation_Motor_Mode', 'Elevation_Motor_Status']

newheader = ['Date_Time', 'System_Status', 'Solar_Panel_Voltage', 'Solar_Panel_Current', 'Solar_Panel_Power', 'Battery_One_Voltage', 'Battery_Two_Voltage', 'Battery_Total_Voltage', 'Battery_Total_Power', 'Load_Voltage', 'Load_Current', 'Load_Power', 'Windspeed', 'Outdoor_Temp', 'Outdoor_Humidity', 'Outdoor_Conditions', 'Azimuth_Reading', 'Azimuth_Command', 'Azimuth_Motor_Mode', 'Azimuth_Motor_Status', 'Elevation_Reading', 'Elevation_Command', 'Elevation_Motor_Mode', 'Elevation_Motor_Status']

try:
    ser = serial.Serial(port, baud)  # 9600 8N1 default
except serial.SerialException:
    ser = serial.Serial()  # the serial port isn't available, create a closed interface

# LOG
# datetime - date time
# state - maint, wind, etc
# solar V\n I\n W\n
# batt 1 V
# batt 2 V
# batt total V\n I\n W\n
# load V\n I\n W\n
# inverter V\n I\n W\n
# motor 1 V\n I\n W\n
# motor 2 V\n I\n W\n
# 5V rail V\n I\n W\n
# wind speed (m/s)
# out temp
# out humidity
# in temp
# in humidity
# azim reading + command
# azim motor mode (auto, manual)
# azim motor status (ccw, cw, off)
# elev reading + command
# elev motor mode (auto, manual)
# elev motor status (ccw, cw, off)

# if a csv exists in current dir, open it
# after N lines in csv, close, move to other dir to get sent to bingweb

# wait for readline() to return "LOG\n"
# if csv doesnt exist in current dir, make a new one with ts value in next readline()
# read in each value from readline(), insert into csv via dict, and repeat

# does not handle errors from arduino, only logs

while (1):
    csvlines = 0
    firstrun = 1

    if glob.glob("*.csv"):
        file = open(glob.glob("*.csv", recursive=False)[0], 'a')
        writer = csv.DictWriter(file, fieldnames=header)
    else:
        file = open("new.csv", 'w')
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()

    while csvlines <= (30 * 60)/2:  # 30 mins @ 2 seconds per measurement

        # may miss one log at first startup, shouldnt be an issue

        line = ser.readline().rstrip().decode("utf-8")

        if (line == "LOG"):
            rx_data(writer)
            csvlines += 1
        elif (line == "new_position"):  # azimuth, then altitude in degrees
            location = get_current_position()
            ser.write("%s\r\n" % int(location['azimuth'] * 180 / math.pi))
            ser.write("%s\r\n" % int(location['altitude'] * 180 / math.pi))
        elif (line == "new_times"):
            times = get_suntimes()
            ser.write("%s\r\n" % times[0].strftime("%H:%M:%S"))
            ser.write("%s\r\n" % times[1].strftime("%H:%M:%S"))
            ser.write("%s\r\n" % times[2].strftime("%H:%M:%S"))
            ser.write("%s\r\n" % times[3].strftime("%H:%M:%S"))

    file.close()

    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect('34.238.23.117', username='watsolar')

    scp = SCPClient(ssh.get_transport())

    new_filename = "data_log_" + rx_datetime_first + ".csv"
    os.rename(glob.glob("*.csv")[0], "move/" + new_filename)
    scp.put("move/" + new_filename, remote_path='datalogs/')
    scp.close()
    ssh.close()
    print("send data")
