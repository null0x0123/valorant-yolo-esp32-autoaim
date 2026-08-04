#include <Arduino.h>//断点表示可能需要删除
#include "USB.h"
#include "USBHIDMouse.h"
#include <U8x8lib.h>
#ifdef U8X8_HAVE_HW_SPI
#include <SPI.h>
#endif

U8X8_SSD1306_128X64_NONAME_SW_I2C
u8x8(4,5,U8X8_PIN_NONE);
USBHIDMouse Mouse;

TaskHandle_t task2;//显示器子线程句柄
TaskHandle_t task3;//自转子线程句柄
TaskHandle_t task4;//自动扳机子线程句柄
TaskHandle_t task5;//背闪1子线程句柄

volatile int ex,ey;
volatile int print_xy = 0;

volatile int print_autoshoot = 0;


volatile int if_spin = 0;
volatile int if_auto_shoot = 0;

volatile int if_back_left = 0;
volatile int if_back_right = 0;



//显示器线程
void print_text(void *pv) {
    while (1) {
        if (print_xy) {
            char exey[20];
            sprintf(exey,"%d,%d     ",ex,ey);
            u8x8.drawString(3,1,"          ");
            u8x8.drawString(6,2,"    ");
            u8x8.drawString(5,3,exey);
            u8x8.setInverseFont(0);
            u8x8.refreshDisplay();
            print_xy = 0;
            delay(20);
        }
        else if (print_autoshoot) {
            u8x8.drawString(3,1,"Auto shoot");
            u8x8.setInverseFont(0);
            u8x8.refreshDisplay();
            u8x8.drawString(6,2,"    ");
            u8x8.drawString(5,3,"       ");
            u8x8.setInverseFont(1);
            u8x8.refreshDisplay();
        }
        else {
            u8x8.drawString(3,1,"          ");
            u8x8.drawString(6,2,"NULL");
            u8x8.drawString(5,3,"       ");
            u8x8.setInverseFont(0);
            u8x8.refreshDisplay();
        }
        delay(1);
    }
}



//自转线程
void self_spin(void *pv) {
    while (1) {
        if (if_spin) {
            Mouse.move(127,0);  //没有显示器功能
        }
        delay(1);
    }
}

//背闪线程
void back_flash(void *pv) {
    while (1) {
        if (if_back_left) {
            Mouse.move(-127,0);  //没有显示器功能
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
            Mouse.click(MOUSE_LEFT);  //调试自动扳机的显示器
            if_auto_shoot = 0;
            print_autoshoot = 0;
        }
        delay(1);
    }
}



void setup() {

    Serial.begin(115200);
    delay(100);

    USB.begin();  //把ESP32作为USB设备
    Mouse.begin();  //同时作为HID鼠标设备

    u8x8.begin();
    u8x8.setPowerSave(0);

    u8x8.setFont(u8x8_font_chroma48medium8_r);

    xTaskCreatePinnedToCore(print_text, "t2", 2048, NULL, 1, &task2, 1);
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

            else if (ex == 4444 && ey == 4444) {
                print_autoshoot = 1;
            }

            //自瞄
            else {
                Mouse.move(ex, ey);
            }

            // //自动扳机显示功能
            // if (ex == 4444 && ey == 4444) {
            //     print_autoshoot = 1;
            // }


            //显示到屏幕上
            print_xy = 1;

        }
    }

    delay(1);

}