# python3.7
# -*- coding: utf-8 -*-
# @Author : listen
# @Time   :
# -*- coding: utf-8 -*-
# python3.7
# @Author : listen
# @Time   :
import sys

import tqdm
from bs4 import BeautifulSoup
import requests
import json
import urllib3
import re
import wget
import os
urllib3.disable_warnings()

def bar_progress(current, total, width=80):
  progress_message = "Downloading: %d%% [%d / %d] bytes" % (current / total * 100, current, total)
  # Don't use print() as it will print in new line every time.
  sys.stdout.write("\r" + progress_message)
  sys.stdout.flush()

if __name__ == '__main__':
    subjects = ["sjwl"]
    grades = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "zk", "g1", "g2", "g3", "gk"]
    for subject in subjects:
        for grade in grades:
            try:
                file_path = "./{}/{}".format(subject, grade)
                if not os.path.exists(file_path):
                    os.makedirs(file_path)
                # URL = https://www.shijuan1.com/a/sjywgk/
                URL = "https://www.shijuan1.com/a/{}{}/".format(subject, grade)
                print(URL)
                resp = requests.get(URL, verify=False)
                resp.encoding = "gbk"
                html = resp.text
                soup = BeautifulSoup(html, "lxml")

                # list_106_
                list_url = soup.find_all("a", text="下一页")
                list_url = list_url[0].get("href")[0:-6]

                pageinfo = soup.find_all("span", {"class": "pageinfo"})
                pageinfo = pageinfo[0].find_all("strong")
                # pages = 最大页数
                pages = pageinfo[0].text
                # print(pages, type(pages))


                for page in tqdm.tqdm(range(1, int(pages)+1)):
                    # print(int(pages)+1)
                    new_url = URL + list_url + str(page) + ".html"
                    print(new_url)
                    new_resp = requests.get(new_url, verify=False)
                    new_resp.encoding = "gbk"
                    list_page_html = new_resp.text
                    list_page_soup = BeautifulSoup(list_page_html, "lxml")
                    list_page_url = list_page_soup.find_all("a", {"class": "title"})
                    for download_page in list_page_url:
                        download_page_url = "https://www.shijuan1.com" + download_page.get("href")
                        download_page_resp = requests.get(download_page_url, verify=False)
                        download_page_resp.encoding = "gbk"
                        # print(resp.status_code)
                        download_page_html = download_page_resp.text
                        # print(html)
                        download_page_soup = BeautifulSoup(download_page_html, "lxml")
                        # print(soup)
                        download_url = download_page_soup.find_all('a', text=re.compile("本地下载"))
                        data_url = 'https://www.shijuan1.com' + download_url[0].get("href")
                        # print(data_url)
                        file_name = None
                        print("\t" + download_page_url)
                        if not os.path.exists(file_path + "/" + re.split("[.*?/]+", download_page_url)[-2] + ".rar"):
                            wget.download(data_url, out=file_path + "/" + re.split("[.*?/]+", download_page_url)[-2] + ".rar", bar=bar_progress)
                        else:
                            continue
            except:
                continue
                    # print(file_path + "/" + re.split("[.*?/]+", download_page)[-2] + ".rar")
                    # input()
                    # print(URL, a)
