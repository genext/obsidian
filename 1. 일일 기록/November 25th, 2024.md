---
title: "November 25th, 2024"
created: 2024-11-25 07:54:15
updated: 2025-06-27 08:50:10
---
  * 07:54 오뎅국
  * 07:54 2개비
  * 소스를 vsc로 분석 중. 그런데 td 제조는 어디에?
  * 13:44 td 제조 찾기
    * 인터페이스 정의서에서 토큰제조요청 찾음: 분산 원장으로 송신.
      * /interfaces/blockchain/BlockchainImpl.java의 sendMintTransaction을  호출해야 하는데 소스에는 해당 메소드를 호출하는 것이 없다.
      * url은 /pdm/manage/dc1Manufacture로 되어 있지만...
      * 그럼 API를 새로 만들어야 한다? 언제 누가 호출?
    * DC1, DC2 차이?
      * 소스를 보니 DC1은 예금 토큰, DC2는 eMoney로 보임.
  * 15:01 td 서비스 모듈 조사
    * 제조지갑은 미리 화면을 통해 만들어져 있다는 조건
    * 예금토큰 제조 승인은 참가기관에서 직접 처리
      * 중앙은행으로 승인요청을 보내면 자동처리 된다.
    * Assert로 에러 처리 충분?
      * 서비스 모듈의 메소드는 throws WalletSdkException이고 globalExceptionHandler가 있는데 어떻게 에러 처리할까?
  * 예금토큰 소각과 폐기 차이?
    * 소각은 환수지갑에서 폐기지갑으로 이동.
    * 폐기는 환수지갑에서 폐기지갑으로 이동