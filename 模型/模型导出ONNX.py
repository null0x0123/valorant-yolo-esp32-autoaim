from ultralytics import YOLO

model = YOLO(r"runs\detect\train\weights\best.pt")
model.export(
    format="onnx",
    imgsz=640,
    simplify=True,
    opset=12,
    half=True  # FP16，也可以后面TensorRT再设
)