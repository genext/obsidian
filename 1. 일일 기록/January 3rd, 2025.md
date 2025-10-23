---
title: "January 3rd, 2025"
created: 2025-01-03 09:44:51
updated: 2025-01-03 14:59:45
---
  * 09:48 오늘 사용처지갑 코딩 완료 목표
  * 09:50 kisa backend는 DEV1이 없다. 여부장에게 문의
  * 10:06 검색어 치면 DEV1이 나오네. 내가 직접 병합
  * 10:42 사용처 지갑 offramp 코딩 시작
    * offramp 시, 연계계좌 상태 조회 bridge gw 미구현 발견
  * 11:15 offramp 코딩 계속
    * 코딩 중, onRamp와 offRamp에서 계좌입출금 처리 순서가 제각각 블록체인 앞, 뒤로 서로 달라서 processKafkaAndBlcokchain 함수 안에 둘 다 몰아넣어야 하면서 함수 파라미터 수정해야 함.
  * 12:04 processKafkaAndBlockchain 파라미터가 너무 많아서 dto로 작성 시작
  * 14:28 dto 작성 후, 코드 수정 시작
    * 처음부터 claude를 써서 코드를 수정하도록 했어야 하는데.
  * 14:59 코드 수정 계속
