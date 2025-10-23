---
title: "December 12th, 2024"
created: 2024-12-12 09:02:35
updated: 2024-12-12 14:27:46
---
  * 09:02 계정계 호출 어디서, 어떻게 할지 파악 시작.
  * 09:32 거래코드 값과 의미 파악 필요
  * 10:55 kafka acknowledge는 메세지를 받아서 처리했다고 명시. 트랜잭션 처리나 에러 처리할 때 유용.
  * 13:16 DB 테이블 TB_SYS_CODE_GROUP에서 TRNSC_STTUS 거래상태(SATP) 찾음.
    * 그런데 이 코드그룹에 속하는 값이 TB_SYS_CODE_VALUE 테이블에 없음.
  * 14:26 BlockChainListener에서 CheckCallBack 컴포넌트에 처리결과를 kafka로 보내는 게 있다.