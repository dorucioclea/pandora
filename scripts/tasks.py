import os
import requests
from celery import Celery
from elasticsearch import Elasticsearch
from worker import app
import api

TIKA_HOST = os.getenv('TIKA_HOST', 'http://localhost:4219')


# just for testing purposes
@app.task
def add(x, y):
    return x + y


# TODO update existing doc found by url
@app.task
def index_file(url):
    print(f'indexing {url}')
    # parse file by given URL
    resp = requests.get(url=TIKA_HOST + '/api/tika/parse', params={'url': url})
    resp.raise_for_status()
    result = resp.json()

    # TODO find existing doc by url

    doc = result['metadata']
    doc['source_url'] = url
    doc['text'] = result['text']

    api.login("system", os.getenv("SYSTEM_PWD"))
    return api.post('/api/data/document', doc)