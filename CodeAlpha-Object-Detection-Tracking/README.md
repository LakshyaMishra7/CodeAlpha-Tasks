# TrailScope — Object Detection & Tracking (Task 4)

A real-time object detection and multi-object tracking tool built with
**YOLOv8 (Ultralytics)**, **ByteTrack**, and **OpenCV** — the same stack the
brief calls for — with its own visual identity and a couple of extra
features on top of the base requirements.

## Features
- Real-time detection with YOLOv8, on webcam or any video file
- Persistent identity tracking via ByteTrack
- Viewfinder-style corner-bracket boxes (instead of full rectangles)
- Fading motion trails behind each tracked object
- Bottom dashboard: live FPS, tracked-object count, session timer, and a
  mini bar-chart breakdown by class
- Optional class filtering (`--classes person,car`)
- Optional annotated video export (`--save output.mp4`)
- Snapshot capture with the `S` key while running
- Toggle to run detection only, without tracking (`--no-track`)

## How it maps to the task brief
| Brief requirement | Where it's handled |
|---|---|
| Real-time video input (webcam or file), via OpenCV | `cv2.VideoCapture` in `run()` |
| Pre-trained detection model (YOLO) | `YOLO(model_path)` (Ultralytics YOLOv8) |
| Process each frame, draw bounding boxes | per-frame loop + `draw_bracket_box()` |
| Object tracking (SORT-family algorithm) | ByteTrack via `model.track(...)` |
| Display labels and tracking IDs live | `draw_id_chip()` + `cv2.imshow()` |

## Install
```bash
pip install -r requirements.txt
```
(Or `python -m pip install -r requirements.txt` on Windows if `pip` isn't on
your PATH.)

The first run will auto-download the YOLOv8n weights (~6 MB) — no model file
needs to be bundled with the project.

## Run it
```bash
# Webcam
python trailscope.py

# A video file
python trailscope.py --source path/to/video.mp4

# Show confidence scores too
python trailscope.py --source path/to/video.mp4 --show-conf

# Only track people and cars, export the annotated result
python trailscope.py --source video.mp4 --classes person,car --save output.mp4

# Detection only, no tracking IDs
python trailscope.py --no-track
```

Press **Q** to quit, **S** to save a snapshot of the current frame.

## Design notes
TrailScope instead colours boxes per
*tracked identity* (so the same object keeps one colour across the whole
clip), draws only the corner brackets of each box for a lighter "viewfinder"
feel, leaves a short fading trail behind moving objects, and moves the stats
into a bottom dashboard with a small bar-chart instead of a plain list.
