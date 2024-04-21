import os
import shutil
'''image'''
source_dir = './data/aicity2024_track5/train_all_img/'
train_dir = './data/aicity2024_track5/stage1/images/train/'
val_dir = './data/aicity2024_track5/stage1/images/val/'
# 创建新的文件夹
os.makedirs(train_dir, exist_ok=True)
os.makedirs(val_dir, exist_ok=True)

# 遍历源文件夹中的所有文件
for filename in os.listdir(source_dir):
    if filename.endswith('.jpg'):
        # 提取文件名中的数字部分
        num_part = filename.split('_')[-1].split('.')[0]
        try:
            num = int(num_part)
        except ValueError:
            continue  # 如果无法将数字部分解析为整数，则跳过这个文件

        # 根据数字部分决定文件夹
        if 0 <= num <= 140:
            destination = os.path.join(train_dir, filename)
        else:
            destination = os.path.join(val_dir, filename)

        # 移动文件
        shutil.move(os.path.join(source_dir, filename), destination)
'''txt'''
# 输入文件路径
input_file_path = './data/aicity2024_track5/gt.txt'
train_output_file_path = './data/aicity2024_track5/stage1/train.txt'
val_output_file_path = './data/aicity2024_track5/stage1/val.txt'

# 打开输入文件和输出文件
with open(input_file_path, 'r') as input_file, open(train_output_file_path, 'w') as train_output, open(val_output_file_path, 'w') as val_output:
    # 逐行读取输入文件
    for line in input_file:
        # 分割每行数据
        columns = line.split(',')

        # 确保至少有两列数据
        if len(columns) >= 2:
            # 获取第二列的内容
            second_column = int(columns[1])  # 假设第二列是整数，如果是字符串，可以直接使用columns[1]

            # 根据第二列的值进行分类
            if second_column > 140:
                val_output.write(line)
            else:
                train_output.write(line)

print("Done")
