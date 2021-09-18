# python3.7
# -*- coding: utf-8 -*-
# @Author : listen
# @Time   :
"""

json 封装

"""
import cv2
import numpy as np
import requests
import base64
import hashlib
# from deploy.python.predict import corrector
from PIL import ImageFont, ImageDraw, Image
from focus import to_correct
import time

def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json()

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

def pic_to_base64(url):
    """

    :param url:
    :return:
    """
    suffix = url.split('.')[-1]
    assert suffix == 'jpg' or suffix == 'jpeg' or suffix == 'png', """无效文件格式"""
    if suffix == 'png':
        with open(url, 'rb') as f:
            return 'data:image/png;base64,' + base64.b64encode(f.read()).decode("utf-8")
    else:
        with open(url, 'rb') as f:
            return 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode("utf-8")


def paper_cut(url):
    """

    :param url:
    :return:
    """
    code = pic_to_base64(url)
    h = hashlib.md5()
    h.update((str(len(code)) + 'duguang.aliyun.comdemo_paper_structured').encode(encoding='utf-8'))
    sign = h.hexdigest()

    headers = {
        'UserAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                     'Chrome/67.0.3396.99 Safari/537.36 '
    }
    playload = {'img': code,
                'type': 'demo_paper_structured',
                'prob': 'true',
                'sign': sign,
                'subjectType': 'default',
                }
    proxy = get_proxy().get("proxy")
    return requests.post('https://duguang.aliyun.com/ocrdemo/ocrDemoEducationService.json', data=playload,
                         headers=headers, proxies={"http": "http://{}".format(proxy)}).text


def qieti(path, pos):
    """

    :param path:
    :param pos:
    :return: loc: {'left': 58, 'height': 32, 'width': 40, 'top': 0}   left_top_x, length_y, length_x left_top_y,
    """
    org_img = cv2.imread(path)
    ptLeftTop = (pos[0]["x"], pos[0]["y"])
    ptRightBottom = (pos[2]["x"], pos[2]["y"])
    # loc = ptLeftTop[1]: ptRightBottom[1], ptLeftTop[0]: ptRightBottom[0]
    # location =
    return org_img[ptLeftTop[1]:ptRightBottom[1], ptLeftTop[0]:ptRightBottom[0]]


def seg_img(path):
    """
    aliyun qieti
    :param path:  tupianlujing
    :return: img:
             location:[{'x': 208, 'y': 81}, {'x': 314, 'y': 80}, {'x': 314, 'y': 94}, {'x': 208, 'y': 94}]
             * -> *
                  |
             * <- *
    """
    suffix = path.split('.')[-1]
    assert suffix == 'jpg' or suffix == 'jpeg' or suffix == 'png', """无效文件格式"""
    data = eval(paper_cut(path))

    for i in data["data"]["part_info"]:
        for j in i["subject_list"]:
            for location in j["pos_list"]:
                img = qieti(path, location)
                # {'left': 58, 'height': 32, 'width': 40, 'top': 0}
                # location["left"] = k[0]["x"]
                # location["height"] = k[0]["x"]
                # location["width"] = k[0]["x"]
                # location["top"] = k[0]["x"]
                success, encoded_image = cv2.imencode('.' + suffix, img)
                byte_data = encoded_image.tobytes()
                if suffix == 'png':
                    yield 'data:image/png;base64,' + base64.b64encode(byte_data).decode("utf-8"), location
                else:
                    yield 'data:image/jpeg;base64,' + base64.b64encode(byte_data).decode("utf-8"), location


def answer_cut(image):
    """
    baidu shibieshouxie
    :param image:
    :return: loc: {'left': 58, 'height': 32, 'width': 40, 'top': 0}   left_top_x, length_y, length_x left_top_y,
             word: Why
    """
    headers = {
        'UserAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                     'Chrome/67.0.3396.99 Safari/537.36 '
    }
    playload = {'image': image,
                'image_url': '',
                'type': 'https://aip.baidubce.com/rest/2.0/ocr/v1/doc_analysis',
                'language_type': 'CHN_ENG',
                'detect_direction': 'true',
                'line_probability': 'true',
                'words_type': 'handprint_mix',
                'layout_analysis': 'true'}

    proxy = get_proxy().get("proxy")
    result = eval(requests.post('https://cloud.baidu.com/aidemo', data=playload, headers=headers, proxies={"http": "http://{}".format(proxy)}).text)
    if result['msg'] == 'success':
        for elem in result['data']['results']:
            if elem['words_type'] == 'handwriting':
                # print("baidu")
                # time.sleep(3)
                yield elem['words']['words_location'], elem['words']['word']
                #{left: 1 ,sdf: 2}
    else:
        print('error')

