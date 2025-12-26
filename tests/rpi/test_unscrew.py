import serial
import time

ser = serial.Serial('/dev/ttyACM1', 9600, timeout=1) # set up serial communication with Arduino UNO at 9600 baud
ser.reset_input_buffer()

# this lowers the tool head for unscrewing
ser.write(b"D")
time.sleep(2)
ser.write(b"R")
ser.write(b"D")
time.sleep(1)
ser.write(b"S")
ser.write(b"U")
time.sleep(0.1)
if ser.in_waiting > 0:
    line = ser.readline().decode("utf-8", errors="ignore").rstrip()
    print("Arduino:", line)