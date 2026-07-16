#V2模板
#优化了自转算法(由硬件自己执行自转)，可手动开关
#配合arduino端V2代码使用
import serial
import time
import dxcam
from ultralytics import YOLO
import threading
import keyboard



############                    自定义-调整参数                          ############


############                    定位速度speed                           ############
speed = 2.2
############                    屏幕大小                                ############
size_x,size_y = 2560,1440
############                    矩形自瞄范围 x * y                      ############
area_x,area_y = 320,320
############                    模型置信度                              ############
conf = 0.75
############                    模型识别类型(身体0头1)                   ############
classes_list = [1]
############                    模型选择                                ############
model = r"D:\code\python\ultralytics-main\perfect.engine"
############                    一键自转                                ############
spin_open_key = b'h'
spin_close_key = b'j'




#初始化

#屏幕中心坐标
ox,oy = size_x // 2,size_y // 2

#模型初始化
yolo = YOLO(model = model,task = "detect")

#自转开关初始化
self_spin = False

#自转确认开关初始化
if_sure_stop_spin = False

#截图范围初始化
left = ox - area_x // 2
right = ox + area_x // 2
top = oy - area_y // 2
down = oy + area_y // 2

#自瞄矩形框大小x1,y1,x2,y2
region = (left,top,right,down)

#截图工具初始化
cam = dxcam.create(output_color="BGR",region = region)
cam.start()

# #帧率工具初始化
# FPS = 0
# last_time = time.time()

#串口波特率初始化
BAUDRATE = 115200

#输入鼠标串口编号
num = input("输入串口编号 : COM")
PORT = 'COM' + f'{num}'

#连接串口
ser = serial.Serial(PORT, BAUDRATE, timeout=0.01)
#等板子复位
time.sleep(2)

#监听按键线程
def listen_key():
    def open():
        global self_spin

        self_spin = True
    def close():
        global self_spin
        global if_sure_stop_spin

        self_spin = False
        if_sure_stop_spin = True
    keyboard.add_hotkey('h',open)
    keyboard.add_hotkey('j',close)
    keyboard.wait()



threading.Thread(target=listen_key, daemon=True).start()



while True:

    #开始截图
    frame_BGR = cam.get_latest_frame()

    #空帧拦截防止崩溃
    if frame_BGR is None:
        time.sleep(0.001)
        continue


    #在截图区域内找到目标
    #模型一次性可以推理多张图片，这些图片的集合在result里
    result = yolo(source = frame_BGR,conf = conf,classes = classes_list)

    # #显示帧率
    # now_time = time.time()
    # FPS = 1/(now_time - last_time)
    # last_time = now_time
    

    #读取第一张图片
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
        # dy = top + y2

        

        #计算相对位移
        if self_spin == True:
            e_x,e_y = 666,666
            data = f"{e_x},{e_y}\n"
            ser.write(data.encode('utf-8'))

        elif if_sure_stop_spin == True:
            e_x,e_y = 555,555
            data = f"{e_x},{e_y}\n"
            ser.write(data.encode('utf-8'))
            if_sure_stop_spin = False

        else:
            e_x,e_y = int((dx - ox) * speed),int((dy - oy) * speed)

            # 限幅防止 HID 鼠标溢出（-127~127）
            e_x = max(-127, min(127, e_x))
            e_y = max(-127, min(127, e_y))

            # 发送命令移动鼠标
            data = f"{e_x},{e_y}\n"
            ser.write(data.encode('utf-8'))

        time.sleep(0.001)
    

    else:
        if self_spin == True:
            e_x,e_y = 666,666
            data = f"{e_x},{e_y}\n"
            ser.write(data.encode('utf-8'))

        if if_sure_stop_spin == True:
            e_x,e_y = 555,555
            data = f"{e_x},{e_y}\n"
            ser.write(data.encode('utf-8'))
            if_sure_stop_spin = False
            
        time.sleep(0.001)