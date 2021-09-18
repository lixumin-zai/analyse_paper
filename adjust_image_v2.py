# python3.7
# -*- coding: utf-8 -*-
# @Author : listen
# @Time   :
import os.path
import time
import numpy as np
from scipy import signal
import cv2
import numpy as np
from skimage.filters import threshold_local

def show_img(img):
    cv2.imshow(str(time.time()), img)
    cv2.waitKey(0)

def imread(path):
    # 用matplotlib的路径
    cv_img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), 1)
    return cv_img

def gray(img):
    Threshold_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return Threshold_img

def resize(img, beta=1):
    new_img = cv2.resize(img, (int(img.shape[1] * beta), int(img.shape[0] * beta)), 0, 0)
    return new_img

def findContours(img):
    """
    1. GaussianBlur, Canny 处理后的灰度图
    2. u2net 处理后的灰度图
    :param img:
    :return: contours: 轮廓坐标 list
             hierarchy: 轮廓之间的关系
    """
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # FIND ALL CONTOURS
    return contours, hierarchy

def drawContours(img, contours):
    """
    画轮廓
    :param img:
    :param contours: 轮廓坐标 list
    :return:
    """
    cv2.drawContours(img, contours, -1, (255, 255, 255), 3)
    return img

def biggestContour(contours, image_area):
    """
    找出最大的轮廓
    :param contours:
    :param image_area: 图片总面积
    :return:
    """
    biggest = np.array([])
    max_area = 0
    for i in contours:
        area = cv2.contourArea(i)
        if area > image_area * 0.5:
            peri = cv2.arcLength(i, True)
            approx = cv2.approxPolyDP(i, 0.02 * peri, True)
            if area > max_area and len(approx) == 4:
                biggest = approx
                max_area = area
    return biggest, max_area

def reorder(myPoints):
    myPoints = myPoints.reshape((4, 2))
    myPointsNew = np.zeros((4, 1, 2), dtype=np.int32)
    add = myPoints.sum(1)

    myPointsNew[0] = myPoints[np.argmin(add)]
    myPointsNew[3] = myPoints[np.argmax(add)]
    diff = np.diff(myPoints, axis=1)
    myPointsNew[1] = myPoints[np.argmin(diff)]
    myPointsNew[2] = myPoints[np.argmax(diff)]
    return myPointsNew

def drawRectangle(img, biggest, thickness):
    cv2.line(img, (biggest[0][0][0], biggest[0][0][1]),
             (biggest[1][0][0], biggest[1][0][1]), (0, 255, 0), thickness)
    cv2.line(img, (biggest[0][0][0], biggest[0][0][1]),
             (biggest[2][0][0], biggest[2][0][1]), (0, 255, 0), thickness)
    cv2.line(img, (biggest[3][0][0], biggest[3][0][1]),
             (biggest[2][0][0], biggest[2][0][1]), (0, 255, 0), thickness)
    cv2.line(img, (biggest[3][0][0], biggest[3][0][1]),
             (biggest[1][0][0], biggest[1][0][1]), (0, 255, 0), thickness)
    return img

def perspective_transform(org_img, contours):
    """
    透视变换
    :param img:
    :param contours:
    :return:
    """
    heigth, width = org_img.shape[0:2]
    biggest, maxArea = biggestContour(contours, heigth* width)
    if biggest.size != 0:
        biggest = reorder(biggest)  # 四个点
        cv2.drawContours(org_img, biggest, -1, (0, 255, 0), 5)  # DRAW THE BIGGEST CONTOUR
        ###
        # show_img(org_img)
        ###
        imgBigContour = drawRectangle(org_img, biggest, 2)  # utlis.drawRectangle(imgBigContour, biggest, 2)
        ###
        # show_img(imgBigContour)
        ###
        pts1 = np.float32(biggest)  # 扭曲准备点
        pts2 = np.float32([[0, 0], [width, 0], [0, heigth], [width, heigth]])  # 扭曲准备点
        # 变换
        matrix = cv2.getPerspectiveTransform(pts1, pts2)

        imgWarpColored = cv2.warpPerspective(org_img, matrix, (width, heigth))

        # REMOVE 20 PIXELS FORM EACH SIDE 删除边边
        imgWarpColored = imgWarpColored[50:imgWarpColored.shape[0] - 50,
                         50:imgWarpColored.shape[1] - 50]

        return imgWarpColored

def my_threshold(img, win=5, beta=0.9):
    if win % 2 == 0:
        win = win - 1
    kern = np.ones([win, win])
    sums = signal.correlate2d(img, kern, 'same')
    cnts = signal.correlate2d(np.ones_like(img), kern, 'same')
    means = sums // cnts
    img = np.where(img < means * beta, img - 50, img+25)
    img = np.where(img < 255, img, 255)
    """
    限制白
    """
    im_at_mean = np.array(img, dtype=np.uint8)
    return im_at_mean

def morphologyEx_open(img):
    """
    开运算
    :param img:
    :return:
    """
    kernel = np.ones((3, 3), np.uint8)
    closing_img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel, iterations=1)
    return closing_img

def main():
    org_img = imread("./test_image/1.png")
    show_img(org_img)
    ##
    u2net_img = imread("./test_image/u2net/1.png")
    ##
    # 灰度图
    process_img = gray(org_img)
    # .......
    # 形态学处理、或u2net处理
    Threshold_img = gray(u2net_img)
    ret, Threshold_img = cv2.threshold(Threshold_img, 150, 255, cv2.THRESH_TRUNC)
    print(Threshold_img[200:250, 200:250])
    # show_img(Threshold_img)
    # 找边缘
    contours, hierarchy = findContours(Threshold_img)
    # draw_img1 = drawContours(process_img, contours)
    # draw_img2 = drawContours(Threshold_img, contours)

    transform_img1 = perspective_transform(process_img, contours)  # upload_img
    show_img(transform_img1)
    fiall_img1 = my_threshold(morphologyEx_open(transform_img1))
    fiall_img2 = morphologyEx_open(my_threshold(transform_img1))
    show_img(fiall_img1)
    show_img(fiall_img2)
    return transform_img1


if __name__ == "__main__":
    main()