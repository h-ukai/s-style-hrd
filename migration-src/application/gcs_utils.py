# -*- coding: utf-8 -*-
"""
GCS ユーティリティ関数

Blobstore → GCS 移行のための統一ユーティリティ
統一仕様: BLOBSTORE-GCS-UNIFIED-SPEC.md
"""

import os
from google.cloud import storage
from google.auth import default, compute_engine
from google.auth.transport import requests
from datetime import timedelta

# 環境変数から取得
BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME', 's-style-hrd-blobs')
GCP_PROJECT = os.environ.get('GCP_PROJECT', 's-style-hrd')


def get_gcs_client():
    """GCS クライアントを取得"""
    return storage.Client()


def generate_object_name(corp_org_key: str, branch_key: str, bk_id: str,
                         blob_no: int, extension: str) -> str:
    """
    統一フォーマットの GCS object name を生成

    フォーマット: {corp_org_key}/{branch_key}/{bk_id}/{blob_no}.{extension}

    Args:
        corp_org_key: 組織キー
        branch_key: 支店キー
        bk_id: 物件ID
        blob_no: Blob連番
        extension: ファイル拡張子

    Returns:
        str: GCS object name
    """
    ext = extension.lower().lstrip('.')
    return f"{corp_org_key}/{branch_key}/{bk_id}/{blob_no}.{ext}"


def upload_file(file_data: bytes, object_name: str, content_type: str = None) -> str:
    """
    ファイルを GCS にアップロード

    Args:
        file_data: ファイルデータ（bytes）
        object_name: GCS object name
        content_type: Content-Type（省略時は自動判定）

    Returns:
        str: アップロードした object_name
    """
    client = get_gcs_client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(object_name)
    blob.upload_from_string(file_data, content_type=content_type)
    return object_name


def download_file(object_name: str) -> bytes:
    """
    GCS からファイルをダウンロード

    Args:
        object_name: GCS object name

    Returns:
        bytes: ファイルデータ
    """
    client = get_gcs_client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(object_name)
    return blob.download_as_bytes()


def delete_file(object_name: str) -> bool:
    """
    GCS からファイルを削除

    Args:
        object_name: GCS object name

    Returns:
        bool: 削除成功
    """
    client = get_gcs_client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(object_name)
    blob.delete()
    return True


def file_exists(object_name: str) -> bool:
    """
    GCS にファイルが存在するか確認

    Args:
        object_name: GCS object name

    Returns:
        bool: 存在する場合 True
    """
    client = get_gcs_client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(object_name)
    return blob.exists()


def generate_signed_url(object_name: str, expiration_minutes: int = 60,
                        method: str = 'GET') -> str:
    """
    Signed URL を生成

    GAEではIAM APIを使用して署名付きURLを生成

    Args:
        object_name: GCS object name
        expiration_minutes: 有効期限（分）
        method: HTTP メソッド ('GET' or 'PUT')

    Returns:
        str: Signed URL
    """
    # デフォルトの認証情報を取得
    credentials, project = default()

    # 認証情報をリフレッシュ
    auth_request = requests.Request()
    credentials.refresh(auth_request)

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(object_name)

    # GAEではIAM API経由で署名
    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=expiration_minutes),
        method=method,
        service_account_email=credentials.service_account_email,
        access_token=credentials.token,
    )
    return url


def generate_upload_signed_url(object_name: str, content_type: str,
                               expiration_minutes: int = 15) -> str:
    """
    アップロード用 Signed URL を生成

    Args:
        object_name: GCS object name
        content_type: Content-Type
        expiration_minutes: 有効期限（分）

    Returns:
        str: アップロード用 Signed URL
    """
    # デフォルトの認証情報を取得
    credentials, project = default()

    # 認証情報をリフレッシュ
    auth_request = requests.Request()
    credentials.refresh(auth_request)

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(object_name)

    # GAEではIAM API経由で署名
    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=expiration_minutes),
        method='PUT',
        content_type=content_type,
        service_account_email=credentials.service_account_email,
        access_token=credentials.token,
    )
    return url


def get_blob_url(object_name: str) -> str:
    """
    統一エンドポイントの bloburl を生成

    Args:
        object_name: GCS object name

    Returns:
        str: "/blob/{object_name}"
    """
    return f"/blob/{object_name}"


def get_thumbnail_url(object_name: str) -> str:
    """
    統一エンドポイントの thumbnailurl を生成

    Args:
        object_name: GCS object name

    Returns:
        str: "/blob/{object_name}/thumbnail"
    """
    return f"/blob/{object_name}/thumbnail"


def generate_html(object_name: str, filename: str, title: str = None,
                  content: str = None, is_image: bool = False) -> str:
    """
    html フィールド用の HTML を生成

    Args:
        object_name: GCS object name
        filename: 元ファイル名
        title: タイトル（省略可）
        content: コンテンツ（省略可）
        is_image: 画像ファイルかどうか

    Returns:
        str: HTML スニペット
    """
    from html import escape

    bloburl = get_blob_url(object_name)

    if is_image:
        thumbnailurl = get_thumbnail_url(object_name)
        title_attr = ""
        if title:
            title_attr = escape(title)
            if content:
                title_attr += ":" + escape(content)
        if title_attr:
            return f'<a href="{bloburl}" target="_blank"><img src="{thumbnailurl}" title="{title_attr}" /></a>'
        else:
            return f'<a href="{bloburl}" target="_blank"><img src="{thumbnailurl}" /></a>'
    else:
        escaped_filename = escape(filename) if filename else "Download"
        return f'<a href="{bloburl}" download="{escaped_filename}">{escaped_filename}</a>'


def is_image_file(extension: str) -> bool:
    """
    画像ファイルかどうかを判定

    Args:
        extension: ファイル拡張子

    Returns:
        bool: 画像ファイルの場合 True
    """
    if not extension:
        return False
    return extension.lower().lstrip('.') in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']


def get_content_type(extension: str) -> str:
    """
    拡張子から Content-Type を取得

    Args:
        extension: ファイル拡張子

    Returns:
        str: Content-Type
    """
    ext = extension.lower().lstrip('.')
    content_types = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'bmp': 'image/bmp',
        'webp': 'image/webp',
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xls': 'application/vnd.ms-excel',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'txt': 'text/plain',
        'csv': 'text/csv',
    }
    return content_types.get(ext, 'application/octet-stream')
