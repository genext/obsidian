---
title: "August 14th, 2025"
created: 2025-08-14 08:36:27
updated: 2025-08-14 17:40:31
---
  * 08:36 cig 2
  * 09:47 cig 3
  * 10:45 claude-code 실행하면 중복 설치되었다는 에러 메시지도 뜨고, 자꾸 auto-update 에러가 발생.
    * 그래서 npm으로 설치한 것을 지우고 anthropic에서 새로 만든 native 설치 방식으로 재설치하려고 함.
    * npm uninstall -g @anthropic-ai/claude-code하면 ENOTEMPTY 에러 발생.
      * 알고 보니 .npm-global/lib/node_modules/@anthropic-ai/claude-code를 ".claude-code-EokMvwXK"으로 바꾸려고 했는데 이미 그 디렉토리가 있었다.
      * 전에 uninstall한 흔적인데...npm은 지울 때 매번 디렉토리명을 바꾸지 않나?
      * 암트 그 디렉토리를 직접 지우고 하면 실행하면 OK.
    * 그리고 설정 파일도 "rm -rf ~/.claude" 실행해서 다 정리.
  * 11:07 claude code 재설치
    * curl -fsSL https://claude.ai/install.sh | bash -s latest
    * 위 명령어는 npm과 달리 /home/genext/.local/bin/에 claude 설치.
  * 11:18 claude setting으로 환경 설정 시작했는데 이상하다. 문서에는 /config라고 되어 있는데..
    * claude jkoh로 시작했더니 jenkins pipeline을 설정하겠다고...엉뚱...
    * 암튼 설정하긴 했는데 별다른 것 없다. 복잡한 설정은 다른 데서 하는 듯.
  * 11:49 cig 5
  * 12:39 몇 번 시행착오 끝에 어디서든 사용할 수 있게 context7 설치.
    * claude mcp add --transport sse context7 https://mcp.context7.com/sse **--scope user**
  * 12:44 context7 접속이 너무 자주 끊어진다. 불편해서 못 쓰겠네...하지만 기업 환경 내에 문서를 보관하는 웹사이트가 있다면 local로 설치해서 사용할 수 있을 듯...
  * 12:49 cig 6
  * 14:50 cig 7
  * 15:30 cig 8
  * 15:59 내가 제대로 context7 호출하지 않으면 연결이 끊어지는 것 같다. 사용언어와 라이브러리명을 프롬프트에 명시해야 하는 모양.
  *  17:40 cig 9
