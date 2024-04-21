from PIL import Image
import json
import os
from collections import defaultdict

def load_json(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    grouped_bboxes = defaultdict(list)
    for entry in data:
        # print(entry['category_id'] )
        if entry['category_id'] == 0:
            if float(entry['score']) > 0.5:
                # print(11111111111)
                image_id = entry['image_id']
                bbox = entry['bbox']
                grouped_bboxes[image_id].append([bbox,entry['score']])
    return grouped_bboxes

def crop_and_save_images(json_file, image_path, save_path,new_json_file):
    grouped_bboxes = load_json(json_file)
    new_data = []
    for image_id, bbox_list in grouped_bboxes.items():
        image_file = os.path.join(image_path, f"{image_id}.jpg")
        image = Image.open(image_file)

        for i, (bbox,score) in enumerate(bbox_list, start = 1):
            # 裁剪图像
            new_image_id = f"{image_id}_{i}"
            left, top, w, h = map(int, bbox)
            # w, h = right - left, bottom - top
            right,bottom = left+w, top+h
            # print((left, top, right, bottom))
            # 扩大1.2倍
            left,top,right,bottom = left - 0.1*w, top-0.1*h, right+0.1*w, bottom+0.1*h
            # print((left, top, right, bottom))
            left = max(0,min(left,1920))
            top = max(0,min(top,1080))
            right = max(0,min(right,1920))
            bottom = max(0,min(bottom,1080))
            if left!=right and top!=bottom:
            # print((left, top, right, bottom))
                cropped_image = image.crop((left, top, right, bottom))
            # 保存裁剪后的图像
            
                new_image_file = os.path.join(save_path, f"{new_image_id}.jpg")
                cropped_image.save(new_image_file)
            
                # 构建新的数据项
                new_entry = {
                    "image_id": new_image_id,
                    "category_id": 0,  # 你的类别ID
                    "bbox": [left, top, w, h],
                    "score": score
                }

                new_data.append(new_entry)

    with open(new_json_file, 'w') as f:
        json.dump(new_data, f, indent=2)

if __name__ == "__main__":
    # 假设你的json文件路径是json_file，图像文件夹路径是image_path，保存裁剪图像的文件夹路径是save_path
    json_file = 'stage1_coarse detector/ultralytics-main/run/stage1_result/predictions.json'
    image_path = './data/aicity2024_track5/test'# '/data1/zhp/2024AICITY/datasets/test_all_img' #  #  #  # '/data/sy_data/zhp/images/val' # 
    save_path = './data/aicity2024_track5/test_stage2_crop'# '/data1/zhp/2024AICITY/inference_v2.0/stage1/val_2cls_mynms/stage1_crop'
    new_json_file = './data/aicity2024_track5/crop_info.json'

    crop_and_save_images(json_file, image_path, save_path, new_json_file)
