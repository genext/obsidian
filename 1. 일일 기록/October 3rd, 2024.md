---
title: "October 3rd, 2024"
created: 2024-10-03 07:38:10
updated: 2024-10-03 14:49:23
---
  * 07:38 오늘 개천절 휴일이지만 출근.
  * 오늘 할 일
    * 업무 메일 확인
    * bytecode 처리하고 front에서 제대로 보내도록.
    * front로 날짜 정보 전달할 때 String이 아닌 LocalDateTime으로 문제가 없을지?
  * 명경지수 -> 명징한 생각
  * 07:48 프론트에서 bytecode 제대로 보내고 서버에서 제대로 받기 시작.
    * invalid params 에러:
      * front에서 보낼 때 Http request payload를 확인해보니 bytecode가 좀 이상?
        * ```plain text
bytecode: "\"608060405234801562000010575f80fd5b5060405162006```
        * 이걸 조치하고 정상으로 보내도 invalid params 발생.
        * 서버 로그를 자세히 보니 bytecode 끝에 '\n'이 붙어 있는 듯.
          * ```plain text
e8ef1620cfca88e1a4f92967c4b4277a42ae1258e1772b251cfc94f664736f6c63430008180033
, constructorParams=[0x10908341980F81985d3198a073aD803eB03ecb1B, 0x10908341980F81985d3198a073aD803eB03ecb1B, 088, 4881008604, 0xb9ff79a5f2a7944584d942f684365d92360640ec])```
    * 정상:
      * 프론트 http payload
        * ```plain text
bytecode: "608060405234801562000010575f80fd5b50604051620063```
      * 서버 로그
        * 자세히 보면 bytecode 이후 줄 바꿈이 없다.
        * ```plain text
e8ef1620cfca88e1a4f92967c4b4277a42ae1258e1772b251cfc94f664736f6c63430008180033, constructorParams=[0x10908341980F81985d3198a073aD803eB03ecb1B, 0x10908341980F81985d3198a073aD803eB03ecb1B, 088, 4881008604, 0xb9ff79a5f2a7944584d942f684365d92360640ec])```
    * 조치
      * 결국 눈에 보이지 않았지만 bytecode 끝에 붙은 new line 때문이었는데 이것도 한 번 더 주의해야 하는 것이 단순히 '\n'만 고려할 게 아니라 윈도우즈까지 감안해서 '\r\n'을 처리해야 한다. 따라서 최종 정상 코드는
        * ```javascript
const abiInfo =
        typeof voucherDetails?.abiInfo === "string"
          ? JSON.parse(voucherDetails.abiInfo)
          : voucherDetails?.abiInfo;

const bytecodeInfo = voucherDetails?.bytecodeInfo.replace(/[\r\n]+/g, "");```
  * 08:26 frontend에서 정상적으로 requestBody를 생성하도록 수정완료하니 이제 서버가 궁금해짐. 서버도 하드코딩으로 시작해서 하나씩 시도?
    * 08:41 하드 코딩으로 테스트할 필요없이 바로 나타남.
      * 프론트에서 나타난 것과 동일하게 bytecode에 '\n'이 있다!!! 그럼 대체 왜? 서버에 newline이 있나?
      * 08:53 아니 서버에서 그냥 모든 \:n', '\r\n'을 없애면 되는데 그래도 원인을 파악해 보자.
        * 원인은 템플릿을 저장한 테이블에 abi와 bytecode가 있는데 거기에 들어가 있는 모양.
      * 조치
        * 서버에서 다음과 같이 처리.
          * ```java
 String abiString = (String) codeInfo.get("abi_info");
        abiString = abiString.replaceAll("[\\r\\n]+", "");

 String bytecode = (String) codeInfo.get("bytecode_info");
        bytecode = bytecode.replaceAll("[\\r\\n]+", "");```
  * 09:19 이제 프론트를 모든 배포 관련 데이터를 묶어서 무거운 요청을 보내는 대신 원래대로 id 등 값만 전송해서 배포하기.
  * 09:31 일단 바우처 배포 실행 시 invalid params 에러 고친 것 commit 완료
  * 11:28 바우처 계약정보 관리 중 서비스 계층에 있는 insertRegister는 @Transactional 이 없었어도 RuntimeException이 발생하니까 자동으로 rollback 되었다.
    * 하지만 확실하게 하는 것이 좋을 것 같아서 @Transactional을 추가.
  * 12:01 휴일 식대 얼큰한 수제비 11,500 ^clfNZO36N
  * 13:14 rebase 하면서 보니 바우처 승인관리 화면이 안 되어 있네. 조회 조건만 거기 있는 것 쓰고 나머지는 코드는 복사해서 넣기로 한다.
  * 14:49 일단 집에 가서 운동하기로 결정.