import numpy as np
import serial
import cv2
import time 
from grbl import GRBL
from screw_detection import ScrewDetectionModel
from modlib.devices import AiCamera
from imx_detect import detect_frame, YOLO

CALIB_FILE = "calib_planar.npz"
GRBL_PORT = "/dev/ttyACM0"
GRBL_BAUD = 115200
SCREWDRIVER_BAUD = 9600 # set baud rate for communication with second Arduino
FEED_MM_MIN = 800    # motion feedrate
G54_OFFSET_X = 0.0   # mm offset   
G54_OFFSET_Y = 0.0

def actuate_screwdriver(ser):
    ser.write(b"D")
    time.sleep(2)
    ser.write(b"R")
    ser.write(b"D")
    time.sleep(1)
    ser.write(b"S")
    ser.write(b"U")


# Import saved calibration (H)
def load_calib(path=CALIB_FILE):
    data = np.load(path)
    return data["H"]

def pix_to_mm(u, v, H):
    pt = np.array([u, v, 1.0])
    world = H @ pt
    world /= world[2]
    x_mm, y_mm = float(world[0]), float(world[1])
    x_mm = x_mm + G54_OFFSET_X
    y_mm = y_mm + G54_OFFSET_Y
    return x_mm, y_mm
    
def main():
    print("started")
    H = load_calib()
    robot = GRBL(GRBL_PORT, GRBL_BAUD)

    ser = serial.Serial('/dev/ttyACM1', SCREWDRIVER_BAUD, timeout=1)
    ser.reset_input_buffer()

    device = AiCamera(image_size=[2028, 1520], frame_rate=16)
    model = YOLO()
    device.deploy(model)
    with device as stream:
        while True:
            frame = next(stream)
            img_bgr = cv2.cvtColor(frame.image, cv2.COLOR_RGB2BGR)
            smaller_frame = cv2.resize(img_bgr, (507*3, 380*3))
            smaller_frame = cv2.cvtColor(smaller_frame, cv2.COLOR_RGB2BGR)
            cv2.imshow("camera feed", smaller_frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('c'):
                print("detecting...")
                # send frame 
                detections = detect_frame(frame=frame)
                time.sleep(5)
                cv2.destroyAllWindows()

                for (u, v) in detections:
                    x_mm, y_mm = pix_to_mm(u, v, H)
                    print(f"[Target] Pixel=({u:.1f},{v:.1f}) → World=({x_mm:.2f},{y_mm:.2f}) mm")
                    confirm_move = input(f"Confirm movement to {x_mm}, {y_mm}: ").strip().lower()
                    if confirm_move == "y":
                        robot.move_linear(x_mm, y_mm)
                    else:
                        break
                    ask_grbl = input("Move using GRBL?").strip().lower()
                    if ask_grbl == 'y': # manual adjustment if screw is not positioned correctly
                        done = False
                        while not done:
                            x = input('x: ')
                            y = input('y: ')
                            
                            robot.move_relative(x, y)
                            
                            ask_done = input("Confirm? (y/n): ").strip().lower()
                            if ask_done == 'y':
                                done = True

                    confirm_actuate = input(f"Confirm unscrew?").strip().lower()
                    if confirm_actuate == "y": 
                        actuate_screwdriver(ser)
                    else:
                        break
                    
                break 
            elif key == ord('q'):
                print('quitting')
                break
    
    robot.close()


if __name__ == "__main__":
    main()
