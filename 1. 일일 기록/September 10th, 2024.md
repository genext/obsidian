---
title: "September 10th, 2024"
created: 2024-09-10 06:01:11
updated: 2024-10-23 14:45:50
---
  * # 화요일
  * 06:01 출근
  * 오늘 할 일
    * 업무 메일 확인
    * cbdc-bok kafka thread 구동 확인
    * front로 날짜 정보 전달할 때 String이 아닌 LocalDateTime으로 문제가 없을지?
  * 명경지수 -> 명징한 생각
  * 06:01 일단 bok-voucher에서 sdk 호출 후 제대로 응답을 못 받는 데 너무 힘 빼지 말고 일단 resttemplate으로 wallet.sdk.demo를 호출하는 식으로 변경.
    * 이게 되면 일단 화면 포함한 일처리를 마저 하고 나중에 위 문제를 해결하는 식으로 하자.
  * 08:27 일단 endpoint(/v1/voucher/deploy) 코드 변경 및 테스트 완료.
    * [x] 코드 review. 특히 새로 사용한 Optional 위주로
  * 09:26 이제 오라클 배포쪽을 개발해야 하는데 위에서 만든 것을 그대로 활용할 수 없을까? 서비스 계층이 걸리네..
  * 09:28 오라클 배포 개발 시작
  * 09:47 역시 여기서 interface를 안 쓰고 바로 구현을 쓸 때 나타나는 문제점이 드러났다.
  * 11:08 이미 개발한 서비스구현은 바꾸기 힘들고 그냥 이들은 의존성 주입으로 처리하기로 함.
  * [x] application-voucher.yml에 kafka 설정이 있다. 혹시 이것 때문에 kafka가 제대로 동작하지 않나?
  * 12:16 바우처 배포 실행 테스트 swagger에서 해서 결과 제대로 나온 것도 확실히 확인했고 이제 오라클 배포 엔드포엔트도 바우처 배포 엔드포인트와 동일하게 작업하되 주입하는 서비스명만 수정해서 완료.
  * 13:44 바우처 오라클 권한 부여 개발
    * EoaWalletManager.signAndSendTx(requestId, walletType("central"), signer, contractAddr, contractAddr, function, function param(toAddress, amount))를 사용해야 하는데 각 인자에는
      * signer: 금결원 권한 주소
      * contratAddr: 각각 proxy, impl을 의미하지만 일단 지금은 바우처 오라클 contractAddress 하나로 한다.
      * function: addPartManagers
      * input: 참가기관 권한 주소(배열이므로 여러 개 가능)
    * 외부 개발계에서 CRUD 중 CR만 개발. 테이블 살펴 보니 UD가 필요없음.
    * Create 개발
      *  화면에 "항목 추가하기" 버튼 누르면 참가기관 선택상자가 뜨는데...
      * Input: [company_id, ...]
      * output: 성공여부
      * rest url: /v1/oracle/insertAuthority
      * service: insertAuthority
      * mapper: insertAuthority
      * xml: insertAuthority
  * 16:22 오라클 권한 부여 모듈의 단순 create, read by id의 개발 및 테스트 완료