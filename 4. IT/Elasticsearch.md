---
title: "Elasticsearch"
created: 2023-09-27 06:12:03
updated: 2024-03-11 18:14:07
---
  * 줄여서 es, 저장 데이터는 몽고와 유사
  * 주 사용처
    * 복잡한 검색
      * 구문 검색, 자동 완성 등
    * 분석
      * 실시간으로 데이터를 모아서 분석 for BI(business intelligence)
    * 보안, 비정상 탐지
      * 로그 데이터로 시스템 모니터링 또는 비정상적인 양상을 탐지
    * APM
    * Content search

  * index, document가 DB의 테이블, 레코드에 대응된다.
  * 개괄 코드
    * ```python
from elasticsearch import Elasticsearch

# Connect to Elasticsearch
es = Elasticsearch()

# Create an index (similar to a database in traditional terms)
index_name = 'my_index'

# Check if the index exists, and if not, create it
if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name)

# Add a document to the index
document = {
    'title': 'Sample Document',
    'content': 'This is a sample document to test Elasticsearch.',
}

# Add the document to the index
response = es.index(index=index_name, body=document)

# Get the document by its id
doc_id = response['_id']
result = es.get(index=index_name, id=doc_id)

print("Retrieved document:")
print(result['_source'])

# Search for documents in the index
query = {
    "query": {
        "match": {
            "content": "sample"
        }
    }
}

search_results = es.search(index=index_name, body=query)

print("Search results:")
for hit in search_results['hits']['hits']:
    print(hit['_source'])

# Delete the index (cleanup)
es.indices.delete(index=index_name)
```