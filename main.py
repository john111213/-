from PIL import Image
import os

# 读取 raw 中所有的图片
original_files = os.listdir("./raw/")

for filename in original_files:
    if not filename.endswith(".jpg"):
        continue
    img = Image.open(f"./raw/{filename}")
    output_num = 20      #旋转次数

    for i in range(1, output_num + 1):
        angle = 360 * i / output_num
        out = img.rotate(angle).convert("RGB")  #jpg支持3通道png支持4通道

        newname = f"./out/{os.path.splitext(filename)[0]}_{i}.jpg"
        out.save(newname)
    print(f"{filename} complete!")

print("all complete!")

#移除raw文件夹里的图片
remove_raw_file = input("remove raw file? (y/n)").lower() == "y"

if remove_raw_file:
    for filename in original_files:
        os.remove(f"./raw/{filename}")
        print("complete!")

# 重命名out文件夹里的图片
folder = "./out/"
suffix = input("suffix: ")    #输入图片名字

original_files = os.listdir(folder)
count = 0

for i in original_files:
    print(i, "=>", f"{suffix} ({count}).jpg")
    os.rename(folder + i, f"{folder}{suffix} ({count}).jpg")
    count += 1
print("complete!")
