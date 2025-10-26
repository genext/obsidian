---
title: "August 7th, 2024"
created: 2024-08-07 06:45:37
updated: 2024-08-08 07:00:05
---
  * 06:43 출근.
  * 오늘 할 일
    * 업무 메일 확인
    * wallet 테스트 결과 및 delete 협의

  * 명경지수
  * 09:53 현재 cdbc backend의 myBatis 구조의 이상한 점을 문의하고 Repository 패턴을 조사한 결과
    * Repository 패턴은 기본적인 형태이고
    * 위 패턴을 적용하는 관점에서 비즈니스 로직 분리까지 생각하면 Service layer를 넣는 것이 좋다.
  * 10:17 어제부터 디스크 드라이브가 꽉 차는 일이 벌어진다.
  * 10:46 [[React]] 메뉴 설정 방법 파악 시작
    * 메뉴 정보의 menu_path를 아래처럼 넣으면 된다.
      * ```javascript
<Link to={item.menu_path}>{item.name}</Link>```
  * 개발자 역할 분담
    * 수직 분할(한 개발자가 특정 모듈 담당해서 frontend-backend 다 처리)이 가능하면 그게 낫다.
    * 업무 분할
      * 참가기관
        * 바우처 관리
          * 승인, 반려
        * 의뢰기관 관리(vinst)
          * CRUD(TB_INSTT)
          * 직원 관리(TB_INSTT_EMP)
        * 바우처 지급 관리
          * CRU~~D~~ (TB_VC_ISU_MASTR, TB_CSTMR_? )
        * 사용처 관리(vplace)
          * web, app
          * CRUD(TB_PLACE)
          * 직원 관리(TB_PLACE_EMP)
          * 바우처 적용(TB_VOUCH_PLACE)
      * 의뢰기관
        * 바우처 관리(pbm)
          * CRUD(TB_VOUCH_MASTR, TB_COIN_MASTR, TB_VOUCH_INDST, TB_VOUCH_COND, TB_VOUCH_UPD_HIST)
      * 이용자 모집, 대상자 추출(TB_CSTMR_RCRIT)?
      * 거래 관리?
      * 스마트컨트랙트(TB_COIN_MASTR) 관리? 수호 아이오?
  * [x] 테스트 데이터 추가 생성.
    * 16:38 사용처를 생성할 때 createUser를 호출하지?
      * 대표에게 얘기한 결과 뭔가 잘못되었다고 함.
  * 17:10 front-end에서 메뉴 처리하는 방법 파악
