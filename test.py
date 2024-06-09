from ResNet import predict
import cv2
from PIL import Image
import socket
import time
import os
from datetime import datetime

# img = cv2.imread("img.jpg")
# result = predict(img)
# print(result[0])
# # d = {"carrot":"place_point_1","vegatable":"place_point_2"}
# # print(d["vegatable"])

def openTcpClient():
    global socket_client
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        ip_Vision = "127.0.0.1"
        port = 8080
        socket_client.connect((ip_Vision, port))
        print('Successful to initialize tcpclient_Vision.')
    except Exception as e:
        print(e)
    
    lastModifiyTime = datetime.now()
    while True:
        try:
            imagePath = "./img.bmp"
            mtime = os.path.getmtime(imagePath)              #修改时间
            mtime_string = datetime.fromtimestamp(int(mtime))
            if mtime_string > lastModifiyTime:
                print(f"检测到新文件")
                # result =  VerifyImage(imagePath) #预测图像
                # print(f"结果:{result['result']},  预测率:{result['probability']}")
                img = cv2.imread(imagePath)
                result = predict(img)
                print(f"结果:{result[0]},预测率:{result[2]}")
                
                socket_client.send(f"{result[0]}".encode('utf-8'))
                lastModifiyTime = mtime_string

        except UnicodeDecodeError:
            print('error')
        time.sleep(0.1)

if __name__ == "__main__":
    openTcpClient()