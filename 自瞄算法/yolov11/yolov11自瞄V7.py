#V6模板
#配合arduino端V6使用

#制作了GUI界面
#删除了显示器功能
#可能可以更改ESP32的设备描述符


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
import customtkinter as ctk
import os
import json



#############  GUI初始化  ############
#GUI界面初始化
ctk.set_appearance_mode("system")
root = ctk.CTk()
root.title("YOLOv11自瞄")
root.geometry("940x540+520+300")


#创建页面容器
page1 = ctk.CTkFrame(root)#调整参数
page2 = ctk.CTkFrame(root)#参数显示和回退
page3 = ctk.CTkFrame(root)#帮助和关于

#优先展示第一页(参数调整)
page1.place(x=0, y=0, relwidth=1, relheight=1)


#GUI参数初始化
#读取历史参数
try:
    with open("配置文件.json", "r", encoding="utf-8") as f:
        data = json.load(f)

#没有则使用默认参数
except:
    data = {
            "speed": "2.0",
            "conf": "0.75",
            "area": "320",
            "backTime": "300",
            "com": "COM11",
            "size": "2560-1440",
            "spinOpen": "h",
            "spinClose": "j",
            "autoShoot": "k",
            "model": "perfect.engine",
            "head": "True",
            "body": "False",
            "object": "True",
            "flash": "True"
        }


#回退开关初始化
if_return = False

#定位速度滑块上下限
val_down_1 = 0
val_up_1 = 3
#滑块步长
val_step_1 = 0.1

#截图区域滑块上下限
val_down_2 = 0
val_up_2 = 1600
#滑块步长
val_step_2 = 160

#模型置信度滑块上下限
val_down_3 = 0
val_up_3 = 1
#滑块步长
val_step_3 = 0.01

#背闪时间滑块上下限
val_down_4 = 0
val_up_4 = 1000
#滑块步长
val_step_4 = 10




##########  组件逻辑主线程  ###########

#弹窗函数
def tip_window(title,content):
    popup = ctk.CTkToplevel(root)
    popup.title(f"{title}")
    popup.geometry("300x150+1000+700")
    popup.resizable(False, False)
    popup.attributes("-topmost", True)
    # 弹窗内容
    label = ctk.CTkLabel(popup, text=f"{content}", font=("微软雅黑", 16))
    label.pack(pady=25)
    btn = ctk.CTkButton(popup, text="确定", width=100, command=popup.destroy)
    btn.pack(pady=10)



if not ctypes.windll.shell32.IsUserAnAdmin():
    tip_window("错误","请以管理员身份运行程序\n5秒后自动退出......")
    root.after(5000,root.destroy)


#定位速度
label = ctk.CTkLabel(page1, text="定位速度")
label.place(x=50, y=50)
#定位速度滑块
val_1 = ctk.DoubleVar(value=data["speed"])
ctk.CTkLabel(page1, textvariable=val_1).place(x=360, y=33)  # 显示当前值
ctk.CTkSlider(page1, from_=val_down_1, to=val_up_1, variable=val_1, width=500, number_of_steps=int((val_up_1 - val_down_1) / val_step_1)).place(x=130, y=58)


#模型置信度
label = ctk.CTkLabel(page1, text="模型置信度")
label.place(x=50, y=100)
#模型置信度滑块
val_3 = ctk.DoubleVar(value=data["conf"])
ctk.CTkLabel(page1, textvariable=val_3).place(x=360, y=83)  # 显示当前值
ctk.CTkSlider(page1, from_=val_down_3, to=val_up_3, variable=val_3, width=500, number_of_steps=int((val_up_3 - val_down_3) / val_step_3)).place(x=130, y=108)


#截图区域
label = ctk.CTkLabel(page1, text="截图区域")
label.place(x=50, y=150)
#截图区域滑块
val_2 = ctk.IntVar(value=data["area"])
ctk.CTkLabel(page1, textvariable=val_2).place(x=360, y=133)  # 显示当前值
ctk.CTkSlider(page1, from_=val_down_2, to=val_up_2, variable=val_2, width=500, number_of_steps=int((val_up_2 - val_down_2) / val_step_2)).place(x=130, y=158)


