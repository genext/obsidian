---
title: "September 27th, 2024"
created: 2024-09-27 06:00:53
updated: 2024-10-23 14:43:55
---
  * 06:00 출근
  * 오늘 할 일
    * 업무 메일 확인
    * [x] 오라클 등록 구현
      * 파일 업로드 후 (기존 엔드포인트 활용) 자동 조회.  -> 30 분
      * 배포 처리 -> 2시간
    * [x] 오라클 등록 및 배포까지 실행 한 후, EOA 등록 테스트 -> 10시까지 완료
    * [x] EOA DB 조회 -> 1시간. 11시 완료
    * [x] 바우처 배포 주소 관리 복사 구현 -> 2시간. 1시 완료
    * 바우처 배포 후 배포주소 테이블과 연결하는 테이블에 데이터 저장 -> 3시간. 5시 완료
    * front로 날짜 정보 전달할 때 String이 아닌 LocalDateTime으로 문제가 없을지?
  * 명경지수 -> 명징한 생각
  * 07:16 파일 업로드 후 결과 표시까지 완료하고 develop를 develop-jkoh로 rebase도 마침.
  * 08:02 오라클 배포에서 기존 개발 문제
    * deplyContract 예제가 있는 postman에 있는 대로 개발하다 보니 프론트엔드에서 블록체인 호출에 필요한 모든 입력값을 작성해야 하는 문제가 있었음. 사실 이것은 서버가 해야 하는 것이었다. 개발을 빨리 편하게 하려다 보니 간과한 것.
    * 수정방안
      * 서버에서는 oracleId만 수신
        * oracleService.insertAuthority()-에서 처리한 것과 비슷하게 처리해야 한다.
          * [x] requestId를 위한 oracleId 수집. --> @RequestParam으로 수신.
          * [x] 금결원 권한 데이터를 얻기 위한 oracleMapper.getSigner 호출.
          * [x] abi, bytecode를 수집 --> sql, mapper 신규 작성(getAbiBytecode)
          * [x]  constructionParams 수집
          * [x] contractDeploymentService.deployContract(DeployRequestDTO req)에게 인자로 넘겨줄 DTO 작성 --> DTO builder 참조.
        * 이 부분을 rest controller에 삽입.
      * frontend
        * [x] 호출 시 oracleId를 넘기기
  * 10:15 오라클 바우처 배포 코딩하고 테스트하는데 시간이 생각보다 걸린다. 지금 swagger에서 테스트했는데 endpoint가 실행되기도 전에 nullPointerException error 가능성이 있다며 실행 자체가 되지 않음.
    * 아 바보같다. 엉뚱한 endpoint를 호출했다. 오라클 관리의 배포 실행을 호출해야 했는데 엉뚱하게 바우처 배포 관리의 배포 실행을 호출했다. 그 때 오라클 관리의 배포실행처럼 request에 oracleId만 넘겨주면서 호출을 했다. 그런데 잘못 호출된 바우처 배포 관리의 배포 실행은 abi가 request에 있기를 기대한 것이었다. 그래서 nullPointerException 에러 발생.
  * [x] 10:29 백엔드에서도 사용자 정보를 accessToken에서 얻을 수 있다.
    * common/DashboardController와 DashboardService 참고.
  * JsonNode 형변환이 안 된다고..이걸 확실하게 파악해야겠다.
    * 이것도 objectMapper 사용
  * 11:04 드디어 배포 실행했지만 배포 에러. 바우처 배포 실행해도 동일한 에러 날까 테스트해보기로.
  * 11:08 이번에는 배포 승인, 반려 창이 문제다. 알고 보니 develop 브랜치에 있었음. 다행..
  * 바우처 배포 관리도 오라클 바우처 배포처럼 frontend가 모든 req를 만들어서 보내야 하는 것으로 개발되었다. 하...생각을 좀 하자.
    * 수정 방안도 위에서 했던 것과 동일하게, 다만 oracleId가 아닌 deployRequestId로 하고 추가로 참가기관에서 바우처 배포하기 때문에 signer는 참가기관으로 해야 한다. 따라서 companyId와 userId도 서버로 전달.
  * 11:46 바우처 배포 승인 확인 후 배포 버튼 추가 및 실행 테스트 완료. 이제 서버쪽 고칠 시간.
  * 12:32 바우처(pbm) 배포용 constructionParams 수집 및 저장 시작
  * [x] 14:08 일단 바우처 배포 관리의 배포도 오라클 바우처 배포 실행처럼 변경 완료. 하지만 테스트 실패. 입력값이 잘못 되었다고. 원인 나중에 파악
  * 14:08 일단 오라클 배포 실패 이유 찾기 시작.
  * 17:16 오라클 배포에서 계속 실패한다. 배열의 배열에서 문제가 되는 것 같은데 일단 나중에 해결하기로 하고 바우처 오라클 권한관리 목록 조회부터 구현.
  * [x] 장보기
    * 계란