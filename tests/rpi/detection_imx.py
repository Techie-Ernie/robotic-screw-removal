import numpy as np
from modlib.apps import Annotator
from modlib.devices import AiCamera
from modlib.models import COLOR_FORMAT, MODEL_TYPE, Model
from modlib.models.post_processors import pp_od_yolo_ultralytics

# model.export(format="imx", data="coco8.yaml")  
# exports with PTQ quantization by default
    

class YOLO(Model):
    """YOLO model for IMX500 deployment."""

    def __init__(self):
        """Initialize the YOLO model for IMX500 deployment."""
        super().__init__(
            model_file="../../imx_model/packerOut.zip",  
            model_type=MODEL_TYPE.CONVERTED,
            color_format=COLOR_FORMAT.RGB,
            preserve_aspect_ratio=False,
        )

        self.labels = np.genfromtxt(
            "../../imx_model/labels.txt",  
            dtype=str,
            delimiter="\n",
        )

    def post_process(self, output_tensors):
        """Post-process the output tensors for object detection."""
        return pp_od_yolo_ultralytics(output_tensors)


device = AiCamera(image_size=[2028,1520], frame_rate=10) 
model = YOLO()
device.deploy(model)
annotator = Annotator()

with device as stream:
    for frame in stream:
        detections = frame.detections
        
        if len(detections) > 0:
            filtered_detections = detections[detections.confidence > 0.34]
            
            if len(filtered_detections) > 0:
                # Ensure arrays are at least 1D
                class_ids = np.atleast_1d(filtered_detections.class_id)
                confidences = np.atleast_1d(filtered_detections.confidence)
                print(filtered_detections)
                # Create labels
                try:
                        labels = [f"{model.labels[int(cid)]}: {conf:0.2f}" for cid, conf in zip(class_ids, confidences)]
             
                        annotator.annotate_boxes(frame, filtered_detections, labels=labels, alpha=0.3, corner_radius=10)
                except:
                        pass
        frame.display()
