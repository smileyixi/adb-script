# 可视化获取数据包
from pickle import LIST
from adb import Adb_func
import subprocess
import re
import os
import pyautogui as auto
import time
import keyboard



class Auto_func():

    # 获取设备最大宽度
    def get_width_max() -> int:
        event_list = subprocess.getoutput(Adb_func.getEvent()).split('\n')
        width = re.findall("max \d{1,4}", event_list[1])[0]
        width = int(width[4:])
        return width
        

    # 获取设备最大高度
    def get_height_max() -> int:
        event_list = subprocess.getoutput(Adb_func.getEvent()).split('\n')
        height = re.findall("max \d{1,4}", event_list[2])[0]
        height = int(height[4:])
        return height


    # autogui保存事件log
    def save_log_auto() -> None:
        auto.PAUSE = 0.5
        auto.FAILSAFE = False

        os.system("open -a 'Terminal'") # 打开Ternimal（只适用于MacOS，其他系统自行更改）
        time.sleep(2)
        
        auto.typewrite(Adb_func.getEventEev(), '0.01') # 调用adb function记录事件 - 手动保存event事件
        auto.press('Enter')
        print("[+] 事件监测已开启,手动保存终端event code到脚本根目录下data/event_temp.txt文件")


    # event code解析器(解析路径:data/event_temp.txt) - 注意txt中咩有数据的情况
    def event_resolver(path = "data/event_temp.txt") -> list:
        event_list = []
        # 判断文件是否存在
        if not os.path.exists(path):
            print("[-] No such file or directory! - event_temp.txt")
        # 循环读取并过滤数据
        for line in open("data/event_temp.txt", "r+"):
            if not line:
                break
            if "/dev/input" in line:
                event_list.append(line.replace("\n", ""))

        # 解析数据（hex->dec）
        for event in event_list:
            # 单条数据格式/dev/input/event5: 0003 0035 000001cb -> /dev/input/event5 0003 0035 459
            param_list = event.split(" ")
            event_list[event_list.index(event)] = event[:-8] + str(int(param_list[-1], 16))
        
        return event_list


    # event发送器
    def send_event(event_list):
        model = "adb shell sendevent "
        param_x = event_list[0].split(" ")[-1]
        param_y = event_list[1].split(" ")[-1]
        os.system(Adb_func.click(param_x, param_y))

# Auto_func.save_log_auto()
list = Auto_func.event_resolver()
print(list)
Auto_func.send_event(list)

