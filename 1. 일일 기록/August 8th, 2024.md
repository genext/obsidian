---
title: "August 8th, 2024"
created: 2024-08-08 06:49:07
updated: 2024-08-13 09:34:29
---
  * 06:45 출근
  * 오늘 할 일
    * 업무 메일 확인
    * 의뢰기관 관리자 등록 기능 테스트

  * 명경지수
  * 07:54 어제 내가 알려드린 문제를 대표님이 vcInst, vcPlace를 수정해서 해결했다고 하지만 에러 발생.
    * 에러
      * ```plain text
Caused by: java.lang.IllegalStateException: Ambiguous mapping. Cannot map 'vcInstManageRestController' method ```
    * 원인
      * The error you're encounting is due to the presence of 2 methods in your controller that mapped to the same HTTP path and HTTP method(POST), which causes ambiguity.
    * 조치
      * post를 복사해서 postOld로 만든 부분을 아예 주석으로 막음. 이게 동일한 path, method였음.
  * 08:23 이번에는 관리자 등록하려는데 에러 발생
    * request body
      * ```plain text
{
  "tbCstmrMastr": {
    "koreanNm": "황길동",
    "rlnmNo": "19881212",
    "telecomTypeCd": "SKT",
    "mbtlnum": "01012341234",
    "pin": "123123",
    "lbdyCrtfcTkn": "Tkn1122334455",
    "lbdyCrtfcYn": "Y",
    "appEsntlNo": "1234567890",
    "pushToken": "qwerasdf",
    "etcNtcnYn": "Y",
    "stplatYn": "Y"
  }
}```
    * response body
      * ```plain text
{
  "status": "500",
  "message": "Cannot invoke \"kr.or.cbdc.domain.main.model.voucher.vcinst.mastr.TbVcInstCstmrMastr.newId()\" because the return value of \"kr.or.cbdc.application.voucher.vcinst.model.VcInstCstmrManageModel.getTbVcInstCstmrMastr()\" is null"
}```
    * 원인
      * 메소드 인자 타입인 VcInstCstmrManageModel 클래스 내 속성명이 TbVcInstCstmrMastr인데 request body내 tbCstmrMastr와 맞지 않다.
    * 조치
      * @JsonProperty 인가 하는 어노테이션을 써서 실제 request body에 있는 변수명을 연결할 수도 있지만 그냥 request body내 속성명을 쓰도록 소스를 수정.
  * 09:24 selectAuth 에러 발생
    * 에러
      * ```plain text
2024-08-08 09:29:10.294 ERROR [25140:http-nio-8085-exec-7] k.o.c.i.error.controller.ErrorHandleController     [] Invalid bound statement (not found): kr.or.cbdc.domain.main.mapper.voucher.vcinst.TbVcInstCstmrMastrMapper.selectAuth
org.apache.ibatis.binding.BindingException: Invalid bound statement (not found): kr.or.cbdc.domain.main.mapper.voucher.vcinst.TbVcInstCstmrMastrMapper.selectAuth
	at org.apache.ibatis.binding.MapperMethod$SqlCommand.<init>(MapperMethod.java:235)
	at org.apache.ibatis.binding.MapperMethod.<init>(MapperMethod.java:53)```
    * 원인
      * sql을 저장하는 xml에 selectAuth가 없다.
    * 조치
      * 일단 소스에서 selectAuth 막을까 했지만 대표님께 확인해 봄. 그랬더니 대표님이 TB_CSTMR_MASTR 관련 sql문을 복사해서 붙임.
  * 11:27 cstmr 관련 sql 중 안 쓰는 것 막고 수정.
  * 11:48 5개비
  * 12: 57 6개비
  * 13:02 DB 접속 문제였는데 에러 난 것 때문에 작업한 것을 날렸다. 다시 작업 시작.
  * 14:14 박은경 부장님에게 의뢰기관 관리 업무 설명
  * 14:24 의뢰기관 직원 생성 완료. TB_INSTT_EMP뿐만 아니라 TB_COM_PERSON, TB_SYS_USER에도 들어감.
  * 14:54 사용처도 동일한 작업
  * 15:21 작업 끝내고 테스트하려고 했지만 DB 관련 에러.
  * 17:06 바우처 모집대상 관련 개발 시작. ^V_KbN7f5x
    * 바우처 모집대상 목록 조회, 바우처 모집대상 상세 조회, 바우처 이용자 목록 조회, 바우처 이용자 목록 csv 다운로드
      * TB_VOUCH_MASTR, TB_VOUCH_INDST, TB_CSTMR_RCRIT
      * /vc/recruit/applcnt
      * 개발 계획
        * TB_CSTMR_RCRIT 테이블에 대한 CRUD
        * ~~바우처 모집 목록 조회 endpoint~~
          * 목록 sql 작성(tb_vouch_master+tb_cstmr_rcrit 숫자만)
          * mapper interface 작성
          * serviceImpl 작성
          * controller 테스트
        * ~~바우처 모집 상세 조회 endpoint~~
          * 상세 sql 작성(tb_vouch_master+tb_vouch_indst+tb_vouch_upd_hist)
          * mapper interface 작성
          * serviceImpl 작성
          * controller 테스트
        * ~~바우처 이용자(신청자) 목록 조회 endpoint~~
          * 이용자목록 sql 작성(tb_vouch_master+tb_tb_cstmr_rcrit)
        * 바우처 신청자 목록 csv 다운로드
          * 4번 sql 결과 + csv 파일
    * ~~바우처 대상확인 목록 조회, 바우처 대상확인 상세 조회~~
      * 바우처 모집 목록 조회와 동일
      * /voucher/rcrit
    * ~~바우처 수혜자 목록 업로드~~
      * file 수신 + 데이터 추출 + update tb_cstmr_rcrit.reqst_yn
      * TB_VOUCH_MASTR, TB_VOUCH_ISU_MASTR
      * /voucher/issue
    * 바우처 사용처 목록 조회, 바우처 사용처 목록 csv 다운로드, 바우처 사용처 목록 업로드
      * ~~바우처 사용처 목록 조회 endpoint~~
        * 사용처목록 sql 작성(tb_vouch_master+tb_tb_vouch_place+tb_place+tb_induty)
      * TB_VOUCH_MASTR, TB_PLACE, TB_VOUCH_PLACE
      * /vc/recruit/place
  * [x] 모집대상 관련 화면 확인