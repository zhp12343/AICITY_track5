import os
import numpy as np

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
    
    # iou = area_inter / area_union if area_union > 0 else 0.0
    
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

def max_bbox(match_driver,match_pass1,match_pass2):
    merge_result = {}
    max_bbox = []
    # print("match_driver",match_driver)
    for key,value in match_driver.items():
        merge_result[key] = value
    for key,value in match_pass1.items():
        if key in merge_result:
            merge_result[key].extend(value)
        else:
            merge_result[key] = value
            print(1111111111)
    for key,value in match_pass2.items():
        if key in merge_result:
            merge_result[key].extend(value)
        else:
            merge_result[key] = value
            print(22222222222)
    # print("merge_result",merge_result)
    for car_info,person_info in merge_result.items():
        car_info = list(car_info)
        if len(person_info) == 0:
            # print(23333333333333)
            max_bbox.append(['0',(car_info[0]+car_info[2])/2, (car_info[1]+car_info[3])/2,car_info[2]-car_info[0],car_info[3]-car_info[1]])
        elif len(person_info) == 1 and (int(person_info[0][-1]) == 2 or int(person_info[0][-1]) == 3):
            xmin = min(car_info[0],min(person_info[i][0] for i in range(len(person_info))))
            ymin = min(car_info[1],min(person_info[i][1] for i in range(len(person_info))))
            xmax = max(car_info[2],max(person_info[i][2] for i in range(len(person_info))))
            ymax = max(car_info[3],max(person_info[i][3] for i in range(len(person_info))))
            w, h = xmax - xmin, ymax - ymin
            max_bbox.append(['1',(xmin+xmax)/2,(ymin+ymax)/2,w,h])
        else:
            xmin = min(car_info[0],min(person_info[i][0] for i in range(len(person_info))))
            ymin = min(car_info[1],min(person_info[i][1] for i in range(len(person_info))))
            xmax = max(car_info[2],max(person_info[i][2] for i in range(len(person_info))))
            ymax = max(car_info[3],max(person_info[i][3] for i in range(len(person_info))))
            w, h = xmax - xmin, ymax - ymin
            max_bbox.append(['2',(xmin+xmax)/2,(ymin+ymax)/2,w,h])
    return max_bbox
  


# 读取gt中的信息  [class,x_center,y_center,w,h]

fp = './data/aicity2024_track5/stage1/annoations/original_train'
save_path = './data/aicity2024_track5/stage1/labels/train'
for txt_fp in os.listdir(fp):
    fp_one = os.path.join(fp,txt_fp)
    # fp_one = '/data/sy_data/zhp/labels/9cls_val/004_188.txt'
    info = []
    with open(fp_one, 'r') as f:
        for line in f:
            info.append(line.strip().split(' '))
        info = np.array(info, dtype=np.float32)

    '''划分车和人'''
    car_info = []
    driver_info = []
    pass1_info = []
    pass2_info = []
    for s in info:
        c,x,y,w,h = s
        xmin,ymin,xmax,ymax = x-w/2,y-h/2,x+w/2,y+h/2
        xmin = max(0,min(1,xmin))
        ymin = max(0,min(1,ymin))
        xmax = max(0,min(1,xmax))
        ymax = max(0,min(1,ymax))
        x,y = (xmin+xmax)/2,(ymin+ymax)/2
        w,h = xmax-xmin,ymax-ymin
        if int(c) == 1:
            car_info.append([c,x,y,w,h])
        elif int(c) in [2,3]:
            # print(c)
            driver_info.append([c,x,y,w,h])
        elif int(c) in [4,5]:
            # print(c)
            pass1_info.append([c,x,y,w,h])
        elif int(c) in [6,7]:
            # print(c)
            pass2_info.append([c,x,y,w,h])

    match_driver = matching(car_info, driver_info) # 匹配的司机
    match_pass1 = matching(car_info, pass1_info) # 匹配的passenger1
    match_pass2 = matching(car_info, pass2_info) # 匹配的passenger2
    result = max_bbox(match_driver,match_pass1,match_pass2)
    new_name = os.path.basename(fp_one)[:-4] # 001_141
    file_name = os.path.join(save_path,f"{new_name}.txt")  
    with open(file_name, 'w') as f:
        for r in result:
            f.write(' '.join([str(i) for i in r]) + '\n')