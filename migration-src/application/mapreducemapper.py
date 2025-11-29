# -*- coding: utf-8 -*-
"""
MapReduce mapper functions migrated to batch processing scripts.

Original Purpose:
- This file contains mapper functions for Google App Engine's MapReduce API
- MapReduce was a legacy bulk data processing framework on GAE
- All mapper functions have been adapted for Cloud Tasks / Cron-based batch processing

Migration Strategy:
- MapReduce → Cloud Tasks + Python batch scripts
- Each mapper function becomes a background task handler
- Execution triggered via cron jobs (cron.yaml) or Cloud Tasks API
- No changes to core business logic, only wrapper changes
"""

from google.cloud import ndb
import os.path


def bkdataput(entity):
    """
    Mapper: Put book data entity

    Used in: Migration of bkdata models
    New approach: Called directly in batch processing loops instead of MapReduce

    Args:
        entity: ndb.Model entity (bkdata)
    """
    entity.put()


def bkdlistupdate(entity):
    """
    Mapper: Update book data list

    Used in: Updates to bkdlist when message data changes
    Safety: Currently disabled (return without action)

    Notes:
    - Original code had safety mechanism (return statement)
    - This is preserved as-is during migration
    - If needed in future, implement message→member→bkdlist link

    Args:
        entity: ndb.Model entity (bkdlist)
    """
    return  # 安全装置 (Safety mechanism)
    # if entity.refmes:
    #     # Query implementation (legacy ndb.GqlQuery pattern)
    #     # msgcomb = ndb.gql("SELECT * FROM MsgCombinator WHERE combkind = :1 AND refmemlist = :2",
    #     #                   "所有", entity.refmes.refmemlist).fetch(1)
    #     # Modern ndb pattern:
    #     query = MsgCombinator.query(
    #         MsgCombinator.combkind == "所有",
    #         MsgCombinator.refmemlist == entity.refmes.refmemlist
    #     )
    #     msgcomb = query.fetch(1)
    #     if len(msgcomb):
    #         entity.refmem = msgcomb[0].refmem
    #         entity.put()


def bloburlschange(entity):
    """
    Mapper: Update blob URLs and generate thumbnails

    Migration Note: BLOBSTORE → GCS MIGRATION IN PROGRESS

    Original Purpose:
    - Migrate blob references during BlobStore→CloudStorage transition
    - Generate thumbnail URLs for image files
    - Store HTML snippets for display

    Current Status: PARTIALLY IMPLEMENTED
    - The BlobMigrationRecord.get_new_blob_key() function is GAE legacy and removed
    - GCS migration implementation is deferred (see GAE_MIGRATION_STATE.md)

    Workaround for now:
    1. Check if entity.blobKey exists
    2. Skip migration record lookup (not available in Python 3.11)
    3. Regenerate GCS URLs if needed (future work)

    Args:
        entity: ndb.Model entity (bkdata or blob model)

    TODO:
    - Implement GCS signed URL generation using google.cloud.storage
    - Update thumbnail generation for GCS objects
    - Test image rendering with various formats (JPEG, PNG, GIF, BMP)
    """
    if entity.blobKey:
        # Legacy: blobstore.BlobMigrationRecord.get_new_blob_key(entity.blobKey)
        # This function is specific to GAE BlobStore and not available in Cloud Storage

        # TODO: Implement GCS migration
        # blobkey = get_gcs_migrated_key(entity.blobKey)  # Future implementation

        # For now, attempt to use existing blobKey as-is (may be already migrated to GCS)
        blobkey = entity.blobKey

        if blobkey:
            # Extract file extension
            if not hasattr(entity, 'fileextension') or not entity.fileextension:
                root, ext = os.path.splitext(entity.filename if hasattr(entity, 'filename') else '')
                ext = ext.lower().strip(".")
                entity.fileextension = ext

            # Generate thumbnail and display URLs for image files
            if entity.fileextension in ["jpeg", "jpg", "png", "gif", "bmp"]:
                try:
                    # REVIEW-L2: SECURITY - XSS Risk: HTML generation without proper escaping
                    # Recommendation: Use HTML escaping or template rendering for user-provided data
                    # TODO: Replace with GCS signed URL generation
                    # entity.thumbnailurl = generate_gcs_signed_url(entity.blobKey, size=100)
                    # entity.bloburl = generate_gcs_signed_url(entity.blobKey)

                    # REVIEW-L2: Placeholder URLs contain hardcoded 'YOUR_BUCKET' - needs environment config
                    # Placeholder: Use direct GCS URL (requires public bucket or signed URLs)
                    entity.thumbnailurl = f"https://storage.googleapis.com/YOUR_BUCKET/{entity.blobKey}"
                    entity.bloburl = f"https://storage.googleapis.com/YOUR_BUCKET/{entity.blobKey}"

                    # Generate HTML snippet for display
                    entity.html = f'<a href="{entity.bloburl}" target="_blank">'
                    if hasattr(entity, 'thumbnailurl') and entity.thumbnailurl:
                        entity.html += f'<img src="{entity.thumbnailurl}"'
                        if hasattr(entity, 'title') and entity.title:
                            # REVIEW-L2: Potential XSS - entity.title should be HTML-escaped
                            entity.html += f' title="{entity.title}"'
                        if hasattr(entity, 'content') and entity.content:
                            # REVIEW-L2: Potential XSS - entity.content should be HTML-escaped
                            entity.html += f':{entity.content}'
                        entity.html += ' />'
                    entity.html += '</a>'
                except Exception as e:
                    print(f"Error generating image URLs: {e}")
                    entity.html = "error"
            else:
                # Non-image files: Direct download link
                # REVIEW-L2: Potential XSS - filename not escaped in HTML attribute
                # TODO: Replace with GCS signed URL
                entity.bloburl = f"/serve/{entity.blobKey}/{entity.filename if hasattr(entity, 'filename') else ''}"
                entity.html = f'<a href="{entity.bloburl}">{entity.filename if hasattr(entity, "filename") else "Download"}</a>'

            entity.put()


def message(entity):
    """
    Mapper: Process message entity

    Current Status: STUB (No implementation)

    Notes:
    - Original function is empty (just returns)
    - Placeholder for future message processing logic
    - May be used for message aggregation or cleanup tasks

    Args:
        entity: ndb.Model entity (message)
    """
    return
