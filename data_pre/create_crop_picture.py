import os
import numpy as np
from PIL import Image

'''IOU'''
def Iou(box1, box2):
    """
    计算两个目标之间的IOU
    box1: [x1, y1, x2, y2],表示目标1的左上角和右下角的坐标
    box2: [x1, y1, x2, y2],表示目标2的左上角和右下角的坐标
    """
    x1_inter = max(box1[0], box2[0])
    y1_inter = max(box1[1], box2[1])
    x2_inter = min(box1[2], box2[2])
    y2_inter = min(box1[3], box2[3])
    
    w_inter = max(0, x2_inter - x1_inter)
    h_inter = max(0, y2_inter - y1_inter)
    area_inter = w_inter * h_inter
    
    area_box1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area_box2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    area_union = area_box1 + area_box2 - area_inter
    
    # 交集/车的面积 
    iou = area_inter / area_box1 if area_box1 > 0 else 0.0
    return iou

def matching(car_info,person_info):    
    '''匹配车和人'''
    result = {}
    for car in car_info:
        cc,cx,cy,cw,ch = car
        cxmin, cxmax, cymin, cymax = cx - cw/2, cx + cw/2, cy - ch/2, cy + ch/2
        num = 0
        # personiou = []
        result[(cxmin,cymin,cxmax,cymax)] = []
        for person in person_info:
            pc,px,py,pw,ph = person
            pxmin, pxmax, pymin, pymax = px - pw/2, px + pw/2, py - ph/2, py + ph/2
            if pymax<=cymax:
                iou = Iou([cxmin, cymin, cxmax, cymax],[pxmin, pymin, pxmax, pymax])
                if iou > 0.1:
                    if num == 0:# result[(cxmin,cymin,cxmax,cymax)]:
                        result[(cxmin,cymin,cxmax,cymax)].append([pxmin,pymin,pxmax,pymax,pc])
                        personiou = iou
                        num = num+1
                    elif num == 1:
                        if iou < personiou:
                            continue
                        else:
                            result[(cxmin,cymin,cxmax,cymax)].remove(result[(cxmin,cymin,cxmax,cymax)][0])
                            result[(cxmin,cymin,cxmax,cymax)].append([pxmin,pymin,pxmax,pymax,pc])
    return result

