#!/usr/bin/python3

#####################################################
# Watson Capstone Projects
# Team ECD311 - Solar Tracking Project
# Team Members - Carson Singh, Selman Oguz, Adam Young, Bea Mulvey
# Advisor - Tara Dhakal
# Instructor - Meghana Jain
#####################################################

import serial # https://pypi.org/project/pyserial/ - provides interactions with serial ports
import csv # builtin module - used here to write to csv files
import os # builtin module - used here for some file operations
import glob # builtin module - used here for filename pattern matching
import ast # builtin module - used here to translate the string representation of a dictionary to an actual python dictionary
from paramiko import SSHClient # https://pypi.org/project/paramiko/ - python implementation of SSHv2
from scp import SCPClient # https://pypi.org/project/scp/ - python bindings for the SCP protocol, using paramiko for SSH
import cachetools # https://pypi.org/project/cachetools/ - used here to cache weather data to avoid too many requests to the openweathermap api
from pyowm import owm # https://pypi.org/project/pyowm/ - python wrapper for the openweathermap api
import sys # builtin module - used here for error handling
from pysolar.solar import get_altitude, get_azimuth # https://pypi.org/project/pysolar/ - python module for simulating solar irradation of the earth
from pysolar.util import get_sunrise_sunset # see above
from datetime import datetime, timezone, timedelta # builtin module - provides objects for date and time interactions
import cronitor # https://pypi.org/project/cronitor/ - python module for interacting with the cronitor service
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

# set api key for cronitor - used for monitoring and alerting about performance
cronitor.api_key = conf.cronitor_api_key

# get the current conditions from openweathermap to be logged with each data point
#   theoretically could be used to correlate power production and consumption with the weather
# 5 minute cache
@cachetools.cached(cache=cachetools.TTLCache(ttl=60*5, maxsize=1))
def get_weather():
    try:
        retval = mgr.weather_at_place(conf.owm_location).weather.detailed_status
    except:
        retval = "conditions unavailable"
    return retval


# calculate the current position of the sun
def get_current_position():  # {'azimuth': azimuth, 'altitude': altitude}
    azimuth = get_azimuth(conf.suncalc_lat, conf.suncalc_lon,
                          datetime.now(tz=timezone.utc))
    altitude = get_altitude(
        conf.suncalc_lat, conf.suncalc_lon, datetime.now(tz=timezone.utc))
    return {'azimuth': azimuth, 'altitude': altitude}


# calculate today's sunrise and sunset time, along with the position of the sun at sunrise
def get_suntimes():  # (sunrise, sunset, azimuth @ sunrise, altitude @ sunrise)
    times = get_sunrise_sunset(
        conf.suncalc_lat, conf.suncalc_lon, datetime.now(tz=timezone.utc))
    sunrise_position_azim = get_azimuth(
        conf.suncalc_lat, conf.suncalc_lon, times[0])
    sunrise_position_alt = get_altitude(
        conf.suncalc_lat, conf.suncalc_lon, times[0])
    return (times[0], times[1], sunrise_position_azim, sunrise_position_alt)


# upload all pending data to bingdev
# should handle reattempting failed transfers
@cronitor.job('upload_data')
def upload_data():
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect('34.238.23.117', username='watsolar')

    scp = SCPClient(ssh.get_transport())

    new_filename = "data_log_" + rx_datetime_first + ".csv"
    os.rename(glob.glob("/home/pi/Scripts/*.csv")
              [0], "/home/pi/Scripts/move/" + new_filename)
    for filename in glob.glob("/home/pi/Scripts/move/*.csv"):
        try:
            scp.put(filename, remote_path='datalogs/')
        except:
            # scp.close()
            # ssh.close()
            print('issue sending csv')
            sys.stderr.write(
                "ERR: Failed to upload file %s to bingdev\r\n" % filename)
            continue
        os.rename(filename, "/home/pi/Scripts/moved/" +
                  filename.split('/')[-1])
    # os.rename("move/" + new_filename, "moved/" + new_filename)
    scp.close()
    ssh.close()
    sys.stdout.write("LOG: Uploaded files to bingdev\r\n")
    print("send data")


# handle receiving data from arduino and writing into a csv file
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


# attempt to detect which serial port the arduino is connected to
# unlikely to be necessary in reality but it has come up when testing
ports = glob.glob("/dev/ttyACM*")
if ports:
    port = ports[0]
else:
    sys.stderr.write("ERR: No serial ports available\r\n")
    port = ""
baud = 115200

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
    sys.stderr.write(
        "ERR: Unable to send start string - arduino will not start up")


# terminate script every 12 hours
# systemd service handles restarting automatically, although if there are too many failures in a short period of time it will give up
while (datetime_start < (datetime_start + timedelta(hours=12))):

    csvlines = 0
    firstrun = 1

    # open existing csv if it exists, otherwise create a new one
    if glob.glob("/home/pi/Scripts/*.csv"):
        file = open(glob.glob("/home/pi/Scripts/*.csv",
                    recursive=False)[0], 'a')
        writer = csv.DictWriter(file, fieldnames=newheader)
    else:
        file = open("/home/pi/Scripts/new.csv", 'w')
        writer = csv.DictWriter(file, fieldnames=newheader)
        writer.writeheader()

    while csvlines <= (30 * 60)/2:  # 30 mins @ 2 seconds per measurement

        # may miss one log at first startup, shouldnt be an issue
        try:
            line = ser.readline().rstrip().decode("utf-8")
        except:
            line = ""

        # handle the 3 possible cases for input from arduino
        #   log - intake fresh data from arduino and write into csv
        #   position - calculate and send the current position of the sun to the arduino
        #   times - calculate and send today's sunrise and sunset times, as well as the position of the sun at sunrise
        if (line == "LOG"):
            if (rx_data(writer) == 0):
                csvlines += 1
                file.flush()
                os.fsync(file.fileno())
        elif (line == "new_position"):  # azimuth, then altitude in degrees
            print("position")
            location = get_current_position()
            azim = b"%i\n" % int(location['azimuth'])
            elev = b"%i\n" % int(location['altitude'])
            ser.write(azim)
            ser.write(elev)
            print("azimuth: %d" % int(location['azimuth']))
            print("elevation: %d" % int(location['altitude']))

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
