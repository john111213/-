import os
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import torch
from torchvision import models, transforms
import torch.nn.functional as F
import torch.nn as nn
import time


# 模型推理
def predict(image, model_path: str = "./model/model.pkl"):
    grey_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    tsfrm = transforms.Compose([
        transforms.Grayscale(3),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    ])
    # 0.水果 1.蔬菜 2.服装 3.零食
    classes = ["luobo", "baicai","boluo"]
    device = torch.device("cpu")
    model_eval = models.resnet18(pretrained=False)
    num_ftrs = model_eval.fc.in_features
    model_eval.fc = nn.Linear(num_ftrs, len(classes))
    model_eval.load_state_dict(torch.load(model_path, map_location=device))
    # 在推理前，务必调用model.eval()去设置dropout和batch normalization层为评估模式
    model_eval.eval()
    # OpenCV转PIL格式
    image = Image.fromarray(cv2.cvtColor(grey_img, cv2.COLOR_GRAY2RGB))
    # PIL图像数据转换为tensor数据，并归一化
    img = tsfrm(image)
    # 图像增加1维[batch_size,通道,高,宽]
    img = img.unsqueeze(0)
    # 输出推理结果
    output = model_eval(img)
    # prob是4个分类的概率
    prob = str(F.softmax(output, dim=1))
    value, predicted = torch.max(output.data, 1)
    prob_stat = prob[prob.find("[[") + 2: prob.find("]]")].replace(" ", "").split(",")
    prob_stat = list(map(float, prob_stat))
    prob = 0
    tmp = 0
    for i, n in zip(range(len(prob_stat)), prob_stat):
        if n > tmp:
            tmp = n
            prob = i
    # 定义 检测方法的返回值  检测的物品名称 检测物品名称的编号  检测成功率
    return classes[prob], prob, tmp
    #return classes[prob]


# 显示推理结果
def showResult(image, text):
    # 设置图片显示分辨率
    newimg = cv2.resize(image, (640, 480))
    fontpath = "simsun.ttc"
    font = ImageFont.truetype(fontpath, 48)
    img_pil = Image.fromarray(newimg)
    draw = ImageDraw.Draw(img_pil)
    # 绘制文字信息
    draw.text((10, 100), text, font=font, fill=(0, 0, 255))
    bk_img = np.array(img_pil)
    # 获取实时时间作为命名，将识别图片和结果保存到文件夹
    str_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    img_name = str_time + '.jpg'
    cv2.imwrite('./result/' + img_name, bk_img)
    cv2.imshow('frame', bk_img)
    # 持续显示3s
    key = cv2.waitKey(3000)
    cv2.destroyAllWindows()


# 清空缓存图片
def remove_result():
    path = './result/'
    # 判断是否存在result文件夹
    if os.path.exists(path):
        for i in os.listdir(path):
            # 遍历拼接文件路径
            path_file = os.path.join(path, i)
            # 判断该路径对象是否为文件
            if os.path.isfile(path_file):
                # 删掉文件    
                os.remove(path_file)
    else:
        # 新建一个result文件夹
        os.mkdir(path)

    # 主程序入口


def do_recognize(image_path: str, show_result: bool, model_path: str = "./model/model.pkl") -> int:
    """
    调用ResNet18框架进行识别
    :param model_path: 模型路径
    :param image_path: 图像路径
    :param show_result: 是否弹框显示结果
    :return:
    """
    # 返回识别到的类型序号.
    # 将图像预处理后的图像进行模型推理
    image = cv2.imread(image_path)
    label, pred_class, prob = predict(image, model_path)
    # 不显示推理结果
    if show_result:
        showResult(image, pred_class)

    if prob < 0.5:
        print(f"!--未知物料--!")
        return -1
    print(f"识别序号: {pred_class}, 识别结果: {label}, 可能性: {prob}")
    return pred_class
