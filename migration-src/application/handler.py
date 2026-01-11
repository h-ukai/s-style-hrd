# -*- coding: utf-8 -*-

from google.cloud import ndb
from google.cloud import storage
from flask import request, redirect, render_template, Response
from urllib.parse import unquote_plus
import application.models.blob as blob_models
from application.models.bkdata import BKdata
from application import gcs_utils
import email.header
import os


# GCS移行完了: Blobstore → GCS


class FileInfo(ndb.Model):
    """
    FileInfo model (migrated from db.Model)

    GCS移行完了: blob フィールドは GCS object name を格納
    """
    blob = ndb.StringProperty(required=True)  # GCS object name を格納
    uploaded_by = ndb.StringProperty(required=True)  # Store user ID/email as string
    uploaded_at = ndb.DateTimeProperty(required=True, auto_now_add=True)


def file_upload_form_route():
    """
    FileUploadForm route handler (converted from webapp2.RequestHandler)

    Migrated from: webapp2.RequestHandler (FileUploadFormHandler class)
    Original path: /FileUploadFormHandler
    """
    return render_template("upload.html")


def file_upload_route():
    """
    FileUpload route handler (converted from BlobstoreUploadHandler)

    Migrated from: blobstore_handlers.BlobstoreUploadHandler (FileUploadHandler class)
    Original path: /FileUploadFormHandler/upload

    GCS移行完了: Flask request.files + gcs_utils でアップロード
    """
    uploaded_file = request.files.get('file')
    if not uploaded_file:
        return "No file uploaded", 404

    filename = uploaded_file.filename
    corp_org_key = request.form.get("CorpOrg_key")
    branch_key = request.form.get("Branch_Key")
    bk_id = request.form.get("bkID")

    # 拡張子を取得
    _, ext = os.path.splitext(filename)
    ext = ext.lower().strip(".")

    # blobNo を取得
    key_name1 = corp_org_key + "/" + branch_key + "/" + bk_id
    blobno = blob_models.blobNo.get_or_insert(key_name1, blob_key_name=key_name1)
    blobnextno = blobno.getNextNum()

    # GCS object name を生成してアップロード
    object_name = gcs_utils.generate_object_name(
        corp_org_key, branch_key, bk_id, blobnextno, ext
    )
    gcs_utils.upload_file(
        uploaded_file.read(),
        object_name,
        content_type=uploaded_file.content_type
    )

    lobdbkey = setblobdb(object_name, filename, corp_org_key, branch_key, bk_id)
    return redirect("/FileUploadFormHandler/file/%d/success" % lobdbkey)


def setblobdb(blobkey, filename, corp_org_key, branch_key, bk_id):
    """
    Helper function to save blob metadata to Datastore

    GCS移行完了: blobkey は GCS object name
    """
    key_name1 = corp_org_key + "/" + branch_key + "/" + bk_id
    bkdb = ndb.Key(BKdata, key_name1).get()
    shzicmi1 = bkdb.shzicmi1 if bkdb else None
    shzicmi2 = bkdb.shzicmi2 if bkdb else None
    ttmnmi = bkdb.ttmnmi if bkdb else None

    blobno = blob_models.blobNo.get_or_insert(key_name1, blob_key_name=key_name1)
    blobnextno = blobno.getNextNum()
    key_name2 = key_name1 + "/" + str(blobnextno)
    blob = blob_models.Blob.get_or_insert(key_name2)
    blob.blobNo = blobnextno
    blob.filename = filename
    blob.blobKey = blobkey
    blob.blob_key_name = key_name2
    blob.CorpOrg_key = corp_org_key
    blob.Branch_Key = branch_key
    bk_id_decoded = unquote_plus(bk_id)
    blob.bkID = bk_id_decoded
    if shzicmi1:
        blob.shzicmi1 = shzicmi1
    else:
        blob.shzicmi1 = None
    if shzicmi2:
        blob.shzicmi2 = shzicmi2
    else:
        blob.shzicmi2 = None
    if ttmnmi:
        blob.ttmnmi = ttmnmi
    else:
        blob.ttmnmi = None
    blob.put()
    return blobnextno


def delete_file_route():
    """
    Delete file route handler

    GCS移行完了: gcs_utils.delete_file() で削除
    """
    key = request.args.get('key') or request.form.get('key')

    query = blob_models.Blob.query(blob_models.Blob.blobKey == key)
    blobs = query.fetch()

    if len(blobs) == 1:
        # GCS からファイルを削除
        try:
            gcs_utils.delete_file(key)
        except Exception:
            pass  # ファイルが存在しない場合は無視

    for blob in blobs:
        blob.key.delete()

    return "Deleted", 200


def ajax_success_route(file_id):
    """
    Ajax success route handler (converted from webapp2.RequestHandler)

    Migrated from: webapp2.RequestHandler (AjaxSuccessHandler class)
    Original path: /FileUploadFormHandler/file/<file_id>/success
    """
    response = Response('%s/FileUploadFormHandler/file/%s' % (request.host_url, file_id))
    response.headers['Content-Type'] = 'text/plain'
    return response


# REVIEW-L1: long() → int() conversion applied
# Python 2: long(file_id)
# Python 3: int(file_id)
def file_info_route(file_id):
    """
    FileInfo route handler (converted from webapp2.RequestHandler)

    Migrated from: webapp2.RequestHandler (FileInfoHandler class)
    Original path: /FileUploadFormHandler/file/<file_id>
    """
    file_info = FileInfo.get_by_id(int(file_id))
    if not file_info:
        return "File not found", 404
    return render_template("info.html", file_info=file_info)


# REVIEW-L1: long() → int() conversion applied
# Python 2: long(file_id)
# Python 3: int(file_id)
def file_download_route(file_id):
    """
    FileDownload route handler (converted from BlobstoreDownloadHandler)

    Migrated from: blobstore_handlers.BlobstoreDownloadHandler (FileDownloadHandler class)
    Original path: /FileUploadFormHandler/file/<file_id>/download

    GCS移行完了: Signed URL にリダイレクト
    """
    file_info = FileInfo.get_by_id(int(file_id))
    if not file_info or not file_info.blob:
        return "File not found", 404

    # GCS Signed URL にリダイレクト
    try:
        signed_url = gcs_utils.generate_signed_url(file_info.blob, expiration_minutes=5)
        return redirect(signed_url)
    except Exception as e:
        return f"File not found: {file_info.blob}", 404


def generate_upload_url_route():
    """
    GenerateUploadUrl route handler (converted from webapp2.RequestHandler)

    Migrated from: webapp2.RequestHandler (GenerateUploadUrlHandler class)
    Original path: /FileUploadFormHandler/generate_upload_url

    GCS移行完了: アップロードはサーバー経由で行うため、エンドポイントURLを返す
    """
    urlstr = ""
    corp_org_key = request.args.get("CorpOrg_key")
    urlstr += "CorpOrg_key=" + corp_org_key
    branch_key = request.args.get("Branch_Key")
    urlstr += "&Branch_Key=" + branch_key
    bk_id = request.args.get("bkID")
    urlstr += "&bkID=" + bk_id

    # GCS移行: サーバー経由でアップロードするため、エンドポイントURLを返す
    upload_url = '/FileUploadFormHandler/upload?' + urlstr

    response = Response(upload_url)
    response.headers['Content-Type'] = 'text/plain'
    return response
