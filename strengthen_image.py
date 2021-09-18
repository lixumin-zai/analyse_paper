# python3.7
# -*- coding: utf-8 -*-
# @Author : listen
# @Time   :
import os
import time
from multiprocessing import Pool, Lock
import matplotlib.pyplot as plt
import cv2
import numpy as np
from math import *
import random

import tqdm


def show_img(img):
    cv2.imshow("123", img)
    # cv2.resizeWindow("123", 500, 500)
    cv2.waitKey(0)

# 滤波
def blur(img):
    # img = cv2.imread("./1.jpg")

    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 高斯平滑,为了消除图像中的噪声
    gaussian_img = cv2.GaussianBlur(gray_img, (3, 3), 2)
    # Canny算子
    # gaussian_canny_edges_img = cv2.Canny(gaussian_img, 100, 200, 5)
    # canny_edges_img = cv2.Canny(gray_img, 100, 200, 5)
    # show_img(gaussian_img)
    return gaussian_img

def adject_angle(gaussian_img):
    height, width = gaussian_img.shape[:2]
    degree = random.randint(-1, 1) * 0.1
    heightNew = ceil(width * fabs(sin(radians(degree))) + height * fabs(cos(radians(degree))))
    widthNew = ceil(height * fabs(sin(radians(degree))) + width * fabs(cos(radians(degree))))
    matRotate = cv2.getRotationMatrix2D((ceil(height/2), ceil(width/2)), degree, 1)    # 为方便旋转后图片能完整展示，所以我们将其缩小
    matRotate[0, 2] += ceil((widthNew - width) / 2)  # 重点在这步，目前不懂为什么加这步
    matRotate[1, 2] += ceil((heightNew - height) / 2)  # 重点在这步
    dst = cv2.warpAffine(gaussian_img, matRotate, (width, height), borderValue=(255, 255, 255))
    # show_img(dst)
    return dst

def threshold(dst):
    # 二值化
    # """
    # 直接用OpenCV的函数会让背景变花，因为背景是渐变的，直接拿均值当阈值的话，总有一些背景像素在阈值下面。
    # 所以需要将阈值乘以一个系数，比如0.9，过滤掉所有背景。同时，因为文字的像素值很小，不受影响。
    # """
    # import numpy as np
    # from scipy import signal
    # print(dst)
    # def adaptive_thres(img, win=9, beta=0.9):
    #     if win % 2 == 0: win = win - 1
    #     # 边界的均值有点麻烦
    #     # 这里分别计算和和邻居数再相除
    #     kern = np.ones([win, win])
    #     sums = signal.correlate2d(img, kern, 'same')
    #     cnts = signal.correlate2d(np.ones_like(img), kern, 'same')
    #     means = sums // cnts
    #     # 如果直接采用均值作为阈值，背景会变花
    #     # 但是相邻背景颜色相差不大
    #     # 所以乘个系数把它们过滤掉
    #     img = np.where(img < means * beta, 0, 255)
    #     return img
    #
    # im_at_mean = adaptive_thres(dst)
    # im_at_mean = np.array(im_at_mean, dtype=np.uint8)
    # print(im_at_mean)
    # show_img(im_at_mean)
    # return im_at_mean

    im_at_mean = cv2.adaptiveThreshold(dst, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 3, 1)
    # show_img(im_at_mean)
    return im_at_mean

def get_point(img):
    """
    二值图片
    :param img:
    :return:
    """
    # kernel = np.ones((3, 3), np.uint8)
    # erosion = cv2.erode(img, kernel, iterations=2)
    # show_img(erosion)
    # 腐蚀
    y, x = img.shape[0:2]
    image = img/255
    hist = [sum(pand) for pand in image]

    left_x, left_y, right_x, right_y = 0, 0, 0, 0
    for x1, y1 in enumerate(hist):
        if y1 > 0.01 * y:
            left_x = x1
            break
    for x1, y1 in enumerate(hist[::-1]):
        if y1 > 0.01 * y:
            right_x = x1
            break


    # print(hist)
    plt.figure(figsize=(50, 50))
    plt.plot(hist, range(len(hist), 0, -1))  # 绘制散点图，透明度为0.6（这样颜色浅一点，比较好看）
    # plt.show()

    # show_img(erosion)
    # contours, hierarchy = cv2.findContours(erosion, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    def draw_approx_hull_polygon(img, cnts):
        # img = np.copy(img)
        img = np.zeros(img.shape, dtype=np.uint8)

        cv2.drawContours(img, cnts, -1, (255, 0, 0), 2)  # blue

        epsilion = img.shape[0] / 32
        approxes = [cv2.approxPolyDP(cnt, epsilion, True) for cnt in cnts]
        cv2.polylines(img, approxes, True, (0, 255, 0), 2)  # green

        hulls = [cv2.convexHull(cnt) for cnt in cnts]
        cv2.polylines(img, hulls, True, (0, 0, 255), 2)  # red

        # 我个人比较喜欢用上面的列表解析，我不喜欢用for循环，看不惯的，就注释上面的代码，启用下面的
        # for cnt in cnts:
        #     cv2.drawContours(img, [cnt, ], -1, (255, 0, 0), 2)  # blue
        #
        #     epsilon = 0.01 * cv2.arcLength(cnt, True)
        #     approx = cv2.approxPolyDP(cnt, epsilon, True)
        #     cv2.polylines(img, [approx, ], True, (0, 255, 0), 2)  # green
        #
        #     hull = cv2.convexHull(cnt)
        #     cv2.polylines(img, [hull, ], True, (0, 0, 255), 2)  # red
        return img


    def draw_min_rect_circle(img, cnts):  # conts = contours
        img = np.copy(img)

        for cnt in cnts:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0), 2)  # blue

            min_rect = cv2.minAreaRect(cnt)  # min_area_rectangle
            min_rect = np.int0(cv2.boxPoints(min_rect))
            cv2.drawContours(img, [min_rect], 0, (0, 255, 0), 2)  # green

            (x, y), radius = cv2.minEnclosingCircle(cnt)
            center, radius = (int(x), int(y)), int(radius)  # for the minimum enclosing circle
            img = cv2.circle(img, center, radius, (0, 0, 255), 2)  # red
            # show_img(img)
        return img


def noise(im_at_mean):
    img_noise = im_at_mean
    # cv2.imshow("src", img)
    rows, cols = img_noise.shape
    noise_num = int(rows * cols * 0.0001)
    # print(noise_num)
    # 加噪声
    for i in range(noise_num):
        x = np.random.randint(0, rows)  # 随机生成指定范围的整数
        y = np.random.randint(0, cols)
        img_noise[x:x+3, y:y+3] = 0

    # show_img(img_noise)
    return img_noise



def cv_img_rgb(path):
    # 用matplotlib的路径
    cv_img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), -1)
    return cv_img

def call(fullname):
    print(fullname)
    img = cv_img_rgb(fullname)
    img = blur(img)
    img = adject_angle(img)
    img = threshold(img)
    img = noise(img)
    path = "F:\\data\\test_paper\\strengthen_img\\{}.png".format(time.time())
    if os.path.exists(path):
        path = path[:-4] + "_1.png"
    cv2.imwrite(path, img)
    print("write,done")
    # input()

if __name__ == "__main__":
    p = Pool(3)
    for root, ds, fs in tqdm.tqdm(os.walk(r'F:\data\test_paper\image')):
        try:
            if fs:
                for f in fs:
                    fullname = os.path.join(root, f)
                    # img = cv2.imread(fullname)
                    call(fullname)
                    p.apply_async(call, args=(fullname,))
        except Exception as e:
            print(e)
            continue

