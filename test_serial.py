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
try:
	import conf
except:
	sys.stderr.write("ERR: conf.py not found")
	sys.exit(1)

owm = owm.OWM(conf.owm_api_key)
mgr = owm.weather_manager()

@cachetools.cached(cache=cachetools.TTLCache(ttl=60*5)) # 5 minute cache
def get_weather():
     return mgr.weather_at_place(conf.place).weather.detailed_status

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
    csvlines = 898
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
        while ser.readline().rstrip().decode("utf-8") != "LOG":
            pass
        print("rx\n")
        rx_datetime = ser.readline().rstrip().decode("utf-8")
        if firstrun:
            rx_datetime_first = rx_datetime
            firstrun = 0
        sys_state = ser.readline().rstrip().decode("utf-8")

        solar_voltage = ser.readline().rstrip().decode("utf-8")
        solar_current = ser.readline().rstrip().decode("utf-8")
        solar_power = ser.readline().rstrip().decode("utf-8")

        bat1_voltage = ser.readline().rstrip().decode("utf-8")
        bat2_voltage = ser.readline().rstrip().decode("utf-8")

        bat_tot_voltage = ser.readline().rstrip().decode("utf-8")
        bat_tot_current = ser.readline().rstrip().decode("utf-8")
        bat_tot_power = ser.readline().rstrip().decode("utf-8")

        load_voltage = ser.readline().rstrip().decode("utf-8")
        load_current = ser.readline().rstrip().decode("utf-8")
        load_power = ser.readline().rstrip().decode("utf-8")

        inverter_voltage = ser.readline().rstrip().decode("utf-8")
        inverter_current = ser.readline().rstrip().decode("utf-8")
        inverter_power = ser.readline().rstrip().decode("utf-8")

        m1_voltage = ser.readline().rstrip().decode("utf-8")
        m1_current = ser.readline().rstrip().decode("utf-8")
        m1_power = ser.readline().rstrip().decode("utf-8")

        m2_voltage = ser.readline().rstrip().decode("utf-8")
        m2_current = ser.readline().rstrip().decode("utf-8")
        m2_power = ser.readline().rstrip().decode("utf-8")

        five_volt_voltage = ser.readline().rstrip().decode("utf-8")
        five_volt_current = ser.readline().rstrip().decode("utf-8")
        five_volt_power = ser.readline().rstrip().decode("utf-8")

        wind_speed = ser.readline().rstrip().decode("utf-8")

        out_temp = ser.readline().rstrip().decode("utf-8")
        out_humid = ser.readline().rstrip().decode("utf-8")

        in_temp = ser.readline().rstrip().decode("utf-8")
        in_humid = ser.readline().rstrip().decode("utf-8")

        azim_reading = ser.readline().rstrip().decode("utf-8")
        azim_command = ser.readline().rstrip().decode("utf-8")
        azim_mode = ser.readline().rstrip().decode("utf-8")
        azim_status = ser.readline().rstrip().decode("utf-8")

        elev_reading = ser.readline().rstrip().decode("utf-8")
        elev_command = ser.readline().rstrip().decode("utf-8")
        elev_mode = ser.readline().rstrip().decode("utf-8")
        elev_status = ser.readline().rstrip().decode("utf-8")

        outdoor_conditions = get_weather()

        # continue for each variable sent
        # ideally read a single json or dict and use json module / ast.literal_eval() to avoid having ~40 separate reads

        writer.writerow({'Date_Time': rx_datetime, 'System_Status': sys_state, 'Solar_Panel_Voltage': solar_voltage, 'Solar_Panel_Current': solar_current, 'Solar_Panel_Power': solar_power, 'Battery_One_Voltage': bat1_voltage, 'Battery_Two_Voltage': bat2_voltage, 'Battery_Total_Voltage': bat_tot_voltage, 'Battery_Total_Current': bat_tot_current, 'Battery_Total_Power': bat_tot_power, 'Load_Voltage': load_voltage, 'Load_Current': load_current, 'Load_Power': load_power, 'Inverter_Voltage': inverter_voltage, 'Inverter_Current': inverter_current, 'Inverter_Power': inverter_power, 'Motor_One_Voltage': m1_voltage, 'Motor_One_Current': m1_current,
                        'Motor_One_Power': m1_power, 'Motor_Two_Voltage': m2_voltage, 'Motor_Two_Current': m2_current, 'Motor_Two_Power': m2_power, 'Five_Volt_Voltage': five_volt_voltage, 'Five_Volt_Current': five_volt_current, 'Five_Volt_Power': five_volt_power, 'Windspeed': wind_speed, 'Outdoor_Temp': out_temp, 'Outdoor_Humidity': out_humid, 'System_Temp': in_temp, 'System_Humidity': in_humid, 'Azimuth_Reading': azim_reading, 'Azimuth_Command': azim_command, 'Azimuth_Motor_Mode': azim_mode, 'Azimuth_Motor_Status': azim_status, 'Elevation_Reading': elev_reading, 'Elevation_Command': elev_command, 'Elevation_Motor_Mode': elev_mode, 'Elevation_Motor_Status': elev_status})
        if csvlines == 0:
            new_filename = "data_log_%s.csv" % rx_datetime
        csvlines += 1
    file.close()
    # using glob may be unnecessary here, there should almost never be existing csvs in the dir

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
