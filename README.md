## AICITY2024_Track5

This repo includes solution for AICity2024 Challenge Track 5 - Detecting Violation of Helmet Rule for Motorcyclists


![framework.png](/_resources/framework.png)

# Installation
Please find installation instructions for PyTorch and YOLOv8 in [here](https://github.com/ultralytics/ultralytics)

Please find installation instructions for PyTorch and Co-DETR. Tested on torch1.11.1+cuda11.3+Pillow10.2.0 [here](https://github.com/Sense-X/Co-DETR)

## Data Preparation For Training
Download the training data (aicity2024_track5) into ./data/

The format of dataset as follows:
>   - data
>     - aicity2024_track5
>       - videos
>       - ReadMe.txt   
>       - gt.txt
>       - ...

```bash
cd data_pre
```
Extract frames and split train-val
```bash
python video2picture.py -f=300
python split_train_val.py
python yolo2coco.py
```

Generate label for YOLOv8
```bash
python original_9cls_to_bigbox.py
```
Generate label for Co-DETA
```bash
python create_crop_picture.py
python yolo2codetr.py
```
## Train
Train YOLOv8(Coarse Detector)
```bash
cd stage1_coarse detector/ultralytics-main
python train.py
```
Train Co-DETR(Fine-grained Detector)
```bash
cd stage2_grained-fine detector/Co-DETR-main
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5  bash tools/dist_train.sh projects/configs/my_model/my.py 6 /data1/zhp/2024AICITY/Co-detr/path
```

## Inference

The checkpoints after trainning process can be downloaded [here](https://drive.google.com/drive/folders/14DnI_kpq2jSh0Ou1_mW9oKfuoNBtyYuw?usp=drive_link), which includes all the checkpoints. After downloading all the checkpoints, please put all files into ./weights/

```bash
cd data_pre
```
Extract frames
```bash
python video2picture.py
python yolo2coco.py
```
Detect results
```bash
cd stage1_coarse detector/ultralytics-main
CUDA_VISIBLE_DEVICES=6 yolo task=detect mode=val batch=8 workers=2 split=test save_json=True augment=True device=6 model=./weights/stage1_best.pt data=ultralytics/cfg/datasets/aicity.yaml 
name=stage1_coarse detector/ultralytics-main/run/stage1_result

cd ../../data_pre
python crop_predict_val_and_test.py

cd ../stage2_grained-fine detector/Co-DETR-main
CUDA_VISIBLE_DEVICES=0,1,2,3 bash tools/dist_test.sh projects/configs/my_model/my.py ./weights/stage1_epoch10.pth 4 --format-only --options "jsonfile_prefix=/data1/zhp/2024AICITY/Co-detr/inference_two_cls/test_epoch10"

cd ../../post_processing
python create_final_json.py

```



## Public Leaderboard
|TeamName|Score|
|--------|-----|
|BUPT_MCPRL|0.3940|

