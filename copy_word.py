# python3.7
# -*- coding: utf-8 -*-
# @Author : listen
# @Time   :
import os
import shutil
import tqdm
if __name__ == '__main__':
    # print('Parent process %s.' % os.getpid())
    # a = 1
    # for root, ds, fs in os.walk(
    #         r'F:\试卷\sjwl'):  # 网上这步没有写入放入word的路径，就会导致转成功后不知道pdf在哪里，这步很关键。
    #     # print(root, ds, fs)
    #     try:
    #         if fs:
    #             for f in tqdm.tqdm(fs):
    #                 fullname = os.path.join(root, f)
    #                 # print(fullname)
    #                 print(f)
    #                 shutil.copyfile(fullname, 'F:\\data\\all_paper\\'+f)
    #
    #
    #     except Exception as e:
    #         print(e)
    #         continue

    print('Parent process %s.' % os.getpid())
    a = 1
    for root, ds, fs in os.walk(
            r'F:\data\all_paper'):  # 网上这步没有写入放入word的路径，就会导致转成功后不知道pdf在哪里，这步很关键。
        print(root, ds, fs)
        try:
            if fs:
                for f in tqdm.tqdm(fs):
                    fullname = os.path.join(root, f)
                    # print(fullname)
                    print(f)
                    shutil.copyfile(fullname, 'F:\\data\\all_paper\\' + f)


        except Exception as e:
            print(e)
            continue
