# measure_and_recommend_depth.py
import cv2
import numpy as np
import json
import csv
import itertools
import pyrealsense2 as rs
import time
import os

# Files
CALIB_FILE = 'calibration.json'      # from checkerboard: {"mm_per_pixel": ...}
DEPTH_CALIB = 'depth_calib.json'     # from depth_calibration.py: {"median_belt_depth_mm": ...}
BOX_CSV = 'box_catalog.csv'

# Safety / params
PADDING_MM = 5.0       # padding inside box
MIN_CONTOUR_AREA = 5000  # pixels (tune based on camera resolution)
DEPTH_PERCENTILE = 5.0  # percentile to estimate closest depth in contour (small percentile -> near object)
DEPTH_NOISE_MM = 5.0    # expected depth noise to add to margin

# Load config
with open(CALIB_FILE, 'r') as f:
    mm_per_px = float(json.load(f)['mm_per_pixel'])
with open(DEPTH_CALIB, 'r') as f:
    depth_calib = json.load(f)
belt_depth_mm = float(depth_calib['median_belt_depth_mm'])
depth_scale_m_per_unit = float(depth_calib['depth_scale_m_per_unit'])

# load box catalog
boxes = []
with open(BOX_CSV,'r') as f:
    rdr = csv.DictReader(f)
    for r in rdr:
        boxes.append({'id': r['id'], 'label': r['label'],
                      'L': float(r['L_mm']), 'W': float(r['W_mm']), 'H': float(r['H_mm'])})

# set up realsense pipeline
pipeline = rs.pipeline()
cfg = rs.config()
cfg.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
cfg.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
profile = pipeline.start(cfg)
align = rs.align(rs.stream.color)  # align depth to color

print("System ready. Press SPACE to capture an object measurement. ESC to quit.")

try:
    while True:
        frames = pipeline.wait_for_frames()
        aligned = align.process(frames)
        depth_frame = aligned.get_depth_frame()
        color_frame = aligned.get_color_frame()
        if not depth_frame or not color_frame:
            continue
        depth_image = np.asanyarray(depth_frame.get_data())  # uint16 depth units
        color_image = np.asanyarray(color_frame.get_data())  # BGR

        disp = color_image.copy()
        cv2.putText(disp, "Press SPACE to measure, ESC to exit", (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        cv2.imshow('stream', cv2.resize(disp, (1280,720)))
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break
        if key != 32:
            continue

        # --- segmentation / object mask (simple approach)
        gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = np.ones((5,5), np.uint8)
        th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel, iterations=2)

        cnts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not cnts:
            print("No object detected. Reposition and try again.")
            continue
        c = max(cnts, key=cv2.contourArea)
        if cv2.contourArea(c) < MIN_CONTOUR_AREA:
            print("Object too small / noise. Reposition.")
            continue

        x,y,w,h = cv2.boundingRect(c)
        # L and W in mm (pixel width -> mm)
        L_obj_mm = w * mm_per_px
        W_obj_mm = h * mm_per_px

        # Get depth pixels inside contour
        mask = np.zeros(depth_image.shape, dtype=np.uint8)
        cv2.drawContours(mask, [c], -1, 255, -1)
        depth_vals_units = depth_image[mask==255].astype(np.float32)
        if depth_vals_units.size == 0:
            print("No depth values found inside contour. Try again.")
            continue

        # Convert depth units -> mm
        depth_vals_m = depth_vals_units * depth_scale_m_per_unit
        depth_vals_mm = depth_vals_m * 1000.0

        # Estimate object surface depth -> use small percentile to robustly pick near-surface
        p = np.percentile(depth_vals_mm, DEPTH_PERCENTILE)
        # clamp and sanity-check: object must be closer than belt_depth_mm
        object_depth_mm = float(p)
        if object_depth_mm >= belt_depth_mm - 1.0:
            # This means depth reading similar to belt — object might be flat or poor depth reading
            # fallback: use min depth (robust) or ask operator
            object_depth_mm = float(np.min(depth_vals_mm))

        # Compute height = belt_depth_mm - object_depth_mm
        H_obj_mm = max(0.0, belt_depth_mm - object_depth_mm)

        # Add small correction for expected noise
        H_obj_mm = max(0.0, H_obj_mm - DEPTH_NOISE_MM)

        dims = [L_obj_mm, W_obj_mm, H_obj_mm]
        obj_vol = dims[0] * dims[1] * dims[2] if dims[2] > 0 else dims[0]*dims[1]*10.0  # fallback small height

        # Evaluate boxes - try orientations
        candidates = []
        for b in boxes:
            bvol = b['L'] * b['W'] * b['H']
            best_orient = None
            for orient in itertools.permutations(dims, 3):
                if orient[0] + PADDING_MM <= b['L'] and orient[1] + PADDING_MM <= b['W'] and orient[2] + PADDING_MM <= b['H']:
                    wasted = bvol - obj_vol
                    candidates.append((b, wasted, orient))
                    best_orient = orient
                    break

        if not candidates:
            print("No candidate box fits. Consider increasing box catalog or padding settings.")
            # still save snapshot
            out = color_image.copy()
            cv2.rectangle(out, (x,y), (x+w, y+h), (0,0,255), 2)
            cv2.putText(out, "No box fits", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
            fname = f"measure_fail_{int(time.time())}.png"
            cv2.imwrite(fname, out)
            print("Saved snapshot:", fname)
            continue

        candidates.sort(key=lambda x: x[1])
        best = candidates[0]
        b, wasted, orient = best

        # Save & annotate
        out = color_image.copy()
        cv2.rectangle(out, (x,y), (x+w,y+h), (0,255,0), 2)
        txt = f"Box:{b['label']} | L={dims[0]:.1f} W={dims[1]:.1f} H={dims[2]:.1f} mm"
        cv2.putText(out, txt, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        cv2.putText(out, f"Orient: {orient[0]:.1f},{orient[1]:.1f},{orient[2]:.1f}", (10,60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
        fname = f"measure_{int(time.time())}.png"
        cv2.imwrite(fname, out)
        print("\nRecommended box:", b['label'], f"({b['id']})")
        print("Box dims (mm):", b['L'], b['W'], b['H'])
        print("Measured object dims (mm): L=%.1f W=%.1f H=%.1f" % tuple(dims))
        print("Orientation to place (L_obj, W_obj, H_obj):", orient)
        print("Wasted volume (mm^3):", wasted)
        print("Snapshot saved:", fname)

finally:
    pipeline.stop()
    cv2.destroyAllWindows()
