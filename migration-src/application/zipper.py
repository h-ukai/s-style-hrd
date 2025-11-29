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
import io
import datetime


class Zipper:
    """ZIP ファイル生成ユーティリティ

    Migration Notes:
    - StringIO.StringIO() → io.BytesIO()（バイナリデータ用）
    - response.out.write() → Flask Response で返却
    """

    def __init__(self, file, mode="w", compression=zipfile.ZIP_DEFLATED, allowZip64=False):
        self.__zipFile = zipfile.ZipFile(file, mode, compression, allowZip64)

    def write(self, writeDataSet=None, writeStrDataSet=None):
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
    """ファイルベースの ZIP 書き込みデータセット"""

    def __init__(self):
        self.__dataSet = []

    def add(self, fileUri, archiveUri=None, compressType=None):
        self.__dataSet.append(WriteData(fileUri, archiveUri, compressType))

    def getDataSet(self):
        return self.__dataSet


class WriteData:
    """ファイルベースの ZIP 書き込みデータ"""

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
    """バイトストリームベースの ZIP 書き込みデータセット"""

    def __init__(self):
        self.__dataSet = []

    def add(self, bytes, zipInfo):
        self.__dataSet.append(WriteStrData(bytes, zipInfo))

    def getDataSet(self):
        return self.__dataSet


class WriteStrData:
    """バイトストリームベースの ZIP 書き込みデータ"""

    def __init__(self, bytes, zipInfo):
        self.__zipInfo = zipInfo
        self.__bytes = bytes

    def getZipInfo(self):
        return self.__zipInfo

    def getBytes(self):
        return self.__bytes


def createBytesFile():
    """バイトストリーム用バッファを作成

    Migration Notes:
    - StringIO.StringIO() → io.BytesIO()（バイナリデータ用）
    """
    return io.BytesIO()


def createZipInfoOfNowTime(archiveUri):
    """現在時刻付きの ZipInfo を作成"""
    date = datetime.datetime.now()
    return zipfile.ZipInfo(archiveUri, date.timetuple()[:6])


def output(response, file, fileName):
    """Flask Response にバイナリデータを出力

    Migration Notes:
    - response.headers（Flask の Response オブジェクト）
    - response.out.write() → Flask で return する

    Args:
        response: Flask Response オブジェクト
        file: io.BytesIO オブジェクト
        fileName: ダウンロードするファイル名
    """
    response.headers["Content-Type"] = "application/zip"
    response.headers['Content-Disposition'] = 'attachment; filename="' + fileName + '"'
    # Flask では response に data をセットするか、return で返す
    # この関数は response に対してヘッダーを設定し、呼び出し元で
    # return response(file.getvalue()) とするか
    # return file.getvalue() とする
    return file.getvalue()


"""
Zipper.py の利用方法は以下となります。

from application.zipper import *

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

# Flask で出力
from flask import Response
response = Response(file.getvalue(), mimetype='application/zip')
response.headers['Content-Disposition'] = 'attachment; filename="sample.zip"'
return response

"""
