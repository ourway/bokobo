from elasticsearch import Elasticsearch

es = Elasticsearch(Host='http://localhost',Port=9200)


#es.index(index='db',doc_type='table',id=2,body=doc2)
#es.get(index='sent',doc_type='nanas',id=2)
#es.search(index='db',body={'from':0,'size':2,'query':{'match':{'sent'='SUNNY'}}})

es.search(index='db', body={'from': 0, 'size': 4, 'query': {
    'bool': {'should': {'match': {'sent': 'nasim'}}, 'must_not': {'match': {'sent': 'sunny'}}}}})


es.search(index='db', body={'from': 0, 'size': 4, 'query':  {'regexp': {'sent': 'coo.*'}}})

es.indices.get_mapping(index='db', doc_type='table')

