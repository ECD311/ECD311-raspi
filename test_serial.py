import serial
import csv
import os
import glob
import ast

port = "/dev/ttyACM0"  # placeholder, switch w actual serial port; use env var?
baud = 115200


header = ['Date_Time', 'System_Status', 'Solar_Panel_Voltage', 'Solar_Panel_Current', 'Solar_Panel_Power', 'Battery_One_Voltage', 'Battery_Two_Voltage', 'Battery_Total_Voltage', 'Battery_Total_Current', 'Battery_Total_Power', 'Load_Voltage', 'Load_Current', 'Load_Power', 'Inverter_Voltage', 'Inverter_Current', 'Inverter_Power', 'Motor_One_Voltage', 'Motor_One_Current', 'Motor_One_Power',
          'Motor_Two_Voltage', 'Motor_Two_Current', 'Motor_Two_Power', 'Five_Volt_Voltage', 'Five_Volt_Current', 'Five_Volt_Power', 'Windspeed', 'Outdoor_Temp', 'Outdoor_Humidity', 'System_Temp', 'System_Humidity', 'Azimuth_Reading', 'Azimuth_Command', 'Azimuth_Motor_Mode', 'Azimuth_Motor_Status', 'Elevation_Reading', 'Elevation_Command', 'Elevation_Motor_Mode', 'Elevation_Motor_Status']

try:
    ser = serial.Serial(port, baud)  # 9600 8N1 default
except serial.SerialException:
    ser = serial.Serial() # the serial port isn't available, create a closed interface

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

    if glob.glob("*.csv"):
        file = open(glob.glob("*.csv", recursive=False)[0], 'a')
        writer = csv.DictWriter(file, fieldnames=header)
    else:
        file = open("new.csv", 'w')
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()

    while csvlines <= (30 * 60)/2:  # 30 mins @ 2 seconds per measurement

        while ser.readline() != "LOG\n":  # may miss one log at first startup, shouldnt be an issue
            pass

        rx_datetime = ser.readline()
        sys_state = ser.readline()

        solar_voltage = ser.readline()
        solar_current = ser.readline()
        solar_power = ser.readline()

        bat1_voltage = ser.readline()
        bat2_voltage = ser.readline()

        bat_tot_voltage = ser.readline()
        bat_tot_current = ser.readline()
        bat_tot_power = ser.readline()

        load_voltage = ser.readline()
        load_current = ser.readline()
        load_power = ser.readline()

        inverter_voltage = ser.readline()
        inverter_current = ser.readline()
        inverter_power = ser.readline()

        m1_voltage = ser.readline()
        m1_current = ser.readline()
        m1_power = ser.readline()

        m2_voltage = ser.readline()
        m2_current = ser.readline()
        m2_power = ser.readline()

        five_volt_voltage = ser.readline()
        five_volt_current = ser.readline()
        five_volt_power = ser.readline()

        wind_speed = ser.readline()

        out_temp = ser.readline()
        out_humid = ser.readline()

        azim_reading = ser.readline()
        azim_command = ser.readline()
        azim_mode = ser.readline()
        azim_status = ser.readline()

        elev_reading = ser.readline()
        elev_command = ser.readline()
        elev_mode = ser.readline()
        elev_status = ser.readline()

        # continue for each variable sent
        # ideally read a single json or dict and use json module / ast.literal_eval() to avoid having ~40 separate reads

        writer.writerow({'Date_Time': rx_datetime, 'System_Status': sys_state})
        if csvlines == 0:
            new_filename = "LOG_%s.csv" % rx_datetime
        csvlines += 1
    file.close()
    # using glob may be unnecessary here, there should almost never be existing csvs in the dir
    os.rename(glob.glob("*.csv")[0], "move/" + new_filename)
