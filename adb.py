# adb封包

import subprocess
import os

class Adb_func():
    
    def showkeys():
        key_info = '''
        \033[1;32;40m===================================\033[0m
        \033[1;32;40m使用 key [num] 形式添加执行按键动作\033[0m
        \033[1;32;40m===================================\033[0m
        按下电源键:26
        按下菜单键:82
        按下HOME 键:3
        按下返回键:4
        增加音量:24
        降低音量:25
        静音:164
        播放/暂停:85
        停止播放:86
        播放下一首:87
        播放上一首:88
        恢复播放:126
        暂停播放:127
        '''
        print(key_info)


    def info():
        info = '''
        \033[1;32;40m=========================\033[0m
        \033[1;32;40m默认可使用adb命令进行调试\033[0m
        \033[1;32;40m=========================\033[0m
        exit -  退出
        click [num1] [num2] - 点击屏幕(x,y)点
            [num] 点击点(x,y)的坐标数值
        keyevent  -  查看所有系统按键
        key [num] -  点击按键
            [num] 按键代码，输入keyevent命令查看代码
        state     -  查看adb连接手机状态
        
        install [-r] [file.apk] -  安装软件
            -r  可选参数，覆盖原有的apk进行安装
            [file.apk] 要安装的App路径
        uninstall [-k] [package] -  卸载软件
            -k  可选参数，保留apk配置文件卸载

        pkg  -  显示所有包名
            -s 只显示系统应用
            -3 只显示第三方应用
            --this  显示当前App的包名
        savepkg [file] [mode]- 保存所有包名到文件默认为 data\packages.txt
            [file] 可选参数，自定义保存文件路径
            [mode] 可选参数，保存包名类型，参数同pkg命令
        exact - 显示当前页面的Activity,并执行可选操作
            --launcher 可选参数，找到当前App启动页面的Activity
        cleardata [package] - 清除当前应用数据
            [package] 可选参数，指定清除的App包名
        '''
        print(info)

    def devices():
        return "adb devices"

    # 查看所有包
    def showAllPkg(mode=None):
        if mode == "-s":
            return "adb shell pm list packages -s"
        elif mode == "-3":
            return "adb shell pm list packages -3"
        elif mode == None:
            return "adb shell pm list packages"
        elif mode == "--this":
            return "adb shell 'dumpsys window | grep mCurrentFocus'"
        else:
            return ""

    # 按键控制
    def keyevent(key:str):
        keyevent = [26, 82, 3, 4, 24, 25, 164, 85, 86, 87, 88, 126, 127]
        for i in keyevent:
            if str(i) == key:
                return "adb shell input keyevent "+key
        return 0
    def click(x:int, y:int):
        # adb shell getevent -p | grep -e "0035" -e "0036" 屏幕最大分辨率
        # iqoo z1 1079 2407
        return "adb shell input tap {} {}".format(x, y)

    # 安装/卸载apk
    def install(apk:str, mode=None):
        if mode == '-r' and os.path.exists(apk):
            return "adb install -r " + apk
        elif os.path.exists(apk):
            return "adb install " + apk
        else:
            return ""
    def uninstall(apk:str, mode=None):
        if mode == '-k':
            return "adb uninstall -k " + apk
        elif "com" in apk:
            return "adb uninstall " + apk
        else:
            return ""

    # 显示appActivity
    def showActivity():
        return "adb shell 'dumpsys window | grep mCurrentFocus'"
    # 显示app启动页面Activity
    def actionAct(activity:str):
        return "adb shell am start -n " + activity
    def clearData(pkg=None):
        if pkg != None:
            return "adb shell pm clear " + pkg
        return "adb shell pm clear " + subprocess.getoutput(Adb_func.showAllPkg("--this")).split(" ")[-1].split("/")[0].replace("\n", "")

    # 可视化auto api
    def getEvent():
        return 'adb shell getevent -p | grep -e "0035" -e "0036"'
    def getEventEev():
        return 'adb shell getevent | grep -e "0035" -e "0036"'
    
# 查看当前Activity
def sh(command, print_msg=True):
    p = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = p.stdout.read().decode('utf-8')
    if print_msg:
        print(result)
    return result

def safe_index_of(str0, substr):
    try:
        return str0.index(substr)
    except ValueError:
        return -1

def get_launcher_activity(package_name):
    result = sh("adb shell dumpsys package %s" %
                (package_name), print_msg=False)
    if not result:
        return
    end_index = safe_index_of(result, "android.intent.category.LAUNCHER")
    if end_index >= 0:
        start_index = (end_index - 150) if end_index - 150 >= 0 else 0
        lines = result[start_index:end_index].split(' ')
        for line in lines:
            if package_name in line:
                return line.strip()

    start_index = safe_index_of(result, "android.intent.action.MAIN")
    if start_index >= 0:
        end_index = (start_index + 300) if (start_index +
                                            300 < len(result)) else len(result)
        lines = result[start_index:end_index].split(' ')
        key = "%s/" % (package_name)
        for line in lines:
            if '/com.' in line:
                if "/%s" % (package_name) in line:
                    return line.strip()
            if key in line:
                return line.strip()
    return ''

# print(get_launcher_activity('com.akatosh.reimu'))
