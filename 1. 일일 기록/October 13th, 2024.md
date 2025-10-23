---
title: "October 13th, 2024"
created: 2024-10-13 00:00:05
updated: 2024-10-14 07:47:58
---
  * 08:17 출근
  * 08:40 바우처 배포 시 tb_ca_register_vc_deployed_address에 데이터 저장하는 것 테스트 시작.
  * [x] 배포주소 관리 수동 입력 시 transaction_status를 CONFIRMED로 넣도록 수정
  * 09:17 이번에는 배포 후 배포주소 데이터 연결 저장을 반드시 완료한다.
    * 09:25 테스트 완료하고 새 브랜치(register_vc_deployed_address)에 commit and push
  * 09:33 이제 alert 대신 toast 사용하도록 수정 시작
  * 10:20 alert -> toast 수정 계속.
  * 10:58 배포주소 수동등록용 api 작성
  * 12:33 개화 점심 식사 ^JMtcD_iXE
  * [x] 바우처 배포 후 배포주소 등록할 때 usage가 1인 mgtId가 없으면 에러 처리.
  * 13:49 바우처 배포후 배포주소 등록에 잘못된 것이 있어서 재수정하고 테스트 시도.
  * 14:32 배포주소 관리 화면에 보여주는 데이터 중 바우처 배포 후 자동으로 등록되지 못한 것도 보여주는 것을 backend에 반영.