# -*- coding: utf-8 -*-

import os.path
from urllib.parse import unquote_plus, unquote
from flask import request, redirect, render_template
from google.cloud import storage
from google.cloud import ndb
import email.header
from application.models.bkdata import BKdata
import application.models.blob as blob_models


# ⚠️ SECURITY WARNING: Blobstore → GCS migration required
# This module uses deprecated Blobstore API which must be migrated to Cloud Storage (GCS)
# Key changes needed:
# - blobstore.create_upload_url() → GCS Signed URL
# - BlobstoreUploadHandler → Flask request.files + GCS client
# - get_serving_url() → GCS public URL / Signed URL
# - BlobReferenceProperty → String property (store GCS object name)
# - db.GqlQuery → ndb.Model.query() with filters


def blobstore_utl_route(corp_org_key, branch_key, bk_id):
    """
    BlobstoreUtl route handler (converted from webapp2.RequestHandler)

    Migrated from: webapp2.RequestHandler (BlobstoreUtlHandler class)
    Original path: /BlobstoreUtl/<corp_org_key>/<branch_key>/<bk_id>

    ⚠️ TODO: Complete Blobstore → GCS migration
    - Replace blobstore.create_upload_url() with GCS Signed URL generation
    - Update blob storage/retrieval to use GCS client
    - Replace get_serving_url() with GCS public/signed URLs
    """
    keypath = corp_org_key + "/" + branch_key + "/" + bk_id

    # ⚠️ TODO: Replace with GCS Signed URL generation
    # upload_url = blobstore.create_upload_url('/upload/' + keypath)
    upload_url = "/upload/" + keypath  # Placeholder - needs GCS implementation

    edit_url = "/upload/" + keypath
    multiupload_url = "/FileUploadFormHandler?CorpOrg_key=" + corp_org_key + "&Branch_Key=" + branch_key + "&bkID=" + bk_id

    # Blobstore に保存されているファイルを取得
    bk_id_decoded = unquote_plus(bk_id)

    # ⚠️ TODO: Replace GqlQuery with ndb.Model.query()
    # Old: db.GqlQuery("SELECT * FROM Blob WHERE ...")
    # New: Blob.query().filter(Blob.CorpOrg_key == corp_org_key, ...)
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
                        # ⚠️ TODO: Replace get_serving_url() with GCS public/signed URL
                        # blob.thumbnailurl = get_serving_url(blob.blobKey, size=100, crop=False)
                        # blob.bloburl = get_serving_url(blob.blobKey)
                        blob.thumbnailurl = f"/gcs-serve/{blob.blobKey}?size=100"  # Placeholder
                        blob.bloburl = f"/gcs-serve/{blob.blobKey}"  # Placeholder
                        blob.html = f'<a href="{blob.bloburl}" target="_blank"><img src="{blob.thumbnailurl}" title="{blob.filename}" /></a>'
                    except Exception:
                        pass
                else:
                    blob.bloburl = "/serve/" + blob.blobKey + "/" + blob.filename
                    blob.html = f'<a href="{blob.bloburl}">{blob.filename}</a>'
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
        # ⚠️ TODO: Replace GqlQuery with ndb.Model.query()
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
        # ⚠️ TODO: Replace GqlQuery with ndb.Model.query()
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

    ⚠️ TODO: Complete Blobstore → GCS migration
    - Replace self.get_uploads() with Flask request.files
    - Upload files to GCS instead of Blobstore
    - Store GCS object names instead of BlobKeys
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

    # ⚠️ TODO: Replace BlobstoreUploadHandler with Flask request.files + GCS upload
    # Old: blob_info = self.get_uploads('file')
    # New: file = request.files.get('file'); upload to GCS
    uploaded_file = request.files.get('file')
    if uploaded_file:
        # ⚠️ TODO: Upload to GCS and store object name
        # blob.filename = uploaded_file.filename
        # blob.blobKey = gcs_object_name  # Store GCS object name instead of BlobKey
        blob.filename = uploaded_file.filename
        # Placeholder - needs GCS implementation
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
                # ⚠️ TODO: Replace get_serving_url() with GCS public/signed URL
                blob.thumbnailurl = f"/gcs-serve/{blob.blobKey}?size=100"  # Placeholder
                blob.bloburl = f"/gcs-serve/{blob.blobKey}"  # Placeholder
                blob.html = f'<a href="{blob.bloburl}" target="_blank">'
                if blob.thumbnailurl:
                    blob.html += f'<img src="{blob.thumbnailurl}"'
                    if blob.title:
                        blob.html += f'title="{blob.title}'
                    if blob.content:
                        blob.html += ":" + blob.content
                    blob.html += '" />'
                blob.html += "</a>"
            except Exception:
                blob.html = "error"
        else:
            blob.bloburl = "/serve/" + blob.blobKey + "/" + blob.filename
            blob.html = f'<a href="{blob.bloburl}">{blob.filename}</a>'
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

    ⚠️ TODO: Update to delete from GCS instead of Blobstore
    """
    try:
        blob = blob_models.Blob.get_by_key_name(key_name)
        if blob:
            if blob.blobKey:
                # ⚠️ TODO: Replace GqlQuery with ndb.Model.query()
                query = blob_models.Blob.query(blob_models.Blob.blobKey == blob.blobKey)
                tempblobs2 = query.fetch()
                if len(tempblobs2) == 1:
                    # ⚠️ TODO: Delete from GCS instead of Blobstore
                    # blob_info = blobstore.get(blob.blobKey)
                    # if blob_info:
                    #     blob_info.delete()
                    pass  # Placeholder - needs GCS implementation
            blob.key.delete()
            return redirect('/BlobstoreUtl/%s' % path)
    except Exception as e:
        return repr(e) + '\n', 500


def serve_route(blob_key, filename=None):
    """
    Serve route handler (converted from BlobstoreDownloadHandler)

    Migrated from: blobstore_handlers.BlobstoreDownloadHandler (ServeHandler class)
    Original path: /serve/<blob_key>[/<filename>]

    ⚠️ TODO: Complete Blobstore → GCS migration
    - Replace BlobstoreDownloadHandler with GCS file serving
    - Use GCS signed URLs or direct streaming
    """
    blob_key_decoded = unquote(blob_key).split("/")[0]

    # ⚠️ TODO: Replace with GCS file serving
    # Old: blob_info = blobstore.BlobInfo.get(blob_key)
    #      self.send_blob(blob_info)
    # New: Fetch from GCS and stream to response

    # Placeholder - needs GCS implementation
    return "GCS file serving not yet implemented", 501
