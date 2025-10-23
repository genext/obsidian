---
title: "SKT MNO AI Platform"
created: 2025-06-25 07:40:02
updated: 2025-08-04 19:12:35
---

## 얻어야 할 것

### 구조 설계 측면

#### 데이터 처리 전반(전처리, 파이프라인, embedding, vectorDB, search)

이번 프로젝트에서 나는 pdf를 markdown으로 변환할 때 pymupdf4llm을 김희민 매니저가 일부 수정(소제목 추출)한 것에 보태서 중첩표가 나왔을 때 부모표와 자식표 관계를 markdown에 표시하도록 함.

### AI 관련 개발 측면

#### 깊이 있는 파이썬 데코레이터 활용

decorator 활용할 일이 많지 않았다. 그냥 pdf변환 과정과 markdown에서 문자열 비교하여 전처리하는 것에 집중하다가 허무하게 한 달만에 퇴출당했다.

#### 성능 최적화 관련 지식

#### context engineering을 내면화

### 통찰력

#### 데이터 처리 관련 context engineering 설계 방법

결국 AI가 쉽게 읽을 수 있는 것은 markdown인가?

## 사전 준비

### 요건

#### RAG

**문서 종류(txt, pdf, binary, html, db)**

**실시간/일괄 처리**

**문서가 변경될 경우, 어떻게 반영?**
- 기존에 같은 문서가 있는지 확인 필요
- 문서 형식도 같이 바뀌면 데이터 전처리가 유연하게 작동하게끔.
  - 문서와 embedding 사이 인터페이스는 모두 텍스트로 한다?

#### 최소 응답 시간, 최대 처리량, 최대 RAG 크기(token limit, context window 크기 등)

### 시스템

**흐름**: data source -> (text spliter to chunks of text) -> preprocessing -> embedding -> vector DB -> 적절한 context 제공 기반을 마련.

**embedding model**

**vectorDB**: pine cone, faiss, mongoDB?

### 개발 언어: Python

[파이썬 학습 동영상](https://www.youtube.com/@pixegami)

### 프레임웍: FastAPI

### 구현 방법 조사

**구글 검색 키워드**: preprocessing, embedding, vector db, rag pipeline

**[Building and Optimizing RAG Pipelines](https://www.youtube.com/watch?v=PazRMY8bo3U)**
- ML engineer가 강의한 것으로 기본적인 내용만 확인했고 추가 개선 작업 내용은 보지 않고 중단.

**위 파이썬 학습 중 [RAG](https://www.youtube.com/@pixegami) 관련 with langchain**
- https://github.com/pixegami/rag-tutorial-v2

### 테스트

가상 질문, 질문을 처리하기에 적절한 RAG, 적절한 대답을 여러 개 담은 테스트 데이터집합을 만들어야 한다 by synthetic test set generator? -> 전처리에 예상보다 시간을 소모한데다 중간에 퇴출 요청을 받아 혼란스러워서 작업을 하지도 못했다.

### python function 기본 형식에서 "->"이 의미하는 것?

예상대로 함수 리턴값 타입을 의미하지만 파이썬 인터프리터는 타입을 강제하지 않음. **pydantic**을 쓰면 실행 시 타입을 강제함.

### 어떤 문서든, 어떤 형식으로 된 데이터든, 전처리 하기 전에 UTF-8 텍스트 문자로 변환하고 묶음(chunk)으로 분할한다.

--> pdf 문서를 아예 구역단위로 쪼개서 주는 방향이 되어서 chunking 자체가 필요없어짐.

### vector DB에 저장한 후에는 사용자가 질문한 내용과 가장 관련이 있는 것을 찾는 로직이 따로 필요하지 않나?

--> 이건 retriever 담당. rag-embedding 모듈이 담당.

### 파이썬에서 *init*.py의 역할

- 그 파일이 속한 디렉토리가 package임을 의미.
- 패키지 참조할 때 필요한 초기화 조건 설정 가능.
- 해당 패키지 내 파일들에 있는 함수를 선택적으로 노출할 수 있다.

### RAG를 이용한 결과가 원하는 대로 나왔는지 검증(intervention)하는 방법은?

- retrieval evaluation
- generation evaluation

## 진행 기록

### async DB 파악

어플리케이션 쓰레드가 DB와 연결된 connection을 async 방식으로 사용할 수 있다.

### pdf에 있는 표를 parsing 잘하는지 빨리 확인해야 한다.

-> pymupdf나 pymupdf4llm 둘 다 중첩표를 구분한다. 하지만 부모표, 자식표 관계를 표시하지 못한다.

### regression test

RAG를 이용한 결과가 원하는 대로 나왔는지 검증하는 방법을 참고하여 테스트 설계

### 2025-07-01 (화)

데이터 전처리가 중요하다. 특히 표로 된 것을 어떻게 잘 묶어서 처리하느냐에 따라 적절한 context 생성 여부가 결정된다.

### 2025-07-02 (수)

- 서창수 매니저 만남
- 권부장과 회의

### 2025-07-03 (목)

PC 설정

### 2025-07-04 (금)

- Context engineering 방향성 확립
- Mochi 카드 첫 사용

### 2025-07-07 (월)

- Confluence 문서 검토
- 변환 포맷 테스트 결과 markdown이 가장 우수
- PDF를 markdown으로 변환 후 vectorDB와 RDB에 저장하기로 결정

### 2025-07-08 (화)

- 사업 계획서 검토
- 개발 환경 설정 시작

### 2025-07-09 (수)

- 아키텍처 논리 구성도 파악
- code-server 접속 및 git 설정
- data pipeline 설계

### 2025-07-10 (목)

PDF → markdown 변환 프로그램을 Claude와 문답으로 작성했으나 Python package 설치 문제로 실행 불가

### 2025-07-11 (금)

패키지 설치 완료 후 프로그램 실행 및 분석 시작

## 총정리

### 주요 성과

- **PDF 중첩 표 처리 개선**: 김희민 매니저가 수정한 pymupdf4llm을 보완하여 부모표-자식표 관계를 markdown에 명시적으로 표시
- **전처리 로직 강화**: 자식표를 참조하는 문장을 자동으로 처리하는 기능 구현
- **PDFConverter 클래스 설계**: PDF 변환과 전처리를 통합 관리하는 클래스 구현
- **확장성 고려**: 향후 다른 PDF API 사용 시 쉽게 교체 가능하도록 공통 인터페이스와 factory 패턴 설계 시도 (프로젝트 상황으로 일부만 구현)

### 개선점

**효율적인 코드 분석 도구 활용 부족**
- pymupdf4llm을 수작업으로 분석하여 시간 낭비
- Claude Code를 활용한 빠른 코드 파악 필요

**변경사항 분석 프로세스 미흡**
- 김희민 매니저의 수정 내용을 diff 도구 없이 분석
- diff + AI 분석을 통한 효율적인 코드 리뷰 필요

**문제 해결 접근법 개선 필요**
- Markdown 전처리 과정에서 오류 원인 파악이 지연됨
- 문제 정의와 원인 분석을 먼저 수행한 후 Claude Code 활용 필요
- 체계적인 디버깅 프로세스 확립 필요
