# -*- coding: utf-8 -*-
'''
Created on 2016/06/04
https://www.evernote.com/shard/s205/nl/24522672/3210e104-9e7e-4a54-8c4b-afd3ec6c49eb/?csrfBusterToken=U%3D1762fb0%3AP%3D%2F%3AE%3D156ed8e362e%3AS%3Dc98c350ed5f36096f4153d8c8aacea82
https://www.dango-itimi.com/blog/archives/2011/001044.html

Google App Engine で Python を用いての、静的ファイルやバイトストリーム状のデータをまとめて zip 圧縮出力し、ダウンロードさせるためのサンプルです。

サンプル用クラスファイルとして以下のような Zipper.py クラスファイルを作成しました。

pylib.core.utils.Zipper.py

@author: hiroshi
'''

import zipfile

class Zipper:

    def __init__(self, file, mode = "w", compression = zipfile.ZIP_DEFLATED, allowZip64=False):
        self.__zipFile = zipfile.ZipFile(file, mode, compression, allowZip64)
    def write(self, writeDataSet = None, writeStrDataSet = None):
        if writeDataSet:
            dataSet = writeDataSet.getDataSet()
            for writeData in dataSet:
                self.__zipFile.write(
                    writeData.getFileUri(),
                    writeData.getArchiveUri(),
                    writeData.getCompressType()
                )
        if writeStrDataSet:
            dataSet = writeStrDataSet.getDataSet()
            for writeStrData in dataSet:
                self.__zipFile.writestr(
                    writeStrData.getZipInfo(),
                    writeStrData.getBytes()
                )

    def close(self):
        self.__zipFile.close()

class WriteDataSet:
    def __init__(self):
        self.__dataSet = []

    def add(self, fileUri, archiveUri=None, compressType=None):
        self.__dataSet.append(WriteData(fileUri, archiveUri, compressType))

    def getDataSet(self):
        return self.__dataSet


class WriteData:
    def __init__(self, fileUri, archiveUri=None, compressType=None):
        self.__fileUri = fileUri
        self.__archiveUri = archiveUri
        self.__compressType = compressType

    def getFileUri(self):
        return self.__fileUri

    def getArchiveUri(self):
        return self.__archiveUri

    def getCompressType(self):
        return self.__compressType


class WriteStrDataSet:
    def __init__(self):
        self.__dataSet = []

    def add(self, bytes, zipInfo):
        self.__dataSet.append(WriteStrData(bytes, zipInfo))

    def getDataSet(self):
        return self.__dataSet

class WriteStrData:

    def __init__(self, bytes, zipInfo):

        self.__zipInfo = zipInfo
        self.__bytes = bytes

    def getZipInfo(self):
        return self.__zipInfo

    def getBytes(self):
        return self.__bytes


def createBytesFile():

    import StringIO
    return StringIO.StringIO()

def createZipInfoOfNowTime(archiveUri):

    import datetime
    date = datetime.datetime.now()

    return zipfile.ZipInfo(archiveUri, date.timetuple()[:6])

def output(response, file, fileName):

    response.headers["Content-Type"] = "application/zip"
    response.headers['Content-Disposition'] = "attachment; filename=" + fileName
    response.out.write(file.getvalue())


"""
Zipper.py の利用方法は以下となります。

from pylib.core.utils.Zipper import *

# 出力用ファイル作成
file = createBytesFile()

# 静的ファイル用 データ作成
writeDataSet = WriteDataSet()
writeDataSet.add("test/index.html", "index.html")
writeDataSet.add("img/purin.jpg", "img/purin.jpg")

# バイトストリーム用 データ作成
writeStrDataSet = WriteStrDataSet()
writeStrDataSet.add(bytesA, createZipInfoOfNowTime("test.swf"))
writeStrDataSet.add(bytesB, createZipInfoOfNowTime("test/aaa.swf"))

# zip 圧縮
zipper = Zipper(file)
zipper.write(writeDataSet, writeStrDataSet)
zipper.close()

# 画面に出力
output(self.response, file, "sample.zip")

"""