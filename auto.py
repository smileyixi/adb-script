# 可视化获取数据包
from pickle import LIST
from adb import Adb_func
import pyautogui as auto
import subprocess
import re
import os
import time


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
    def event_log(self):
        auto.PAUSE = 0.5
        auto.FAILSAFE = False

        os.system("open -n /System/Applications/Utilities/Terminal.app") # 打开Ternimal（只适用于MacOS，其他系统自行更改）
        os.system("clear")
        time.sleep(2)
        
        auto.typewrite(Adb_func.getEventEev(), '0.01') # 调用adb function记录事件 - 手动保存event事件
        auto.press('Enter')
        print("[+] 事件监测已开启,手动保存终端event code到脚本根目录下data/event_temp.txt文件")

    # 解析装载payload
    def init_event(self, timestamp_step_time = 0.2, path = "data/event_temp.txt"):
        self.event_resolver(timestamp_step_time, path)
        self.event_loader()
        return self.event_payload_list


    # event code解析器(解析路径:data/event_temp.txt) - 注意txt中咩有数据的情况
    # 根据time间隔判断是否为同一组数据
    def event_resolver(self, timestamp_step: float, path: str) -> list:
        self.event_num = 0                  # 事件总数
        event_list = []                 # 事件列表
        self.event_group_list = [[]]         # 事件分组
        timestamp_list = []             # 时间戳列表
        self.timestamp_group_list = [[]]     # 时间戳分组
        timestamp_step = timestamp_step # 时间容差（以此判断分组,建议0.2并小于0.5）

        # 判断文件是否存在
        if not os.path.exists(path):
            print("[-] No such file or directory! - event_temp.txt")
            return 0
        # 读取数据->过滤数据
        for line in open("data/event_temp.txt", "r+"):
            if "/dev/input" in line:
                event_list.append(line.replace("\n", ""))

        # 至少有两条数据,否则返回0
        if len(event_list) < 2:
            print("[-] Auto_func.event_resolver |  Data acquisition failure!")
            return 0

        # 解析数据（获取时间戳）
        for event in event_list:
            param_top = re.findall("\[(.*?)\]", event)
            timestamp_list.append(param_top[0].replace(" ", ""))

        # 解析数据（hex->dec）
        for event in event_list:
            # 单条数据格式/dev/input/event5: 0003 0035 000001cb -> /dev/input/event5 0003 0035 459
            param_list = event.split(" ")
            event_list[event_list.index(event)] = event[:-8] + str(int(param_list[-1], 16))


        # (获取event时间戳分组)（分析event分组的间隔时间）
        # [['614.144441', '614.144441'], ['616.025771', '616.030530', '616.034555'], ['616.268549']]
        group_id = 0
        self.timestamp_group_list[0].append(timestamp_list[0])
        for timestamp_index in range(0, len(timestamp_list)):
            if timestamp_index == len(timestamp_list)-1:
                break
            gap = float(timestamp_list[timestamp_index+1]) - float(timestamp_list[timestamp_index])
            if gap >= 0 and gap <= timestamp_step:     # 满足要求，放入当前组数据
                self.timestamp_group_list[group_id].append(timestamp_list[timestamp_index+1])
            elif gap > timestamp_step:                 # 不是一组数据，把当前数据加入开新的一组
                group_id += 1
                self.timestamp_group_list.append([])
                self.timestamp_group_list[group_id].append(timestamp_list[timestamp_index+1])

        # 计算分组深度
        latNumTwo_timestamp_group_list = []  # 第二维数组深度 [2, 3, 1]
        for list in self.timestamp_group_list:
            latNumTwo_timestamp_group_list.append(len(list))

        # 根据时间戳分组获取event分组
        self.event_group_list = [[]for i in range(len(latNumTwo_timestamp_group_list))]   # 预先分好空组
        event_list_index = 0
        for event_group in self.event_group_list:
            event_group += event_list[event_list_index:event_list_index+int(latNumTwo_timestamp_group_list[self.event_group_list.index(event_group)])]
            event_list_index += int(latNumTwo_timestamp_group_list[self.event_group_list.index(event_group)])

        # 事件总数
        self.event_num = len(self.event_group_list)

    # event装载器
    # 根据事件组（二维），时间戳组（二维），以[Adb_func]类为基础装载事件代码
    # event：[     614.144441] /dev/input/event5: 0003 0035 192
    def event_loader(self):
        CLIENT_X = 35
        CLIENT_Y = 36
        self.timeslice_list = []     # 事件时间片列表
        self.event_payload_list = []    # 事件装载列表
        
        # 时间戳组处理 -（判断点击和滑动）（获取事件间隔时间）
        for timestamp_group_index in range(len(self.timestamp_group_list)):
            if timestamp_group_index == len(self.timestamp_group_list)-1:
                break
            timeslice = float(self.timestamp_group_list[timestamp_group_index+1][0]) - float(self.timestamp_group_list[timestamp_group_index][-1])
            self.timeslice_list.append(round(timeslice, 2))  # 保留两位小数
        
        # 事件组处理 - 提取单次event的(x,y)
        for event_group in self.event_group_list:
            event_group_len = len(event_group)

            if event_group_len == 2:    # click - 装载单击事件
                if int(event_group[0][19:].split(" ")[-2]) == CLIENT_X and int(event_group[1][19:].split(" ")[-2]) == CLIENT_Y:
                    param_x = int(event_group[0][19:].split(" ")[-1])
                    param_y = int(event_group[1][19:].split(" ")[-1])

                    self.event_payload_list.append(Adb_func.click(param_x, param_y))
                else:
                    print("[!] Auto_func.event_loader | Unknown operands!") 
                    break

            elif event_group_len > 2:   # slide - 装载滑动事件
                x_list = []
                y_list = []
                
                # 获取单个分组中的x,y集合
                for event in event_group:
                    if int(event[19:].split(" ")[-2]) == CLIENT_X:
                        x_list.append(int(event[19:].split(" ")[-1]))
                    elif int(event[19:].split(" ")[-2]) == CLIENT_Y:
                        y_list.append(int(event[19:].split(" ")[-1]))
                    else:
                        print("[!] Bad data | " + event)
                        print("[!] Data source error!") 
                        break
                # 起始 - 终点 坐标
                param_x1 = x_list[0]
                param_y1 = y_list[0]
                param_x2 = x_list[-1]
                param_y2 = y_list[-1]

                self.event_payload_list.append(Adb_func.swipe(param_x1, param_y1, param_x2, param_y2))

            else:                       # 数据解析错误，残缺的参数
                print("[-] Auto_func.event_loader | Data parsing error, incomplete parameters!") 
                break
 
    # event发送器
    def send_event(self):
        for index in range(len(self.event_payload_list)):
            if index != len(self.event_payload_list)-1:
                print("[*] Executing load [{}]".format(self.event_payload_list[index]))
                os.system(self.event_payload_list[index])
                time.sleep(float(self.timeslice_list[index]))    # 等待
                
            else:
                print("[*] Executing load [{}]".format(self.event_payload_list[index]))
                os.system(self.event_payload_list[index])

# 测试代码
# if __name__ == "__main__":
#     auto_func = Auto_func()
#     auto_func.init_event(0.2)
#     print("event num:"+str(auto_func.event_num))

#     input("[Enter] execute..")
#     auto_func.send_event()

