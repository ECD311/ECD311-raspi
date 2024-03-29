#!/usr/bin/python2

#####################################################
# Watson Capstone Projects
# Team ECD311 - Solar Tracking Project
# Team Members - Carson Singh, Selman Oguz, Adam Young, Bea Mulvey
# Advisor - Tara Dhakal
# Instructor - Meghana Jain
#####################################################

# this is a complete rewrite of the old code to take the contents of uploaded csv files and put them in the sql server
# the old code is commented at the bottom file for posterity, but some of the choices made when writing don't make a lot of sense so it may not be useful
# this no longer sits in an infinite loop and is now periodically run using a cron job


from __future__ import print_function
import csv
import MySQLdb
import os
import conf
import glob
import sys

src = 'datalogs/'
dst = 'archive/'


# read each row in the provided csv file with the exception of the header, and insert it into the table specified in conf.py
def intake_csv(filename):
    try:
        mydb = MySQLdb.connect(host='bingdev-db.binghamton.edu',
                           user='watsonsolar', passwd=conf.sql_passwd, db='watsonsolar')
    except:
        sys.stderr.write("Failed to connect to SQL database\r\n")
        return -1
    cursor = mydb.cursor()
    file = open(filename, 'r')
    reader = csv.reader(file)
    for idx, row in enumerate(reader):
        if (idx != 0): # skip the header
            string = ''
            for idx, element in enumerate(row):
                if(idx == 0):
                    string += "'%s'" % element
                else:
                    string += ",'%s'" % element 
            try:
                cursor.execute('INSERT INTO %s VALUES(%s)' % (conf.sql_table, string))
            except:
                # this typically seems to happen if the contents of the csv file are malformed - this is likely if there are any spaces in strings
                # although building up a string containing each element of the row seems to mitigate this issue
                sys.stderr.write("ERR: Failed to execute SQL query\r\n")
                mydb.commit()
                cursor.close()
                file.close()
                return -2
    mydb.commit()
    cursor.close()
    file.close()
    # move the file to the destination folder after the contents are successfully inserted into the sql table
    os.rename(filename, dst+(filename.split('/')[-1]))
    return 0


# iterate over all files in the source directory, and insert the contained data to the sql server
if glob.glob(src+'*.csv'):
    for filename in glob.glob(src+'*.csv'):
        retval = intake_csv(filename)
        if (retval != 0):
            pass # todo: do something to log/notify about errors

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
