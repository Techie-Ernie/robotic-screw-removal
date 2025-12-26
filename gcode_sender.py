import serial
import time

PORT = "/dev/ttyACM0"
BAUD = 115200

ser = serial.Serial(PORT, BAUD)
time.sleep(2)
ser.flushInput()

# Unlock
ser.write(b"$X\n")
time.sleep(0.1)

# Set units and mode
ser.write(b"G21\n")   
ser.write(b"G91\n")   


ser.write(b"$3=2\n") # flip y axis
time.sleep(0.1)
#ser.write(b"$3=1\n") # flip x axis



# follow x and y-axis according to YOLO
# Down: +ve y 
# Right: +ve x 
time.sleep(0.1)

ser.write(b"$100=5.1\n")
ser.write(b"$101=5.2\n")
ser.write(b"$110=4000\n")
ser.write(b"$111=4000\n")
time.sleep(0.1)

try:
    while True:
        cmd = input("> ").strip()

        if cmd.lower() in ["q", "quit", "exit"]:
            break

        
        if cmd == "?":
            ser.write(b"?")  
            time.sleep(0.03)

            if ser.in_waiting:
                line = ser.readline().decode().strip()
                print("GRBL:", line)
            else:
                print("GRBL: (no response)")

            continue  

       
        ser.write((cmd + "\n").encode())

        while True:
            if ser.in_waiting:
                line = ser.readline().decode().strip()
                print("GRBL:", line)
                if line.startswith("ok") or line.startswith("error"):
                    break
            else:
                time.sleep(0.01)

finally:
    ser.close()
    print("Closed serial connection.")
