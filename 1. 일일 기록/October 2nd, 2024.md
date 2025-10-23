---
title: "October 2nd, 2024"
created: 2024-10-02 00:00:02
updated: 2024-10-02 17:14:44
---
  * 07:50 출근. 어제 잠을 못 자서 늦게 출근
  * 오늘 할 일
    * 업무 메일 확인
    * 바우처 배포 테스트를 위해 restTemplate 호출하는 endpoint 작성.
    * front로 날짜 정보 전달할 때 String이 아닌 LocalDateTime으로 문제가 없을지?
  * 명경지수 -> 명징한 생각
  * 09:04 contractManager.deployContract에 중단점을 설정하고 디버그한 결과, 요청 검증이 되고 kafka를 통해 블록체인쪽으로 메세지 전송이 제대로 된 것 확인.
    * 다만, kafka 응답에서 Invalid params가 떨어짐.
  * 09:18 wallet.sdk.demo와 cbdc-backend는 wallet.sdk 라이브러리 파일의 크기가 다르다.
    * 그래서 wallet.sdk.demo의 wallet.sdk 라이브러리를 cbdc-backend-sooho로 옮김.
      * 13:14 13:14 쓸데없는 로그가 많이 생겨서 다시 원상 복구.
    * 오라클 관리에서 배포는 잘 되지만 바우처 배포는 여전히 Invalid params 에러 발생.
  * 09:46 동일한 테스트 조건을 만들기
    * prepareDeploy를 동일하게 사용하고 그 결과를 restTemplate으로 송신 --> Invalid params 에러 발생. 그렇다면 역시 prepareDeploy가 문제?
    * prepareDeploy를 그대로 쓴 것은 아니지만 값만 복사해서 json 형태로 테스트하는 swagger에서 실행하면 정상적으로 실행. 역시 parepareDeploy 결과가 문제?
    * 10:13 결국 frontend에서 하드코딩한 것으로 보내니까 된다. 흠...
  * 10:45 확실하게 하기 위해 바우처 오라클 배포도 다시 테스트.
    * 이상하네...오라클 배포할 때는 동일한 prepareDeploy를 쓰는데 이건 아무 문제가 없잖아?
  * 11:00 일단 바우처 배포만 frontend에서 json body를 만들어서 보내는 것으로 바꾸기.
  * 12:33 지금 배포주소 관리하는 manage쪽 배포가 안 된다. sol 파일이 잘못된 듯.
    * error
      * ```plain text
 [ErrorCode: BWS800] wallet sdk error: Abi data not found accessing "addPartManagers type list" for contractAddress: 0x6682e7d9b5667e02ef2fb607ad99b4641d4b6e7d. error: Cannot invoke "kr.or.bok.wallet.sdk.abi.FunctionAbi.getTypeList()" because the return value of "kr.or.bok.wallet.sdk.abi.ContractAbi.getFunctionAbi(String)" is null```
    * 원인:
      * 14:48 배포주소 관리 스마트계약 배포 에러는 바우처 오라클 관리와 달리 addPartManagers를 안 쓰고 registVcAccount를 쓰기 때문.
  * 그래서 바우처 배포 후 tb_ca_register_vc_deployed_address에 데이터를 저장해야 하는데 바로 위 문제 때문에 배포는 성공했지만 전체 트랜잭션 실패.
  * 14:00 ContractDeploymentService에 바우처 계약정보 관련 DB 저장을 아무 생각없이 넣었다가 바우처 오라클 배포에서 에러 발생. 그 서비스 모듈은 스마트계약 배포 rest controller가 모두 사용하는 것이다.
  * 16:28 배포주소 관리 스마트계약 배포 성공. 아까 ContractDeploymentService에 insertRegister를 넣은 것이 잘못된 듯. 이건 바우처 오라클과 마찬가지로 나중에 은행과 바우처를 연결하면서 실행해야 할 듯.
  * 17:13 바우처 배포가 또 Invalid params 에러가 났다. 알고 보니 아까 됐던 것은 이렇게 보낸 것이었다. 그런데 내가 방심하고 하드코딩된 것을 변수로 바꿨더니 그 때부터 invalid params 에러 발생. 변수값을 또 변환해야 하는가...
