---
title: "September 25th, 2024"
created: 2024-09-25 00:00:07
updated: 2025-01-27 08:54:00
---
  * 오늘 할 일
    * 업무 메일 확인
    * 배포 테스트(wallet sdk과 동일한 방식으로 하되, devtool 의존성 제거)
    * 배포 테스트 OK 후 지금까지 개발한 것 처음부터 테스트
    * front로 날짜 정보 전달할 때 String이 아닌 LocalDateTime으로 문제가 없을지?
  * 명경지수 -> 명징한 생각
  * 09:36 contract 배포를 wallet.sdk 라이브러리 호출로 변경하는 작업 시작.
    * 작업 시작하기 전에 영향 범위를 먼저 분석했어야 한다. 관련 함수가 다른 데서도 쓰인다는 것을 모르고 괜히 합쳤다가 다시 나누었다.
    * 14:14 [[json]] 형식으로 된 Object 타입은 objectMapper를 통해 변환한다. Map<String, Object>로 형변환이 허용되지 않음.
    * [x] devtools는 함부로 쓸 일이 아니다. 검색해 보니 kafka singleton 관련하여 보고된 버그가 있었음.
      * 코드 고칠 때마다 매번 빌드 다시 하니 시간이 걸려서 불편하긴 하지만 외부 라이브러리 사용할 경우에는 영향이 있을 수 있다는 것을 잊지 말아야 함.
  * 11:45 간신히 wallet.sdk 라이브러리 호출하는 것으로 변경
  * 11:46 이제 오라클 배포 실행 시작. 그런데 파일 올리기에서 잘 안 되는 듯.
  * 12:21 오라클 파일 업로드는 swagger에서만 테스트한 것으로 한 듯. 화면은 안 건드리고...하아...답답.
  * 12:22 내가 develop-jkoh를 develop에 합쳤더니 build가 안 된다고. lint 점검에서 에러가..
    * [x] yarn run lint로 점검한다.
  * 14:21 배포 승인 목록 조회, 상세 조회 테스트 OK
  * 15:51 오라클 관리 상세 조회 화면이 아직 안 되어 있는 상태. 개발 시작.
    * rest controller에서 요청을 바로 처리하고 응답을 주면 간단하지만, 만약 다른 endpoint를 호출해야 한다면 accessToken을 잊지 말고 전달해야 한다.
    * [x] 전달 방법
      * rest controller
        * ```javascript
@Operation(summary = "0.1.8.1 오라클 배포주소 파일 업로드 및 등록" )
    @PostMapping(value = "/uploadMgtContract", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<ApiResponse<String>> createMgt(
            @RequestParam("mgtName") String mgtName,
            @RequestPart("file")MultipartFile file,
            @RequestHeader("Authorization") String authorizationHeader) throws Exception {
        // Extract the Bearer token from the Authorization header
        String accessToken = authorizationHeader.replace("Bearer ", "");

        ContractFileInfo contractFileInfo = multipartFileToFileInfo(file);

        VcMgtInfoInsertDTO vcMgtInfoInsertDTO = manageService.uploadAndCompile(mgtName, contractFileInfo, accessToken);

        String mgtId = manageService.insertMgt(vcMgtInfoInsertDTO);

        return ResponseEntity.ok(ApiResponse.success("201", "Mgt inserted successfully", mgtId));
    }
```
      * service layer
        * ```javascript
public VcMgtInfoInsertDTO uploadAndCompile(String mgtName, ContractFileInfo contractFileInfo, String accessToken) throws Exception {
        // send the file to minio server
        SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMdd_HHmmss");
        String currentDateTime = sdf.format(new Date());
        String filePath = contractFileService.uploadVerificationContract(currentDateTime, contractFileInfo);

        // Call compile endpoint
        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(accessToken);
        headers.set("Content-Type", "application/json");
        HttpEntity<String> requestEntity = new HttpEntity<>(filePath, headers);
        ContractCompileResultDto response = restTemplate.postForObject(compileUrl, requestEntity, ContractCompileResultDto.class);

        if (response != null) {
            VcMgtInfoInsertDTO vcMgtInfoInsertDTO = VcMgtInfoInsertDTO.of(
                    mgtName,
                    contractFileInfo.getContent(),
                    filePath,
                    contractFileInfo.getName(),
                    response.getAbi(),
                    response.getBytecode(),
                    0
            );
            return vcMgtInfoInsertDTO;
        }
        else {
            log.error("Received null response!!!");
            return null;
        }
    }```
  * 18:08 오라클 상세 조회 화면 개발 완료. 버튼 처리만 남음.
  * 20:51 로쉘이 사업을 조금 넓히면서 돈이 필요해서 다시 돈을 빌려서 송금 시작. 이번에는 내년 6월까지 돈 보내주지 않아도 된다.