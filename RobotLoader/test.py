# import time
# i = 0
# j = 0
# print('start...')
# while True:
#     print('i = ',i)
#     print('j = ',j)
#     if j < 2 and i <= 2:
#         j += 1
#     elif j >= 2 and i < 2:
#         j = 0
#         i += 1
#     else:
#         break
#     time.sleep(2)
# print('finish...')

# import time
# i = 0
# j = 0
# k = 0
# print('start...')
# while True:
#     print('i = ',i)
#     print('j = ',j)
#     print('k = ',k)
#     if j < 1 and i <= 1:
#         j += 1
#     elif j >= 1 and i < 1:
#         j = 0
#         i += 1
#     else:
#         i = 0
#         j = 0
#         k += 1
#         if k==2:
#             break
#     time.sleep(2)
# print('finish...')

# 5行4列矩阵
# 00 10 20 30
# 01 11 21 31
# 02 12 22 32
# 03 13 23 33
# 04 14 24 34
import time
i = 0
j = 0
print('start...')
while True:
    print('j = ',j)
    print('i = ',i)
    if j < 3 and i <= 4:
        j += 1
    elif j >= 3 and i < 4:
        j = 0
        i += 1
    else:
        break
    time.sleep(2)
print('finish...')

############### 测试参考代码 ###################
# # 5*4矩阵(一层)
# if j < 3 and i <= 4:
#     j += 1
# elif j >=3  and i < 4:
#     j = 0
#     i += 1
# else:
#     print('机械臂结束上料')
#     sys.exit()

# # 3*3矩阵(两层)
# if j < 2 and i <= 2:
#     j += 1
# elif j >= 2 and i < 2:
#     j = 0
#     i += 1
# else:
#     i = 0
#     j = 0
#     k += 1
#     if k==2:
#         print('机械臂结束上料')
#         sys.exit()
