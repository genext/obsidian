---
title: "September 29th, 2024"
created: 2024-09-29 00:00:10
updated: 2024-09-30 15:14:13
---
  * 09:04 출근
  * 오늘 할 일
    * 업무 메일 확인
    * [x] 바우처 배포 주소 관리 복사 구현 -> 2시간 12시 완료
    * 바우처 배포 후 배포주소 테이블과 연결하는 테이블에 데이터 저장 -> 2시간
    * front로 날짜 정보 전달할 때 String이 아닌 LocalDateTime으로 문제가 없을지?
  * 명경지수 -> 명징한 생각
  * 09:16 wallet.sdk.demo에서도 되는지 먼저 확인
  * 09:22 지금 갑자기 든 생각인데 모든 것이 딱딱 맞아 떨어져야 sw가 제대로 실행된다. 그렇다면 처음에 deploy할 때 abi에 input 정의가 어떻게 되어 있는지 확인해야겠다는 생각이 들었다.
    * 그런데 abi에 있는 input 정의는 deploy용 input 같은데..signAndSendTx용 input이 아닐 듯...deploy와 signAndSendTx 관계를 잘 모르겠다.
  * 09:37 postman으로 테스트한 결과 역시 어제와 동일한 에러 발생.
    * test body
      * ```plain text
{
    "requestId": "con-dep-004",
    "signer": {
        "walletAddress": "0x0162162512CAd8721CdfF2bAB3403FAeF2CC93D4",
        "hdKeyId": "3fa0b1fa-35c5-31c2-a190-7922376eeaa3",
        "hdKeyAccToken": "eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJCS01TIiwiaWF0IjoxNzI0NjQ5NTQ2LCJzdWIiOiJCS01TX0hEX0tFWV9BQ0NfVE9LRU4iLCJhdWQiOiJXQVMiLCJleHAiOjE3NTYxODU1NDYsImhkS2V5SWQiOiIzZmEwYjFmYS0zNWM1LTMxYzItYTE5MC03OTIyMzc2ZWVhYTMifQ.9QyoxgT4rnQUI_vSCkLMOWAi9cGcdHRJwS6stj9tM8M)"
    },
    "walletType": "central",
    "contractAddress": "0xb9ff79a5f2a7944584d942f684365d92360640ec",
    "implContractAddress": "0xb9ff79a5f2a7944584d942f684365d92360640ec",
    "functionName": "addPartManagers",
    "inputParams": [
        [
        "0x10908341980F81985d3198a073aD803eB03ecb1B"
        ]
    ]
}```
    * response
      * ```plain text
{
    "requestId": "con-dep-004",
    "returnCode": "BWS000",
    "errorMessage": "[requestId: con-dep-004] [ErrorCode: BWS000] wallet sdk error: internal server error: For input string: \"[0\" under radix 16",
    "decodedErrorMessage": null
}```
    * 원인은?
  * 10:04 바우처 계약 관리 모듈 백엔드와 프론트엔드 개발 시 고려사항
    * 백엔드
      * 테이블명과 칼럼명 수정
      * insert시 오라클 바우처와 달리 두 테이블에 저장
    * 프론트
      * 화면명 수정
        * 바우처 오라클 -> 바우처 배포주소
        * 오라클 등록 -> 배포주소 등록(배포)
        * 오라클 관리 -> 배포주소 관리
  * 10:43 대표님에게 wallet.sdk 에러 문의한 결과 내일 관련자(이정주 팀장, 하홍준 박사)다 같이 모여서 해결하기로 함.
  * 10:43 바우처 오라클 배포 주소 관리 개발 시작
    * 단순 복사이간 한데 logic만 복사하는 거지 이름(테이블명, 칼럼명, 변수명 등)을 다 바꿔야 한다.
    * 빨리 하려면 어디부터 손봐야 할까? 근본이 DB니까 xml mapper부터 수정해야 하지 않을까?
  * 12:15 개화 식사 아멕스카드 ^Vjc1x-fb7
  * 12:21 xml mapper와 mapper를 마쳤고 이제 서비스와 콘트롤러 시작.
  * 13:55 수정 완료 후 테스트 시작
  * 14:21 바우처 배포주소 등록 완료
  * 15:03 사용상태 변경하기 테스트 완료
  * 15:16 바우처 배포주소 관리 화면 중 참가기관 EOA목록을 제대로 표시하려면 일단 tb_ca_register_vc_deployed_address에 데이터가 제대로 들어가야 한다.
    * 계약 관리 정보는 원래 있다. 사용 중인 것 하나.
    * 바우처 배포 신청 의뢰가 들어갈 때마다 tb_ca_register_vc_deployed_address가 들어가야 하나?
  * 15:35 EOA 목록 조회를 위한 sql 수정 및 테스트 완료
  * 16:15 일단 바우처 배포 승인 요청할 때 tb_ca_register_vc_deployed_address 테이블에 저장하도록 코딩함. 내일 아침 테스트.