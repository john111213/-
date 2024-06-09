# -*- coding: utf-8 -*-
import os
import sys
import socket
from threading import Thread
import time
import DobotDllType as dType
import multiprocessing

sampleClass = ["luobo", "baicai","boluo"]
安全点 = [143.9588, 225.4592, 97.3874, 0]

归零点=[250, 0, 120, 0] #归零点

抓取点 = [
    [-145.5422, 262.4383, 58.5201, 75.4757],    
    [-145.5422, 262.4383, 58.5201, 75.4757],
    [-145.5422, 262.4383, 58.5201, 75.4757],
    [-145.5422, 262.4383, 58.5201, 75.4757],
    [-145.5422, 262.4383, 58.5201, 75.4757]
]
放置点=[
    [208.1685, 201.3569, 16.9426, 44.0471],
    [275.0948, 7.1190, 29.5964, 1.4824],
    [270.2278, 40 ,  0, 80.3771],
    [270.2278, -20 , 0, 80.3771],
    [270.2278, -80 , 0, 80.3771]
]
横累加计数=[
    0,
    0,
    0,
    0,
    0
]
列累加计数=[
    0,
    0,
    0,
    0,
    0
]
纵累加计数=[
    0,0,0,0,0
]



# 创建socket客户端变量
socket_server = ''
tcpCliSock1 = '' #分类模块(下料)
tcpCliSock2 = '' #视觉
tcpCliSock3 = '' #上料
# 定义全局变量
i = 0
j = 0
k = 0
# coord_X = 0
# coord_Y = 0
coord_X = multiprocessing.Value('d', 0)
coord_Y = multiprocessing.Value('d', 0)