#背闪时间
label = ctk.CTkLabel(page1, text="背闪时间")
label.place(x=50, y=200)
#背闪时间滑块
val_4 = ctk.IntVar(value=data["backTime"])
ctk.CTkLabel(page1, textvariable=val_4).place(x=360, y=183)  # 显示当前值
ctk.CTkSlider(page1, from_=val_down_4, to=val_up_4, variable=val_4, width=500, number_of_steps=int((val_up_4 - val_down_4) / val_step_4)).place(x=130, y=208)


#串口连接
label = ctk.CTkLabel(page1, text="串口连接")
label.place(x=50, y=250)
#串口连接输入框
input_COM = ctk.StringVar(value=data["com"])
ctk.CTkEntry(page1, textvariable=input_COM).place(x=140, y=250)


#游戏内分辨率
label = ctk.CTkLabel(page1, text="游戏内分辨率")
label.place(x=50, y=300)
#游戏分辨率输入框
input_size = ctk.StringVar(value=data["size"])
ctk.CTkEntry(page1, textvariable=input_size).place(x=140, y=300)


#自转开始按键
label = ctk.CTkLabel(page1, text="自转开始按键")
label.place(x=50, y=350)
#自转开始按键输入框
input_spin_open = ctk.StringVar(value=data["spinOpen"])
ctk.CTkEntry(page1, textvariable=input_spin_open).place(x=140, y=350)


#自转结束按键
label = ctk.CTkLabel(page1, text="自转结束按键")
label.place(x=50, y=400)
#自转结束按键输入框
input_spin_close = ctk.StringVar(value=data["spinClose"])
ctk.CTkEntry(page1, textvariable=input_spin_close).place(x=140, y=400)


#自动扳机按键
label = ctk.CTkLabel(page1, text="自动扳机按键")
label.place(x=50, y=450)
#自动扳机按键输入框
input_auto_click_open = ctk.StringVar(value=data["autoShoot"])
ctk.CTkEntry(page1, textvariable=input_auto_click_open).place(x=140, y=450)


#模型选择
dir_path = os.path.dirname(os.path.abspath(__file__))
file_list = os.listdir(dir_path)
files_list = []
for i in file_list:
    if i.endswith(('.pt','onnx','engine')):
        files_list.append(i)
label = ctk.CTkLabel(page1, text="模型选择")
label.place(x=380, y=250)
selected_1 = ctk.StringVar(value=data["model"])
ctk.CTkOptionMenu(page1, variable=selected_1,values = files_list).place(x=450, y=250)


#模型识别类型开关
head_var = ctk.BooleanVar(value=data["head"])
body_var = ctk.BooleanVar(value=data["body"])
object_var = ctk.BooleanVar(value=data["object"])
flash_var = ctk.BooleanVar(value=data["flash"])
label = ctk.CTkLabel(page1, text="锁头开关")
label.place(x=410, y=300)
label = ctk.CTkLabel(page1, text="锁身开关")
label.place(x=410, y=350)
label = ctk.CTkLabel(page1, text="锁物开关")
label.place(x=410, y=400)
label = ctk.CTkLabel(page1, text="背闪开关")
label.place(x=410, y=450)
ctk.CTkSwitch(page1, text="", variable=head_var).place(x=500, y=303)
ctk.CTkSwitch(page1, text="", variable=body_var).place(x=500, y=353)
ctk.CTkSwitch(page1, text="", variable=object_var).place(x=500, y=403)
ctk.CTkSwitch(page1, text="", variable=flash_var).place(x=500, y=453)


