---
title: "August 6th, 2024"
created: 2024-08-06 06:59:21
updated: 2025-03-23 15:47:16
---
  * 06:59 출근
  * 명경지수
  * 08:11 바우처 관리/유통 시스템에 있어서 중요한 것은?
    * 유통
      * 결제 거래
        * 이용자 앱 - web view + all link sdk
        * backend로 거래 시작 요청 -> 블록체인 SDK -> Kafka -> 참가기관 DB 저장
          * 바우처 유통 시스템 역할은?
      * 거래 기록
        * 조회 화면과 interface 제공하고 참가기관이 해당 인터페이스 활용해서 자신들 DB에서 조회해서 던져줌.
    * 관리
      * 참가기관이 의뢰기관 등록할 때
        * 기존 시스템은 TB_PRT_CMPNY가 참여기관
          * 바우처 시스템은 동일한 테이블을 의뢰기관으로 사용.
            * 바우처 금액 이동은 의뢰기관 소속 직원(TB_CSTMR_MASTR) 지갑에서 은행 고객(이용자, 사용처) 지갑으로 
  * [x] TB_COM_PERSON, TB_COM_PERSON_CMPNY, TB_COM_PERSON_USER를 잠시 추적했는데 이건 개발한 사람이 와서 설명하는 것이 효율적
  * 10:28 대표님 요청 사항
    * [x] 개발자 역할 분담 고민
    * [x] wallet test
      * CRUD 중 CRU OK. D는 없음.
    * [x] 바우처 의뢰, 지급 등 화면 설계 내용을 DB 테이블로 현행화, 즉 테이블 칼럼명을 맞출 것.
  * 10:32 바우처 관리(vM) 중 참가기관 관리 시스템 화면 정의서를 토대로 테이블 현행화
  * 11:09 4개비
  * 11:12 DB 현행화 시작
    * [x] 11:19 TB_SYS_USER의 LOGIN_NM을 의뢰기관 직원, 사용처 직원, 고객에 전부 삽입? 아니면 CSTMR_NO를 LOGIN_NM에 저장?
    * 바우처 사업의뢰 상세 정보화면에 있는 항목 중 테이블 칼럼으로 등록되지 않은 것을 TB_VOUCH_MASTR와 관련 테이블에 추가.
  * 11:49 대표와 TB_SYS_USER, TB_VOUCH_INSTT_EMP 연결관계를 의논한 결과 현재로서는 그냥 LOGIN_NM에 CSTMR_NO 값이 들어가는 것으로 정하고 개발.  
  * 12:02 5개비
  * 12:33 DB 현행화 계속
  * 12:53 대표님 호출
    * 사용처 승인, 반려 부분을 테이블에 반영.
    * [x] 기존 백엔트 소스 구조대로 호출해서 사용. 내가 작업한 것도 수정할 필요가 있음.
  * 14:05 6개비
  * 14:12 김정은 부장이 바우처 관련 칼럼 추가한 것을 반영
  * 테이블 명 수정
    * TB_VOUCH_PLACE -> TB_PLACE
    * TB_VOUCH_PLACE_EMP -> TB_PLACE_EMP
    * TB_VOUCH_INSTT -> TB_INSTT
    * TB_VOUCH_INSTT_EMP -> TB_INSTT_EMP 등 그외 사용처 테이블명.
  * 16:59 개발자 교육
  * 16:43 7개비
  * 16:59 바우처 관리 update 테스트 OK
    * [x] 이로 미루어 짐작할 수 있는 것은 TbVcMastrEntityMapper클래스를 abstract로 하고 그것을 상속하는 TbVcMastrMapper를 써서 TbVcMastrEntityMapper의 메소드를 호출해도 아무 문제가 없다. chatGPT에 자바 상속 시 super class의 메소드를 그냥 바로 호출해도 문제가 없는지 확인 필요. --> 하지만 pdm과 ewa를 별도로 빌드하는 과정에서 abstract로 선언된 클래스의 메소드를 찾지 못하는 에러(?)가 있었던 것 같음. 이 부분은 나중에 다시 참고할 필요가 있음.