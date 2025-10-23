---
title: "September 30th, 2024"
created: 2024-09-30 00:00:08
updated: 2024-09-30 16:47:00
---
  * 06:00 출근
  * 오늘 할 일
    * 업무 메일 확인
    * 바우처 배포 후 배포 정보 관리 테이블 저장 테스트
    * front로 날짜 정보 전달할 때 String이 아닌 LocalDateTime으로 문제가 없을지?
  * 명경지수 -> 명징한 생각
  * 09:03 블록체인에서 배포(deployContract)나 참가기관권한추가(addPartManagers)가 안 되는 것을 objectMapper로 바꿔서 테스트해도 동일하게 에러 발생.
    * constructorParams
      * ```json
 "constructorParams": [
        "0x10908341980F81985d3198a073aD803eB03ecb1B",
        "0x10908341980F81985d3198a073aD803eB03ecb1B",
		"088",
		"4881008604",
		"0xb9ff79a5f2a7944584d942f684365d92360640ec"
    ]```
    * 백엔드에서 constructorParams를 넣는 여러 방법 시도
      * 그냥 constructorParams내 값들을 writeValueAsString을 써서 String으로 변환한 다음 List로 만들어서 보내기 
        * ```java
 public KafkaMessagesFromCore deployContract(DeployRequestDTO req) {
        final long kafkaConsumeStatusCheckerTimeoutMillis = 60000;  // Example timeout value
        final long kafkaConsumeStatusCheckerIntervalMillis = 1000;

        long startTime = System.currentTimeMillis();
        boolean timeoutFlag = false;
        log.debug("constructorParama: {}", req.getConstructorParams());

        try {
          // Step 1: Put the request ID in the KafkaMessageConsumerThread (assumed service)
          KafkaMessageConsumerThread.putKey(req.getRequestId());

          ObjectMapper objectMapper = new ObjectMapper();
          String constructorParamsJson = objectMapper.writeValueAsString(req.getConstructorParams());
          List<Object> constructorParamNew = List.of(constroctorParamsJson);

           // Step 2: Call the SDK to deploy the contract
            KafkaProduceResponse kafkaProduceResponse = contractManager.deployContract(
                    req.getRequestId(),
                    req.getSigner(),
                    req.getAbi().toString(),
                    req.getBytecode(),
                    constructorParamsNew);
//            req.getConstructorParams());

            // Step 3: Wait for Kafka message consumption to finish
            while (true) {
                if (KafkaMessageConsumerThread.kafkaConsumeIsFinishedFor(req.getRequestId())) {
                    break;
                }

                // Check if max timeout has been reached
                long elapsedTimeMillis = System.currentTimeMillis() - startTime;
                if (elapsedTimeMillis >= kafkaConsumeStatusCheckerTimeoutMillis) {
                    timeoutFlag = true;
                    break;
                }
                // Sleep before the next check
                TimeUnit.MILLISECONDS.sleep(kafkaConsumeStatusCheckerIntervalMillis);
            }

            long endTime = System.currentTimeMillis();
            double elapsedTimeSeconds = (endTime - startTime) / 1000.0;

            // Step 4: Retrieve the Kafka messages related to the request
            KafkaMessagesFromCore kafkaMessagesFromCore = KafkaMessageConsumerThread.getKafkaMessagesFromCoreBy(req.getRequestId());

            // Register Kafka produce response and elapsed time
            kafkaMessagesFromCore.setKafkaProduceResponse(kafkaProduceResponse);
            kafkaMessagesFromCore.setElapsedTimeSeconds(elapsedTimeSeconds);
            if (timeoutFlag) {
                kafkaMessagesFromCore.setMaxTimeoutReached("true");
            }

            // Step 5: Remove the request ID from the consumer thread
            KafkaMessageConsumerThread.removeKey(req.getRequestId());

            return kafkaMessagesFromCore;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Thread interrupted: " + e.getMessage(), e);
        } catch (WalletSdkException e) {
            throw new RuntimeException("Wallet SDK error: " + e.getMessage(), e);
        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }
    }

```
      * 그냥 constructorParams내 값들을 writeValueAsString을 써서 String으로 변환한 다음 이것을 다시 readValue를 써서 List로 만들어서 보내기 
        * ```java
    public KafkaMessagesFromCore deployContract(DeployRequestDTO req) {
        final long kafkaConsumeStatusCheckerTimeoutMillis = 60000;  // Example timeout value
        final long kafkaConsumeStatusCheckerIntervalMillis = 1000;

        long startTime = System.currentTimeMillis();
        boolean timeoutFlag = false;
        log.debug("constructorParama: {}", req.getConstructorParams());

        try {
            // Step 1: Put the request ID in the KafkaMessageConsumerThread (assumed service)
            KafkaMessageConsumerThread.putKey(req.getRequestId());

            ObjectMapper objectMapper = new ObjectMapper();
            String constructorParamsJson = objectMapper.writeValueAsString(req.getConstructorParams());
            log.debug("Constructor Params as JSON: {}", constructorParamsJson);
            List<Object> constructorParamsList = objectMapper.readValue(constructorParamsJson, new TypeReference<List<Object>>() {});
            log.debug("Constructor Params as List<Object>: {}", constructorParamsList);

            // Step 2: Call the SDK to deploy the contract
            KafkaProduceResponse kafkaProduceResponse = contractManager.deployContract(
                    req.getRequestId(),
                    req.getSigner(),
                    req.getAbi().toString(),
                    req.getBytecode(),
                    constructorParamsList);
//            req.getConstructorParams());

            // Step 3: Wait for Kafka message consumption to finish
            while (true) {
                if (KafkaMessageConsumerThread.kafkaConsumeIsFinishedFor(req.getRequestId())) {
                    break;
                }

                // Check if max timeout has been reached
                long elapsedTimeMillis = System.currentTimeMillis() - startTime;
                if (elapsedTimeMillis >= kafkaConsumeStatusCheckerTimeoutMillis) {
                    timeoutFlag = true;
                    break;
                }
                // Sleep before the next check
                TimeUnit.MILLISECONDS.sleep(kafkaConsumeStatusCheckerIntervalMillis);
            }

            long endTime = System.currentTimeMillis();
            double elapsedTimeSeconds = (endTime - startTime) / 1000.0;

            // Step 4: Retrieve the Kafka messages related to the request
            KafkaMessagesFromCore kafkaMessagesFromCore = KafkaMessageConsumerThread.getKafkaMessagesFromCoreBy(req.getRequestId());

            // Register Kafka produce response and elapsed time
            kafkaMessagesFromCore.setKafkaProduceResponse(kafkaProduceResponse);
            kafkaMessagesFromCore.setElapsedTimeSeconds(elapsedTimeSeconds);
            if (timeoutFlag) {
                kafkaMessagesFromCore.setMaxTimeoutReached("true");
            }

            // Step 5: Remove the request ID from the consumer thread
            KafkaMessageConsumerThread.removeKey(req.getRequestId());

            return kafkaMessagesFromCore;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Thread interrupted: " + e.getMessage(), e);
        } catch (WalletSdkException e) {
            throw new RuntimeException("Wallet SDK error: " + e.getMessage(), e);
        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }
    }```
      * 그냥 constructorParams내 값들을 writeValueAsString을 써서 String으로 변환한 다음 이것을 for-loop를 써서 List로 만들어서 보내기 
        * ```java
    public KafkaMessagesFromCore deployContract(DeployRequestDTO req) {
        final long kafkaConsumeStatusCheckerTimeoutMillis = 60000;  // Example timeout value
        final long kafkaConsumeStatusCheckerIntervalMillis = 1000;

        long startTime = System.currentTimeMillis();
        boolean timeoutFlag = false;
        log.debug("constructorParama: {}", req.getConstructorParams());

        try {
            // Step 1: Put the request ID in the KafkaMessageConsumerThread (assumed service)
            KafkaMessageConsumerThread.putKey(req.getRequestId());

            ObjectMapper objectMapper = new ObjectMapper();
            String constructorParamsJson = objectMapper.writeValueAsString(req.getConstructorParams());
            log.debug("Constructor Params as JSON: {}", constructorParamsJson);

            List<Object> constructorParamsArrayList = new ArrayList<>();
            List<Object> jsonArray = objectMapper.readValue(constructorParamsJson, List.class);

            for (Object element : jsonArray) {
                constructorParamsArrayList.add(element);  // Wrapping each element in a List
            }

            log.debug("Constructor Params as List<List<Object>>: {}", constructorParamsList);

            // Step 2: Call the SDK to deploy the contract
            KafkaProduceResponse kafkaProduceResponse = contractManager.deployContract(
                    req.getRequestId(),
                    req.getSigner(),
                    req.getAbi().toString(),
                    req.getBytecode(),
                    constructorParamsArrayList);
//            req.getConstructorParams());

            // Step 3: Wait for Kafka message consumption to finish
            while (true) {
                if (KafkaMessageConsumerThread.kafkaConsumeIsFinishedFor(req.getRequestId())) {
                    break;
                }

                // Check if max timeout has been reached
                long elapsedTimeMillis = System.currentTimeMillis() - startTime;
                if (elapsedTimeMillis >= kafkaConsumeStatusCheckerTimeoutMillis) {
                    timeoutFlag = true;
                    break;
                }
                // Sleep before the next check
                TimeUnit.MILLISECONDS.sleep(kafkaConsumeStatusCheckerIntervalMillis);
            }

            long endTime = System.currentTimeMillis();
            double elapsedTimeSeconds = (endTime - startTime) / 1000.0;

            // Step 4: Retrieve the Kafka messages related to the request
            KafkaMessagesFromCore kafkaMessagesFromCore = KafkaMessageConsumerThread.getKafkaMessagesFromCoreBy(req.getRequestId());

            // Register Kafka produce response and elapsed time
            kafkaMessagesFromCore.setKafkaProduceResponse(kafkaProduceResponse);
            kafkaMessagesFromCore.setElapsedTimeSeconds(elapsedTimeSeconds);
            if (timeoutFlag) {
                kafkaMessagesFromCore.setMaxTimeoutReached("true");
            }

            // Step 5: Remove the request ID from the consumer thread
            KafkaMessageConsumerThread.removeKey(req.getRequestId());

            return kafkaMessagesFromCore;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Thread interrupted: " + e.getMessage(), e);
        } catch (WalletSdkException e) {
            throw new RuntimeException("Wallet SDK error: " + e.getMessage(), e);
        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }
    }```
    * 09:39 이상한 건 이정주 팀장 자리에서는 별 문제 없이 된다는 것. 이상한데..
      * 내 PC에서 안 되는 것이 이것 말고 또 있다. 며칠 전에 나타난 것은데 front에서 분명 한글로 보냈는데 서버에서 받을  때는 한글이 깨지는 것이다. 흠...다 내 PC안에서 이루어지는 것인데.
  * 10:09 계약 관리 정보 입력 후 배포 실행 점검 시작.
  * 13:34 "HttpServletRequest request"로 request 관련 모든 정보 알아내기
    * endpoint 인자에 추가.
      * ```java
  public ResponseEntity<ApiResponse<BaseMapList>> listAllMgts() -> public ResponseEntity<ApiResponse<BaseMapList>> listAllMgts(HttpServletRequest request)```
    * accessToken 얻어서 로그인 관련 정보 얻기
      * ```java
import kr.or.cbdc.infrastructure.framework.core.support.security.JwtUtil;

public class RestController {
  
  @Autowired
    private JwtUtil jwtUtil;

    @Operation(summary = "0.1.8.4 오라클 배포주소 목록 조회" )
    @GetMapping("/searchMgt")
    public ResponseEntity<ApiResponse<BaseMapList>> listAllMgts(HttpServletRequest request) {
      String authorizationHeader = request.getHeader("Authorization");
        if (authorizationHeader == null || !authorizationHeader.startsWith("Bearer ")) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST )
                    .body(ApiResponse.error(String.valueOf(HttpStatus.BAD_REQUEST.value()), "인증 정보가 없습니다."));
        }
        String bearerToken = authorizationHeader.startsWith("Bearer ")
                ? authorizationHeader.substring(7)
                : authorizationHeader;

        Map userInfo = jwtUtil.extractClaimsFromToken(bearerToken);

        Map<String, Object> result = this.dashboardService.select(userInfo);
        log.debug("++++++++++++++ userInfo: {}", result);
        log.debug("++++++++++++++ userInfo: {}", userInfo.get("userId"));
  ...
}```
  * 16:29 wallet.sdk 안 되는 문제는 jar 파일 교체로 해결. 이제부터 테스트를 하나씩 하기로.
    * 바우처 생성 및 승인 OK
    * 바우처 배포 실행 에러
      * signerInfo가 Null -> swagger를 써서 테스트하면 안 된다.
