#!/usr/bin/python3
import serial
import csv
import os
import glob
import ast
from paramiko import SSHClient
from scp import SCPClient
import cachetools
from pyowm import owm
import sys
from pysolar.solar import get_altitude, get_azimuth
from pysolar.util import get_sunrise_sunset
from datetime import datetime, timezone, timedelta
import cronitor
try:
    import conf
except:
    sys.stderr.write("ERR: conf.py not found\r\n")
    sys.exit(1)

owm = owm.OWM(conf.owm_api_key)
mgr = owm.weather_manager()

rx_datetime_first = "0000-00-00_00:00:00"
datetime_start = datetime.now(tz=timezone.utc)
firstrun = 1


# 5 minute cache
@cachetools.cached(cache=cachetools.TTLCache(ttl=60*5, maxsize=1))
def get_weather():
    try: 
        retval = mgr.weather_at_place(conf.owm_location).weather.detailed_status
    except:
        retval = "conditions unavailable"
    return retval


def get_current_position():  # {'azimuth': azimuth, 'altitude': altitude}
    azimuth = get_azimuth(conf.suncalc_lat, conf.suncalc_lon,
                          datetime.now(tz=timezone.utc))
    altitude = get_altitude(
        conf.suncalc_lat, conf.suncalc_lon, datetime.now(tz=timezone.utc))
    return {'azimuth': azimuth, 'altitude': altitude}


def get_suntimes():  # (sunrise, sunset, azimuth @ sunrise, altitude @ sunrise)
    times = get_sunrise_sunset(
        conf.suncalc_lat, conf.suncalc_lon, datetime.now(tz=timezone.utc))
    sunrise_position_azim = get_azimuth(
        conf.suncalc_lat, conf.suncalc_lon, times[0])
    sunrise_position_alt = get_altitude(
        conf.suncalc_lat, conf.suncalc_lon, times[0])
    return (times[0], times[1], sunrise_position_azim, sunrise_position_alt)

@cronitor.job('upload_data')
def upload_data():
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect('34.238.23.117', username='watsolar')

    scp = SCPClient(ssh.get_transport())

    new_filename = "data_log_" + rx_datetime_first + ".csv"
    os.rename(glob.glob("*.csv")[0], "move/" + new_filename)
    for filename in glob.glob("move/*.csv"):
        try:
            scp.put(filename, remote_path='datalogs/')
        except:
            # scp.close()
            # ssh.close()
            print('issue sending csv')
            sys.stderr.write("ERR: Failed to upload file %s to bingdev\r\n" % filename)
            continue
        os.rename(filename, "moved/" + filename.split('/')[-1])
    # os.rename("move/" + new_filename, "moved/" + new_filename)
    scp.close()
    ssh.close()
    sys.stdout.write("LOG: Uploaded files to bingdev\r\n")
    print("send data")

@cronitor.job('rx_data')
def rx_data(writer):
    print("rx\n")
    global firstrun
    global rx_datetime_first
    try:
        line = ser.readline().rstrip().decode("utf-8")
        # print(line)
    except:
        sys.stderr.write("WARN: Failed to receive/decode input\r\n")
        pass
    try:
        dict = ast.literal_eval(line)
        # print(dict)
    except:  # just ignore errors here, should only error once
        print("failed read")
        sys.stderr.write("WARN: failed to literal eval input\r\n")
        return -1

    if firstrun:
        rx_datetime_first = dict['Date_Time']
        firstrun = 0

    outdoor_conditions = get_weather()
    dict["Outdoor_Conditions"] = outdoor_conditions
    writer.writerow(dict)
    return 0


port = "/dev/ttyACM0"  # placeholder, switch w actual serial port; use env var?
baud = 115200