#帮助说明
label = ctk.CTkLabel(page3, text="定位速度：  准星移动速度，根据自己灵敏度调整，使准星不会左右震荡即可")
label.place(x=140, y=50)
label = ctk.CTkLabel(page3, text="模型置信度：  模型判定目标有效的把握程度，置信度过低将导致乱识别目标，置信度过高将导致识别不出目标")
label.place(x=140, y=80)
label = ctk.CTkLabel(page3, text="截图区域：  范围自瞄，超出截图区域的目标将不被识别，截图区域越小，程序运行越快")
label.place(x=140, y=110)
label = ctk.CTkLabel(page3, text="背闪时间：  填入的数值是半个周期，单位是毫秒(1秒=1000毫秒)，由于灵敏度不同，根据需要自行调整")
label.place(x=140, y=140)
label = ctk.CTkLabel(page3, text="串口连接：  电脑打开 ‘设备管理器’ ,找到 ‘端口’ 把板子右边的接口连接电脑后，出现的编号填入即可 (如COM 3)")
label.place(x=140, y=170)
label = ctk.CTkLabel(page3, text="游戏内分辨率：  一般就是电脑屏幕分辨率，如果锁敌偏移，进入游戏后查看游戏设置的分辨率，填入即可")
label.place(x=140, y=200)
label = ctk.CTkLabel(page3, text="自转开始按键：  设置一个键 (如键盘的h键) ，进游戏单击这个键即可开始自转")
label.place(x=140, y=230)
label = ctk.CTkLabel(page3, text="自转停止按键：  设置一个键 (如键盘的j键) ，进游戏单击这个键即可停止自转")
label.place(x=140, y=260)
label = ctk.CTkLabel(page3, text="自动扳机按键：  一次性功能，按下之后执行一次会自动关闭 (如键盘的k键) ，进游戏单击这个键即可开启自动扳机")
label.place(x=140, y=290)
label = ctk.CTkLabel(page3, text="模型选择：  选择后缀为(.engine)的文件，如果没有，则先选择(.pt)文件，首次运行后将自动构建(.engine)文件")
label.place(x=140, y=320)
label = ctk.CTkLabel(page3, text="模型识别类型开关：  可开启相应功能。注意：锁头和锁身体不能同时执行，如果同开，将执行锁头")
label.place(x=140, y=350)



