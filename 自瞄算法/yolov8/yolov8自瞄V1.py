import numpy as np
from mss import mss
import serial
import time
from ultralytics import YOLO



#调整参数#######################################################
#定位速度speed
speed = 2
#预测强度predict
predict = 0
#矩形自瞄范围 x * y
area_x,area_y = 500,500
#锁歪了可以自定义参数
#左右调整(正值向右)
move_X = 0
#上下调整(正值向上)
move_Y = 20
#模型置信度
conf = 0.2
#模型识别类型(target或者head)具体的编号对应类型查看yolo-bvn.yaml
classes_list = [0]



#屏幕中心坐标
ox,oy = 1280,720

#截图初始化
sct = mss()


#输入鼠标串口编号
num = input("输入串口编号 : COM")

PORT = 'COM' + f'{num}'

#串口波特率初始化
BAUDRATE = 115200

#连接串口
ser = serial.Serial(PORT, BAUDRATE, timeout=0.01)
#等板子复位
time.sleep(2)


#初始化旧目标位置
last_x,last_y = 0,0

#模型初始化
yolo = YOLO(r"runs\detect\train\weights\best.engine",task = "detect")



while True:
    
    #截图范围
    left = ox - area_x // 2
    top = oy - area_y // 2
    monitor = {"top":top, "left":left, "width":area_x, "height":area_y}

    #开始截图
    img = sct.grab(monitor)

    #截图转换成YOLO需要的格式
    frame = np.array(img)

    #去除α通道
    #去掉 Alpha 通道，只留BGR
    frame_BGR = frame[..., :3]
    #BGR转RGB,以便给YOLO
    frame_RGB = frame_BGR[..., ::-1]

    #在截图区域内找到目标
    #模型一次性可以推理多张图片，这些图片的集合在result里
    result = yolo(source = frame_RGB,conf = conf,classes = classes_list)

    res = result[0]

    #该图里面的所有框
    boxes = res.boxes

    #如果检测到目标：
    if len(boxes) > 0:

        #距离准星最近的目标
        closest = None

        #设一个可变的最小初始值
        min_distance = 9999999

        #获取所有框信息的数组
        xyxy_list = boxes.xyxy.cpu().numpy()

        #遍历这些框
        for c in xyxy_list:
            
            #获取每个框的具体信息
            x1,y1,x2,y2 = c

            #计算框的相对中心坐标(因为是截图区域内的)
            relative_x = (x1 + x2) / 2
            relative_y = (y1 + y2) / 2

            #转换成框中心的绝对坐标
            cx = left + relative_x
            cy = top + relative_y

            #计算到准星距离平方和
            distance = (ox - cx) ** 2 + (oy - cy) ** 2
            if distance < min_distance:
                min_distance = distance
                #找到距离准星最近的目标
                closest = c


        #因为closest结构：[x1,y1,x2,y2](是相对坐标)
        #确定最近框的坐标数据
        x1,y1,x2,y2 = closest
        #所以最终目标绝对坐标dx,dy：
        dx = left + (x1 + x2) / 2
        dy = top + (y1 + y2) / 2


        #计算预测位置
        #两帧的位移
        vel_x,vel_y = dx - last_x,dy - last_y
        #预测的坐标
        pred_x,pred_y = dx + vel_x * predict,dy + vel_y * predict

        #刷新旧目标位置
        last_x,last_y = dx,dy

        #计算相对位移
        e_x,e_y = int((pred_x + (move_X) - ox) * speed),int((pred_y - (move_Y) - oy) * speed)


        # 限幅防止 HID 鼠标溢出（-127~127）
        e_x = max(-127, min(127, e_x))
        e_y = max(-127, min(127, e_y))

        # 发送最新命令
        data = f"{e_x},{e_y}\n"
        ser.write(data.encode('utf-8'))