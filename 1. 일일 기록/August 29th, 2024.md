---
title: "August 29th, 2024"
created: 2024-08-29 08:01:09
updated: 2024-10-03 14:30:50
---
  * 07:16 출근
  * 오늘 할 일
    * 업무 메일 확인
    * 블록체인 helper 분석

  * 명경지수 -> 명징한 생각
  * 08:02 생각나는 대로 말하지 말자. 필요한 얘기인지 아닌지 정도는 판단할 수 있지 않나? 꼭 필요한 얘기가 아니면 일단 보류하자.
  * 09:53 모집관리에서 사용처 정보 제대로 표시하도록 테이블 데이터, 서버 sql, front 코드 수정 완료
  * 10:45 이정주 팀장에게서 업무 전달 받음.
    * frontend: 화면 개발 바우처 생성, 승인관리
      * source
    * backend: mysql DB는 local
      * 소스 받은 후 docker desktop 먼저 실행
      * gitbash 띄워서 프로젝트 디렉토리로 가서 start.sh 실행 --> local에 minio, sql 등 docker 이미지 받아서 실행.
        * [x] docker-compose.yml 참고
      * DB 테이블 변경사항 발생 시 /docker/data/mysql과 redis 디렉토리 삭제하고 bootRun 재실행
      * gradlew bootRun
      * error 및 조치
        * FN_UID 에러
          * func-all.sql 내 다음 sql 실행
            * ```sql
create  DEFINER='root'@'%' function  FN_UID(
    I_TYPE                          VARCHAR(1)
) RETURNS varchar(18) CHARSET utf8mb4
    NO SQL
    DETERMINISTIC
BEGIN

    DECLARE V_TYPE                          VARCHAR(1);
    DECLARE V_BASE_STR                      VARCHAR(36);
    DECLARE V_BASE_LEN                      TINYINT;
    DECLARE V_DATE_NUM                      BIGINT;
    DECLARE V_DATE_VAL                      VARCHAR(9);
    DECLARE V_SEQU_VAL                      VARCHAR(8);

    IF I_TYPE IS NOT NULL AND I_TYPE != '' THEN
        SET V_TYPE = I_TYPE;
    ELSE
        SET V_TYPE = '0';
    END IF;

    SET V_BASE_STR = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    SET V_BASE_LEN = LENGTH(V_BASE_STR);
    SET V_DATE_NUM = DATE_FORMAT(SYSDATE(), '%Y%m%d%H%i%s');
    SET V_DATE_VAL = '';

    WHILE V_DATE_NUM >= V_BASE_LEN DO
        SET V_DATE_VAL = CONCAT(SUBSTRING(V_BASE_STR, MOD(V_DATE_NUM, V_BASE_LEN) + 1, 1), V_DATE_VAL);
        SET V_DATE_NUM = TRUNCATE(V_DATE_NUM / V_BASE_LEN, 0);
    END WHILE;

    SET V_DATE_VAL = CONCAT(SUBSTRING(V_BASE_STR, V_DATE_NUM + 1, 1), V_DATE_VAL);

    IF V_TYPE = '1' THEN
        SET V_SEQU_VAL = LEFT(HEX(AES_ENCRYPT(SYSDATE(), RAND() * RAND())), 8);
    ELSE
        SET V_SEQU_VAL = UCASE(LEFT(REPLACE(UUID(), '-', ''), 8));
    END IF;

    RETURN CONCAT(V_DATE_VAL, V_SEQU_VAL, V_TYPE);

END```
        * FN_UID는 테이블 primary key를 일정한 규칙에 따라 자동생성하기 위한 도구
    * wallet sdk demo backend: 포트는 8051
      * nas2에 있는 zip 소스
      * hosts 파일에 다음 세 개 추가
        * 127.0.0.1 kafka-1
        * 127.0.0.1 kafka-2
        * 127.0.0.1 kafka-3
      * docs에 있는 json 파일을 postman에서 import
  * 11:25 검증쪽 신속하게 개발하기 위한 준비
    * 화면 정의서, 인터페이스 정의서
    * 검증쪽에서 개발할 기능과 비슷한 것을 구현한 것을 찾아서 재활용
    * 일단 한 화면에 대해서 front-backend 개발하고 나머지는 복사해서 사용?
    * 남은 기간 2주일
    * 개발할 화면과 백엔드 기능
      * F 바우처 배포 생성 화면
        * [x] 바우처 배포 승인 요청
      * F 바우처 승인 현황 목록 화면
        * [x] 바우처 승인 현황 목록 조회
        * [x] ==바우처 배포 실행==
      * 바우처 승인 현황 상세 화면
        * [x] 바우처 승인 현황 상세 조회
      * 배포된 바우처 목록 화면
        * [x] 배포된 바우처 목록 조회
      * 배포 실행 트랜잭션 화면
        * [x] 배포 실행 트랜잭션 조회
      * 배포 승인 목록
        * [x] 배포 승인 목록 조회
      * 배포 승인 상세
        * [x] 배포 승인 상세 조회
        * [x] 스마트계약 배포 승인
        * [x] 스매트계약 배포 반려
  * 14:24 vcdevelop 브랜치와 feature/vcdevelop-sooho 브랜치에서 블록체인 sdk 호출하는 부분을 비교 중.
  * 16:13 오늘 집중을 못 하네...
  * 17:56 cursor IDE 설치했다. 일단 프론트 개발할 때 활용해보기로.