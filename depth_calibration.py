import pyrealsense2 as rs
import numpy as np
import json
import time

# Parameters
N_FRAMES = 60
OUTPUT = 'depth_calib.json'

pipeline = rs.pipeline()
cfg = rs.config()
cfg.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
cfg.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipe_profile = pipeline.start(cfg)
time.sleep(1.0)  # warm-up

depth_sensor = pipe_profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()  # meters per unit
print("Depth scale (m/unit):", depth_scale)
frames_collected = []
try:
     for i in range(N_FRAMES):
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        if not depth_frame: 
            continue
        depth_image = np.asanyarray(depth_frame.get_data())  # units: depth units (u)
        frames_collected.append(depth_image)
        print(f"Captured frame {i+1}/{N_FRAMES}", end='\r')
finally:
    pipeline.stop()
# stack and compute per-pixel median, then sample central area
stack = np.stack(frames_collected, axis=0)  # shape (N,H,W)
median_frame = np.median(stack, axis=0)  # median per-pixel

# sample central region (avoid edges)
h, w = median_frame.shape
cx, cy = w//2, h//2
crop = median_frame[cy-30:cy+30, cx-60:cx+60]  # 60x120 area centered
# convert to meters then to mm
median_depth_units = np.median(crop)
median_depth_m = float(median_depth_units) * depth_scale
median_depth_mm = median_depth_m * 1000.0

out = {
    "depth_scale_m_per_unit": float(depth_scale),
    "median_belt_depth_mm": float(median_depth_mm)
}
with open(OUTPUT, 'w') as f:
    json.dump(out, f, indent=2)
print("\nSaved depth calibration to", OUTPUT)
print("Median belt depth (mm):", median_depth_mm)