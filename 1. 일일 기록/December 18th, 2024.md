---
title: "December 18th, 2024"
created: 2024-12-18 08:52:24
updated: 2025-06-27 08:49:10
---
  * 오늘 할 일
    * openapi 호출 지점 표시 및 토큰 처리

  * 명경지수 -> 명징한 생각
  * 오늘 일 중 꼭 기억할 것은
    * 데이타 정합성을 위한 주석 @Validated, @Valid
      * @Validated는 메소드 파라미터 검증하기 위해서 @Valid를 사용할 때는 해당 클래스에 꼭 붙여야 하지만 config 클래스에는 안 붙여도 하위 요소에 붙은 @Valid는 효과가 있다
  * 10:03 한범진 부장이 늦게까지 출근하지 않아서 내가 대신 일일회의 참석
  * OpenApiService 단위테스트 방안
  * 11:09 개발1팀이 쓸 api를 다 넣었다.
    * 각 api마다 dto, url를 정의.
  * 14:01 OpenApiService는 서비스 모듈이 아니라 bridge gw의 서비스안에 넣어야 한다. bridge gw는 was로 따로 기동할 계획
  * 14:27 EwaBridgeSerice 수정 시작
