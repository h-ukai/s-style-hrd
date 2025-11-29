# -*- coding: utf-8 -*-

from google.cloud import tasks_v2
from google.api_core.gapic_v1 import client_info as grpc_client_info
import json
import os

"""
changetantoWorker と changetantotask は循環参照を避けるため messageManager の中に記述
"""

# Cloud Tasks client initialization
def _get_tasks_client():
    return tasks_v2.CloudTasksClient()

class chagetanto:
    #https://localhost:8080/tasks/changetantoWorker?corp_name=s-style&tantoID=3&oldtantoID=1
    @classmethod
    def tantoallchange(cls, corp, tantoID, oldtantoID):
        try:
            client = _get_tasks_client()
            project = os.environ.get('GCP_PROJECT')
            queue = 'mintask'
            location = 'asia-northeast1'  # Adjust based on your region

            parent = client.queue_path(project, location, queue)

            task = {
                'http_request': {
                    'http_method': tasks_v2.HttpMethod.POST,
                    'url': 'https://{}.appspot.com/tasks/changetantoWorker'.format(project),
                    'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
                    'body': 'corp_name={}&tantoID={}&oldtantoID={}'.format(corp, tantoID, oldtantoID).encode(),
                }
            }

            response = client.create_task(request={'parent': parent, 'task': task})
            return response
        except Exception as e:
            # Log error and re-raise
            print(f'Error creating task for tantoallchange: {str(e)}')
            raise

    #https://localhost:8080/tasks/changetantotask?corp_name=s-style&mamberID=2&tantoID=3&oldtantoID=1
    @classmethod
    def tantochange(cls, corp, memberID, tantoID, oldtantoID):
        try:
            client = _get_tasks_client()
            project = os.environ.get('GCP_PROJECT')
            queue = 'mintask'
            location = 'asia-northeast1'  # Adjust based on your region

            parent = client.queue_path(project, location, queue)

            task = {
                'http_request': {
                    'http_method': tasks_v2.HttpMethod.POST,
                    'url': 'https://{}.appspot.com/tasks/changetantotask'.format(project),
                    'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
                    'body': 'corp_name={}&memberID={}&tantoID={}&oldtantoID={}'.format(
                        corp, memberID, tantoID, oldtantoID
                    ).encode(),
                }
            }

            response = client.create_task(request={'parent': parent, 'task': task})
            return response
        except Exception as e:
            # Log error and re-raise
            print(f'Error creating task for tantochange: {str(e)}')
            raise
