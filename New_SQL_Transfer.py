#!/usr/bin/python2
from __future__ import print_function
import csv
import MySQLdb
import os
import time
import conf
import glob

src = 'datalogs/'
dst = 'archive/'

def intake_csv(filename):
    mydb = MySQLdb.connect(host='bingdev-db.binghamton.edu',
                           user='watsonsolar', passwd=conf.sql_passwd, db='watsonsolar')
    cursor = mydb.cursor()
    file = open(filename, 'r')
    reader = csv.reader(file)
    for idx, row in enumerate(reader):
        if (idx != 0): # skip the header
            cursor.execute('INSERT INTO %s VALUES(%s)',conf.sql_table, row) # check, will substitution work here
    mydb.commit()
    cursor.close()
    file.close()
    os.rename(filename, dst+(filename.split('/')[-1]))

while 1:
    if glob.glob(src+'*.csv'):
        for file in glob.glob(src+'*.csv'):
            intake_csv(file)
    time.sleep(15*60) # wait for 15 minutes

# while True:
#     while True:
#         datestring = datetime.strftime(datetime.now(), '%Y_%m_%d_%H_%M_%S')
#         for file in os.listdir(src):
#             i = 1
#             break

#         if i != 0:
#             i = 0
#             break

#         print(datestring)
#         print('Waiting for new file')
#         print
#         # change to 120? (check every 2 minutes for a new file)
#         time.sleep(15)

#     for file in os.listdir(src):
#         src_file = os.path.join(src, file)
#         dst_file = os.path.join(dst, file)
#         print(src_file)

#         # open the connection to the MySQL server
#         # using MySQL
#         mydb = MySQLdb.connect(host='bingdev-db.binghamton.edu',
#                                user='watsonsolar', passwd=conf.sql_passwd, db='watsonsolar')
#         print(mydb)
#         cursor = mydb.cursor()
#         with open(src_file, 'rb') as csvfile:
#             csv_data = csv.reader(csvfile)
#             # execute and insert the the csv into the database.
#             j = 0
#             for row in csv_data:
#                 if j == 1:
#                     cursor.execute('INSERT INTO GOLDEN(Date_Time,System_Status,Solar_Panel_Voltage,Solar_Panel_Current,Solar_Panel_Power, \
#                                 Battery_One_Voltage,Battery_Two_Voltage,Battery_Total_Voltage,Battery_Total_Current,Battery_Total_Power,Load_Voltage, \
#                                 Load_Current,Load_Power,Inverter_Voltage,Inverter_Current,Inverter_Power,Motor_One_Voltage,Motor_One_Current,Motor_One_Power, \
#                                 Motor_Two_Voltage,Motor_Two_Current,Motor_Two_Power,Five_Volt_Voltage,Five_Volt_Current,Five_Volt_Power,Windspeed,Outdoor_Temp, \
#                                 Outdoor_Humidity,System_Temp,System_Humidity,Azimuth_Reading,Azimuth_Command,Azimuth_Motor_Mode,Azimuth_Motor_Status,Elevation_Reading, \
#                                 Elevation_Command,Elevation_Motor_Mode,Elevation_Motor_Status)'
#                                    'VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', row)

#                     cursor.execute('INSERT INTO GOLDEN2(Date_Time,System_Status,Solar_Panel_Voltage,Solar_Panel_Current,Solar_Panel_Power, \
#                                 Battery_One_Voltage,Battery_Two_Voltage,Battery_Total_Voltage,Battery_Total_Current,Battery_Total_Power,Load_Voltage, \
#                                 Load_Current,Load_Power,Inverter_Voltage,Inverter_Current,Inverter_Power,Motor_One_Voltage,Motor_One_Current,Motor_One_Power, \
#                                 Motor_Two_Voltage,Motor_Two_Current,Motor_Two_Power,Five_Volt_Voltage,Five_Volt_Current,Five_Volt_Power,Windspeed,Outdoor_Temp, \
#                                 Outdoor_Humidity,System_Temp,System_Humidity,Azimuth_Reading,Azimuth_Command,Azimuth_Motor_Mode,Azimuth_Motor_Status,Elevation_Reading, \
#                                 Elevation_Command,Elevation_Motor_Mode,Elevation_Motor_Status)'
#                                    'VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', row)
#                 if j > 1:
#                     cursor.execute('INSERT INTO GOLDEN(Date_Time,System_Status,Solar_Panel_Voltage,Solar_Panel_Current,Solar_Panel_Power, \
#                 		Battery_One_Voltage,Battery_Two_Voltage,Battery_Total_Voltage,Battery_Total_Current,Battery_Total_Power,Load_Voltage, \
#                 		Load_Current,Load_Power,Inverter_Voltage,Inverter_Current,Inverter_Power,Motor_One_Voltage,Motor_One_Current,Motor_One_Power, \
#                 		Motor_Two_Voltage,Motor_Two_Current,Motor_Two_Power,Five_Volt_Voltage,Five_Volt_Current,Five_Volt_Power,Windspeed,Outdoor_Temp, \
#                 		Outdoor_Humidity,System_Temp,System_Humidity,Azimuth_Reading,Azimuth_Command,Azimuth_Motor_Mode,Azimuth_Motor_Status,Elevation_Reading, \
#                 		Elevation_Command,Elevation_Motor_Mode,Elevation_Motor_Status)'
#                                    'VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', row)
#                 j = j+1
#             print("CSV has been imported into the database")

#         shutil.move(src_file, dst_file)
#         print('A file has been moved: ', file)
#         time.sleep(1)

#         # close the connection to the database.
#         mydb.commit()
#         cursor.close()
