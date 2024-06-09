# -*- coding: utf-8 -*-
import os
import sys
import socket
import threading
import time
import DobotDllType as dType

抓取点=[268.5032, -2.7289, 39.5789, -7.0851]

放置点=[25.9040, -280.8107, 80, -88.5706]

安全点=[143.8237, -204.4392, 61.2637, -59.1162]

# 创建socket客户端变量
socket_client1 = ''
# 定义全局变量
x = 0
y = 0
k = 0

# 定义机械臂状态,用键值存储
CON_STR = {
    dType.DobotConnect.DobotConnect_NoError: "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}
# 加载机械臂动态链接库DobotDll.dll
api = dType.load()
# 连接机械臂
state = dType.ConnectDobot(api, "COM10", 115200)[0]  ###注意机器人端口
# 打印机械臂连接状态
print("Connect status:", CON_STR[state])
# 设置机械臂PTP运动模式参数(门型运动时抬升高度为100,最大高度为110)
dType.ClearAllAlarmsState(api)
dType.SetPTPJumpParams(api, 100, 110, isQueued=1)
dType.SetInfraredSensor(api, 1, 2, version=1) #设置光电传感器
# 设置机械臂末端为夹爪
dType.SetEndEffectorParams(api, 59.7, 0, 0, 1)
# 初始化清空机械臂的指令
dType.SetQueuedCmdClear(api)
# 开始执行队列指令
dType.SetQueuedCmdStartExec(api)
#机械臂回零
# dType.SetHOMECmd(api, 1, isQueued=1)
# 机械臂初始位置
dType.SetPTPCmd(api, 1, 218, -100, 50, 0, isQueued=1) #运动到初始位置s

print('Starting...')

# 光电到物料到位检测
def target_reach():
    # 使能光电传感器
    # 
    time_start = time.time()
    while True:
        # dType.SetInfraredSensor(api, 1, 1, version=0)
        i = [0]
        # 获取光电传感器的值
        i = dType.GetInfraredSensor(api, 2)
        # print(i[0])
        time_end = time.time()
        # 检测光电信号判断物料到位，25秒之后取消等待
        if (time_end - time_start) > 25:
            break
        elif i[0] == 1:
            print(f"检测到光电信号:{i[0]}")
            break


# 光电物料离位检测
def target_leave():
    time_start = time.time()
    while True:
        i = dType.GetInfraredSensor(api, 2)
        time_end = time.time()
        if i[0] == 1 and (time_end - time_start) < 25:
            time.sleep(0.2)
            pass
        else:
            print(f"检测到光电信号离开:{i[0]}")
            break


# 码垛堆叠多个方块
def pileup():
    global x, y, k

    dType.SetEndEffectorGripper(api, 1, 0, isQueued=1)
    #step1:到达安全点
    dType.SetPTPCmdEx(api, 1, 安全点[0], 安全点[1], 安全点[2], 安全点[3], isQueued=1)
    #step2:计算抓取的位置
    piont_x = (int)(抓取点[0] - (x * 50))
    piont_y = (int)(抓取点[1] - (y * 50))
    print(f"{piont_x} {piont_y} {抓取点[2]} {抓取点[3]}")

    dType.SetPTPCmdEx(api, 1, piont_x, piont_y, 抓取点[2], 抓取点[3], isQueued=1)
    dType.SetPTPCmdEx(api, 1, piont_x, piont_y, 抓取点[2]-50,    抓取点[3], isQueued=1)
    dType.SetEndEffectorGripper(api, 1, 1, isQueued=1)
    dType.dSleep(1000)
    dType.SetPTPCmdEx(api, 1, piont_x, piont_y, 抓取点[2], 抓取点[3], isQueued=1)
    # 延时500ms
    dType.dSleep(500)
    #step3:放置
    # 放置                   
    dType.SetPTPCmdEx(api, 1, 放置点[0], 放置点[1], 放置点[2], 放置点[3], isQueued=1)
    dType.SetPTPCmdEx(api, 1, 放置点[0], 放置点[1], 放置点[2]-10, 放置点[3], isQueued=1)
    dType.SetEndEffectorGripper(api, 1, 0, isQueued=1)
    dType.dSleep(1000)
    dType.SetPTPCmdEx(api, 1, 放置点[0], 放置点[1], 放置点[2], 放置点[3], isQueued=1)
    #step4:检测物料
    dType.SetEMotor(api, 0, 1, -10000, isQueued=1)
    # 光电物料到位阻塞检测，限时25s
    target_reach()
    # 传送带停止，触发相机拍照定位                                                           
    dType.SetEMotor(api, 0, 0, 0, isQueued=1)
    socket_client.send("arrive".encode('utf-8'))
    # 光电物料离位阻塞检测，限时25s                                      
    target_leave()
    # # 2*4矩阵(一层)
    #step5:计算累加值
    if y < 2 and x <=1:
        y+=1
    elif x<2:
        x += 1
        y = 0
    if x==2:
        return False
    return True



# 初始化TCP客户端，连接视觉服务端，等待信号
def TCPClient_Vision():
    global socket_client
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        ip_Vision = "127.0.0.1"
        port = 8080
        socket_client.connect((ip_Vision, port))
        print('Successful to initialize tcpclient_Vision.')
    except Exception as e:
        print(e)
    while True:
        try:
            data = socket_client.recv(1024).decode('utf-8')
            print(data)
            checkdata = data[:5]
            # 当接收到run指令开始上料
            if checkdata == 'run':
                print('机械臂上料')
                result = pileup()
                if not result:
                    break
            elif str(data) == "exit":
                break

        except UnicodeDecodeError:
            print('error')
        time.sleep(0.1)


# 主程序入口
if __name__ == "__main__":
    TCPClient_Vision()