header = ['Date_Time', 'System_Status', 'Solar_Panel_Voltage', 'Solar_Panel_Current', 'Solar_Panel_Power', 'Battery_One_Voltage', 'Battery_Two_Voltage', 'Battery_Total_Voltage', 'Battery_Total_Current', 'Battery_Total_Power', 'Load_Voltage', 'Load_Current', 'Load_Power', 'Inverter_Voltage', 'Inverter_Current', 'Inverter_Power', 'Motor_One_Voltage', 'Motor_One_Current', 'Motor_One_Power',
          'Motor_Two_Voltage', 'Motor_Two_Current', 'Motor_Two_Power', 'Five_Volt_Voltage', 'Five_Volt_Current', 'Five_Volt_Power', 'Windspeed', 'Outdoor_Temp', 'Outdoor_Humidity', 'System_Temp', 'System_Humidity', 'Azimuth_Reading', 'Azimuth_Command', 'Azimuth_Motor_Mode', 'Azimuth_Motor_Status', 'Elevation_Reading', 'Elevation_Command', 'Elevation_Motor_Mode', 'Elevation_Motor_Status']

newheader = ['Date_Time', 'System_Status', 'Solar_Panel_Voltage', 'Solar_Panel_Current', 'Solar_Panel_Power', 'Battery_One_Voltage', 'Battery_Two_Voltage', 'Battery_Total_Voltage', 'Battery_Total_Power', 'Load_Voltage', 'Load_Current', 'Load_Power',
             'Windspeed', 'Outdoor_Temp', 'Outdoor_Humidity', 'Outdoor_Conditions', 'Azimuth_Reading', 'Azimuth_Command', 'Azimuth_Motor_Mode', 'Azimuth_Motor_Status', 'Elevation_Reading', 'Elevation_Command', 'Elevation_Motor_Mode', 'Elevation_Motor_Status']

try:
    ser = serial.Serial(port, baud)  # 9600 8N1 default
except serial.SerialException:
    ser = serial.Serial()  # the serial port isn't available, create a closed interface
    sys.stderr.write("ERR: Unable to open serial port %s\r\n" % port)

# if a csv exists in current dir, open it
# after N lines in csv, close, move to other dir to get sent to bingweb

# LOG\r\n
# dict containing all sensor data, using ast.literal_eval() to transform into actual python dict
#   dict based on newheader

# optional:
# new_position
# respond with the current azimuth and elevation of the sun
# new_times
# respond with today's sunrise/sunset and position at sunrise

# wait for readline() to return "LOG\n"
# if csv doesnt exist in current dir, make a new one with ts value in next readline()

# does not handle errors from arduino, only logs
try:
    ser.write("start\n")
except:
    sys.stderr.write("ERR: Unable to send start string - arduino will not start up")

while (datetime_start < datetime_start + timedelta(hours=12)):
    csvlines = 0

    if glob.glob("*.csv"):
        file = open(glob.glob("*.csv", recursive=False)[0], 'a')
        writer = csv.DictWriter(file, fieldnames=newheader)
    else:
        file = open("new.csv", 'w')
        writer = csv.DictWriter(file, fieldnames=newheader)
        writer.writeheader()

    while csvlines <= (30 * 60)/2:  # 30 mins @ 2 seconds per measurement

        # may miss one log at first startup, shouldnt be an issue
        try:
            line = ser.readline().rstrip().decode("utf-8")
        except:
            line = ""

        print(line)
        if (line == "LOG"):
            if (rx_data(writer) == 0):
                csvlines += 1
        elif (line == "new_position"):  # azimuth, then altitude in degrees
            print("position")
            location = get_current_position()
            azim = b"%i\n" % int(location['azimuth'])
            elev = b"%i\n" % int(location['altitude'])
            ser.write(azim)
            ser.write(elev)
            print("azimuth: %d" % int(location['azimuth']))
            print("elevation: %d" % int(location['altitude']))
            #print('actual: ' + str(int(location['azimuth'])))
            #print('actual: ' + str(int(location['altitude'])))
            # print(ser.read(6).rstrip().decode("utf-8"))

        elif (line == "new_times"):
            print("times")
            times = get_suntimes()
            time0 = "%s\n" % times[0].strftime("%H:%M:%S")
            time1 = "%s\n" % times[1].strftime("%H:%M:%S")
            azim = b"%i\n" % int(times[2])
            elev = b"%i\n" % int(times[3])
            ser.write(time0.encode())
            ser.write(time1.encode())
            ser.write(azim)
            ser.write(elev)

    file.close()

    upload_data()
