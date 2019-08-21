from elasticsearch import Elasticsearch

es = Elasticsearch(Host='http://localhost',Port=9200)
es.cluster.health(wait_for_status='yellow', request_timeout=1)

