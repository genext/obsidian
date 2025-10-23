---
title: "August 2nd, 2024"
created: 2024-08-02 00:00:09
updated: 2024-08-02 18:02:11
---
  * 06:46 출근
  * 오늘 할 일
    * 업무 메일 확인
    * 의뢰기관, 사용처 관리 소스 분석 및 구조 파악.
    * 위에서 분석한 구조대로 pbm, issue, sc 맞물려서 돌아가도록
  * 의뢰기관 관리 소스 분석 시작
    * 모델 세 개
      * TbVcInstCstmrMastrEntity
      * TbVcInstCstmrMastr
      * TbVcInstCstmrUpdate
      * 기본적으로 Cstmr 테이블은 고객 자체 정보만 있고 계정 정보는 TB_ACNUT_MASTR에 있다.
      * 일단 구조가 이상해서 대표님께 문의한 결과 기존 구조가 이상하게 되었다는 것을 인정하고 다시 작업하기로 함.
  * 그래도 기존 소스 다른 부분을 보고 어떻게 구성했는지 파악 필요.
    * 모델
      * /src/main/java/kr.or/cbdc/domain/main/model/ewa/cstr.mastr
        * TbCstmrMastrEntity: TB_CSTMR_MASTR
          * 상속 관계 TbCstmrMastr extends TbCstmrMastrEntity 이것도 이상하다.
  * 9:21 [[디지털 바우처 회의록]] [[Roam/genext-2025-10-05-02-18-30/디지털 바우처 회의록#^gjlGti51t|2024. 8. 2. 금.]]
  * 10:38 일단 ERD와 테이블 정의서 수정해서 신은지 책임에게 알림. 알려달라고 했으면 잊지 말고 바로 알려주어야 한다.
  * ((-Cl2o5KMT))
  * 12:55 CDATA 의 용도
    * ### Purpose of CDATA Sections
      * **Character Data Handling**:
        * CDATA stands for "Character Data," and it's used to wrap sections of text in XML that should not be parsed by the XML parser.
        * It allows you to include special characters (like <, >, and &) without being mistaken for XML markup.
      * **SQL Queries**:
        * In the context of MyBatis, CDATA sections can be used to write raw SQL that might include special characters or keywords that could interfere with XML parsing.
    * ### Conclusion
      * **Optional Use**: CDATA is not necessary for SQL to function correctly unless you have special characters or want to avoid potential parsing conflicts.
      * **Readability and Consistency**: Developers may choose to use CDATA to clearly separate SQL logic from XML structure, especially in larger or more complex queries.
  * 13:22 바우처 관리 pbm 조회 완료
    * 참가기관: vouchId
    * 의뢰기관: prtCmpnyId, vouchId
  * 대표님 작업한 것 중 의뢰기관 관리 CRUD 중 CRU는 끝내고 D 시작
    * 에러 발생
      * ```plain text
Caused by: com.fasterxml.jackson.core.JsonParseException: Unexpected character ('}' (code 125)): was expecting double-quote to start field name```
  * 15:56 스마트 계약 생성 시 vouch_id를 인자로 넘겨주면 내부에서 생성된 coinId를 TB_VOUCH_MASTR에 저장하도록.
  * 16:44 스마트계약 신청 완료 후 coinId를 TB_VOUCH_MASTR에 저장 완료.
  * 의뢰기관 관리 분석
    * 대표님이 application/domain 구분할 때 application은 다른 테이블과 조인하거나 하는 것들을 저장하고 domain에는 해당 도메인 테이블 자체 CRUD 관련된 것만 저장한다고 했는데 여기는 반대로 했다.
  * 18:02 오늘 작업 커밋하고 퇴근.