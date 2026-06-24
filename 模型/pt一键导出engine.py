from ultralytics import YOLO
model = YOLO(r"D:\code\python\ultralytics-main\perfect.pt")
model.export(format="engine", imgsz=320, half=True,nms=True)