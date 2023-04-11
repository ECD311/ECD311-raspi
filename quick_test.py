import serial
import time

ser = serial.Serial("/dev/ttyACM0", 115200)

while 1:
    ser.write(b"-324\r\n")
    print(ser.readline().decode("utf-8").rstrip())