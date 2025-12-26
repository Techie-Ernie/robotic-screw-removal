import cv2
import serial
import time
from picamera2 import Picamera2
from ultralytics import YOLO

# Initialize the Picamera2
picam2 = Picamera2()
picam2.preview_configuration.main.size = (1280, 720)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()
    
# Load the YOLO11 model
model = YOLO("yolo11n.pt")

# setup serial communication
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser.reset_input_buffer()


while True:
    frame = picam2.capture_array()

    results = model(frame)

    annotated_frame = results[0].plot()

    # check if bottle exists
    boxes = results[0].boxes
    if boxes is not None and len(boxes) > 0:
        # Find the prediction with the highest confidence
        top = boxes.conf.argmax()
        cls_id = int(boxes.cls[top])
        conf = boxes.conf[top].item()
        label = model.names[cls_id]

        print(f"Top prediction: {label} ({conf:.2f})")
    
        if label == "bottle":
            ser.write(b"bottle")
            #line = ser.readline().decode('utf-8').rstrip()
            #print(line)
            time.sleep(1)

    cv2.imshow("Camera", annotated_frame)

    if cv2.waitKey(1) == ord("q"):
        break

cv2.destroyAllWindows()