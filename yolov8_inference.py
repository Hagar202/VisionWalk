"""VisionWalk inference: person detection on images, videos and a live camera feed."""
import os

import cv2
from streamlit_webrtc import VideoTransformerBase
from ultralytics import YOLO

WEIGHTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weights")
FINETUNED_PATH = os.path.join(WEIGHTS_DIR, "best.pt")      # YOLOv8s fine-tuned on Caltech Pedestrian
PRETRAINED_PATH = os.path.join(WEIGHTS_DIR, "yolov8n.pt")  # COCO-pretrained YOLOv8n

PERSON_CLASS = 0
BOX_COLOR = (0, 255, 0)

# The pretrained model handles images and the live camera.
model_2 = YOLO(PRETRAINED_PATH)

# The fine-tuned model handles video. Fall back to the pretrained model if best.pt
# has not been downloaded yet (see weights/README.md).
if os.path.exists(FINETUNED_PATH):
    model = YOLO(FINETUNED_PATH)
else:
    print("weights/best.pt not found, using yolov8n.pt for video. See weights/README.md.")
    model = model_2


def draw_detections(frame, results, conf_threshold, label_prefix="Conf: "):
    """Draw a box and confidence label for every detected person."""
    for result in results:
        for box in result.boxes:
            if int(box.cls[0]) != PERSON_CLASS:
                continue
            conf = float(box.conf[0])
            if conf < conf_threshold:
                continue
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), BOX_COLOR, 2)
            cv2.putText(frame, f"{label_prefix}{conf:.2f}", (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, BOX_COLOR, 1)
    return frame


def detect_image(image_path, output_path):
    """Detect people in an image and save the annotated copy."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    results = model_2.predict(image_path, save=False, conf=0.5, classes=[PERSON_CLASS])
    frame = cv2.imread(image_path)
    draw_detections(frame, results, 0.5)
    cv2.imwrite(output_path, frame)
    return output_path


class LiveCamProcessor(VideoTransformerBase):
    """Runs detection on each frame from the browser camera."""

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        results = model_2.predict(img, conf=0.4, save=False, classes=[PERSON_CLASS], verbose=False)
        return draw_detections(img, results, 0.4, label_prefix="")


def detect_video(video_path, output_path):
    """Detect people frame by frame and write an annotated .webm video."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25

    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"vp80"), fps, (width, height))
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        results = model.predict(frame, save=False, conf=0.5, classes=[PERSON_CLASS], verbose=False)
        out.write(draw_detections(frame, results, 0.5))

    cap.release()
    out.release()
    return output_path
