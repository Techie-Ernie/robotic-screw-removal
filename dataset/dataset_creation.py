
import cv2
from modlib.devices import AiCamera
import time
device = AiCamera(image_size=[2028,1520], frame_rate=1)  # Optimal frame rate for maximum DPS of the YOLO model running on the AI Camera
stream = device.__enter__()  # manually start camera context

def capture_frame():
    """Grab a single BGR frame from the AI camera."""
    frame = next(stream)
    img_rgb = frame.image
    return cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
time.sleep(15)
for i in range(80):
    frame = capture_frame()
    cv2.imwrite(f'dataset/frame{i+200}.jpg', frame)
device.__exit__(None, None, None)
cv2.destroyAllWindows()
