---
title: "August 4th, 2024"
created: 2024-08-04 09:43:06
updated: 2024-10-23 16:39:55
---
  * 09:43 출근
  * 오늘 할 일
    * 업무 메일 확인
    * pbm과 sc를 transaction으로 묶기
    * 바우처 지급 트랜잭션 작성
  * 10:16 @EnableTransactionManagement를 DataSourceMainConfig에 추가
  * 11:24 지금까지 한 작업 정리
    * RestController에서 smartcontract 계약 후 바우처 테이블을 갱신한 부분을 ServiceImpl로 옮겨서 rest controller와 비즈니스 로직을 분리.
    * VcSmartContractManageServiceImpl가 다른 Bean을 Autowired로 한 것을 막아 버리고 Autowired한 것을 클래스의 final 속성으로 바꾸고 lombok의 RequiredArgsConstructor를 써서 자동으로 초기화되도록 수정. 그러니까 내가 TbVcMastrServiceImpl를 Autowired로 하려고 할 때 발생하는 에러가 나지 않음.
    * 서비스에 에러 처리(try/catch) 추가.
      * TransactionAspectSupport.*currentTransactionStatus*().setRollbackOnly();의 의미 파악
    * VcSmartContractManageRestController에서 쓸데없이 Autowired 사용한 것을 막고 RequireArgsConstructor를 이용하도록 주입 받는 Bean의 속성을 final로 함.
    * rest controller에서 쓸데없는 try/catch 구문 삭제
  * 12:10 개화 식사 신한카드 ^_ukSqOK-1
  * 12:59 바우처 지급 생성 시작
    * 설계 -> chatGPT 요청
  * 13:58 코딩 시작
    * cstmr쪽 xml, mapper, service 코딩 마치고 VcIsuManageServiceImpl에 cstmr쪽 서비스 호출 작성 중.
  * 14:25 코딩 계속
    * [x] 처음에는 그냥 New로 생성했다가 아래 코드 때문에 TbVcIsuMastr를 생성할 때 builder()로 생성하는 것으로 바꾸었다.
      * ```java
public class TbVcIsuMastr extends TbVcIsuMastrEntity {
  ...
  public TbVcIsuMastr newId() {
          this.setIsuId(IdGenerationUtil.createUid("TB_VOUCH_ISU_MASTR"));
  
          return this;
      }
}```
  * 15:00 아까 스마트컨트랙트 refactoring한 것 테스트 시작. -> 테스트 결과 정상.
  * 15:08 바우처 지급 생성은 전에 됐던 것 같은데 TB_VOUCH_MASTR를 바꾼 후 foreign key 제약 때문에 안 된다.
    * cstmr_id와 vouch_id가 제대로 있어야 바우처 지급 데이터가 생성됨
  * 15:16 바우처 지급 복수 생성 테스트 시작. -> 테스트 결과 정상. 이제 집에 퇴근!!