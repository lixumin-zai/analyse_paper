# python3.7
# -*- coding: utf-8 -*-
# @Author : listen
# @Time   :
from unrar import rarfile
import os
from multiprocessing import Pool


def unrar_process(file_name, root_path, save_path):
    if not os.path.exists(root_path):
        os.makedirs(root_path)
    print(file_name)
    f = rarfile.RarFile(os.path.join(root_path, file_name))
    f.extractall(save_path)


if __name__ == "__main__":
    print('Parent process %s.' % os.getpid())
    p = Pool(8)
    # root 根目录
    # ds 根目录下的子文件夹
    # fs 根目录下的文件
    for root, ds, fs in os.walk("./data"):
        if fs:
            print(fs)
            root_path = root
            save_path = "../data/test_paper/word_data" + root[6:]
            if not os.path.exists(save_path):
                # print(root[6:])
                os.makedirs(save_path)
            # print(save_path)
            for f in fs:
                p.apply_async(unrar_process, args=(f, root_path, save_path))
    p.close()
    p.join()
        # print(root, ds, fs)
        # os.makedirs(file_path)
    # f = rarfile.RarFile("./192471.rar")   # 传入rar文件路径
    # f.extractall("./")
