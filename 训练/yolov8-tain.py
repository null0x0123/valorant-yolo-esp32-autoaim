#训练模型
#需要yolo-bvn.yaml配置文件

from ultralytics import YOLO

model = YOLO('yolov8n.pt')

model.train(data='yolo-bvn.yaml', workers=0, epochs=150, batch=16)