'''计算匹配的最大外接矩形'''
def max_bbox(fp,img_path,save_image_path,save_txt_path):
    info = []
    with open(fp, 'r') as f:
        for line in f:
            info.append(line.strip().split(' '))
        info = np.array(info, dtype=np.float32)
    '''划分车和人'''
    car_info = []
    driver_info = []
    pass0_info = []
    pass1_info = []
    pass2_info = []
    merge_result = {}
    for s in info:
        c,x,y,w,h = s
        xmin,ymin,xmax,ymax = x-w/2,y-h/2,x+w/2,y+h/2
        xmin = max(0,min(1,xmin))
        ymin = max(0,min(1,ymin))
        xmax = max(0,min(1,xmax))
        ymax = max(0,min(1,ymax))
        x,y = (xmin+xmax)/2,(ymin+ymax)/2
        w,h = xmax-xmin,ymax-ymin
        if int(c) == 1:car_info.append([c,x,y,w,h])
        elif int(c) in [2,3]:driver_info.append([c,x,y,w,h])
        elif int(c) in [4,5]:pass1_info.append([c,x,y,w,h])
        elif int(c) in [6,7]:pass2_info.append([c,x,y,w,h])
        elif int(c) in [8,9]:pass0_info.append([c,x,y,w,h])
        match_driver = matching(car_info, driver_info) # 匹配的司机
        match_pass1 = matching(car_info, pass1_info) # 匹配的passenger1
        match_pass2 = matching(car_info, pass2_info) # 匹配的passenger2
        match_pass0 = matching(car_info, pass0_info) # 匹配的passenger0
        for key,value in match_driver.items():
            merge_result[key] = value
        for key,value in match_pass1.items():
            if key in merge_result:merge_result[key].extend(value)
            else:merge_result[key] = value
        for key,value in match_pass2.items():
            if key in merge_result:merge_result[key].extend(value)
            else:merge_result[key] = value
        for key,value in match_pass0.items():
            if key in merge_result:merge_result[key].extend(value)
            else:merge_result[key] = value
        # print(merge_result)
        # 裁剪图片，生成image和labels
        i = 0
        for car,person in merge_result.items():
            # 左上角右下角坐标
            i+=1
            car = list(car)
            if len(person) == 0:
                car[0],car[1],car[2],car[3] = car[0]*1920,car[1]*1080,car[2]*1920,car[3]*1080
                car_x1,car_x2=car[0]-0.1*(car[2]-car[0]),car[2]+0.1*(car[2]-car[0])
                car_y1,car_y2=car[1]-0.1*(car[3]-car[1]),car[3]+0.1*(car[3]-car[1])
                car_x1,car_x2=max(0,min(car_x1,1920)),max(0,min(car_x2,1920))
                car_y1,car_y2=max(0,min(car_y1,1080)),max(0,min(car_y2,1080))
                image_path = os.path.join(img_path,os.path.basename(fp)[:-4]+'.jpg')
                if os.path.exists(image_path):
                    image = Image.open(image_path)
                    if car_x2!=car_x1 and car_y1!=car_y2:
                        # 裁剪图片并保存
                        # crop_image = image.crop((car_x1,car_y1,car_x2,car_y2))
                        new_name = os.path.basename(fp)[:-4] + '_' + str(i)
                        # new_image_name = os.path.join(save_image_path,f"{new_name}.jpg") 
                        # crop_image.save(new_image_name)
                        # 保存labels
                        txt_path = os.path.join(save_txt_path,f"{new_name}.txt")
                        # 归一化
                        new_car_x1,new_car_y1,new_car_x2,new_car_y2 = (car[0]-car_x1)/(car_x2-car_x1),(car[1]-car_y1)/(car_y2-car_y1),(car[2]-car_x1)/(car_x2-car_x1),(car[3]-car_y1)/(car_y2-car_y1)
                        new_car_w,new_car_h = new_car_x2-new_car_x1,new_car_y2-new_car_y1
                        new_car_x,new_car_y = (new_car_x1+new_car_x2)/2,(new_car_y1+new_car_y2)/2
                        with open(txt_path,'w') as f:
                            f.write(f"0 {new_car_x} {new_car_y} {new_car_w} {new_car_h}")
            else:
                
                # 最大外接矩形
                xmin = min(car[0],min(person[i][0] for i in range(len(person))))
                ymin = min(car[1],min(person[i][1] for i in range(len(person))))
                xmax = max(car[2],max(person[i][2] for i in range(len(person))))
                ymax = max(car[3],max(person[i][3] for i in range(len(person))))
                w, h = xmax - xmin, ymax - ymin
                # 扩大1.2倍
                sxmin,sxmax,symin,symax = xmin-0.1*w,xmax+0.1*w,ymin-0.1*h,ymax+0.1*h
                sxmin,sxmax=max(0,min(sxmin*1920,1920)),max(0,min(sxmax*1920,1920))
                symin,symax=max(0,min(symin*1080,1080)),max(0,min(symax*1080,1080))
                sw,sh,sxcenter,sycenter = sxmax-sxmin,symax-symin,(sxmax+sxmin)/2,(symax+symin)/2
                image_path = os.path.join(img_path,os.path.basename(fp)[:-4]+'.jpg')
                if os.path.exists(image_path):
                    image = Image.open(image_path)
                    if sxmax!=sxmin and symax!=symin:
                        # 裁剪图片并保存
                        # crop_image = image.crop((sxmin,symin,sxmax,symax))
                        new_name = os.path.basename(fp)[:-4] + '_' + str(i)
                        # new_image_name = os.path.join(save_image_path,f"{new_name}.jpg") 
                        # crop_image.save(new_image_name)
                        # 保存labels
                        txt_path = os.path.join(save_txt_path,f"{new_name}.txt")
                        # 归一化车
                        car[0],car[1],car[2],car[3] = car[0]*1920,car[1]*1080,car[2]*1920,car[3]*1080
                        new_car_x1,new_car_y1,new_car_x2,new_car_y2 = (car[0]-sxmin)/sw,(car[1]-symin)/sh,(car[2]-sxmin)/sw,(car[3]-symin)/sh
                        new_car_w,new_car_h = new_car_x2-new_car_x1,new_car_y2-new_car_y1
                        new_car_x,new_car_y = (new_car_x1+new_car_x2)/2,(new_car_y1+new_car_y2)/2
                        with open(txt_path,'w') as f:
                            f.write(f"0 {new_car_x} {new_car_y} {new_car_w} {new_car_h}\n")
                            for j in range(len(person)):
                                c = int(person[j][-1])-1
                                pxmin,pymin,pxmax,pymax = (person[j][0]*1920 -sxmin)/sw,(person[j][1]*1080-symin)/sh,(person[j][2]*1920-sxmin)/sw,(person[j][3]*1080-symin)/sh
                                pxmin,pymin,pxmax,pymax = max(0,min(pxmin,1)),max(0,min(pymin,1)),max(0,min(pxmax,1)),max(0,min(pymax,1))
                                px,py,pw,ph = (pxmax+pxmin)/2,(pymax+pymin)/2,pxmax-pxmin,pymax-pymin
                                f.write(f"{c} {px} {py} {pw} {ph}\n")
        
if __name__ == '__main__':
    fp = './data/aicity2024_track5/stage1/annoations/original_train'   # 原labels的路径
    img_path = './data/aicity2024_track5/stage1/images/train'
    '''保存路径'''
    save_image_path = './data/aicity2024_track5/stage2/images/train/' # "/data1/zhp/2024AICITY/stage2_datasets_v2.0/image/train"
    save_txt_path = './data/aicity2024_track5/stage2/labels/train' # "/data1/zhp/2024AICITY/stage2_datasets_v2.0/labels/train"
    '''最大外接矩形'''
    for txt_fp in os.listdir(fp):
        fp_one = os.path.join(fp,txt_fp)
        max_bbox(fp_one,img_path,save_image_path,save_txt_path)
        