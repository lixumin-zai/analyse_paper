# python3.7
# -*- coding: utf-8 -*-
# @Author : listen
# @Time   :
import os
import time
from multiprocessing import Pool

import requests
import base64
import hashlib

from pathlib import PurePath, PureWindowsPath
from tqdm import tqdm


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json()

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

def pic_to_base64(url):
    format = url.split('.')[-1]
    # print(format)
    assert format == 'jpg' or format == 'jpeg' or format == 'png', """无效文件格式"""
    if format == 'png':
        with open(url, 'rb') as f:
            return 'data:image/' + format + ';base64,' + base64.b64encode(f.read()).decode("utf-8")
    else:
        with open(url, 'rb') as f:
            return 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode("utf-8")


def get_cookie():
    headers = {
        'UserAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                     'Chrome/67.0.3396.99 Safari/537.36 '
    }
    playload = {'image': '',
                'image_url': 'https://ai.bdstatic.com/file/270491698BE74D17AB4B243C4BF27DF9',
                'type': 'https://aip.baidubce.com/rest/2.0/ocr/v1/doc_analysis',
                'language_type': 'CHN_ENG',
                'detect_direction': 'true',
                'line_probability': 'true',
                'words_type': 'handprint_mix',
                'layout_analysis': 'true'}

    return requests.post('https://cloud.baidu.com/aidemo', data=playload, headers=headers).text


def paper_cut(url):

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

def call(path):
    # print(path)
    resp = paper_cut(path)
    time.sleep(1)
    path = "F:\\data\\test_paper\\strengthen_img_test\\json\\{}.json".format(path[39:-4])
    if os.path.exists(path):
        path = path[:-5] + "_1.json"
    with open(path, "w", encoding="utf-8") as f:
        f.write(resp)
    print("done")

if __name__ == "__main__":
    # p = Pool(3)
    for root, ds, fs in os.walk(r'F:/data/test_paper/strengthen_img_test'):
        try:
            if fs:
                for f in tqdm(fs):
                    try:
                        fullname = os.path.join(root, f)
                        # print(fullname)
                        # img = cv2.imread(fullname)
                        call(fullname)
                        # p.apply_async(call, args=(fullname,))
                    except Exception as e:
                        print(e)
                        continue
        except Exception as e:
            print(e)
            continue
