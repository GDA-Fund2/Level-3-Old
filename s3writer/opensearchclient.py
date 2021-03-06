import os
import datetime
from opensearchpy import OpenSearch
from dotenv import load_dotenv
from osbot_utils.utils.Http import GET_json, GET
from base64 import b64encode

class OpenSearchClient(object):

    def __init__(self):
        load_dotenv(override=True)
        self.host = os.getenv("OPENSEARCH_HOST", '')
        self.port = int(os.getenv("OPENSEARCH_PORT", 443))
        self.schema = 'https'
        user = os.getenv("OPENSEARCH_USER", '')
        psw  = os.getenv("OPENSEARCH_PASSWORD", '')
        authstr   = (f'{user}:{psw}').encode("ascii")
        userAndPass = b64encode(authstr).decode("ascii")
        self.headers = { 'Authorization' : 'Basic %s' %  userAndPass }

        # Create the client with SSL/TLS enabled, but hostname verification disabled.
        self.client = OpenSearch(
            hosts = [{'host': self.host, 'port': self.port}],
            http_compress = True, # enables gzip compression for request bodies
            http_auth = (user, psw),
            use_ssl = True,
            verify_certs = False,
            ssl_assert_hostname = False,
            ssl_show_warn = False,
        )

        self.enabled = False
        self.server_online()

        if not self.enabled:
            print('OpenSearch client failed to connect')

    def server_online(self):
        elastic_url = f'{self.schema}://{self.host}:{self.port}'
        try:
            response = GET_json(elastic_url, headers=self.headers).get('tagline')
            assert response == "The OpenSearch Project: https://opensearch.org/"
            self.enabled = True
            return True
        except:
            return False

    def delete_index(self, index_name):
        response = None

        if not self.enabled:
            return None

        try:
            response = self.client.indices.delete(index_name, request_timeout=20)
        except Exception as ex:
            print(ex)
            return None

        return response

class Index(object):
    def __init__(self, client:OpenSearchClient, prefix:str, exchange:str, topic:str, taskid:str ):
        self.osclient = client
        self.taskid = taskid
        self.name = f'{prefix}-{taskid}'
        self.id = 0
        self.index_body = {
            'settings': {
                'index': {
                'number_of_shards': 1
                }
            }
        }
        self.exchage = exchange
        self.topic = topic

    def delete(self):
        return self.osclient.delete_index(f'{self.name}*')

    def create(self):
        response = None

        if not self.osclient.enabled:
            return None

        self.delete()

        try:
            response = self.osclient.client.indices.create(self.name, body=self.index_body, request_timeout=60)
        except Exception as ex:
            print(ex)
            return None

        return response

    def add_document(self, document, timestamp = None):
        response = None

        if not self.osclient.enabled:
            return None

        self.id += 1

        try:
            if not timestamp:
                timestamp = datetime.datetime.utcnow()

            data = {
                "timestamp" : timestamp.isoformat(),
                "exchange"  : self.exchage,
                "topic"     : self.topic,
                "taskid"    : self.taskid,
                "indexid"   : f'{self.exchage}-{self.topic}-{self.taskid}',
                "document"  : document
            }
            response = self.osclient.client.index(
                index = f'{self.name}-{timestamp.year}-{timestamp.month}-{timestamp.day}',
                body = data,
                id = self.id,
                refresh = True,
                request_timeout=20
            )
        except Exception as ex:
            print(ex)
            return None

        return response

    def run_query(self, query):
        response = None
        try:
            response = self.osclient.client.search(
                    body = query,
                    index = self.name,
                    request_timeout=20
                )
        except Exception as ex:
            print(ex)

        return response

    def delete_document(self, id):
        response = None
        try:
            response = self.osclient.client.delete(
                    index = self.name,
                    id = id,
                    request_timeout=20
                )
        except Exception as ex:
            print(ex)
        return response

def delete_indexes(list):
    osclient = OpenSearchClient()
    for item in list:
        print(f'Deleting {item}')
        print(osclient.delete_index(item))

def test_it():
    print('\nConnecting:')
    osclient = OpenSearchClient()

    print('\nCreating index:')
    test_index = Index(osclient,'python-test-index','none','none','none')
    test_index.create()

    # Add a document to the index.
    document = {
    'title': 'Moneyball',
    'director': 'Bennett Miller',
    'year': '2011'
    }

    print('\nAdding document:')
    print(test_index.add_document(document))

    # Search for the document.
    q = 'miller'
    query = {
        'size': 5,
        'query': {
            'multi_match': {
            'query': q,
            'fields': ['title^2', 'director']
            }
        }
    }

    print('\nSearch results:')
    print(test_index.run_query(query))

    print('\nDeleting document:')
    print(test_index.delete_document(test_index.id))

    print('\nDeleting index:')
    print(test_index.delete())

    osclient.delete_index("")

if __name__ == '__main__':
    # test_it()

    # list = ['*-2021-12-5']
    list = ['price-*','sysinfo-*']

    delete_indexes(list=list)