from PIL import Image
import json
import os
from collections import defaultdict

def load_json(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    grouped_bboxes = defaultdict(list)
    for entry in data:
        image_id = entry['image_id']
        bbox = entry['bbox']
        cls = entry['category_id']
        if int(cls) in [0,1,2]:
            if float(entry['score'])>0.3:
                grouped_bboxes[image_id].append([bbox,entry['score'],cls])
            else:
                grouped_bboxes[image_id].append([bbox,round(float(entry['score'])*0.8,4),cls])
        if int(cls) in [3,4]:
            if float(entry['score'])>0.2:
                grouped_bboxes[image_id].append([bbox,entry['score'],cls])
            else:
                grouped_bboxes[image_id].append([bbox,round(float(entry['score'])*0.8,4),cls])
        if int(cls) in [5,6]:
            if float(entry['score'])>0.15:
                grouped_bboxes[image_id].append([bbox,entry['score'],cls])
            else:
                grouped_bboxes[image_id].append([bbox,round(float(entry['score'])*0.8,4),cls])
        if int(cls) in [7,8]:
            if float(entry['score'])>0.1:
                grouped_bboxes[image_id].append([bbox,entry['score'],cls])
            else:
                grouped_bboxes[image_id].append([bbox,round(float(entry['score'])*0.6,4),cls])
    return grouped_bboxes

def create_new_bbox(stage1_bigbox_json, stage2_json, save_path):
    bigbox_info = load_json(stage1_bigbox_json)
    stage2_info = load_json(stage2_json)

    # 保证裁剪出的整体框中，每个类别只能有一个检测结果
    filtered_stage2_info = defaultdict(list)
    for image_id, bbox_list in stage2_info.items():
        max_score_by_cls = {}
        for bbox,score,cls in bbox_list:
            # print(cls)
            if cls in max_score_by_cls:
                # print(1111111111)
                if float(score)>float(max_score_by_cls[cls][1]):
                    max_score_by_cls[cls] = [bbox,score,cls]
            else:
                max_score_by_cls[cls] = [bbox,score,cls]

        # # 如果2和3不存在，删除5-9的预测结果
        # if 2 not in max_score_by_cls and 3 not in max_score_by_cls:
        #     for m in range(4,10):
        #         if m in max_score_by_cls:
        #             print(max_score_by_cls)
        #             del max_score_by_cls[m]
        #             print(max_score_by_cls)

        # 过滤互斥类别
        # if 2 in max_score_by_cls and 3 in max_score_by_cls:
        #     # print('去除前',max_score_by_cls)
        #     if float(max_score_by_cls[2][1]) > float(max_score_by_cls[3][1]):
        #         del max_score_by_cls[3]
        #         # print('去除后',max_score_by_cls)
        #     else:
        #         del max_score_by_cls[2]
        #         # print('去除后',max_score_by_cls)
        # if 4 in max_score_by_cls and 5 in max_score_by_cls:
        #     # print(max_score_by_cls)
        #     if float(max_score_by_cls[4][1]) > float(max_score_by_cls[5][1]):
        #         del max_score_by_cls[5]
        #     else:
        #         del max_score_by_cls[4]
        # if 6 in max_score_by_cls and 7 in max_score_by_cls:
        #     # print(max_score_by_cls)
        #     if float(max_score_by_cls[6][1]) > float(max_score_by_cls[7][1]):
        #         del max_score_by_cls[7]
        #     else:
        #         del max_score_by_cls[6]

        # print(image_id,max_score_by_cls)
    # 将筛选后的结果加入新的字典
        filtered_stage2_info[image_id].append(list(max_score_by_cls.values()))
    # print(filtered_stage2_info)
    result = []
    for image_id, bbox_list in filtered_stage2_info.items():
        xy = bigbox_info[image_id][0][0][:2]
        score1 = bigbox_info[image_id][0][1]  # stage1的得分
        # print(bbox_list)
        for i, (bbox,score,cls) in enumerate(bbox_list[0], start = 1):
            # print(bbox,score,cls)
            bbox[0] += xy[0]
            bbox[1] += xy[1]
            bbox[0] = max(0,min(bbox[0],1920))
            bbox[1] = max(0,min(bbox[1],1080))
            score = round(((0.5*score+0.5*score1)),3)# round((0.3*score+0.7*score1),3) #  # round((0.5*score+0.5*score1),3) # stage2*0.5+stage1*0.5:mAP0.5921 # score*(score1**0.5):mAP0.5827

            video_id = int(image_id.split("_")[0])
            frame = int(image_id.split("_")[1])
            if frame<201:
                # if score>0.1:
                    result.append([video_id,frame,round(bbox[0],3),round(bbox[1],3),round(bbox[2],3),round(bbox[3],3),cls+1,score])
            # else:
            #     print(frame)
    result = sorted(result, key=lambda x: (x[0], x[1]))

    with open(save_path,'w') as f:
        for item in result:
            line = ",".join(map(str, item))
            f.write(line + "\n")

    

if __name__ == "__main__":
    # 假设你的json文件路径是json_file，图像文件夹路径是image_path，保存裁剪图像的文件夹路径是save_path
    # one-persom
    # stage1_yolov8_stage2_co-detr
    stage1_json1 =  './data/aicity2024_track5/crop_info.json'# '/data1/zhp/2024AICITY/inference_v2.0/stage1/val_2cls/crop_info.json'
    stage2_json1 = '/data1/zhp/2024AICITY/Co-detr/inference_two_cls/test_epoch10.bbox.json' # '/data1/zhp/2024AICITY/inference_v2.0/stage2/val_2cls_1.2/predictions.json' # '/data/sy_data/zhp/datasets/test_all_img'
    save_path = 'result.txt'

    create_new_bbox(stage1_json1, stage2_json1, save_path)
