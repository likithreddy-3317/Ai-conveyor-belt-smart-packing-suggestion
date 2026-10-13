from ultralytics import YOLO

model = YOLO("yolov8m.pt")   # strong model
model.train(
    data="data.yaml",
    epochs=100,
    imgsz=640,
    batch=8
)