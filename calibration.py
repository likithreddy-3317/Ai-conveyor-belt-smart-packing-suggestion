# calibration.py
import cv2
import numpy as np
import json

# Usage: run with a checkerboard printed and visible
# Outputs: scale_mm_per_pixel in a JSON file 'calibration.json'

CHECKER_ROWS = 6 # inner corners
CHECKER_COLS = 9
SQUARE_SIZE_MM = 20.0 # physical size of printed checker squares

objp = np.zeros((CHECKER_ROWS*CHECKER_COLS,3), np.float32)
objp[:,:2] = np.mgrid[0:CHECKER_COLS,0:CHECKER_ROWS].T.reshape(-1,2)
objp *= SQUARE_SIZE_MM

cam = cv2.VideoCapture(0)
ret, frame = cam.read()
if not ret:
    raise RuntimeError('Camera not available. Make sure it is connected and not in use.')

print('Press SPACE when checkerboard is visible and framed')
while True:
    ret, frame = cam.read()
    if not ret:
     break
    disp = frame.copy()
    cv2.imshow('checker', cv2.resize(disp, (900,600)))
    k = cv2.waitKey(1) & 0xFF
    if k == 27: # ESC
     break
    if k == 32: # SPACE
      gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
      retc, corners = cv2.findChessboardCorners(gray, (CHECKER_COLS, CHECKER_ROWS), None)
      if retc:
        corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1),
                                    (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
# compute distances between known squares to get mm/pixel ratio
# take two corner points separated by known squares
        p1 = corners2[0,0]
        p2 = corners2[-1,0]
        pixel_dist = np.linalg.norm(p2 - p1)
# physical distance
        phys_dist = np.linalg.norm([(CHECKER_COLS-1)*SQUARE_SIZE_MM, (CHECKER_ROWS-1)*SQUARE_SIZE_MM])
        mm_per_pixel = phys_dist / pixel_dist
        out = {'mm_per_pixel': float(mm_per_pixel)}
        with open('calibration.json','w') as f:
            json.dump(out,f)
        print('Calibration saved:', out)
    else:
        print('Checkerboard not detected, try again')
cam.release()
cv2.destroyAllWindows()