def rectangle(img, ptLeftTop, ptRightBottom, point_color):
    # point_color = (0, 0, 255) # BGR
    # print(ptLeftTop, ptRightBottom)
    thickness = 1
    cv2.rectangle(img, ptLeftTop, ptRightBottom, point_color, thickness)
    return img
    # cv2.imshow("123", img)
    # cv2.waitKey(0)

def get_json(path):
    data = {
        "imageID": None,
        "shape": {
            "width": None,
            "height": None
        },
        "questions": []
    }

    image = cv2.imread(path)
    x, y = image.shape[0:2]
    ####
    data["shape"]["width"], data["shape"]["height"] = (x, y)
    ####

    for questionsID, (img, ques_loc) in enumerate(seg_img(path)):
        question = {
            "questionsID": None,
            "location": [  # 左上角，右上角
                {
                    "x": None,
                    "y": None
                },
                {
                    "x": None,
                    "y": None
                }
            ],
            "answers": []
        }
        # print("ques:", ques_loc)
        ptLeftTop0 = (ques_loc[0]["x"], ques_loc[0]["y"])
        ptRightBottom0 = (ques_loc[2]["x"], ques_loc[2]["y"])
        image = rectangle(image, ptLeftTop0, ptRightBottom0, (0, 0, 255))

        ####
        # print(questionsID)
        question["questionsID"] = questionsID
        question["location"][0]["x"] = ques_loc[0]["x"]/x
        question["location"][0]["y"] = ques_loc[0]["y"]/y
        question["location"][1]["x"] = ques_loc[2]["x"]/x
        question["location"][1]["y"] = ques_loc[2]["y"]/y
        ####

        for answerID, (loc, word) in enumerate(answer_cut(img)):
            answer = {
                "answersID": None,
                "location": [
                    {
                        "x": None,
                        "y": None
                    },
                    {
                        "x": None,
                        "y": None
                    }
                ],
                "text": "",
                "corrector": 0  # 0:未批改,找不到答案 , 1:正确, 2:错误, 3:不确定
            }
            answer_loc = [{"x": ques_loc[0]["x"] + loc["left"], "y": ques_loc[0]["y"] + loc["top"]},
                          {"x": ques_loc[0]["x"] + loc["left"] + loc["width"], "y": ques_loc[0]["y"] + loc["top"]},
                          {"x": ques_loc[0]["x"] + loc["left"] + loc["width"],
                           "y": ques_loc[0]["y"] + loc["top"] + loc["height"]},
                          {"x": ques_loc[0]["x"] + loc["left"], "y": ques_loc[0]["y"] + loc["top"] + loc["height"]}]

            # 常看图片信息
            # ptLeftTop1 = (answer_loc[0]["x"], answer_loc[0]["y"])
            # ptRightBottom1 = (answer_loc[2]["x"], answer_loc[2]["y"])
            # image = rectangle(image, ptLeftTop1, ptRightBottom1, (0, 255, 0))

            # img_PIL = Image.fromarray(image)
            # font = ImageFont.truetype('./simkai.ttf', 10)
            # fillColor = (0, 0, 0)
            # draw = ImageDraw.Draw(img_PIL)
            # draw.text((answer_loc[3]["x"], answer_loc[3]["y"]), word, font=font, fill=fillColor)
            # # cv2.putText(image, word, ptLeftTop1, font, 2, (0, 0, 255), 1)
            # # print("answer:", answer_loc)
            # image = cv2.cvtColor(np.asarray(img_PIL), cv2.COLOR_RGB2BGR)
            ####

            # print(answerID)
            answer["answersID"] = answerID
            answer["location"][0]["x"] = answer_loc[0]["x"]/x
            answer["location"][0]["y"] = answer_loc[0]["y"]/y
            answer["location"][1]["x"] = answer_loc[2]["x"]/x
            answer["location"][1]["y"] = answer_loc[2]["y"]/y
            answer["text"] = word
            ####
            question["answers"].append(answer)
            ###
        data["questions"].append(question)
    # cv2.imshow("dsf", image)
    # cv2.waitKey(0)
    return data

def show_image(org_image, resp):
    x = resp["shape"]["width"]
    y = resp["shape"]["height"]
    image = org_image
    for question in resp["questions"]:
        # print(question)
        ques_loc = question["location"]
        ptLeftTop0 = (int(ques_loc[0]["x"]*x), int(ques_loc[0]["y"]*y))
        ptRightBottom0 = (int(ques_loc[1]["x"]*x), int(ques_loc[1]["y"]*y))
        # print(image, ptRightBottom0, ptLeftTop0)
        image = rectangle(image, ptLeftTop0, ptRightBottom0, (255, 0, 0))

        for answer in question["answers"]:
            answer_loc = answer["location"]
            ptLeftTop1 = (int(answer_loc[0]["x"]*x), int(answer_loc[0]["y"]*y))
            ptRightBottom1 = (int(answer_loc[1]["x"]*x), int(answer_loc[1]["y"]*y))
            if answer["corrector"] == 0:
                image = rectangle(image, ptLeftTop1, ptRightBottom1, (0, 0, 0))
            if answer["corrector"] == 1:
                image = rectangle(image, ptLeftTop1, ptRightBottom1, (0, 255, 0))
            if answer["corrector"] == 2:
                image = rectangle(image, ptLeftTop1, ptRightBottom1, (0, 0, 255))
            if answer["corrector"] == 3:
                image = rectangle(image, ptLeftTop1, ptRightBottom1, (255, 255, 0))
    cv2.imshow("ds{}f".format(image[2, 3]), image)


