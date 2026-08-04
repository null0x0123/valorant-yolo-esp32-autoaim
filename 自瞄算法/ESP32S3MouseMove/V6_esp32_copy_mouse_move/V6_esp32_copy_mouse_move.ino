#include <Arduino.h>
#include "USB.h"
#include "USBHIDMouse.h"

USBHIDMouse Mouse;

TaskHandle_t task3;//自转子线程句柄
TaskHandle_t task4;//自动扳机子线程句柄
TaskHandle_t task5;//背闪1子线程句柄

volatile int ex,ey;

volatile int if_spin = 0;
volatile int if_auto_shoot = 0;

volatile int if_back_left = 0;
volatile int if_back_right = 0;



//自转线程
void self_spin(void *pv) {
    while (1) {
        if (if_spin) {
            Mouse.move(127,0);
        }
        delay(1);
    }
}

//背闪线程
void back_flash(void *pv) {
    while (1) {
        if (if_back_left) {
            Mouse.move(-127,0);
        }
        if (if_back_right) {
            Mouse.move(127,0);
        }
        delay(1);
    }
}




//自动扳机线程
void auto_shoot(void *pv) {
    while (1) {
        if (if_auto_shoot) {
            Mouse.click(MOUSE_LEFT);
            delay(120);
            Mouse.click(MOUSE_LEFT);
            if_auto_shoot = 0;
        }
        delay(1);
    }
}



void setup() {

    Serial.begin(115200);
    delay(100);

    USB.begin();  //把ESP32作为USB设备
    Mouse.begin();  //同时作为HID鼠标设备

    xTaskCreatePinnedToCore(self_spin, "t3", 2048, NULL, 1, &task3, 1);
    xTaskCreatePinnedToCore(auto_shoot, "t4", 2048, NULL, 1, &task4, 1);
    xTaskCreatePinnedToCore(back_flash, "t5", 2048, NULL, 1, &task5, 1);

}



void loop() {

    //检查是否有数据
    if (Serial.available() > 0) {

        String data = Serial.readStringUntil('\n');
        data.trim();
        int comma = data.indexOf(',');

        if (comma != -1) {

            //x轴偏移量（相对位移）
            ex = data.substring(0, comma).toInt();

            //y轴偏移量（相对位移）
            ey = data.substring(comma + 1).toInt();


            //背闪
            if (ex == 777) {
                if_back_left = 1;
                delay(ey);
                if_back_left = 0;

                if_back_right = 1;
                delay(ey);
                if_back_right = 0;
            }


            //自转
            else if (ex == 666 && ey == 666) {
                if_spin = 1;
                ex = 127;
                ey = 0;
            }

            //停止自转
            else if (ex == 555 && ey == 555) {
                if_spin = 0;
            }

            //自动扳机
            else if (ex == 444 && ey == 444) {
                if_auto_shoot = 1;
            }

            //自瞄
            else {
                Mouse.move(ex, ey);
            }

        }
    }

    delay(1);

}