# 定义机械臂状态,用键值存储
CON_STR = {
    dType.DobotConnect.DobotConnect_NoError: "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}
# 加载机械臂动态链接库DobotDll.dll
api = dType.load()
# 连接机械臂
state = dType.ConnectDobot(api, "COM9", 115200)[0]  ###注意机器人端口
# 打印机械臂连接状态
print("Connect status:", CON_STR[state])
# 设置机械臂PTP运动模式参数(门型运动时抬升高度为100,最大高度为110)
dType.ClearAllAlarmsState(api)
dType.SetPTPJumpParams(api, 100, 110, isQueued=0)
dType.SetInfraredSensor(api, 1, 1, version=0)
# 设置机械臂末端为夹爪
dType.SetEndEffectorParams(api, 59.7, 0, 0, 1)
#设置光电传感器V2-GP4
dType.SetInfraredSensor(api, 1, 2, version=1)
# 初始化清空机械臂的指令
dType.SetQueuedCmdClear(api)
# 开始执行队列指令
dType.SetQueuedCmdStartExec(api)
# 机械臂初始位置
# dType.SetHOMECmd(api,1,isQueued=1) #执行归零命令
dType.SetPTPCmd(api, 0, 安全点[0], 安全点[1], 安全点[2], 安全点[3], isQueued=1)
print('Starting...')

tcpClient={
    "cliSock":'',
    'addr':''
}



def 视觉监听(coord_X,coord_Y,socker, addr, info):
    global tcpCliSock1
    # global coord_X
    # global coord_Y
    while True:
        data = socker.recv(1024).decode("utf-8")
        print(f"{addr} 发来消息:{str(data)}")
        if str(data).split(";")[0] == "OK":
            # coord_X = str(data).split(";")[1] #获取X坐标
            # coord_Y = str(data).split(";")[2] #获取Y坐标
            coord_X.value = float(str(data).split(";")[1])
            coord_Y.value = float(str(data).split(";")[2])
            print(f"接受到坐标:{coord_X.value};{ coord_Y.value}")
            tcpCliSock1.send(str(data).encode('utf-8'))
        elif str(data) == "exit":
            break
        data = "null"
        time.sleep(0.5)

    socker.close()

def 上料监听(socker,addr, info):
    global tcpCliSock2
    while True:
        data = socker.recv(1024).decode("utf-8")
        print(f"{addr} 发来消息:{str(data)}")
        if(str(data) == "arrive"):
            tcpCliSock2.send("getPhoto".encode('utf-8')) #发送视觉触发命令

        elif str(data) == "exit":
            break
        data = "null"
        time.sleep(0.5)

    socker.close()

def 视觉分类(coord_X,coord_Y,socker, addr, info):
    global tcpCliSock3
    # global coord_X
    # global coord_Y
    while True:
        data = socker.recv(1024).decode("utf-8")  #carrot
        print(f"{addr} 发来消息:{str(data)}")
        try:
            
            # coord_X = -80.625
            # coord_Y = 241.818
            r = 172.0037
            index = sampleClass.index(str(data))#0
            dType.SetEndEffectorGripper(api, 0, 0, isQueued=1)
            dType.dSleep(1000)
            dType.SetEndEffectorGripper(api, 1, 0, isQueued=1)   #释放夹爪
            dType.SetPTPCmdEx(api, 1, coord_X.value-20, coord_Y.value, 抓取点[index][2] + 50, r, isQueued=1)
            dType.dSleep(500)
            dType.SetPTPCmdEx(api, 1, coord_X.value-20, coord_Y.value, 抓取点[index][2]-20, r, isQueued=1)
            dType.SetEndEffectorGripper(api, 1, 1, isQueued=1)   #闭合夹爪
            dType.dSleep(1000)
            dType.SetPTPCmdEx(api, 1, coord_X.value-20, coord_Y.value, 抓取点[index][2] + 50, r, isQueued=1) #抬起

            dType.SetPTPCmdEx(api, 1, 安全点[0], 安全点[1], 安全点[2] + 50, 安全点[3], isQueued=1) #抬起
            dType.dSleep(1000)
            # print(f"放置点:{(放置点[index][0] - 横累加计数[index] * 50)}, {(放置点[index][1] - 列累加计数[index] * 50)}, {放置点[index][2]}, {放置点[index][3]}")

            # x = (int)(放置点[index][0] - 横累加计数[index] * 50)
            # y = (int)(放置点[index][1] - 列累加计数[index] * 50)
            delta_z = 纵累加计数[index] * 50 + 60
            x = (int)(放置点[index][0])
            y = (int)(放置点[index][1])
            z = (int)(放置点[index][2] + delta_z)
            r = (int)(放置点[index][3])
            print(f"放置点:{x}, {y}, {z}, {r}")
            dType.SetPTPCmdEx(api, 1, x, y, z, r, isQueued=1)
            dType.SetPTPCmdEx(api, 1, x, y, z - 60, r, isQueued=1)
            dType.SetEndEffectorGripper(api, 1, 0, isQueued=1)   #释放夹爪
            dType.dSleep(2000)
            dType.SetPTPCmdEx(api, 1, x, y, z, r, isQueued=1)
            dType.SetPTPCmdEx(api, 1, 归零点[0], 归零点[1], 归零点[2], 归零点[3], isQueued=1)
            
            
            checkdata = 'null'
            #2*3
            # if 横累加计数[index] <= 1 and 列累加计数[index] <= 2:
            #     横累加计数[index]+=1
            # elif 横累加计数[index] >= 1 and 列累加计数[index] < 2:
            #     横累加计数[index] = 0
            #     列累加计数[index] += 1
            纵累加计数[index]+=1
            print("帮运结束")
            dType.SetEndEffectorGripper(api, 0, 0, isQueued=1)
            
            #tcpCliSock3.send("run".encode('utf-8'))
        except:
            print("")
        if str(data) == "exit":
            break
        data = "null"
        time.sleep(0.5)

    socker.close()

def openTCPServer():
    global socket_server
    global tcpCliSock1
    global tcpCliSock2
    global tcpCliSock3
    #step1:开启服务端
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_server.bind(('127.0.0.1', 8080))
    socket_server.listen(5) #最大等待5台设备

    print(f".........等待分类模块连接.........")
    tcpCliSock1, addr1 = socket_server.accept()
    clientThread1 = Thread(target=视觉分类, args=(coord_X,coord_Y,tcpCliSock1, addr1, f"客户端{addr1}"))           #开启监听线程
    clientThread1.start()
    print(f"#########分类模块已连接###########")

    print(f".........等待视觉模块连接.........")
    tcpCliSock2, addr2 = socket_server.accept()
    clientThread2 = Thread(target=视觉监听, args=(coord_X,coord_Y,tcpCliSock2, addr2, f"客户端{addr2}"))           #开启监听线程
    clientThread2.start()
    print("#########视觉模块已连接###########")

    print(f".........等待上料模块连接.........")
    tcpCliSock3, addr3 = socket_server.accept()
    clientThread3 = Thread(target=上料监听, args=(tcpCliSock3, addr3, f"客户端{addr3}")) #开启监听线程
    clientThread3.start()
    print(f"#########上料模块已连接###########")
    tcpCliSock1.send(str(12134).encode('utf-8'))
    
    while True:
        temp = input(f"接受指令:")
        tcpCliSock3.send(temp.encode("utf-8"))
        #tcpCliSock2.send(temp.encode("utf-8"))

        time.sleep(0.5)
        if temp == "exit":
            tcpCliSock1.send("exit".encode("utf-8"))
            tcpCliSock2.send("exit".encode("utf-8"))
            tcpCliSock3.send("exit".encode("utf-8"))
            break

        temp = "null"

    socket_server.close()

if __name__ == "__main__":
    openTCPServer()
