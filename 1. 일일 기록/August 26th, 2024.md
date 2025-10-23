---
title: "August 26th, 2024"
created: 2024-08-26 06:15:21
updated: 2024-08-26 19:48:29
---
  * 06:13 출근
  * 06:36 어제 갑자기 떠오른 대로 테이블명이 비슷한 것이 두 개 있었다. TB_CSTMR_RCRIT와 TB_VOUCH_CSTMR_RCRIT.
    * 앞으로 무조건 TB_VOUCH_CSTMR_RCRIT 쓴다.
  * 오늘 할 일
    * 업무 메일 확인
    * backend 소스 중 파일 업로드할 때 엑셀 칼럼 위치 잘못 쓴 것 수정한 것 commit

  * 명경지수
  * 09:13 git pull이 안 되어서 이정주 팀장이 처리해 줌. 그냥 간단하게 지우고 다시 받으면 되는 거였다.
    * 다른 브랜치로 옮겨서 vcdevelop 브랜치를 삭제.
      * ```shell
C:\codes\cbdc-backend>git checkout -b test
Switched to a new branch 'test'

C:\codes\cbdc-backend>git branch
* test
  vcdevelop
  voucher

C:\codes\cbdc-backend>git branch -D vcdevelop
Deleted branch vcdevelop (was c430468).

C:\codes\cbdc-backend>git fetch

C:\codes\cbdc-backend>git checkout vcdevelop
branch 'vcdevelop' set up to track 'origin/vcdevelop'.
Switched to a new branch 'vcdevelop'

C:\codes\cbdc-backend>git pull
Already up to date.```
  * 09:24 검증기(CA) 배포쪽 해야 한다.
  * 김정은 부장이 화면 변경해서 이에 맞춰 다시 프론트, 백엔드 수정.
  * 17:04 김인술 대리 지원 
    * 엑셀 다운로드가 제대로 안 되는 이유. 조회 조건에서 걸려서 그렇다고...그런 것 같네...흠...
    * pagination이 잘 안 되는 이유. 서버에서 정해준 숫자보다 많이 보낸다.
  * 18:11 pagination 에러 잡았다. 내가 꼼꼼하게 살펴보지 않은 탓이다. 처음에 할 때 놓치지 말아야 나중에 고생하지 않는다.