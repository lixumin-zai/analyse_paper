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

## TO STACK ALL THE IMAGES IN ONE WINDOW
def stackImages(imgArray, scale, lables=[]):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range(0, rows):
            for y in range(0, cols):
                imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None,
                                            scale, scale)
                if len(imgArray[x][y].shape) == 2:
                    imgArray[x][y] = cv2.cvtColor(imgArray[x][y],
                                                  cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank] * rows
        hor_con = [imageBlank] * rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
            hor_con[x] = np.concatenate(imgArray[x])
        ver = np.vstack(hor)
        ver_con = np.concatenate(hor)
    else:
        for x in range(0, rows):
            imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            if len(imgArray[x].shape) == 2:
                imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor = np.hstack(imgArray)
        hor_con = np.concatenate(imgArray)
        ver = hor
    if len(lables) != 0:
        eachImgWidth = int(ver.shape[1] / cols)
        eachImgHeight = int(ver.shape[0] / rows)
        print(eachImgHeight)
        for d in range(0, rows):
            for c in range(0, cols):
                cv2.rectangle(ver, (c * eachImgWidth, eachImgHeight * d),
                              (c * eachImgWidth + len(lables[d][c]) * 13 + 27,
                               30 + eachImgHeight * d), (255, 255, 255),
                              cv2.FILLED)
                cv2.putText(ver, lables[d][c],
                            (eachImgWidth * c + 10, eachImgHeight * d + 20),
                            cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 0, 255), 2)
    return ver


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


def biggestContour(contours):
    biggest = np.array([])
    max_area = 0
    for i in contours:
        area = cv2.contourArea(i)
        if area > 5000:
            peri = cv2.arcLength(i, True)
            approx = cv2.approxPolyDP(i, 0.02 * peri, True)
            if area > max_area and len(approx) == 4:
                biggest = approx
                max_area = area
    return biggest, max_area


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


def nothing(x):
    pass


def initializeTrackbars(intialTracbarVals=0):
    cv2.namedWindow("Trackbars")
    cv2.resizeWindow("Trackbars", 360, 240)
    cv2.createTrackbar("Threshold1", "Trackbars", 200, 255, nothing)
    cv2.createTrackbar("Threshold2", "Trackbars", 200, 255, nothing)


def valTrackbars():
    Threshold1 = cv2.getTrackbarPos("Threshold1", "Trackbars")
    Threshold2 = cv2.getTrackbarPos("Threshold2", "Trackbars")
    src = Threshold1, Threshold2
    return src


def show_img(img):
    cv2.imshow(str(time.time()), img)
    cv2.waitKey(0)

def imread(path):
    # 用matplotlib的路径
    cv_img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), 1)
    return cv_img


def otsu(gray_img):
    h = gray_img.shape[0]
    w = gray_img.shape[1]
    threshold_t = 0
    max_g = 0
    # 遍历每一个灰度层
    for t in range(255):
        # 使用numpy直接对数组进行计算
        n0 = gray_img[np.where(gray_img < t)]
        n1 = gray_img[np.where(gray_img >= t)]
        w0 = len(n0) / (h * w)
        w1 = len(n1) / (h * w)
        u0 = np.mean(n0) if len(n0) > 0 else 0
        u1 = np.mean(n1) if len(n1) > 0 else 0

        g = w0 * w1 * (u0 - u1) ** 2
        if g > max_g:
            max_g = g
            threshold_t = t
    print('类间方差最大阈值：', threshold_t)
    gray_img = np.where(gray_img < threshold_t, gray_img-50, 255)
    # gray_img[gray_img < threshold_t] = gray_img-50
    # gray_img[gray_img > threshold_t] = gray_img+25
    return gray_img


def adaptive_thres(img, win=10, beta=0.95):
    if win % 2 == 0 : win = win - 1
    # 边界的均值有点麻烦
    # 这里分别计算和和邻居数再相除
    kern = np.ones([win, win])
    sums = signal.correlate2d(img, kern,  'same')
    cnts = signal.correlate2d(np.ones_like(img), kern, 'same')
    means = sums // cnts
    # 如果直接采用均值作为阈值，背景会变花
    # 但是相邻背景颜色相差不大
    # 所以乘个系数把它们过滤掉
    img = np.where(img < means * beta, 0, 255)
    im_at_mean = np.array(img, dtype=np.uint8)
    return im_at_mean

