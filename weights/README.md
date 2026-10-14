# Model weights

| File | What it is | How to get it |
|---|---|---|
| `yolov8n.pt` | COCO-pretrained YOLOv8n, used for images and the live camera | Included in this folder |
| `best.pt` | YOLOv8s fine-tuned on the Caltech Pedestrian dataset, used for video | Download from the [latest release](https://github.com/Hagar202/VisionWalk/releases/latest) and place it here |

If `best.pt` is missing, the app still runs and uses `yolov8n.pt` for video too.
