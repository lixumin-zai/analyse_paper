# python3.7
# -*- coding: utf-8 -*-
# @Author : listen
# @Time   :
import base64
import json
from aliyun_api import ocr
import cv2


def seg_img(path):
    # with open("./test.json", "r", encoding="utf-8") as f:
    #     json_data = f.read()
    json_data = ocr.paper_cut(path)
    json_data = json.loads(json_data)
    imgs = []
    # print(json_data["data"]["part_info"][0]["subject_list"][0]["element_list"][0]["content_list"][0]["pos"])
    for i in json_data["data"]["part_info"]:
        for j in i["subject_list"]:
            for k in j["pos_list"]:
                print(k)
                #  图片数组转byte
                success,encoded_image = cv2.imencode(".png", qieti(path, k))
                byte_data = encoded_image.tobytes()
                imgs.append(base64.b64encode(byte_data).decode("utf-8"))
    print(imgs[0])

def rectangle(img, ptLeftTop, ptRightBottom):
    point_color = (0, 0, 255) # BGR
    thickness = 2
    cv2.rectangle(img, ptLeftTop, ptRightBottom, point_color, thickness)
    # cv2.imshow("123", img)
    # cv2.waitKey(0)

def qieti(path, pos):
    org_img = cv2.imread(path)
    ptLeftTop = (pos[0]["x"], pos[0]["y"])
    ptRightBottom = (pos[2]["x"], pos[2]["y"])
    # rectangle(org_img, ptLeftTop, ptRightBottom)
    seg_img = org_img[ptLeftTop[1]:ptRightBottom[1], ptLeftTop[0]:ptRightBottom[0]]
    # cv2.imshow("123", a)
    # cv2.waitKey(0)
    # print(seg_img)

    return seg_img


if __name__ == "__main__":
    seg_img("test1.png")