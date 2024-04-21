from numpy import *

# fp = open("H:/Datasets/2023AICity/aicity2023_track5/dataset/split_video/val/val_gt.txt",'r')
fp = open("./data/aicity2024_track5/stage1/train.txt",'r')
datanum=-1
for eachline in fp.readlines():  # 读取每一行数据
    data = eachline.strip().split(',') # 提取出的数据
    
    # 如果和上一行数据的帧数不一样，就给新的txt名
    if data[1] != datanum:
        new_name = (data[0]).zfill(3)+'_'+ data[1]  #读取第几个视频的第几帧 100_199 


    '''将标注数据转化为yolov7格式'''
    w = format(int(data[4])/1920, '.6f')   # 中心点坐标
    h = format(int(data[5])/1080, '.6f')
    x = format(int(data[2])/1920+float(w)/2, '.6f')
    y = format(int(data[3])/1080+float(h)/2, '.6f')


    new_line = str(int(data[-1])) + ' ' + str(x) + ' ' +  str(y) + ' ' +  str(w) + ' '  +  str(h) + '\n'
    datanum=data[1]
    '''将同一张图片同一帧的数据保存在同一个txt里'''
    filename = f"./data/aicity2024_track5/stage1/annoations/original_train/{new_name}.txt"
    with open(filename,'a') as output_file:
        output_file.write(new_line)

   

