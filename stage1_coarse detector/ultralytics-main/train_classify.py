from ultralytics import YOLO
 
 
# 加载模型
model = YOLO('yolov8x-cls.yaml').load('yolov8x-cls.pt')  # 从YAML构建并转移权重
 
if __name__ == '__main__':
    # 训练模型
    results = model.train(data='/data1/zhp/2024AICITY/yolov8_classify/datasets', epochs=100, imgsz=640, batch = 48) # stage1:1280; stage2:576
 
    metrics = model.val()