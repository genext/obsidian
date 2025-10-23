---
title: "August 15th, 2024"
created: 2024-08-15 07:49:38
updated: 2024-08-28 14:00:30
---
  * 07:45 10분 전에 이미 도착했었지만 철문이 닫혀 있었다. 당황해서 경비실을 찾을 생각을 못했다. 당연히 회사에 경비실이 있을 거라는 생각을 했어야 했는데. ㅋ
  * 07:50 3개비
  * 08:49 gitlab에서 이상한 현상. 대소문자 구분 못하는 문제
    * 디렉토리명이 대문자로 만들어진 것이 있어서 RecruitManagement를 recruitManagement로 수정하고 commit했는데도 git pull하면 recruitManagement가 지워지고 RecruitManagement가 만들어짐.
    * 조치
      * ```shell
# To make sure, do this first.
git config core.ignorecase false

# make recruitManagement first and change directory name
mv recruitManagement tempDirectory
git add tempDirectory
git commit -m "Temporary rename to avoid case-sensitivity issue"
git push origin vcdevelop

#mv directory name back
mv tempDirectory recruitManagement
git add recruitManagement
git commit -m "Renaming directory with the correct case"
git push origin <your_branch_name>```
    * 이후 git pull하면 recruitManagement만 보이지만 이상하게 gitlab 서버에는 RecruitManagement가 recruitManagement와 같이 있다.
  * 08: 58 일단 frontend 띄우는데 이상한 에러가 났지만 화면이 일단 떴다. 그런데 모집관리 화면을 띄웠더니 서버가 무한 루프 돈다.
    * [x] useEffect를 막으니까 무한 루프 사라짐. 이건 useEffect를 안 써도 자동으로 서버로 요청을 보내네?
  * 09:02 엉뚱한 데서 어제 front-end가 내 server로 send request를 못 찾는 이유를 찾았다.
    * 어제 이경진 차장님이 .env.test를 수정해서 REACT_APP_PROXY_HOST를 우분투 서버에서 localhost:8085로 수정했다. ㅋㅋ 왜 그 생각을 못 했지?
  * 09:05 frontend 메뉴 중 제대로 작동하는 것처럼 보이는 것은 의뢰기관 관리의 기관 관리다. 제대로 DB에서 조회해서 화면에 보여준다.
  * 09:31 모집관리 디버깅
  * 10:21 드디어 모집관리 데이터 표시. mapper xml에 if 조건에 변수명이 맞지 않아서 그랬다.
  * 10:54 이제 여기 frontend 동작방식을 살펴보면서 react 확실히 파악.
  * 12:32 향미 식사 신한카드 ^TNeAPZmKe
  * 13:01 frontend 분석 준비
    * [x] index.ts와 index.tsx 차이?
      * ts만 붙은 것은 typescript나 javascript만 가능. tsx는 react 사용할 때 JSX를 지원한다는 것.
    * [x] public 디렉토리분석