def my_huiduchuli(img, win=5, beta=0.95):
    # im_at_mean = otsu(img)
    if win % 2 == 0: win = win - 1
    kern = np.ones([win, win])
    sums = signal.correlate2d(img, kern, 'same')
    cnts = signal.correlate2d(np.ones_like(img), kern, 'same')
    means = sums // cnts
    # print(means * beta)
    print(img[150:170, 150:170])
    img = np.where(img < means * beta, img-(means*0.5), img+(means*0.5))
    print(img[150:170, 150:170])
    img = np.where(img < 255, img, 255)
    print(img[150:170,150:170])
    # show_img(img)
    #
    # print(img)
    """
    限制白
    """

    # img = np.where(img > means * beta, img-50, img)
    print(img[100:110,100:110])
    im_at_mean = np.array(img, dtype=np.uint8)
    return im_at_mean

def main(pathImage):
    count = 0
    org_img = imread(pathImage)
    img = cv2.resize(org_img, (int(org_img.shape[1]*0.5), int(org_img.shape[0]*0.5)), 0, 0)
    print(img.shape)
    # show_img(img)
    heightImg = int(org_img.shape[0]*0.5)
    widthImg = int(org_img.shape[1]*0.5)
    imgBlank = np.zeros(
        (heightImg, widthImg, 3),
        np.uint8)

    # 解决偏色问题
    # b, g, r = cv2.split(img)
    # img = cv2.merge([r, g, b])
    # orig = img.copy()

    # # 设置图像大小,A4纸的大小
    # heightImg = 3508
    # widthImg = 2479
    # # img = imutils.resize(img, width=widthImg, height = heightImg) # 500
    # img = cv2.resize(img, (widthImg, heightImg))  # RESIZE IMAGE

    # imgBlank = np.zeros(
    #     (heightImg, widthImg, 3),
    #     np.uint8)  # CREATE A BLANK IMAGE FOR TESTING DEBUGING IF REQUIRED
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # CONVERT IMAGE TO GRAY SCALE
    # show_img(imgGray)
    next_img = imgGray

    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 3)  # ADD GAUSSIAN BLUR
    show_img(imgBlur)

    # kernel = np.ones((5, 5))
    # imgBlur = cv2.dilate(next_img, kernel, iterations=5)
    imgThreshold = cv2.Canny(imgBlur, 100, 200)  # 更改这个200*200来调整框
    show_img(imgThreshold)

    kernel = np.ones((5, 5))
    imgDial = cv2.dilate(imgThreshold, kernel, iterations=5)  # APPLY DILATION
    # imgThreshold = cv2.erode(imgThreshold, kernel, iterations=2)  # APPLY EROSION
    show_img(imgDial)

    imgContours = img.copy()  # COPY IMAGE FOR DISPLAY PURPOSES
    imgBigContour = img.copy()  # COPY IMAGE FOR DISPLAY PURPOSES
    contours, hierarchy = cv2.findContours(
        imgThreshold, cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)  # FIND ALL CONTOURS
    cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 5)  # DRAW ALL DETECTED CONTOURS
    show_img(imgContours)
    # imgThreshold = cv2.adaptiveThreshold(imgGray,255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 3)

    biggest, maxArea = biggestContour(contours)  # utlis.biggestContour(contours)  # FIND THE BIGGEST CONTOUR
    if biggest.size != 0:
        biggest = reorder(biggest)  # utlis.reorder(biggest)
        cv2.drawContours(imgBigContour, biggest, -1, (0, 255, 0),
                         20)  # DRAW THE BIGGEST CONTOUR
        imgBigContour = drawRectangle(imgBigContour, biggest, 2)  # utlis.drawRectangle(imgBigContour, biggest, 2)
        pts1 = np.float32(biggest)  # PREPARE POINTS FOR WARP
        pts2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg],
                           [widthImg, heightImg]])  # PREPARE POINTS FOR WARP
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        imgWarpColored = cv2.warpPerspective(img, matrix, (widthImg, heightImg))

        imgOri = cv2.warpPerspective(img, matrix, (widthImg, heightImg))

        # REMOVE 20 PIXELS FORM EACH SIDE
        imgWarpColored = imgWarpColored[20:imgWarpColored.shape[0] - 20,
                         20:imgWarpColored.shape[1] - 20]
        imgWarpColored = cv2.resize(imgWarpColored, (widthImg, heightImg))

        # APPLY ADAPTIVE THRESHOLD
        imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
        imgAdaptiveThre = cv2.adaptiveThreshold(imgWarpGray, 255, 1, 1, 7, 2)
        imgAdaptiveThre = cv2.bitwise_not(imgAdaptiveThre)
        imgAdaptiveThre = cv2.medianBlur(imgAdaptiveThre, 3)

        # Image Array for Display
        imageArray = ([img, imgGray, imgThreshold, imgContours], [
            imgBigContour, imgWarpColored, imgWarpGray, imgAdaptiveThre
        ])

    else:
        imageArray = ([img, imgGray, imgThreshold,
                       imgContours], [imgBlank, imgBlank, imgBlank, imgBlank])
    show_img(imageArray[1][1])
    erzhi = adaptive_thres(imageArray[1][1])
    show_img(erzhi)

    print(biggest)
    print(maxArea)  # 最大面积




