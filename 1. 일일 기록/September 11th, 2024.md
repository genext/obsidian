---
title: "September 11th, 2024"
created: 2024-09-11 00:00:09
updated: 2024-09-11 20:27:51
---
  * 06:30 출근. 어제 모기 때문에 잠을 설치고 또 이상하게 잠을 잘 못 잔 것 같은 느낌이다. 그런데 의외로 깊은 잠을 평소보다 훨씬 많이 잤네?
  * 오늘 할 일
    * 업무 메일 확인
    * oracle signAndSendTx 구현 및 테스트
    * cbdc-bok kafka thread 구동 확인
    * front로 날짜 정보 전달할 때 String이 아닌 LocalDateTime으로 문제가 없을지?
  * 명경지수 -> 명징한 생각
  * 06:37 오라클 권한 부여 블록체인 호출 개발
    * 오라클 입력 후 oracleId를 requestId로 사용.
    * wallet_id로 참가기관 집 권한주소 얻기
    * signer 정보 채우기 위한 금결원 정보 얻기. endpoint 호출 시 RequestParam으로 전달. 즉, /v1/oracle/insertAuthority?comany=1
    * contractAddress, implContractAddress 구하기. 
    * sql 두 개 실행 후, DTO 만들기
    * 호출.
  * 10:45 일단 오라클 바우처 권한 부여 뼈대만 개발. wallet.sdk.demo 호출하는 것까지 테스트 됨. 나머지는 데이터 문제
  * 11:07 일단 화면 개발 시작하자.
  * 14:00 프론트엔드 소스 조사 중, 수호 아이오의 이충률 매니저가 와서 대략 설명해줌.
    * GET, POST는 /src/service/http/system.service.ts에 있는 것 사용.
    * 서버의 ApiResponse에 대응되는 타입을 만들었다.
      * /src/domain/http.ts에 SystemServerResponse라는 타입을 만듦.
    * 로그인한 사용자 정보는 AccountStoreService를 사용. 바우처 배포 생성 화면 page.ts에 사용례를 코딩함.
  * 16:47 또 바보같이 굴었다. 뭔가 잘 안 될 때 하나 하나 제대로 따져봐야 한다. 참말로...url이 제대로 되었는지부터 확인했어야 하지 않나..
  * 16:55 url prefix를 관리하는 방법
    * /src/constant/url.ts
      * ```javascript
// url.ts

export const API_PREFIX_VOUCHER = "/v1/voucher";
export const API_PREFIX_PAYMENT = "/v2/payment";
// Add more prefixes as needed

// Full URLs for specific endpoints
export const VOUCHER_DEPLOY_PRE_REQUEST = `${API_PREFIX_VOUCHER}/deployPreRequest`;
export const PAYMENT_INIT = `${API_PREFIX_PAYMENT}/initiatePayment`;
// Add more full URLs if needed
```