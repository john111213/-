'''
1. 处理图像的函数
    1. 读取数据集
    2. 读取训练集
    3. 使用方法训练
    4. 生成训练模型
2. 验证结果
    1. 调用训练模型
    2. 输出返回值
3. 使用训练模型
    1. 调用
    2. 编写函数
    3. 定义输出值
'''
# 加载库函数
import os
import time
import torch
import torchvision
from torchvision import datasets, models, transforms
import numpy as np
import copy
import glob
import shutil
import torch.nn as nn
import torch.optim as optim
from torch.optim import lr_scheduler

# 数据集存放路径
path = './data/'
# 定义两个数据集合 和data 下的文件下的内容要符合
folder_list = ["0.carrot", "1.vegatable"]

# 遍历数据集
for folder in folder_list:
    # 图片格式为.jpg或.png
    jpg_files = glob.glob(os.path.join(path, "train", folder, "*.jpg"))
    png_files = glob.glob(os.path.join(path, "train", folder, "*.png"))
    files = jpg_files + png_files
    # 统计训练集数据
    num_of_img = len(files)
    print(f"Total number of {folder} image is {num_of_img}")  # .format(folder, num_of_img)
    # 从训练集里面抽取20%作为验证集
    shuffle = np.random.permutation(num_of_img)
    percent = int(num_of_img * 1)
    print("Select {} img as valid image".format(percent))
    # 新建val文件夹存放验证集数据
    path_val = os.path.join(path, "val", folder)
    if not os.path.exists(path_val):
        os.makedirs(path_val)
    # 把训练集里面抽取20%的数据复制到val文件夹
    # shuffle()方法将序列的所有元素随机排序
    for i in shuffle[:percent]:
        print("copy file {} ing".format(files[i].split('\\')[-1]))
        shutil.copy(files[i], path_val)

# 数据增强与变换
data_transforms = {
    'train': transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.Grayscale(3),
        transforms.RandomRotation(5),
        transforms.RandomVerticalFlip(0.5),
        transforms.RandomHorizontalFlip(0.5),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    ]),
    'val': transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.Grayscale(3),
        transforms.RandomRotation(5),
        transforms.RandomVerticalFlip(0.5),
        transforms.RandomHorizontalFlip(0.5),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    ])
}

# 加载数据
data_dir = './data/'
image_datasets = {x: datasets.ImageFolder(os.path.join(data_dir, x), data_transforms[x]) for x in ['train', 'val']}
print(image_datasets)
dataloaders = {x: torch.utils.data.DataLoader(image_datasets[x],
                                              batch_size=4,
                                              shuffle=True,
                                              num_workers=0) for x in ['train', 'val']}
print(dataloaders)
dataset_sizes = {x: len(image_datasets[x]) for x in ['train', 'val']}
print(dataset_sizes)
class_names = image_datasets['train'].classes
print(class_names)

# 判断GPU是否可用
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(device)


# 通用训练模型函数
def train_model(model, criterion, optimizer, scheduler, num_epochs=25):
    since = time.time()
    # state_dict是Python字典对象，它将每一层映射到其参数张量
    # deepcopy为深拷贝
    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0

    for epoch in range(num_epochs):
        print('Epoch {}/{}'.format(epoch, num_epochs - 1))
        print('-' * 10)

        # 每个epoch都有一个训练和验证阶段
        for phase in ['train', 'val']:
            if phase == 'train':
                # 调用Optimizer的step函数使它所有参数更新
                scheduler.step()
                model.train()  # Set model to training mode
            else:
                model.eval()  # Set model to evaluate mode

            running_loss = 0.0
            running_corrects = 0

            # 迭代数据
            for inputs, labels in dataloaders[phase]:
                # GPU加速
                inputs = inputs.to(device)
                labels = labels.to(device)
                # 清空梯度，在每次优化前都需要进行此操作
                optimizer.zero_grad()
                # 前向
                # track history if only in train
                # forward + backward + optimize
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)
                    # 后向 + 仅在训练阶段进行优化
                    if phase == 'train':
                        # 反向传播：根据模型的参数计算loss的梯度
                        loss.backward()
                        # 调用Optimizer的step函数使它所有参数更新
                        optimizer.step()
                # 打印统计数据
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects.double() / dataset_sizes[phase]

            print('{} Loss: {:.4f} Acc: {:.4f}'.format(
                phase, epoch_loss, epoch_acc))

            if phase == 'val' and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_model_wts = copy.deepcopy(model.state_dict())
        print()
    time_elapsed = time.time() - since
    print('Training complete in {:.0f}m {:.0f}s'.format(
        time_elapsed // 60, time_elapsed % 60))
    print('Best val Acc: {:4f}'.format(best_acc))
    # 加载最佳模型权重
    model.load_state_dict(best_model_wts)
    return model


# 主程序入口
if __name__ == "__main__":
    # 加载resnet18网络结构
    model_ft = torchvision.models.resnet18(pretrained=False)
    # 加载resnet18网络参数
    model_ft.load_state_dict(torch.load('./model/resnet18.pth'))
    num_ftrs = model_ft.fc.in_features
    model_ft.fc = nn.Linear(num_ftrs, len(folder_list))
    model_ft = model_ft.to(device)
    # 这里使用分类交叉熵Cross-Entropy作为损失函数，动量SGD作为优化器
    criterion = nn.CrossEntropyLoss()
    # 初始化优化器
    optimizer_ft = optim.SGD(model_ft.parameters(), lr=0.001, momentum=0.9)
    # 每7个epochs衰减LR通过设置gamma = 0.1
    exp_lr_scheduler = lr_scheduler.StepLR(optimizer_ft, step_size=7, gamma=0.1)
    # 开始训练模型 (每类120张图像迭代30次, 用时约40分钟)
    model_ft = train_model(model_ft, criterion, optimizer_ft, exp_lr_scheduler, num_epochs=15)
    # ----------------------
    # 保存加载模型
    torch.save(model_ft.state_dict(), 'model/model.pkl')