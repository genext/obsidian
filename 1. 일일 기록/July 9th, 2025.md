---
title: "July 9th, 2025"
created: 2025-07-09 07:06:15
updated: 2025-08-04 21:17:02
---
  * 오늘 할 일
    * code-server 접속 및 개발 환경 설정
    * 개발 관련 문서 정리
  * 명경지수 -> 명징한 생각
  * 오늘 일 중 꼭 기억할 것은?
  * 내가 한 일 중 중요하고도 잘 했던 일은?
  * 07:06 cig 1
  * 어제 저녁 8시부터 에어콘이 안 돌았다. 더우니 잘 시간에 못 자서 오늘 달리지 않고 거의 7시까지 잤다.
    * 명경지수라는 게 역시 쉽지 않다.
  * 08:29 cig 2
  * MNO: Mobile Network Operator
  * 08:49 confluence/2025 MAP1.5 구축/1100.공통/1110. 아키텍처 논리구성도 파악
    * 사용자/채널
      * 일반 에이전트
      * 로밍 에이전트
      * 요금 에이전트
    * MAP(MNO AI Platform)
      * UI Layer
      * Outer Integration Layer
        * API Gateway
      * Service Layer
      * Inner Integration Layer
      * Infrastructure Layer
        * AWS public cloud
  * 09:34 jenkins, efs 서버에 mobeXterm으로 접속 확인.
  * 09:43 code-server 접속 확인.
  * 10:00 cig 3
  * 10:22 개발환경 설정 시작
    * code-server 접속
      * python 가상환경 설정
    * access token 취득 후 git global 환경 설정
      * 사실 이건 문서 잘못이다. code-server에 접속할 때 각 개발자 계정으로 따로 들어간 것이 아니기 때문에 git 설정은 clone한 디렉토리에만 적용되게 설정해야 함.
    * git clone하면 authentication fail.
      * DS010158로 하면 되는데 token값 문제였나? 이상.
  * 11:12 vscode terminal에서 명령어를 쳐도 화면에 바로 나타나지 않는 문제
    * ctrl + , 해서 설정 화면을 띄운 다음에 "terminal render"로 검색하면 여러 설정값이 나온다. 그 중 gpu acceleration을 off로 변경하고 크롬을 다시 띄우면 된다.
  * 12:00 cig 4
  * 13:07 data pipeline 설계 방안
    * 기동
      * batch
      * real time
    * pdf 적재
    * preprocessing
      * pdf 분석 -> 이건 로그 확인하면서 분석. pymupdf4llm 라이브러리가 pdf를 읽어서 markdown으로 바꾼다. 이 라이브러리 분석해야 할까?
      * md 출력
      * DB 저장
    * 공통부
      * 파일 탐색
      * logging
  * 14:07 cig 5
  * 15:14 cig 6
  * 내가 직접 엑셀 테이블을 만들어서 AI가 이를 잘 이해하는지 테스트해보기
  * 16:56 테스트용 pdf를 다운로드 받음.
  * 16:59 cig 7
  * 17:33 git pull할 때마다 login해야 하는 것이 귀찮아서 일단 한 번 로그인하면 cache되도록 함. 하지만 그것도 귀찮아지면 url1에 id/token을 붙여서 하는 방법도 있다.
  * 19:40 cig 9
  * 20:32 cig 10
  * 21:12 cig 11