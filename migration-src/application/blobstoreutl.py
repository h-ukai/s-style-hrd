# -*- coding: utf-8 -*-

import os.path
from urllib.parse import unquote_plus, unquote
from flask import request, redirect, render_template
from google.cloud import storage
from google.cloud import ndb
import email.header
from application.models.bkdata import BKdata
import application.models.blob as blob_models
from application import gcs_utils


# GCS移行完了: Blobstore → GCS
# - blobstore.create_upload_url() → /blob/upload エンドポイント
# - BlobstoreUploadHandler → Flask request.files + gcs_utils
# - get_serving_url() → gcs_utils.get_blob_url(), get_thumbnail_url()
# - BlobReferenceProperty → String property (GCS object name)


def blobstore_utl_route(corp_org_key, branch_key, bk_id):
    """
    BlobstoreUtl route handler (converted from webapp2.RequestHandler)

    Migrated from: webapp2.RequestHandler (BlobstoreUtlHandler class)
    Original path: /BlobstoreUtl/<corp_org_key>/<branch_key>/<bk_id>

    GCS移行完了: アップロードは /blob/upload エンドポイントを使用
    """
    keypath = corp_org_key + "/" + branch_key + "/" + bk_id

    # GCS移行: アップロードは /upload/ エンドポイント経由
    upload_url = "/upload/" + keypath

    edit_url = "/upload/" + keypath
    multiupload_url = "/FileUploadFormHandler?CorpOrg_key=" + corp_org_key + "&Branch_Key=" + branch_key + "&bkID=" + bk_id

    # Blobstore に保存されているファイルを取得
    bk_id_decoded = unquote_plus(bk_id)

    query = blob_models.Blob.query(
        blob_models.Blob.CorpOrg_key == corp_org_key,
        blob_models.Blob.Branch_Key == branch_key,
        blob_models.Blob.bkID == bk_id_decoded
    ).order(blob_models.Blob.media, blob_models.Blob.pos)
    blobs = query.fetch()

    mblobs = []
    cblobs = []
    chk = ""
    if len(blobs) >= 1:
        chk = blobs[0].media
        for blob in blobs:
            if blob.filename and blob.html is None:
                root, ext = os.path.splitext(blob.filename)
                ext = ext.lower().strip(".")
                blob.fileextension = ext
                if ext in ["jpeg", "jpg", "png", "gif", "bmp"]:
                    try:
                        # GCS移行完了: 統一エンドポイントを使用
                        blob.thumbnailurl = gcs_utils.get_thumbnail_url(blob.blobKey)
                        blob.bloburl = gcs_utils.get_blob_url(blob.blobKey)
                        blob.html = gcs_utils.generate_html(
                            blob.blobKey, blob.filename, title=blob.filename, is_image=True
                        )
                    except Exception:
                        pass
                else:
                    # GCS移行完了: 統一エンドポイントを使用
                    blob.bloburl = gcs_utils.get_blob_url(blob.blobKey)
                    blob.html = gcs_utils.generate_html(blob.blobKey, blob.filename, is_image=False)
                blob.put()
            if chk != blob.media:
                mblobs.append({"media": chk, "cblob": cblobs})
                chk = blob.media
                cblobs = []
            cblobs.append(blob)
        mblobs.append({"media": blob.media, "cblob": cblobs})

    key_name = corp_org_key + "/" + branch_key + "/" + bk_id_decoded
    bkdb = BKdata.get_or_insert(key_name, bkID=bk_id_decoded)
    tempblobs1 = []
    tempblobs2 = []

    if bkdb.shzicmi1 and bkdb.shzicmi2:
        query = blob_models.Blob.query(
            blob_models.Blob.CorpOrg_key == corp_org_key,
            blob_models.Blob.shzicmi1 == bkdb.shzicmi1,
            blob_models.Blob.shzicmi2 == bkdb.shzicmi2
        ).order(blob_models.Blob.bkID, blob_models.Blob.media, blob_models.Blob.pos)
        tempblobs1 = query.fetch()

    for b in tempblobs1:
        for t in tempblobs2:
            if b.blobKey == t.blobKey:
                break
        else:
            tempblobs2.append(b)

    if bkdb.ttmnmi:
        query = blob_models.Blob.query(
            blob_models.Blob.CorpOrg_key == corp_org_key,
            blob_models.Blob.ttmnmi == bkdb.ttmnmi
        ).order(blob_models.Blob.bkID, blob_models.Blob.media, blob_models.Blob.pos)
        tempblobs1 = query.fetch()

    for b in tempblobs1:
        for t in tempblobs2:
            if b.blobKey == t.blobKey:
                break
        else:
            tempblobs2.append(b)

    # テンプレートを使って出力
    data = dict(
        blobs=mblobs,
        upload_url=upload_url,
        edit_url=edit_url,
        samples=tempblobs2,
        multiupload_url=multiupload_url,
        bkID=bk_id_decoded
    )
    return render_template('blobstoreutl.html', **data)


