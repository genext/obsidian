---
title: "August 4th, 2025"
created: 2025-08-04 07:17:58
updated: 2025-08-04 15:35:26
---
  * 07:18 github 도구 4종
    * gitingest
      * github 저장소를 LLM 친화적인 글로 변환. 단순히 url에서 github의 hub을 ingest로 바꾸기만 하면 된다. 이렇게 나온 결과를 AI에게 주면 알아서 분석해줄 수 있지만, md 파일이 너무 크면 토큰 많이 소모할 가능성. 
    * Deepwiki
      * 기술 문서 작성 해준다. 오픈 소스 학습용으로 좋다
    * gitMCP
      * gitingest의 단점 보완
      * github 프로젝트마다 전용 MCP서버 만들어준다. gitingest처럼 url의 hub을 mcp로 바꾸면 된다.
    * gitPodcast
      * github 내용을 팟캐스트 이야기로 바꿔줌.
  * 07:39 nomadcoder 동영상 중 github 도구 4종을 보니까 mdx 파일 타입이 있다. 이거 활용분야? markdown이던 react component던 둘 다 렌더링할 수 있는 것 같은데 react component는 왜 할까?
    * 동적으로 사용자와 상호작용을 처리하고 싶을 때, 버튼 등 추가 가능. 
    * 그런데 너무 번거롭다. next.js 등 react 설치되어야 하고...별로 유용하지 않은 듯.
  * 12:17 오늘 치과 진료 받음. 큰 이상은 없고 다만 앞니쪽 잇몸이 조금 내려앉았다고....앞니쪽에 치실에 자주 사용하라고 함.
  * 13:27 Zapier 조사. 앱 연결해서 업무 자동화를 쉽게 해주는 사이트.
    * 그런데 내가 자동화하고 싶은 것이 있나?
      * 개발: claude code로 개발할 때 git commit할 때마다 roam research "Daily Notes"에 시간과 commit 메시지를 기록.
  * 14:11 지금 버스 주차 게임 중. 광고가 너무 많다. 
  * 15:11 일단 오늘 중으로 roam research mcp 서버 설치하고 사용해 보기. 
  * 15:17 roam research mcp 설치 시작.
    * npm으로 설치했는데 터미널에서 실행되지 않는다.
    * claude desktop에서 mcp 연결할까 했는데 이것도 window, mac만 있다.
    * 다행히 claude-desktop-debian이 github에 있는 배포버전이...
      * https://github.com/aaddrick/claude-desktop-debian/releases github에 가면 releases 메뉴가 없는데 url 끝에 /releases를 붇면 나온다.