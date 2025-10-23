---
title: "September 9th, 2024"
created: 2024-09-09 00:00:07
updated: 2024-10-05 20:53:09
---
  * # 월요일
  * 06:02 출근
  * 오늘 할 일
    * 업무 메일 확인
    * [[September 3rd, 2024#^FWjHFBcc_|바우처 배포 constructor param]] 재확인
    * [[September 8th, 2024#^JrtjDnDym|{{DONE}} 이정주 팀장에게 문의]]
    * front로 날짜 정보 전달할 때 String이 아닌 LocalDateTime으로 문제가 없을지?
  * 명경지수 -> 명징한 생각
  * 06:25 DB 테이블에 데이터를 저장할 때 기본키를 Auto Increment로 자동생성하지 않고 굳이 GENERATE_ID, FN_UID 같은 함수를 만들어서 따로 생성하는 이유가 뭘까? 단순 숫자키가 인덱스로서 성능이 더 낫지 않은가?
    * 모든 것이 장단점이 있듯이 이것도 장단점이 있다.
    * auto-incremented numeric key
      * pros: fast, simple
      * cons: scalability, security concern
    * generated unique key
      * pros: slow
      * cons: distributed systems
    * 하지만 이해가 안 가는 점은 분산 시스템에서 key가 충돌할 가능성이 있다는 얘기다. 어차피 어느 테이블에서 생성한 키인지 알 텐데 왜 충돌한다는 것인지 모르겠다. 이메일 주소는 @으로 구분하기 때문에 시스템이 다르면 아이디가 동일해도 아무 문제 없다.
  * 09:11 이정주 팀장과 문답
    * 초기화값 순서가 정해져야 abi input param과 순서를 맞출 수 있지 않나?
      * 이정주: factor_id가 numeric key이므로 asc로 얻으면 된다.
    * 오라클 참가기관 권한 테이블 wallet_id는?
      * 이정주: 참가기관별 지갑이 두 개이기 때문.
    * transaction_*는?
      * 이정주: 이것도 wallet.sdk를 호출해서 받는 값이다. 이 때 signAndsendTx의 function name을 확인해서 호출
    * [x] scheduler 바우처 관리 테이블과 바우처 배포 테이블 연결하는 테이블에 데이터 저장하는 것
    * [x] 오라클 새로 등록 시, 기존 참가기관 권한을 자동으로 연결해서 새로 저장
  * 10:31 바우처 배포 실행 후 deployed_address와 hash, status 저장 시작
  * swagger authorization
    * SecurityFilterChain에서 일부 주석 처리
    * 또는 tb_ca_user에 있는 정보를 참고해서 처리 가능.
  * 11:49 배포 실행 테스트하는 이상하게 kafka가 오동작한다. 아까 wallet.sdk.demo를 같이 띄웠더니 그쪽으로만 데이터가 날아간다.
  * 14:37 배포 실행 테스트가 잘 안 돼서 디버그. 기존 cbdc-backend-sooho 대신 wallet.sdk.demo를 사용해보기로.
    * 일단 wallet.sdk.demo를 8085로 뜨게 하고 rest controller의 url도 /vc/v1/voucher/deploy 로 수정해서 테스트해보기로.
      * 깜박하고 cbdc-backend-sooho의 swagger 페이지에서 보내면 마찬가지로 timeout 날 때까지 응답을 돌려주지 않는다. 하지만 응답은 kafka에서 보내준 그대로 보여준다. 
      * swagger를 제대로 띄워서 테스트해보니 바로 duplicate requestId 응답이 온다.
      * 로그 상 차이는 아래 로그가 있으면 정상 처리되고 없으면 안 된다.
        * ```plain text
16:45:49.120 [Thread-0] DEBUG k.o.b.w.s.k.SdkKafkaConsumerSingleton - Kafka message consumed & processed. [topic=wallet-core.dev.transactions.response, offset=146, key=0xDeEbda439aEC0983a21363B8b0bDcf9EC4230CF6, value={"requestId":"VCD20240909000001","responseType":"deployContract","results":{"returnCode":"KMS001","errorMessage":"Duplicated requestId: VCD20240909000001"},"status":"FAILED","occurrenceTime":"2024-09-09 16:45:47"}, headers=RecordHeaders(headers = [], isReadOnly = false)]```