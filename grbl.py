import serial
import time
FEED_MM_MIN = 800    # motion feedrate

class GRBL:
    def __init__(self, port, baud):
        self.s = serial.Serial(port, baud, timeout=1)
        time.sleep(2)  # allow GRBL reset
        self.cmd("$X")      # unlock
        self.cmd("G21")     # mm mode
        self.cmd("G90")     # absolute coords
        self.cmd("$3=2")
        self.cmd("$100=5.1")
        self.cmd("$101=5.2")
        #self.cmd("G10 L2 P1 X-105.87 Y-34.43")
        #self.cmd("G10 L2 P1 X10 Y20 Z0")  # G54 origin = (10, 20, 0) mm from machine zero
        self.cmd("G54")     
        
        time.sleep(0.1)

    def cmd(self, g):
        self.s.write((g + "\n").encode())
        self.s.flush()
        while True:
            line = self.s.readline().decode(errors="ignore").strip()
            if not line:
                break
            if line == "ok" or "error" in line:
                break

    def move_linear(self, x=None, y=None, f=FEED_MM_MIN):
        cmd = "G1"
        if x is not None: cmd += f" X{float(x):.3f}"
        if y is not None: cmd += f" Y{float(y):.3f}"
        cmd += f" F{f}"
        self.cmd(cmd)

    def close(self):
        self.s.close()