def upload_route(corp_org_key, branch_key, bk_id, blob_no=None):
    """
    Upload route handler (converted from BlobstoreUploadHandler)

    Migrated from: blobstore_handlers.BlobstoreUploadHandler (UploadHandler class)
    Original path: /upload/<corp_org_key>/<branch_key>/<bk_id>[/<blob_no>]

    GCS移行完了: Flask request.files + gcs_utils でアップロード
    """
    key_name1 = corp_org_key + "/" + branch_key + "/" + bk_id
    key_name2 = ""

    if blob_no is None:
        blobno_entity = blob_models.blobNo.get_or_insert(key_name1, blob_key_name=key_name1)
        blobnextno = blobno_entity.getNextNum()
        key_name2 = key_name1 + "/" + str(blobnextno)
    else:
        key_name2 = key_name1 + "/" + blob_no

    str1 = request.form.get("submit")
    if str1 == "削除":
        return delete_blob(key_name2, key_name1)

    blob = blob_models.Blob.get_or_insert(key_name2)
    if not blob.blobNo:
        blob.blobNo = blobnextno

    # GCS移行完了: Flask request.files + gcs_utils でアップロード
    uploaded_file = request.files.get('file')
    if uploaded_file:
        blob.filename = uploaded_file.filename
        # 拡張子を取得
        root, ext = os.path.splitext(uploaded_file.filename)
        ext = ext.lower().strip(".")
        blob.fileextension = ext

        # GCS object name を生成してアップロード
        object_name = gcs_utils.generate_object_name(
            corp_org_key, branch_key, bk_id, blob.blobNo, ext
        )
        gcs_utils.upload_file(
            uploaded_file.read(),
            object_name,
            content_type=uploaded_file.content_type
        )
        # GCS object name を blobKey に保存
        blob.blobKey = object_name
    else:
        if str1 == "登録":
            return redirect('/BlobstoreUtl/%s' % key_name1)
        if str1 == "追加":
            bloburl = request.form.get("bloburl")
            if bloburl and bloburl != "None":
                blob.bloburl = bloburl
            thumbnailurl = request.form.get("thumbnailurl")
            if thumbnailurl and thumbnailurl != "None":
                blob.thumbnailurl = thumbnailurl
            filename = request.form.get("filename")
            if filename and filename != "None":
                blob.filename = filename
            html = request.form.get("html")
            if html and html != "None":
                blob.html = html
            blobKey = request.form.get("blobKey")
            if blobKey and blobKey != "None":
                blob.blobKey = blobKey

    blob.blob_key_name = key_name2
    blob.CorpOrg_key = corp_org_key
    blob.Branch_Key = branch_key
    bk_id_decoded = unquote_plus(bk_id)
    key_name = blob.CorpOrg_key + "/" + blob.Branch_Key + "/" + bk_id_decoded
    bkdb = BKdata.get_or_insert(key_name, bkID=bk_id_decoded)

    shzicmi1 = "None"
    shzicmi2 = "None"
    ttmnmi = "None"
    if bkdb.shzicmi1:
        shzicmi1 = bkdb.shzicmi1
    if bkdb.shzicmi2:
        shzicmi2 = bkdb.shzicmi2
    if bkdb.ttmnmi:
        ttmnmi = bkdb.ttmnmi

    blob.bkID = bk_id_decoded
    blobkind = request.form.get("blobkind")
    if blobkind and blobkind != "None":
        blob.blobkind = blobkind
    else:
        blob.blobkind = None
    title = request.form.get("title")
    if title and title != "None":
        blob.title = title
    else:
        blob.title = None
    content = request.form.get("content")
    if content and content != "None":
        blob.content = content
        ext = blob.fileextension
        if not ext:
            root, ext = os.path.splitext(blob.filename)
            ext = ext.lower().strip(".")
            blob.fileextension = ext

        if ext in ["jpeg", "jpg", "png", "gif", "bmp"]:
            try:
                # GCS移行完了: 統一エンドポイントを使用
                blob.thumbnailurl = gcs_utils.get_thumbnail_url(blob.blobKey)
                blob.bloburl = gcs_utils.get_blob_url(blob.blobKey)
                blob.html = gcs_utils.generate_html(
                    blob.blobKey, blob.filename,
                    title=blob.title, content=blob.content, is_image=True
                )
            except Exception:
                blob.html = "error"
        else:
            # GCS移行完了: 統一エンドポイントを使用
            blob.bloburl = gcs_utils.get_blob_url(blob.blobKey)
            blob.html = gcs_utils.generate_html(blob.blobKey, blob.filename, is_image=False)
    else:
        blob.content = None

    media = request.form.get("media")
    if media and media != "None":
        blob.media = media
    else:
        blob.media = None
    pos = request.form.get("pos")
    if pos and pos != "None":
        blob.pos = pos
    else:
        blob.pos = None
    if shzicmi1 and shzicmi1 != "None":
        blob.shzicmi1 = shzicmi1
    else:
        blob.shzicmi1 = None
    if shzicmi2 and shzicmi2 != "None":
        blob.shzicmi2 = shzicmi2
    else:
        blob.shzicmi2 = None
    if ttmnmi and ttmnmi != "None":
        blob.ttmnmi = ttmnmi
    else:
        blob.ttmnmi = None

    blob.put()
    return redirect('/BlobstoreUtl/%s' % key_name1)


