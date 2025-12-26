
import cv2
from modlib.devices import AiCamera
device = AiCamera(image_size=[2028,1520], frame_rate=10)  # Optimal frame rate for maximum DPS of the YOLO model running on the AI Camera
stream = device.__enter__()  # manually start camera context

def capture_frame():
    """Grab a single BGR frame from the AI camera."""
    frame = next(stream)
    img_rgb = frame.image
    return cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)


while True:
    frame = capture_frame()
    cv2.imshow("camera feed", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'):
        print('gurt')
    elif key == ord('q'):
        print("quitting")
        break
device.__exit__(None, None, None)
cv2.destroyAllWindows()