#保存参数函数
def save_data():
    data = {
        "speed": f"{val_1.get():.1f}",
        "conf": f"{val_3.get():.2f}",
        "area": f"{val_2.get()}",
        "backTime": f"{val_4.get()}",
        "com": f"{input_COM.get()}",
        "size": f"{input_size.get()}",
        "spinOpen": f"{input_spin_open.get()}",
        "spinClose": f"{input_spin_close.get()}",
        "autoShoot": f"{input_auto_click_open.get()}",
        "model": f"{selected_1.get()}",
        "head": f"{head_var.get()}",
        "body": f"{body_var.get()}",
        "object": f"{object_var.get()}",
        "flash": f"{flash_var.get()}"
    }

    with open("配置文件.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    tip_window("提示","保存成功！")


#回退函数2
def back_page_1_1():
    page3.place_forget()
    page1.place(x=0, y=0, relwidth=1, relheight=1)


#帮助函数
def help():
    page1.place_forget()
    page3.place(x=0, y=0, relwidth=1, relheight=1)


#退出函数
def exit():
    sys.exit()


#回退函数1
def back_page_1():
    global if_return
    global ser

    if_return = True
    cam.stop()
    cam.release()
    ser.close()
    page2.place_forget()
    page1.place(x=0, y=0, relwidth=1, relheight=1)



#主逻辑
def run():
    global cam
    global ser

    page1.place_forget()
    #第二页(参数显示和回退)
    page2.place(x=0, y=0, relwidth=1, relheight=1)


    ####################################     参数初始化     ############################################

    #定位速度
    speed = val_1.get()

    #游戏屏幕分辨率大小
    size_x,size_y = map(int, input_size.get().split('-'))

    #矩形自瞄范围
    area_x,area_y = val_2.get(),val_2.get()

    #模型置信度
    conf = val_3.get()

    #模型识别类型(0身1头2队友3道具4闪)
    classes_list = []
    list_cn = []
    if head_var.get():
        classes_list.append(1)
    elif body_var.get():
        classes_list.append(0)
    if object_var.get():
        classes_list.append(3)
    if flash_var.get():
        classes_list.append(4)
    for i in classes_list:
        if i == 0:
            list_cn.append("身")
        if i == 1:
            list_cn.append("头")
        if i == 3:
            list_cn.append("物")
        if i == 4:
            list_cn.append("闪")

    #模型选择
    model = selected_1.get()

    #一键自转
    spin_open_key = input_spin_open.get()
    spin_close_key = input_spin_close.get()

    #自动扳机
    auto_click_open_key = input_auto_click_open.get()

    #背闪时间(半个周期)(单位：毫秒)
    back_time = val_4.get()

    ####还可以增加更多自定义参数#####
    ####################################     参数初始化     ############################################


    #参数显示
    label = ctk.CTkLabel(page2, text="当前参数")
    label.place(x=400, y=100)
    label = ctk.CTkLabel(page2, text=f"定位速度：  {speed:.1f}                          游戏分辨率：  {size_x}-{size_y}              截图区域：  {area_x}              模型置信度：  {conf:.2f}")
    label.place(x=100, y=140)

    label = ctk.CTkLabel(page2, text=f"模型识别类型：  {list_cn}            模型选择：  {model}            一键自转开启键：  {spin_open_key}            一键自转关闭键：  {spin_close_key}")
    label.place(x=100, y=180)
    label = ctk.CTkLabel(page2, text=f"                           自动扳机开启键：  {auto_click_open_key}            背闪时间：  {back_time}ms")
    label.place(x=200, y=220)


    #初始化
    try:
        #如果是pt模型，构建成engine文件
        if model.split('.')[1] == 'pt':
            tip_window("提示","正在编译engine文件\n预计需要5分钟......")
            model_pt = YOLO(model)
            model = model_pt.export(format="engine", imgsz=320, half=True,nms=True)
            tip_window("提示","编译成功！")

        #engine文件初始化
        if model.split('.')[1] == 'engine':
            yolo = YOLO(model = model,task = "detect")

        else:
            tip_window("错误","模型格式错误\n5秒后自动退出......")
            root.after(5000,root.destroy)
    
    except:
        tip_window("错误","模型错误\n5秒后自动退出......")
        root.after(5000,root.destroy)


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

    PORT = f'{input_COM.get()}'
    try:
        #连接串口
        ser = serial.Serial(PORT, BAUDRATE, timeout=0.01)
    except:
        tip_window("错误","串口连接失败\n5秒后退出程序......")
        root.after(5000,root.destroy)


    #等板子复位
    time.sleep(2)



    #监听按键线程
    def listen_key():

        def open_spin():
            nonlocal self_spin
            self_spin = True

        def close_spin():
            nonlocal self_spin
            nonlocal if_sure_stop_spin
            self_spin = False
            if_sure_stop_spin = True

        def open_shoot():
            nonlocal if_auto_shoot
            if_auto_shoot = True


        keyboard.add_hotkey(spin_open_key,open_spin)
        keyboard.add_hotkey(spin_close_key,close_spin)
        keyboard.add_hotkey(auto_click_open_key,open_shoot)
        keyboard.wait()



    #自瞄主逻辑
    def main_control():

        nonlocal if_sure_stop_spin
        nonlocal if_auto_shoot
        global if_return

        while True:

            if if_return:
                if_return = False
                return

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
                    e_x,e_y = 777,back_time
                    data = f"{e_x},{e_y}\n"
                    ser.write(data.encode('utf-8'))
                    time.sleep(back_time * 2 / 1000)
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



                #closest结构：[x1,y1,x2,y2](相对坐标)
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



    threading.Thread(target=listen_key, daemon=True).start()
    threading.Thread(target=main_control, daemon=True).start()




#保存参数按钮
ctk.CTkButton(page1, text="保存参数", command=save_data, width=150, height=45).place(x=700, y=70)


#退出按钮
ctk.CTkButton(page1, text="退出程序", command=exit, width=150, height=45).place(x=700, y=170)

#帮助按钮
ctk.CTkButton(page1, text="疑问", command=help, width=150, height=45).place(x=700, y=270)

#开始按钮
ctk.CTkButton(page1, text="开始运行", command=run, width=250, height=110).place(x=600, y=360)

#重新调整参数按钮
ctk.CTkButton(page2, text="调整参数", command=back_page_1, width=150, height=45).place(x=500, y=300)

#退出按钮
ctk.CTkButton(page2, text="退出程序", command=exit, width=150, height=45).place(x=220, y=300)

#帮助返回按钮
ctk.CTkButton(page3, text="确定", command=back_page_1_1, width=400, height=80).place(x=250, y=420)


root.mainloop()