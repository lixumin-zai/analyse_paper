# python3.7
# -*- coding: utf-8 -*-
# @Author : listen
# @Time   :
import re
from multiprocessing import Pool, Lock
import os

import tqdm
from win32com.client import Dispatch, constants, gencache
from win32com import client
a = 0
lock=Lock()

def doc2pdf(doc_name, pdf_name):
    global a
    lock.acquire()
    a += 1
    lock.release()
    pdf_name = pdf_name + str(a) + ".pdf"
    gencache.EnsureModule('{00020905-0000-0000-C000-000000000046}', 0, 8, 4)
    w = Dispatch("Word.Application")
    try:
        if os.path.exists(pdf_name):
            os.remove(pdf_name)
        doc = w.Documents.Open(doc_name, ReadOnly=1)
        doc.ExportAsFixedFormat(pdf_name, constants.wdExportFormatPDF, Item=constants.wdExportDocumentWithMarkup,
                                CreateBookmarks=constants.wdExportCreateHeadingBookmarks)
        print(pdf_name)
    except Exception as e:
        print(e)
        return 1
    finally:
        w.Quit(constants.wdDoNotSaveChanges)
    #
    # try:
    #     word = client.DispatchEx("Word.Application")
    #     if os.path.exists(pdf_name):
    #         os.remove(pdf_name)
    #     print(doc_name)
    #     worddoc = word.Documents.Open(doc_name, ReadOnly=1)
    #     worddoc.SaveAs(pdf_name, FileFormat=17)
    #     worddoc.Close()
    #     print(pdf_name)
    # except Exception as e:
    #     print(e)
    #     return 1
    # finally:
    #     w.Quit(constants.wdDoNotSaveChanges)

def createpdf(wordPath, pdfPath):
    global a
    lock.acquire()
    a += 1
    lock.release()
    pdfPath = pdfPath + str(a) + ".pdf"
    if os.path.exists(pdfPath):
        return 0
    word = gencache.EnsureDispatch('Word.Application')
    doc = word.Documents.Open(wordPath, ReadOnly=1)
    # 转换方法
    # 设置导出格式为pdf
    # pdfPath为导出后的文件路径及文件名，第二个参数为导出的格式
    doc.ExportAsFixedFormat(pdfPath, constants.wdExportFormatPDF)
    word.Quit()
    print(pdfPath)



if __name__ == '__main__':
    print('Parent process %s.' % os.getpid())
    p = Pool(4)
    for root, ds, fs in os.walk(
            'F:\\data\\test_paper\\word_data'):  # 网上这步没有写入放入word的路径，就会导致转成功后不知道pdf在哪里，这步很关键。
        # print(root, ds, fs)
        try:
            if fs:
                for f in tqdm.tqdm(fs):
                    fullname = os.path.join(root, f)
                    if 'docx' or 'doc' in fullname:
                        p.apply_async(createpdf, args=(fullname, "F:/data/test_paper/pdf_data/"))
        except Exception as e:
            print(e)
            continue

    p.close()
    p.join()

    print('All subprocesses done.')