def delete_blob(key_name, path):
    """
    Delete blob helper function

    GCS移行完了: gcs_utils.delete_file() で削除
    """
    try:
        blob = blob_models.Blob.get_by_key_name(key_name)
        if blob:
            if blob.blobKey:
                query = blob_models.Blob.query(blob_models.Blob.blobKey == blob.blobKey)
                tempblobs2 = query.fetch()
                if len(tempblobs2) == 1:
                    # GCS からファイルを削除
                    try:
                        gcs_utils.delete_file(blob.blobKey)
                    except Exception:
                        pass  # ファイルが存在しない場合は無視
            blob.key.delete()
            return redirect('/BlobstoreUtl/%s' % path)
    except Exception as e:
        return repr(e) + '\n', 500


def serve_route(blob_key, filename=None):
    """
    Serve route handler (converted from BlobstoreDownloadHandler)

    Migrated from: blobstore_handlers.BlobstoreDownloadHandler (ServeHandler class)
    Original path: /serve/<blob_key>[/<filename>]

    GCS移行完了: Signed URL にリダイレクト
    """
    blob_key_decoded = unquote(blob_key)

    # GCS Signed URL にリダイレクト
    try:
        signed_url = gcs_utils.generate_signed_url(blob_key_decoded, expiration_minutes=5)
        return redirect(signed_url)
    except Exception as e:
        return f"File not found: {blob_key_decoded}", 404
