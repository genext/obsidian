---
title: "December 17th, 2024"
created: 2024-12-17 08:26:35
updated: 2024-12-17 20:36:18
---
  * 오늘 할 일
    * openAPI 서비스 모듈 코딩

  * 명경지수 -> 명징한 생각
  * 오늘 일 중 꼭 기억할 것.
  * 08:27 claude가 기존 ApiCallHelper를 개선을 위해 제안한 것 분석 및 소화 시작
    * claude가 너무 많이 바꿔서 일단 통과
    * 대신 claude가 제안한 openAPI 서비스 모듈 설계를 살펴보다가 토큰이 있어서 잠시 샛길
      * 이 프로젝트는 토큰을 httprequest의 bearer에서 얻음.
      * 따라서 claude에게 토큰을 yml에서 빼고 다시 만들라고 함. -> 오후에 openAPI 담당자에게 물어보니 토큰을 안 쓰고 API 키도 안 쓸 가능성이 있다고 함.
  * 09:23 dto, config class 파악 시작
  * 10:20 gradle build가 안 돼서 예전에 git clone한 것을 old로 바꾸고 git bash에서 git clone 다시 실행 --> 이번에는 제대로 build script가 만들어지고 bootrun도 생성됨.
  * 10:54 open jdk 삭제하고 여명동 부장이 올린 windows용 자바 설치
    * 일단 불완전하나마 빌드 됨.
  * 13:40 apiservice branch 개발
  * 16:24 일단 apiservice 뼈대는 완성