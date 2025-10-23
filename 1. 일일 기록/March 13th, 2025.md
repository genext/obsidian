---
title: "March 13th, 2025"
created: 2025-03-13 09:40:51
updated: 2025-03-13 15:46:51
---
  * 오늘 할 일
    * kisa 전반적 수정.
    * 배포요청서 전달
    * rollback 시 db 데이터가 원복되어야 하는지? enabletransactionmanagement 확인
  * 명경지수 -> 명징한 생각
  * 09:41 롤백을 하지 않도록 수정했지만 김영훈 차장의 의견은 kisa 기준으로 rollback이 되도록 놔둬야 하지 않냐는 것이었다. 맞는 것 같다.
  * 15:44 일단 kisa offRamp 에러 처리 작업은 되었다. 신기한 건 insert commit이 되지 않았더라도 해당 데이터를 update하려고 하면 대기한다는 것이다. 마치 그 데이터가 이미 테이블에 있는 것처럼...
