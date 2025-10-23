---
title: "August 14th, 2024"
created: 2024-08-14 06:53:50
updated: 2024-08-28 13:27:49
---
  * 06:45 출근. 기수형이 이미 나와있다.
  * 오늘 할 일
    * 업무 메일 확인
    * 모집관리 화면 개발

  * 명경지수
  * 08:32 front-end 소스 분석
    * features와 vc/vcr는 동일한 디렉토리 구조다. 그럼 차이점은?
      * features: 주화면 이외 컴포넌트들
      * vc/vcr: 주화면 컴포넌트
  * 09:12 화면 검색 조건 중 신청시작일, 종료일 선택 상자가 있다. 이게 조금 헷갈린다.
    * 신청 시작일(신청 시작일) 선택하고 검색 하면 바우처의 신청 시작일(신청 종료일)이 기간 조건에 포함되는 바우처들 보여주는 것이다.
  * 09:25 일단 react에 익숙해져야 한다.
    * 화면 구성 컴포넌트 중 표 제목 headerList
  * [x] 변액 연금보험. 10년 만기는 이자소득 비과세?
  * 10:14 4개비
  * 15:10 일단 front-end쪽 코딩 고쳤다. 이제 백엔드도 되게끔 수정.
  * 15:17 백엔드 수정할 것
    * selectList sql resultType은 "kr.or.cbdc.infrastructure.framework.core.support.collection.CamelKeyMap"로 수정
  * 17:39 모집관리 관련해서 frontend와 backend 코딩 다 했지만 실제 실행하면 front에서 backend로 요청이 안 간다.
    * CORS 문제 같다. front end url은 localhost로 시작. -> frontend 설정 파일에 backend가 제대로 설정되지 않음.