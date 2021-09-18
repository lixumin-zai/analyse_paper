import requests
import base64
import hashlib


def pic_to_base64(url):
    format = url.split('.')[-1]
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

    return requests.post('https://duguang.aliyun.com/ocrdemo/ocrDemoEducationService.json', data=playload,
                         headers=headers).text


if __name__ == "__main__":
    print(paper_cut('test1.png'))
    # paper_cut('test1.png')
