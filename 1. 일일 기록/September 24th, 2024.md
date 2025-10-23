---
title: "September 24th, 2024"
created: 2024-09-24 07:16:03
updated: 2024-10-03 14:15:38
---
  * 07:16 공항 도착해서 커피와 함께 담배 피우고 공항철도 타러 가는중.
  * 09:44 오라클 조회하는 것을 전에 구현했지만 DB 테이블 각 칼럼을 구체적으로 정해서 조회한 것이 아니고 그냥 "select * ..." 이런 식으로 구현한 것이라 완성도가 50%도 안 되는 것이었다.
    * 휴가 전에 이를 보완하는 작업 중이었는데 마무리 다 하지 못해서 지금부터 이 작업 재개 예정.
  * 09:46 오라클 조회 보완 개발 이어서 시작
    * 화면 명: 바우처 오라클 관리
    * 오라클 조회 목록표 칼럼명: 바우처 오라클 명, 권한 수, 상태, 생성자, 생성일, 배포 일자, 마지막 수정
  * 11:06 이정주 팀장과 회의
    * fix/blockchain 브랜치를 만들어서 wallet쪽 kafka 메시지 잘 못 받는 것을 해결하려고 노력 중.
    * pagination
      * front: regulator/system/log에 pagination 관련 코드 추가. useApiLog
      * backend:
        * controller: SysRestController 
        * sql: SysMapper.xml에 pagination
    * front 내 담당 업무 중 
      * 권한 EOA, 배포 EOA, 계정 로그인 이미 이정주 팀장이 개발
  * 11:32 boolean 타입 데이터는 react나 HTML에서 제대로 표시하지 않는다. 따라서 이를 true/false에 따라 string 형식으로 바꿔야 함. '사용 중/중지 됨'으로 변경
  * 11:34 일단 오라클 목록 화면과 오라클 목록 조회 기능 구현 완료.
  * [x] 화면 내 생성자, 수정자 등을 user_id가 아닌 note로 바꾸기?
  * 12:01 types 내 타입 정의를 domain으로 옮기기
  * 스마트계약 배포 승인 개발 확인 및 테스트 시작
  * 17:05 recoil도 page reload 시에는 초기화된다. 그것을 방지하려면 local storage에 상태를 저장할 수 있는데 일단 userId를 useEffect 실행조건에 추가하고 companyId에 값이 들어올 때까지 return하는 식으로 변경. 그럼 결국에는 userId에 값이 들어오고 companyId에도 값이 들어간다.
