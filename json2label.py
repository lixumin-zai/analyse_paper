# python3.7
# -*- coding: utf-8 -*-
# @Author : listen
# @Time   :
import os

import cv2
import numpy as np
import requests
import base64
import hashlib
# from deploy.python.predict import corrector
from PIL import ImageFont, ImageDraw, Image

def qieti(org_img, pos):
    """

    :param path:
    :param pos:
    :return: loc: {'left': 58, 'height': 32, 'width': 40, 'top': 0}   left_top_x, length_y, length_x left_top_y,
    """
    # org_img = cv2.imread(path)
    ptLeftTop = (pos[0]["x"], pos[0]["y"])
    ptRightBottom = (pos[2]["x"], pos[2]["y"])
    # loc = ptLeftTop[1]: ptRightBottom[1], ptLeftTop[0]: ptRightBottom[0]
    # location =
    return org_img[ptLeftTop[1]:ptRightBottom[1], ptLeftTop[0]:ptRightBottom[0]]

def get_label(pos):
    ptLeftTop = (pos[0]["x"], pos[0]["y"])
    ptRightBottom = (pos[2]["x"], pos[2]["y"])

    length = ptRightBottom[1] - ptLeftTop[1]
    width = ptRightBottom[0] - ptLeftTop[0]

    center_x = width / 2 + ptLeftTop[0]
    center_y = length / 2 + ptLeftTop[1]
    # loc = ptLeftTop[1]: ptRightBottom[1], ptLeftTop[0]: ptRightBottom[0]
    # location =
    return center_x, center_y, width, length


def seg_img(json_path, img_path):
    """
    aliyun qieti
    :param path:  tupianlujing
    :return: img:
             location:[{'x': 208, 'y': 81}, {'x': 314, 'y': 80}, {'x': 314, 'y': 94}, {'x': 208, 'y': 94}]
             * -> *
                  |
             * <- *
    """
    txt_path = json_path.replace("json", "txt", -1)
    with open(txt_path, "a", encoding="utf-8") as txt:
        with open(json_path, "r", encoding="utf-8") as f:
            data = f.read()
        data = eval(data)
        org_img = cv2.imread(img_path)
        y, x = org_img.shape[0:2]
        for i in data["data"]["part_info"]:
            for j in i["subject_list"]:
                for location in j["pos_list"]:
                    cv2.imshow("sdf",qieti(org_img, location))
                    cv2.waitKey(0)
                    center_x, center_y, width, length = get_label(location)
                    txt.write("0 {} {} {} {}\n".format(center_x/x, center_y/y, width/x, length/y))
                    # {'left': 58, 'height': 32, 'width': 40, 'top': 0}
                    # location["left"] = k[0]["x"]
                    # location["height"] = k[0]["x"]
                    # location["width"] = k[0]["x"]
                    # location["top"] = k[0]["x"]


if __name__ == "__main__":
    # img_path = r"F:\data\test_paper\strengthen_img_test\"
    # json_path = r"F:\data\test_paper\strengthen_img_test\json\1631674725.0438766.json"
    json_paths = []
    img_paths = []
    for root, ds, fs in os.walk(r'F:\data\test_paper\strengthen_img_test\image'):
        for f in fs:
            fullname = os.path.join(root, f)
            img_paths.append(fullname)
    for root, ds, fs in os.walk(r'F:\data\test_paper\strengthen_img_test\json'):
        for f in fs:
            fullname = os.path.join(root, f)
            json_paths.append(fullname)
    seg_img(json_paths, img_paths)