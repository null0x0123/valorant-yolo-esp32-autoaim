#include <Arduino.h>
#include "USB.h"
#include "USBHIDMouse.h"

USBHIDAbsoluteMouse Mouse1;//绝对移动
USBHIDMouse Mouse2;//相对移动

int ex,ey,comma;

void setup() {

    Serial.begin(115200);
    delay(100);

    USB.begin();  //把ESP32作为USB设备
    Mouse1.begin();  //同时作为HID鼠标设备
    // Mouse2.begin();

}

void loop() {

    //检查是否有数据
    if (Serial.available() > 0) {

        String data = Serial.readStringUntil('\n');
        data.trim();
        comma = data.indexOf(',');

        if (comma != -1) {

            //x轴偏移量（绝对位移）
            ex = data.substring(0, comma).toInt();

            //y轴偏移量（绝对位移）
            ey = data.substring(comma + 1).toInt();

            if (ex <= 0) {
                Mouse2.move(ex, 0);
            }
            if (ey <= 0) {
                Mouse2.move(0, ey);
            }
            if (ex > 0) {
                Mouse1.move(ex, 0);
            }
            if (ey > 0) {
                Mouse1.move(0, ey);
            }

        }
    }
    delay(1);

}