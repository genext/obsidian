---
title: "December 16th, 2024"
created: 2024-12-16 12:38:52
updated: 2025-06-27 08:49:24
---
  * 12:38 계정계와 통신할 때 꼭 gw를 써야 할까?
    * on ramp 경우, gw에는 on ramp 결과를 전탈하는 open api 호출만 있다?
    * 하지만 계정계는 on ramp전 계좌조회를 먼저 요구한다. 이건 블록체인 호출하기 전에 계정계 open api 호출해야 한다.
  * kafka 메세지를 받으면 이게 어떤 거래인지(on ramp 등) 어떻게 알지?
  * openAPI 공통 모듈 만들 때
    * 여러 개 있을 수 있는데 url과 전문 dto, 재시도 횟수, timeout 묶어서 enum화 가능?
    * 매개변수 조금씩 다르다
    * 응답에 응답코드와 메세지 외에 배열이 있을 수 있다.
    * url과 retry 등을 저장할 때 config 말고 다른 방안은?
  * 20:32 claude를 이용해서 ApiCallHelper와 함께 openAPI 호출 서비스 모듈 사전 설계