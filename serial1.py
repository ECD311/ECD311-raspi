import serial
import csv
import ast



port = '/dev/ttyACM0'
baud = 115200

header = ['voltage', 'current']

ser = serial.Serial(port, baud)  # 9600 8N1 default

file = open("new.csv", 'w')
writer = csv.DictWriter(file, fieldnames=header)
writer.writeheader()

while(1):
    while ser.readline().rstrip().decode("utf-8") != "LOG":
            pass
    dict = ast.literal_eval(ser.readline().rstrip().decode("utf-8"))
    writer.writerow(dict)