def main1():
    count = 0
    org_img = imread("./test_image/2.png")
    Threshold_img = imread("./test_image/u2net/2.png")
    Threshold_img = cv2.cvtColor(Threshold_img, cv2.COLOR_BGR2GRAY)
    img = org_img
    # img = cv2.resize(org_img, (int(org_img.shape[1]*0.5), int(org_img.shape[0]*0.5)), 0, 0)
    # Threshold_img = cv2.resize(Threshold_img, (int(org_img.shape[1]*0.5), int(org_img.shape[0]*0.5)), 0, 0)
    print(Threshold_img.shape, img.shape)
    # show_img(img)
    # show_img(Threshold_img)
    # heightImg = int(org_img.shape[0]*0.5)
    # widthImg = int(org_img.shape[1]*0.5)
    heightImg, widthImg = org_img.shape[0:2]
    imgBlank = np.zeros(
        (heightImg, widthImg, 3),
        np.uint8)


    imgContours = Threshold_img.copy()  # COPY IMAGE FOR DISPLAY PURPOSES
    imgBigContour = img.copy()  # COPY IMAGE FOR DISPLAY PURPOSES
    contours, hierarchy = cv2.findContours(
        Threshold_img, cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)  # FIND ALL CONTOURS
    cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 5)  # DRAW ALL DETECTED CONTOURS
    show_img(imgContours)
    # imgThreshold = cv2.adaptiveThreshold(imgGray,255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 3)

    biggest, maxArea = biggestContour(contours)  # utlis.biggestContour(contours)  # FIND THE BIGGEST CONTOUR
    if biggest.size != 0:
        biggest = reorder(biggest)  # utlis.reorder(biggest)
        cv2.drawContours(imgBigContour, biggest, -1, (0, 255, 0),
                         20)  # DRAW THE BIGGEST CONTOUR
        imgBigContour = drawRectangle(imgBigContour, biggest, 2)  # utlis.drawRectangle(imgBigContour, biggest, 2)
        pts1 = np.float32(biggest)  # PREPARE POINTS FOR WARP
        pts2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg],
                           [widthImg, heightImg]])  # PREPARE POINTS FOR WARP
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        imgWarpColored = cv2.warpPerspective(img, matrix, (widthImg, heightImg))

        imgOri = cv2.warpPerspective(img, matrix, (widthImg, heightImg))

        # REMOVE 20 PIXELS FORM EACH SIDE
        imgWarpColored = imgWarpColored[20:imgWarpColored.shape[0] - 20,
                         20:imgWarpColored.shape[1] - 20]
        imgWarpColored = cv2.resize(imgWarpColored, (widthImg, heightImg))

        # APPLY ADAPTIVE THRESHOLD
        imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
        imgAdaptiveThre = cv2.adaptiveThreshold(imgWarpGray, 255, 1, 1, 7, 2)
        imgAdaptiveThre = cv2.bitwise_not(imgAdaptiveThre)
        imgAdaptiveThre = cv2.medianBlur(imgAdaptiveThre, 3)

        # Image Array for Display
        imageArray = ([img, Threshold_img, imgContours], [
            imgBigContour, imgWarpColored, imgWarpGray, imgAdaptiveThre
        ])

    else:
        imageArray = ([img, Threshold_img,
                       imgContours], [imgBlank, imgBlank, imgBlank, imgBlank])
    show_img(imageArray[0][2])
    sdf = cv2.cvtColor(imageArray[1][1], cv2.COLOR_BGR2GRAY)
    show_img(sdf)
    # im_at_mean = cv2.adaptiveThreshold(sdf, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 3, 1)
    im_at_mean = my_huiduchuli(sdf)
    show_img(im_at_mean)
    # erzhi = adaptive_thres(sdf)
    # show_img(erzhi)

    print(biggest)
    print(maxArea)  # 最大面积
    # 二值化
    """
    直接用OpenCV的函数会让背景变花，因为背景是渐变的，直接拿均值当阈值的话，总有一些背景像素在阈值下面。
    所以需要将阈值乘以一个系数，比如0.9，过滤掉所有背景。同时，因为文字的像素值很小，不受影响。
    """







if __name__ == "__main__":
    # for root, ds, fs in os.walk(r"F:\试卷\test_image"):
    #     if fs:
    #         for f in fs:
    #             path = os.path.join(root, f)
    #             main(path)
    main1()