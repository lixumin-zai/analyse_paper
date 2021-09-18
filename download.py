# -*- coding: utf-8 -*-
# python3.7
# @Author : listen
# @Time   :
from bs4 import BeautifulSoup
import requests
import json
import urllib3
import re
import wget
import os

def download_url(url):
    """

    :param url:  download_page
    :return:
    """
    resp = requests.get(url, verify=False)
    resp.encoding = "gbk"
    # print(resp.status_code)
    html = resp.text
    # print(html)
    soup = BeautifulSoup(html, "lxml")
    # print(soup)
    a = soup.find_all('a', text=re.compile("本地下载"))
    data_url = 'https://www.shijuan1.com' + a[0].get("href")
    print(data_url)
    file_name = None
    wget.download(data_url, out=file_name)
    print(URL, a)


def download_page(url):
    resp = requests.get(url, verify=False)
    resp.encoding = "gbk"
    list_page_html = resp.text
    list_page_soup = BeautifulSoup(list_page_html, "lxml")
    list_url = list_page_soup.find_all("a", {"class": "title"})
    for url in list_url:
        download_page = "https://www.shijuan1.com" + url.get("href")
        download(download_page)

    return download_page


def list_page():
    subjects = ["sjyw"]
    grades = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "zk", "g1", "g2", "g3", "gk"]
    for subject in subjects:
        for grade in grades:
            # URL = https://www.shijuan1.com/a/sjywgk/
            URL = "https://www.shijuan1.com/a/{}{}/".format(subject, grade)
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
            print(pages, type(pages))

            for page in tqdm.tqdm(range(1, int(pages)+1)):
                # https://www.shijuan1.com/a/sjyw1/list_106_1.html
                new_url = URL + list_url + str(page) + ".html"
                download_page(new_url)
                print(new_url)
                input()


if __name__ == '__main__':
    # subjects = ["sjyw"]
    # grades = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "zk", "g1", "g2", "g3", "gk"]
    # for subject in subjects:
    #     for grade in grades:
    #         # URL = https://www.shijuan1.com/a/sjywgk/
    #         URL = "https://www.shijuan1.com/a/{}{}/".format(subject, grade)
    #         resp = requests.get(URL, verify=False)
    #         resp.encoding = "gbk"
    #         html = resp.text
    #         soup = BeautifulSoup(html, "lxml")
    #
    #         # list_106_
    #         list_url = soup.find_all("a", text="下一页")
    #         list_url = list_url[0].get("href")[0:-6]
    #
    #         pageinfo = soup.find_all("span", {"class": "pageinfo"})
    #         pageinfo = pageinfo[0].find_all("strong")
    #         # pages = 最大页数
    #         pages = pageinfo[0].text
    #         print(pages, type(pages))
    #
    #         for page in range(1, int(pages)+1):
    #             new_url = URL + list_url + str(page) + ".html"
    #             print(new_url)
    #             input()




    choices_subject = subject[0]
    file_path = "./{}".format(choices_subject)
    if not os.path.exists(file_path):
        os.mkdir(file_path)
    try:
        URL = "https://www.shijuan1.com/a/{}/302550.html".format(choices_subject)
        print(URL)
        resp = requests.get(URL, verify=False)
        resp.encoding = "gbk"
        # print(resp.status_code)
        html = resp.text
        # print(html)
        soup = BeautifulSoup(html, "lxml")
        # print(soup)
        a = soup.find_all('a', text=re.compile("本地下载"))
        data_url = 'https://www.shijuan1.com' + a[0].get("href")
        print(data_url)
        file_name = None
        wget.download(data_url, out=file_name)
        print(URL, a)
    except:
        print("错误")
