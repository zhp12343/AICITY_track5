from ultralytics import YOLO
 
 
# 加载模型
model = YOLO('yolov8x.yaml').load('yolov8x.pt')  # 从YAML构建并转移权重
 
if __name__ == '__main__':
    # 训练模型
    results = model.train(data='VisDrone.yaml', epochs=50, imgsz=1280, batch = 6) # stage1:1280; stage2:576
 
    metrics = model.val()