if __name__ == "__main__":
    teacher = cv2.imread("teacher.jpg")
    student = cv2.imread("student.jpg")
    resp_t = get_json("teacher.jpg")
    resp_s = get_json("student.jpg")
    resp_s = to_correct(resp_t, resp_s)
    # print(resp_s)
    show_image(teacher, resp_t)
    show_image(student, resp_s)
    cv2.waitKey(0)

    # print(resp_s)
    # resp_teacher = {
    #     "imageID": 0,
    #     "shape": {
    #         "width": 800,
    #         "height": 1000
    #     },
    #     "questions": [
    #         {
    #             "questionsID": 0,
    #             "location": [  # 左上角，右上角
    #                 {
    #                     "x": 0.1,
    #                     "y": 0.1
    #                 },
    #                 {
    #                     "x": 0.2,
    #                     "y": 0.2
    #                 }
    #             ],
    #             "answers": [
    #                 {
    #                     "answersID": 0,
    #                     "location": [
    #                         {
    #                             "x": 0.12,
    #                             "y": 0.12
    #                         },
    #                         {
    #                             "x": 0.18,
    #                             "y": 0.18
    #                         }
    #                     ],
    #                     "text": "text",
    #                     "corrector": "0"
    #                 }
    #             ]
    #         },
    #         {
    #             "questionsID": 1,
    #             "location": [  # 左上角，右上角
    #                 {
    #                     "x": 0.3,
    #                     "y": 0.3
    #                 },
    #                 {
    #                     "x": 0.4,
    #                     "y": 0.4
    #                 }
    #             ],
    #             "answers": [
    #                 {
    #                     "answersID": 0,
    #                     "location": [
    #                         {
    #                             "x": 0.32,
    #                             "y": 0.32
    #                         },
    #                         {
    #                             "x": 0.34,
    #                             "y": 0.34
    #                         }
    #                     ],
    #                     "text": "text",
    #                     "corrector": "0"
    #                 },
    #                 {
    #                     "answersID": 1,
    #                     "location": [
    #                         {
    #                             "x": 0.35,
    #                             "y": 0.35
    #                         },
    #                         {
    #                             "x": 0.37,
    #                             "y": 0.37
    #                         }
    #                     ],
    #                     "text": "text",
    #                     "corrector": "0"
    #                 }
    #             ]
    #         }
    #     ]
    # }
    # resp_student = {
    #     "imageID": 0,
    #     "shape": {
    #         "width": 800,
    #         "height": 1000
    #     },
    #     "questions": [
    #         {
    #             "questionsID": 0,
    #             "location": [  # 左上角，右上角
    #                 {
    #                     "x": 0.102,
    #                     "y": 0.103
    #                 },
    #                 {
    #                     "x": 0.21,
    #                     "y": 0.21
    #                 }
    #             ],
    #             "answers": [
    #                 {
    #                     "answersID": 0,
    #                     "location": [
    #                         {
    #                             "x": 0.12,
    #                             "y": 0.12
    #                         },
    #                         {
    #                             "x": 0.18,
    #                             "y": 0.18
    #                         }
    #                     ],
    #                     "text": "text",
    #                     "corrector": "0"
    #                 }
    #             ]
    #         },
    #     ]
    # }

    # x, y = image.shape[0:2]

    # resp = {
    #     "imageID": 0,
    #     "shape": {
    #         "width": 1561,
    #         "height": 1321
    #     },
    #     "questions": [
    #         {
    #             "questionsID": 0,
    #             "location": [  # 左上角，右上角
    #                 {
    #                     "x": 0.4,
    #                     "y": 0.5
    #                 },
    #                 {
    #                     "x": 0.4,
    #                     "y": 0.5
    #                 }
    #             ],
    #             "answers": [
    #                 {
    #                     "answerID": 0,
    #                     "location": [
    #                         {
    #                             "x": 0.4,
    #                             "y": 0.5
    #                         },
    #                         {
    #                             "x": 0.4,
    #                             "y": 0.5
    #                         }
    #                     ],
    #                     "text": "text",
    #                     "corrector": "0"
    #                 }
    #             ]
    #         },
    #     ]
    # }

            # print(loc, word)
            # print(corrector(word, word))