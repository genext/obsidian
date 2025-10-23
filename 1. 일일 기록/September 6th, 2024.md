---
title: "September 6th, 2024"
created: 2024-09-06 00:00:08
updated: 2024-09-08 19:14:34
---
  * # 금요일
  * 06:14 출근. 오다가 대변 마려워서 동작역에서 해결하고 오느라 늦음.
  * 오늘 할 일
    * 업무 메일 확인
    * 정규표현식 해결

  * 명경지수 -> 명징한 생각
  * 06:44 AI도 정규표현식 문제를 해결하지 못하니 내가 공부해서 해결해야지.
  * [[Regex(Regular Expression)]]
  * 08:54 정규표현식이 못 찾는 이유를 찾았다.
    * windows에서는 filePath는 C:\...\ 이런 식으로 '\' backslash가 사용된다.
    * 하지만 linux는 '/'가 사용된다.
    * 그렇다면 그냥 간단하게 filePath를 linux 형식으로 바꾸면 될 거를 괜히 regular expression을 지지고 볶고 했다. 그냥 핵심만 바꾸자.
    * 어제 하홍준 박사가 이미 힌트를 줬다. 경로를 리눅스 형식으로 바꾸는 것.
  * 10:50 오라클 등록 개발 시작
    * file upload 확인
      * /vc/v1/verification/request endpoint를 차용
  * 11:13 갑자기 h키만 모든 창에서 계속 입력되는 현상이 일어나서 재부팅함. 다행히 이게 괜찮다.
  * 11:45 오라클 등록 개발 시작
    * 수신한 파일 정보(이름, 내용)를 클래스 생성자를 이용해서 파일 정보 클래스에 저장.
      * ```java
 private ContractFileInfo multipartFileToFileInfo(MultipartFile file) {
        if (file.getOriginalFilename().endsWith(".sol")) {
            try {
                return new ContractFileInfo(file.getOriginalFilename(), file.getInputStream());
            } catch (IOException e) {
                log.error("Error converting multipart file to file info", e);
                throw new RuntimeException(e.getCause());
            }
        } else {
            throw new IllegalArgumentException("File must have .sol");
        }
    }```
  * 12:59 minio에 파일 올리기
    * minio 서버에 전송 -> filepath 얻기
  * 13:25 이제 rest controller에서 다른 rest controller(solidity compiler)를 호출해야 한다. 
    * filepath를 compiler controller에 전달하면서 호출 -> abi, bytecode 얻기
    * RestTemplate을 사용해서 구현.
      * compiler controller는 input이 String이고 return이 {"bytecode": "...", "abi": "..."}이다.
      * return 값을 받을 DTO를 정의해야 하는데 이미 정의되었다. ContractCompileResultDto
      * 디버그할 때 정말 정신 차리고 해야 한다. 로그를 제대로 안 찍은 줄 모르고 로그에 안 나왔다고 데이터 제대로 못 받은 줄 알고 그걸 디버그하느라 시간 낭비했다.
    * 15:09 restTemplate으로 컴파일 호출해서 결과값 받는데 성공.
  * 15:48 유승헌 부장이 말하길 내가 엑셀 다운로드할 때 전에 grid library 고친 것 때문에 칼럼명이 안 나온다고 했다. 내가 그걸 원복을 안 했구나..사실 처음에 그리드 안 쓰고 혼자 만들 때는 필요했지만 이제 그리드 안에서 자동으로 하는 것을 쓴다면 내가 작업하느라 고쳤던 것을 원복했어야 했다.
  * 16:25 위 모든 정보를 모아서 DB에 저장 시작
  * 17:00 DB 저장 계속 개발
  * 17:15 오라클 파일 올리기 -> 컴파일 -> DB 저장까지 한 endpoint에서 한 번에 처리 개발 완료