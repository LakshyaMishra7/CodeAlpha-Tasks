"""
trailscope.py
TrailScope — Real-Time Object Detection & Tracking

Model    : YOLOv8 (Ultralytics)
Tracker  : ByteTrack (Ultralytics built-in)
Input    : webcam (default) or any video file
Output   : live preview window, optional annotated video export

This is a from-scratch rewrite of the CodeAlpha "object detection & tracking"
brief — same core stack (YOLOv8 + OpenCV, ByteTrack for identity persistence)
but a different visual language and a few extra features: per-track fading
motion trails, corner-bracket viewfinder boxes instead of full rectangles,
a bottom dashboard with mini bar-chart class counts, class filtering, and
optional video export.
"""

import argparse
import random
import time
from collections import defaultdict, deque

import cv2
from ultralytics import YOLO

FONT = cv2.FONT_HERSHEY_SIMPLEX

# ── Palette: teal / amber "recon" scheme ────────────────────────────────────
PANEL_BG   = (18, 24, 24)     # near-black teal panel
TEXT_MAIN  = (235, 235, 220)
TEXT_DIM   = (140, 150, 145)
ACCENT     = (60, 220, 190)   # teal accent (FPS / headline numbers)
WARN       = (60, 170, 235)   # amber-ish in BGR for alerts / rec dot


def track_color(track_id: int) -> tuple:
    """A stable, visually distinct BGR colour per tracked identity (not per class)."""
    seed = 1 if track_id is None else int(track_id)
    random.seed(seed * 97 + 13)
    return (random.randint(70, 255), random.randint(70, 255), random.randint(70, 255))


def draw_bracket_box(frame, x1, y1, x2, y2, color, thickness=2, arm=14):
    """Viewfinder-style corner brackets instead of a full rectangle."""
    for (px, py, dx, dy) in [
        (x1, y1, 1, 1), (x2, y1, -1, 1), (x1, y2, 1, -1), (x2, y2, -1, -1)
    ]:
        cv2.line(frame, (px, py), (px + dx * arm, py), color, thickness, cv2.LINE_AA)
        cv2.line(frame, (px, py), (px, py + dy * arm), color, thickness, cv2.LINE_AA)


def draw_id_chip(frame, x1, y1, text, color):
    """Small filled tag above the box, with a short pointer tab."""
    (tw, th), baseline = cv2.getTextSize(text, FONT, 0.5, 1)
    pad = 6
    chip_y2 = max(y1 - 4, th + baseline + 4)
    chip_y1 = chip_y2 - th - baseline - pad
    chip_x1, chip_x2 = x1, x1 + tw + pad * 2
    cv2.rectangle(frame, (chip_x1, chip_y1), (chip_x2, chip_y2), color, -1)
    cv2.putText(frame, text, (chip_x1 + pad, chip_y2 - baseline - 2),
                FONT, 0.5, (10, 10, 10), 1, cv2.LINE_AA)
    cv2.line(frame, (chip_x1 + 6, chip_y2), (chip_x1 + 6, y1), color, 2, cv2.LINE_AA)


def draw_trail(frame, points: deque, color):
    """Fading dotted trail of a track's recent center positions."""
    n = len(points)
    if n < 2:
        return
    for i in range(1, n):
        alpha = i / n
        radius = max(1, int(3 * alpha))
        faded = tuple(int(c * (0.35 + 0.65 * alpha)) for c in color)
        cv2.circle(frame, points[i], radius, faded, -1, cv2.LINE_AA)


def draw_dashboard(frame, fps: float, counts: dict, total: int, elapsed: float, recording: bool):
    """Bottom-of-frame dashboard: FPS, live count, mini bar-chart per class."""
    h, w = frame.shape[:2]
    bar_h = 34 + 20 * max(1, len(counts))
    y0 = h - bar_h

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, y0), (w, h), PANEL_BG, -1)
    cv2.addWeighted(overlay, 0.72, frame, 0.28, 0, frame)

    cv2.putText(frame, f"FPS {fps:4.1f}", (16, y0 + 24), FONT, 0.55, ACCENT, 1, cv2.LINE_AA)
    cv2.putText(frame, f"TRACKED {total}", (140, y0 + 24), FONT, 0.55, TEXT_MAIN, 1, cv2.LINE_AA)

    mins, secs = divmod(int(elapsed), 60)
    cv2.putText(frame, f"{mins:02d}:{secs:02d}", (w - 90, y0 + 24), FONT, 0.55, TEXT_DIM, 1, cv2.LINE_AA)

    if recording:
        blink = int(time.time() * 2) % 2 == 0
        if blink:
            cv2.circle(frame, (w - 110, y0 + 20), 5, (60, 60, 235), -1, cv2.LINE_AA)
        cv2.putText(frame, "REC", (w - 100, y0 + 24), FONT, 0.5, (60, 60, 235), 1, cv2.LINE_AA)

    if counts:
        max_count = max(counts.values())
        bar_x0 = 16
        bar_max_w = 160
        y = y0 + 46
        for cls_name, cnt in sorted(counts.items(), key=lambda kv: -kv[1]):
            bar_w = int(bar_max_w * (cnt / max_count))
            cv2.rectangle(frame, (bar_x0 + 90, y - 9), (bar_x0 + 90 + bar_w, y), ACCENT, -1)
            cv2.putText(frame, cls_name[:12], (bar_x0, y), FONT, 0.42, TEXT_MAIN, 1, cv2.LINE_AA)
            cv2.putText(frame, str(cnt), (bar_x0 + 90 + bar_w + 6, y), FONT, 0.42, TEXT_DIM, 1, cv2.LINE_AA)
            y += 20

    watermark = "TrailScope | YOLOv8 + ByteTrack"
    (tw, _), _ = cv2.getTextSize(watermark, FONT, 0.4, 1)
    cv2.putText(frame, watermark, (w - tw - 12, 22), FONT, 0.4, TEXT_DIM, 1, cv2.LINE_AA)


