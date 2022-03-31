import os
import subprocess
import datetime
import platform
import re
import adb
from adb import Adb_func
from auto import Auto_func


class FileInit():
    def console_char(self):
        print('''
     ██     ███████   ██████          ████████   ██████  ███████   ██ ███████  ██████████
    ████   ░██░░░░██ ░█░░░░██        ██░░░░░░   ██░░░░██░██░░░░██ ░██░██░░░░██░░░░░██░░░ 
   ██░░██  ░██    ░██░█   ░██       ░██        ██    ░░ ░██   ░██ ░██░██   ░██    ░██    
  ██  ░░██ ░██    ░██░██████   █████░█████████░██       ░███████  ░██░███████     ░██    
 ██████████░██    ░██░█░░░░ ██░░░░░ ░░░░░░░░██░██       ░██░░░██  ░██░██░░░░      ░██    
░██░░░░░░██░██    ██ ░█    ░██             ░██░░██    ██░██  ░░██ ░██░██          ░██    
░██     ░██░███████  ░███████        ████████  ░░██████ ░██   ░░██░██░██          ░██    
░░      ░░ ░░░░░░░   ░░░░░░░        ░░░░░░░░    ░░░░░░  ░░     ░░ ░░ ░░           ░░    
        ''')
        print("                                                                        \033[31m v1.0 by smilesl \033[0m")

    # 初始化信息
    # [1]setInfo() - 设置信息 - [para:file_path 文件相对路径 / authorname 作者]
    # [2]createFile() - 创建脚本
    def __init__(self, file_path, author = "SMILESL", reWrite=True) -> None:
        self.os = platform.system   # 检测系统类型
        #self.__init()
        self.setInfo(file_path, author)
        self.createFile(reWrite=reWrite)
        self.__is_init_event = False    # 是否初始化了event
        self.auto_func = Auto_func()    # 实例化Auto_func
        self.adb_func = Adb_func()      # 实例化Adb_func

    # 启动自检函数 [文件目录是否存在以及完整性等]
    # def __init(self):
    #     pass

    def pErr(self, cls=0x00):
        if cls == 0x01:
            print("\n参数错误！- Type 'help' to view the help\n")
        elif cls == 0x02:
            print("[-]Unknown Command!")
        elif cls == 0x03:
            print("[-] Adb has no connected device!")
        elif cls == 0x04:
            print("[-] The ADB environment is not configured!")
        else:
            print("[OS]未知的错误类型")

    # 判断参数个数
    def paraTest(self, cmd,  num:int) -> bool:
        if len(cmd) != num:
            self.pErr(0x01)
            return False
        return True

    def connInit(self):
        # 检测是否连接设备
        self.conn_state = False
        self.conn_devices = []
        # 初始化adb devices
        subprocess.getoutput("adb devices")
        # 检测是否安装adb，或配置adb环境
        if "List of devices attached" not in subprocess.getoutput("adb devices"):
            self.pErr(0x04)
        
        dev_list = subprocess.getoutput(self.adb_func.devices()).split("\n")
        dev_list.pop()
        if len(dev_list)==1:
            self.pErr(0x03)
            self.conn_state = False
        else:
            dev_list.pop(0)
            for i in dev_list:
                device = i.replace("\t", " ")
                if "device" in i:
                    self.conn_state = True
                    self.conn_devices.append(device)
                    print("[+] Adb successfully connected to " + device)
                elif "offline" in i:
                    self.conn_state = False
                    print("[!] 设备连接异常! at " + device)
                elif "unauthorized" in i:
                    self.conn_state = False
                    print("[!] usb调试未授权! at " + device)
                else:
                    self.pErr(0x03)

    def addCmdLine(self, string:str):
        self.f.write("os.system('"+string.replace('\n', '')+"')\n")

    def userCmd(self):
        # 初始化输出屏幕
        if self.os == "Windows":
            os.system("cls")
        else:
            os.system("clear")
        self.connInit()
        print(self.file_state)
        print("\n出现问题可尝试使用'adb kill-server'命令重启adb服务，或者'adb connect [device]' 命令连接设备")
        print("使用脚本前请检查adb工具是否已安装或是否可用\n")

        # console char
        self.console_char()
        
        step = 1

        while True:
            cmd = input("\033[1;34;40m[OS]\033[0m 输入help查看帮助信息:")

            if ' ' in cmd:
                cmd = cmd.split(' ')
            if cmd == "":
                continue
            if not self.conn_state and cmd != "exit" and step:
                self.pErr(0x03)
                step = 0
            # package handle
            elif cmd == "pkg" or cmd[0] == "pkg":
                if isinstance(cmd,list):
                    if cmd[1] == "--this":
                        print(subprocess.getoutput(self.adb_func.showAllPkg("--this")).split(" ")[-1].split("/")[0])
                    else:
                        os.system(self.adb_func.showAllPkg(cmd[1]))
                else:
                    os.system(self.adb_func.showAllPkg())
            elif cmd[0] == "savepkg" or cmd == "savepkg":
                if len(cmd) == 3:
                    pkgs = subprocess.getoutput(self.adb_func.showAllPkg(cmd[2]))
                else:
                    pkgs = subprocess.getoutput(self.adb_func.showAllPkg())
                if isinstance(cmd,list):
                    f = open(cmd[1], "w+")
                    print("[+] Successfully saved to "+cmd[1])
                else:
                    f = open("data/packages.txt", "w+")
                    print("[+] Successfully saved to "+"data/packages.txt")
                f.write(pkgs)
                f.close()

            elif cmd == "help":
                self.adb_func.info()
            elif cmd == "exit":
                print("[+] All changes have been saved to " + self.file_path)
                break
            elif cmd == "clear":
                os.system("clear")
            elif cmd == "state":
                self.connInit()
            
            # key click handle
            elif cmd == "keyevent":
                self.adb_func.showkeys()
            elif cmd[0] == "key":
                if not self.paraTest(cmd, 2):
                    continue
                if not self.adb_func.keyevent(cmd[1]):
                    self.pErr(0x01)
                    continue
                self.addCmdLine(self.adb_func.keyevent(cmd[1]))
                print("[+] Add key " + cmd[1])
            elif cmd[0] == "click":
                if not self.paraTest(cmd, 3):
                    continue
                self.addCmdLine(self.adb_func.click(cmd[1], cmd[2]))
                print("[+] click ({x}, {y})".format(x=cmd[1], y=cmd[2]))
            elif cmd == "swipe":
                width_max  = float(self.auto_func.get_width_max())
                height_max = float(self.auto_func.get_height_max())

                if width_max == 0 or height_max == 0:
                    self.pErr(0x01)
                    return 0

                param_x1 = int(width_max * 0.5)
                param_y1 = int(height_max * 0.8)
                param_x2 = int(width_max * 0.5)
                param_y2 = int(height_max * 0.2)
                self.addCmdLine(self.adb_func.swipe(param_x1, param_y1, param_x2, param_y2))
                print("[+] swipe ({},{}) to ({},{})".format(param_x1, param_y1, param_x2, param_y2))
            elif cmd[0] == "wait":
                if not self.paraTest(cmd, 2):
                    continue
                self.f.write("time.sleep("+cmd[1]+")"+"\n")
                print("[+] wait "+cmd[1])

            # apk activity handle
            elif cmd[0] == "install":
                if len(cmd) == 3:
                    if not self.adb_func.install(cmd[2], cmd[1]):
                        self.pErr(0x01)
                    else:
                        self.addCmdLine(self.adb_func.install(cmd[2], cmd[1]))
                        print("[+] Add install " + cmd[2])
                else:
                    if not self.adb_func.install(cmd[1]):
                        self.pErr(0x01)
                        break
                    else:
                        self.addCmdLine(self.adb_func.install(cmd[1]))
                        print("[+] Add install " + cmd[1])
            elif cmd[0] == "uninstall":
                if len(cmd) == 3:
                    if not self.adb_func.uninstall(cmd[2], cmd[1]):
                        self.pErr(0x01)
                    else:
                        self.addCmdLine(self.adb_func.uninstall(cmd[2], cmd[1]))
                        print("[+] Add uninstall " + cmd[2])
                else:
                    if not self.adb_func.uninstall(cmd[1]):
                        self.pErr(0x01)
                    else:
                        self.addCmdLine(self.adb_func.uninstall(cmd[1]))
                        print("[+] Add uninstall " + cmd[1])
            elif cmd == "exact" or cmd[0] == "exact":
                result = subprocess.getoutput(self.adb_func.showActivity())
                currentAct = "com." + re.findall("com.(.*?)}",result)[0]
                # 获取launcher Activity
                if isinstance(cmd, list):
                    if not self.paraTest(cmd, 2):
                        continue
                    if cmd[1] == "--launcher":
                        currentAct = currentAct.split(" ")[-1].split("/")[0].replace(" ", "")
                        currentAct = adb.get_launcher_activity(currentAct).split("\n")[0].replace(" ", "").replace("\n", "")
                    else:
                        self.pErr(0x01)
                        continue
                # 获取当前 Activity
                else:
                    currentAct = currentAct.split(" ")[-1].replace(" ", "").replace("\n", "")
                print(currentAct)
                flag = input("是否添加<执行当前活动到'{}'>(输入任意字符取消):".format(self.file_path))
                if flag == "":
                    self.addCmdLine(self.adb_func.actionAct(currentAct).strip("\n"))
                    print("[+] Add execute activity {} task".format(currentAct))
                else:
                    print("[-] Cancel the add operation") 
            elif cmd[0] == "cleardata" or cmd == "cleardata":
                if isinstance(cmd, list):
                    os.system(self.adb_func.clearData(cmd[1]))
                else:
                    os.system(self.adb_func.clearData())
            
            # 录制手势 - 无需root！
            elif cmd == "getevent":  # 获取event数据
                if self.os == "Windows" or self.os == "Linux":
                    print("[-] 不支持此操作，请查看[README.md]获取帮助")
                else:
                    self.auto_func.event_log()
            elif cmd == "sendevent": # 测试使用payload
                if not self.__is_init_event:
                    print("[*] 正在初始化event事件")
                    self.event_payload_list, self.event_timestamp_list = self.auto_func.init_event(0.2)
                    self.__is_init_event == True
                self.auto_func.send_event()


            elif cmd == "saveevent": # 保存动作数据到脚本
                if not self.__is_init_event:
                    print("[*] 正在初始化event事件")
                    self.event_payload_list, self.event_timestamp_list = self.auto_func.init_event(0.2)
                    self.__is_init_event = True

                # 添加payload - 间隔时间片 到脚本
                for payload_index in range(len(self.event_payload_list)):
                    if payload_index == len(self.event_payload_list) - 1:
                        break
                    self.f.write("print('[*] 正在执行payload | ' + '"+self.event_payload_list[payload_index]+"')" + "\n")  # console msg
                    self.addCmdLine(self.event_payload_list[payload_index])    # payload code
                    self.f.write("time.sleep("+str(self.event_timestamp_list[payload_index-1])+")"+"\n")   # timestamp
                    
                
                print("[+] add event | num {}".format(self.auto_func.event_num))

            # adb shell
            elif cmd[0] == "adb":
                adb_cmd = ""
                for i in cmd:
                    adb_cmd = adb_cmd + i + " "
                os.system(adb_cmd)
            else:
                self.pErr(0x02)
            
    
    # 创建文件 - [para：reWrite 重写文件]
    # Api - self.f 文件对象
    def createFile(self, reWrite):
        if not os.path.exists(self.file_path) or reWrite:
            f = open(self.file_path, "w+")
            f.write("# [INFORMATION]\n")
            f.write("# 脚本名称[{}]\n".format(self.info_dict['file_name']))
            f.write("# 作者[{}]\n".format(self.info_dict['author_name']))
            f.write("# 创建日期[{}]\n\n".format(self.info_dict['creattime']))
            f.write("import os\n")
            f.write("import subprocess\n")
            f.write("import time\n")
            self.file_state = "[+] Script file creation is normal."
            self.f = f
        else: # 文件已存在：不重写，返回追加file对象
            self.file_state = "[!] File already exists!You can continue to add content."
            self.f = open(self.file_path, "a")    

    # 设置信息，内部func
    def setInfo(self, file_path, author):
        if "/" in file_path or "\\" in file_path: self.file_path = file_path
        else: self.file_path = "script/" + file_path
        self.file_name = os.path.basename(file_path)
        self.author_name = author
        self.createtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.info_dict = {
            "file_name": self.file_name,
            "author_name": self.author_name,
            "creattime": self.createtime
        }
 
    # 获取信息，测试func
    def getInfo(self):
        print("脚本名称[{}]".format(self.file_name))
        print("作者[{}]".format(self.author_name))
        print("创建日期[{}]".format(self.createtime))
