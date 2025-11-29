# -*- coding: utf-8 -*-

from google.cloud import ndb
from google.cloud import storage
from flask import request, redirect, render_template, Response
from urllib.parse import unquote_plus
import application.models.blob as blob_models
from application.models.bkdata import BKdata
import email.header
import os


# ⚠️ SECURITY WARNING: Blobstore → GCS migration required
# This module uses deprecated Blobstore API which must be migrated to Cloud Storage (GCS)
# See blobstoreutl.py for detailed migration notes


class FileInfo(ndb.Model):
    """
    FileInfo model (migrated from db.Model)

    ⚠️ TODO: Update BlobReferenceProperty → String property (store GCS object name)
    """
    blob = ndb.StringProperty(required=True)  # Store GCS object name instead of BlobKey
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

    ⚠️ TODO: Complete Blobstore → GCS migration
    - Replace self.get_uploads() with Flask request.files
    - Upload files to GCS instead of Blobstore
    - Store GCS object names instead of BlobKeys
    """
    uploaded_file = request.files.get('file')
    if not uploaded_file:
        return "No file uploaded", 404

    # ⚠️ TODO: Upload to GCS and get object name
    # Old: blob_info = self.get_uploads('file')[0]
    #      blob_info = blobstore.BlobInfo.get(blob_info.key())
    #      filename = blob_info.filename
    # New: Upload to GCS, store object name
    filename = uploaded_file.filename
    # Placeholder - needs GCS implementation
    blobkey = "gcs-placeholder-key"  # TODO: Replace with GCS object name

    corp_org_key = request.form.get("CorpOrg_key")
    branch_key = request.form.get("Branch_Key")
    bk_id = request.form.get("bkID")

    lobdbkey = setblobdb(blobkey, filename, corp_org_key, branch_key, bk_id)
    return redirect("/FileUploadFormHandler/file/%d/success" % lobdbkey)


def setblobdb(blobkey, filename, corp_org_key, branch_key, bk_id):
    """
    Helper function to save blob metadata to Datastore

    ⚠️ TODO: Update to store GCS object names instead of BlobKeys
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

    ⚠️ TODO: Update to delete from GCS instead of Blobstore
    """
    key = request.args.get('key') or request.form.get('key')

    # ⚠️ TODO: Replace GqlQuery with ndb.Model.query()
    query = blob_models.Blob.query(blob_models.Blob.blobKey == key)
    blobs = query.fetch()

    if len(blobs) == 1:
        # ⚠️ TODO: Delete from GCS instead of Blobstore
        # Old: blobstore.delete(key or '')
        pass  # Placeholder - needs GCS implementation

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

    ⚠️ TODO: Complete Blobstore → GCS migration
    - Replace BlobstoreDownloadHandler with GCS file serving
    - Use GCS signed URLs or direct streaming
    """
    file_info = FileInfo.get_by_id(int(file_id))
    if not file_info or not file_info.blob:
        return "File not found", 404

    # ⚠️ TODO: Replace with GCS file serving
    # Old: self.send_blob(file_info.blob, save_as=True)
    # New: Fetch from GCS and stream to response with Content-Disposition header

    # Placeholder - needs GCS implementation
    return "GCS file download not yet implemented", 501


def generate_upload_url_route():
    """
    GenerateUploadUrl route handler (converted from webapp2.RequestHandler)

    Migrated from: webapp2.RequestHandler (GenerateUploadUrlHandler class)
    Original path: /FileUploadFormHandler/generate_upload_url

    ⚠️ TODO: Complete Blobstore → GCS migration
    - Replace blobstore.create_upload_url() with GCS Signed URL generation
    """
    urlstr = ""
    corp_org_key = request.args.get("CorpOrg_key")
    urlstr += "CorpOrg_key=" + corp_org_key
    branch_key = request.args.get("Branch_Key")
    urlstr += "&Branch_Key=" + branch_key
    bk_id = request.args.get("bkID")
    urlstr += "&bkID=" + bk_id

    # ⚠️ TODO: Replace with GCS Signed URL generation
    # Old: blobstore.create_upload_url('/FileUploadFormHandler/upload?' + urlstr)
    # New: Generate GCS Signed URL for upload
    upload_url = '/FileUploadFormHandler/upload?' + urlstr  # Placeholder

    response = Response(upload_url)
    response.headers['Content-Type'] = 'text/plain'
    return response
