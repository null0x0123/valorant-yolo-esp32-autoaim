#V4模板
#配合arduino端V4代码使用

#增加了模型识别类型
#算法优化
#增加了背闪功能


#准备打包成exe,然后增加图形化窗口，自定义的参数做成可勾选的菜单
#准备商用，使用时间戳，制成天卡、周卡、月卡
#商用可细分成纯自瞄版本，自瞄加自转，自瞄加自转加自动扳机，自瞄加自转加自动扳机加背闪，然后分开计价
import serial
import time
import dxcam
from ultralytics import YOLO
import threading
import keyboard
import ctypes
import sys

if not ctypes.windll.shell32.IsUserAnAdmin():
    print("请以管理员身份运行\n5秒后自动退出......")
    time.sleep(5)
    sys.exit()



print("正在初始化......")


############                    自定义-调整参数                          ############


############                    定位速度speed                           ############
speed = 1.8
############                    屏幕大小                                ############
size_x,size_y = 2560,1600
############                    矩形自瞄范围 x * y                      ############
area_x,area_y = 320,320
############                    模型置信度                              ############
conf = 0.75
############             模型识别类型(0身1头2队友3道具4闪)                ############
classes_list = [1,3,4]
############                    模型选择                                ############
model = "perfect.engine"
############                    一键自转                                ############
spin_open_key = b'h'
spin_close_key = b'j'
############                    自动扳机                                ############
auto_click_open_key = b'k'




#初始化

#模型初始化开关初始化
if_begin = True

#engine文件初始化
try:
    yolo = YOLO(model = model,task = "detect")
    if_begin = False

except:
    print("首次初始化大约需要5分钟......")
    time.sleep(5)
    model = YOLO("perfect.pt")
    model.export(format="engine", imgsz=320, half=True,nms=True)
    print("加载成功!")
    time.sleep(3)

#模型初始化
if if_begin:
    yolo = YOLO(model = model,task = "detect")

#屏幕中心坐标
ox,oy = size_x // 2,size_y // 2

#自转开关初始化
self_spin = False

#自转确认开关初始化
if_sure_stop_spin = False

#自动扳机开关初始化
if_auto_shoot = False

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

    def open_spin():
        global self_spin
        self_spin = True

    def close_spin():
        global self_spin
        global if_sure_stop_spin
        self_spin = False
        if_sure_stop_spin = True

    def open_shoot():
        global if_auto_shoot
        if_auto_shoot = True

        e_x,e_y = 4444,4444
        data = f"{e_x},{e_y}\n"
        ser.write(data.encode('utf-8'))

    keyboard.add_hotkey('h',open_spin)
    keyboard.add_hotkey('j',close_spin)
    keyboard.add_hotkey('k',open_shoot)
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

    #自转
    if self_spin == True:
        e_x,e_y = 666,666
        data = f"{e_x},{e_y}\n"
        ser.write(data.encode('utf-8'))
    
    #停止自转
    if if_sure_stop_spin == True:
        e_x,e_y = 555,555
        data = f"{e_x},{e_y}\n"
        ser.write(data.encode('utf-8'))
        if_sure_stop_spin = False



    #如果检测到目标：
    if len(boxes) > 0:

        #距离准星最近的目标
        closest = None

        #设一个可变的最小初始值
        min_distance = 9999999

        #获取所有框信息的数组
        xyxy_list = boxes.xyxy.cpu().numpy()

        #获取类型信息
        cls_list  = boxes.cls.cpu().numpy()


        #如果是闪，则发送背闪代码
        if 4 in cls_list:
            e_x,e_y = 777,777
            data = f"{e_x},{e_y}\n"
            ser.write(data.encode('utf-8'))
            continue


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

            #找到距离准星最近的目标
            distance = (ox - cx) ** 2 + (oy - cy) ** 2
            if distance < min_distance:
                min_distance = distance
                closest = c



        #因为closest结构：[x1,y1,x2,y2](是相对坐标)
        #确定最近框的坐标数据
        x1,y1,x2,y2 = closest
        
        #所以最终目标绝对坐标dx,dy：
        dx = left + (x1 + x2) / 2
        dy = top + (y1 + y2) / 2
        # dy = top + y2



        #普通自瞄
        if self_spin == False:
            e_x,e_y = int((dx - ox) * speed),int((dy - oy) * speed)
            e_x = max(-127, min(127, e_x))
            e_y = max(-127, min(127, e_y))
            data = f"{e_x},{e_y}\n"
            ser.write(data.encode('utf-8'))


        #自动扳机
        if if_auto_shoot == True:
            e_x,e_y = 444,444
            data = f"{e_x},{e_y}\n"
            ser.write(data.encode('utf-8'))
            if_auto_shoot = False

        time.sleep(0.001)
    

    else:
            
        time.sleep(0.001)