def parse_class_filter(raw: str, class_names: dict):
    """Turns '--classes person,car' into a set of matching class ids, or None for all."""
    if not raw:
        return None
    wanted = {name.strip().lower() for name in raw.split(",") if name.strip()}
    return {cid for cid, name in class_names.items() if name.lower() in wanted}


def run(source, model_path, conf_thresh, iou_thresh, show_conf, trail_len,
        class_filter_raw, save_path, no_track):

    print(f"[TrailScope] loading model: {model_path}")
    model = YOLO(model_path)
    class_names = model.names
    class_filter = parse_class_filter(class_filter_raw, class_names)
    print(f"[TrailScope] {len(class_names)} classes available"
          + (f" · filtering to {len(class_filter)} class(es)" if class_filter else ""))
    print(f"[TrailScope] source: {'webcam 0' if source == 0 else source}")
    print("[TrailScope] press Q to quit, S to save a snapshot\n")

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print("[TrailScope] ERROR — could not open that video source.")
        return

    writer = None
    if save_path:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        fps_in = cap.get(cv2.CAP_PROP_FPS) or 25
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        writer = cv2.VideoWriter(save_path, fourcc, fps_in, (w, h))
        print(f"[TrailScope] exporting annotated video to: {save_path}")

    trails = defaultdict(lambda: deque(maxlen=trail_len))
    fps_avg = 0.0
    prev_time = time.time()
    start_time = prev_time
    snap_count = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            print("[TrailScope] stream ended.")
            break

        if no_track:
            results = model.predict(frame, conf=conf_thresh, iou=iou_thresh, verbose=False)
        else:
            results = model.track(
                frame, conf=conf_thresh, iou=iou_thresh,
                tracker="bytetrack.yaml", persist=True, verbose=False,
            )

        counts = defaultdict(int)
        total = 0

        boxes = results[0].boxes
        if boxes is not None:
            for box in boxes:
                cls_id = int(box.cls[0])
                if class_filter is not None and cls_id not in class_filter:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                cls_name = class_names[cls_id]
                conf = float(box.conf[0])
                track_id = int(box.id[0]) if box.id is not None else None

                color = track_color(track_id if track_id is not None else cls_id)
                draw_bracket_box(frame, x1, y1, x2, y2, color)

                id_part = f"#{track_id} " if track_id is not None else ""
                conf_part = f" {conf:.0%}" if show_conf else ""
                draw_id_chip(frame, x1, y1, f"{id_part}{cls_name}{conf_part}", color)

                if track_id is not None:
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    trails[track_id].append((cx, cy))
                    draw_trail(frame, trails[track_id], color)

                counts[cls_name] += 1
                total += 1

        now = time.time()
        inst_fps = 1.0 / (now - prev_time + 1e-6)
        fps_avg = inst_fps if fps_avg == 0 else (0.9 * fps_avg + 0.1 * inst_fps)
        prev_time = now

        draw_dashboard(frame, fps_avg, dict(counts), total, now - start_time, writer is not None)

        cv2.imshow("TrailScope — Object Detection & Tracking", frame)
        if writer is not None:
            writer.write(frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            print("[TrailScope] quit requested.")
            break
        elif key == ord("s"):
            snap_count += 1
            snap_name = f"trailscope_snapshot_{snap_count}.png"
            cv2.imwrite(snap_name, frame)
            print(f"[TrailScope] saved {snap_name}")

    cap.release()
    if writer is not None:
        writer.release()
    cv2.destroyAllWindows()
    print("[TrailScope] session ended.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="TrailScope — YOLOv8 + ByteTrack real-time object detection & tracking"
    )
    parser.add_argument("--source", default="0",
                         help="0 for webcam, or a path to a video file")
    parser.add_argument("--model", default="yolov8n.pt",
                         help="Ultralytics YOLOv8 weights to load (auto-downloads if missing)")
    parser.add_argument("--conf", type=float, default=0.40, help="minimum detection confidence")
    parser.add_argument("--iou", type=float, default=0.45, help="NMS IoU threshold")
    parser.add_argument("--show-conf", action="store_true", help="show confidence % on each chip")
    parser.add_argument("--trail-len", type=int, default=20, help="motion-trail length in frames")
    parser.add_argument("--classes", default=None,
                         help="comma-separated class names to keep, e.g. 'person,car'")
    parser.add_argument("--save", default=None, help="path to write an annotated .mp4 copy")
    parser.add_argument("--no-track", action="store_true",
                         help="run detection only, without ByteTrack identity tracking")
    args = parser.parse_args()

    source = int(args.source) if args.source.isdigit() else args.source

    run(
        source=source,
        model_path=args.model,
        conf_thresh=args.conf,
        iou_thresh=args.iou,
        show_conf=args.show_conf,
        trail_len=args.trail_len,
        class_filter_raw=args.classes,
        save_path=args.save,
        no_track=args.no_track,
    )
