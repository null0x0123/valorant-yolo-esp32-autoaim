from ultralytics import YOLO

#自定义参数######################

#图片来源
source_list = [r"E:\桌面\d81599d7c81869de352ab4007462fee9.jpg"]
# #识别类型
classes_list = [0]
# #置信度
conf = 0.3
#模型
model = r"D:\code\python\ultralytics-main\perfect.engine"


#模型初始化
yolo = YOLO(model = model,task = "detect")

#图片的返回的结果
result = yolo(source=source_list,classes = classes_list,conf = conf,save = True)