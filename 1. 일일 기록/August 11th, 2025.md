---
title: "August 11th, 2025"
created: 2025-08-11 09:08:32
updated: 2025-08-11 12:28:00
---
  * 오늘 RAG 시스템 만들까.
    * 전에 skt map 1.5 프로젝트 하면서 만든 PDFConverter.py 이용할 것
    * 일단 가장 간단한 것부터.
  * 09:55 자료 조사 중 teddynote의 document parser 동영상 시청.
    * 의문점: 왜 document parser가 필요한가? 결국 왜 RAG가 필요한가?
      * 비용과 토큰 제한
      * 해결
        * 전처리 + 의미 단위 쪼개기 ->  embedding 처리해서 vectorDB 저장
        * embedding vector 검색 가능
        * metadata(제목, 저자, 날짜, 구역)도 함께 저장 -> 보다 정확한 검색 가능.
    * 비교
      * 질문할 때마다 내 지식 자료를 모두 올리기
      * RAG with parsers: 질문과 관련 있는 정보만 찾아주는 사서가 있다.
    * 메타인지적 결론
      * RAG는 LLM 능력 발전과 별개이며 LLM을 보조하는 지식 검색 수단으로 따로 발전할 것이다.
      * 문서 구문 해석기는 RAG 시스템 구축하는 데 있어서 필수다.
      * 더 자세한 내용을 파고드는 것은 여기서는 별 의미 없을 것 같다. 일단 문서 구문 해석기가 왜 RAG 시스템을 구축하는데 꼭 필요하다는 정도 인식을 가진 것으로 충분할 듯.
  * [[AI#^G-1FDuLTG|RAG 시스템 개발]] 