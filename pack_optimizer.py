# pack_optimizer.py
import csv
import itertools

def load_boxes(path='box_catalog.csv'):
    boxes = []
    with open(path,'r') as f:
      rdr = csv.DictReader(f)
      for r in rdr:
        boxes.append({'id':r['id'],'label':r['label'], 'L':float(r['L_mm']), 'W':float(r['W_mm']), 'H':float(r['H_mm'])})
    return boxes


def find_best_box(dims, boxes, padding_mm=5.0, top_k=3):
    import math
    obj_vol = dims[0]*dims[1]*dims[2]
    candidates = []
    for b in boxes:
      bvol = b['L']*b['W']*b['H']
      for orient in itertools.permutations(dims,3):
         if orient[0] + padding_mm <= b['L'] and orient[1] + padding_mm <= b['W'] and orient[2] + padding_mm <= b['H']:
            wasted = bvol - obj_vol
            candidates.append((b, wasted, orient))
            break
    candidates.sort(key=lambda x: x[1])
    return candidates[:top_k]