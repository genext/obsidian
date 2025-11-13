---
title: "August 1st, 2024"
created: 2024-08-01 00:00:00
updated: 2024-10-23 16:40:59
---
  * 06:54 출근
  * 오늘 할 일
    * 업무 메일 확인
    * [x] 바우처 유통관리 시스템 프로그램 목록과 테이블 연결
    * pbm, issue, sc 맞물려서 돌아가도록
  * 오늘 하고 싶은 것
  * 08:13 gitlab.ccmedia.co.kr의 내 계정에 ssh-key를 추가함.
  * 08:57 대표님 지시사항
    * [x] smartContract와 issue 키가 맞으면서 기어가 맞물려서 돌아가듯 만들기
    * [x] 의뢰기관, 사용처 골격은 대표가, 나는 전체(pbm, issue, sc, 의뢰기관, 사용처) 실행 여부 확인.
  * 09:39 [[디지털 바우처 회의록]] [[Roam/genext-2025-10-05-02-18-30/디지털 바우처 회의록#^wdKn75KCe|2024. 8. 1. 목.]]
  * 10:28 개발자가 단 한 명만 온다니...좋게 생각하자. 내가 코딩 많이 할 수 있는 기회다. 현명하게 chatGPT를 써야겠다.
  * 10:33 issue 생성 에러
    * Caused by: java.sql.SQLException: Field 'ISU_GROUP_ID' doesn't have a default value -> DB 테이블 ISU_GROUP_ID에서 Not null 삭제.
    * Caused by: java.sql.SQLException: Field 'USER_ID' do  esn't have a default value -> TbVcIsuMastrEntityMapper.xml의 insert sql에 USER_ID 추가.
    * Caused by: java.sql.SQLException: Column count doesn't match value count at row 1 -> TbVcIsuMastrEntityMapper.xml의 insert sql에 USER_ID에 대응되는 values 추가.
  * 10:47 issue update 테스트 OK. 이건 실질적으로 ISU_AMOUNT만 수정한다.
  * 10:48 issue 전체 조회가 안 된다. -> selectList sql 문에서 from 절 삭제.
  * 11:00 4개비
  * 11:08 issue CRUD 완료
  * 11:09 이제 pbm, issue, sc가 맞물리도록 foreign key 살펴 보기
    * 현재 TB_CSTMR_MASTR에 있는 테스트 데이터는 NHB 이용자인 듯.
  * 11:48 지금까지 우리가 bok에 만들었던 테이블을 모두 bokv로 옮기고 앞으로 bokv를 기준으로 개발할 예정.
  * 12:59 테이블을 bokv로 옮긴 후, 소스 config에서 DB 연결 정보를 bok에서 bokv로 수정해서 테스트했지만 에러가 남.
    * 이상하게 id를 dcapp으로 바꿔서 접속한다. 알고 보니 DB 시스템에서 procedure도 만들어야 했다. 
      * DB 시스템 중 Procedures에 함수가 5개 있음.
        * FN_CODE_NAME
          * ```sql
CREATE DEFINER=`root`@`%` FUNCTION `bokv`.`FN_CODE_NAME`(
    I_CODE_GROUP                    VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
  , I_CODE_VALUE                    VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
  , I_USER_LOCALE                   VARCHAR(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
  , I_DEFAULT_LOCALE                VARCHAR(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
  , I_DEFAULT_TEXT                  VARCHAR(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
) RETURNS varchar(500) CHARSET utf8mb4
    NO SQL
    DETERMINISTIC
BEGIN

    DECLARE R_VALUE VARCHAR(500);

    SELECT FN_TITLE(TSCV.CD_VALUE_ID, I_USER_LOCALE, I_DEFAULT_LOCALE, NULL)
    INTO   R_VALUE
    FROM   TB_SYS_CODE_VALUE TSCV
           INNER JOIN TB_SYS_CODE_GROUP TSCG ON TSCG.CD_GROUP_ID = TSCV.CD_GROUP_ID
    WHERE  TSCG.CD_GROUP = I_CODE_GROUP
    AND    TSCV.CD_VALUE = I_CODE_VALUE
    ;

    IF R_VALUE IS NULL THEN
        SET R_VALUE = IFNULL(I_DEFAULT_TEXT, I_CODE_VALUE);
    END IF;

    RETURN R_VALUE;

END```
        * FN_PERSON_NAME
          * ```sql
CREATE DEFINER=`root`@`%` FUNCTION `bokv`.`FN_PERSON_NAME`(
    I_PERSON_ID                     VARCHAR(18)  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
  , I_USER_LOCALE                   VARCHAR(5)  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
) RETURNS varchar(100) CHARSET utf8mb4
    DETERMINISTIC
BEGIN

    DECLARE R_VALUE VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

    SELECT TCP.PERSON_NM
    INTO   R_VALUE
    FROM   TB_COM_PERSON TCP
    WHERE  TCP.PERSON_ID = I_PERSON_ID
    ;

    RETURN R_VALUE;

END```
        * FN_TITLE
          * ```sql
CREATE DEFINER=`root`@`%` FUNCTION `bokv`.`FN_TITLE`(
    I_TITLE_CODE                    VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
  , I_USER_LOCALE                   VARCHAR(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
  , I_DEFAULT_LOCALE                VARCHAR(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
  , I_DEFAULT_TEXT                  VARCHAR(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
) RETURNS varchar(2000) CHARSET utf8mb4
    NO SQL
    DETERMINISTIC
BEGIN

    DECLARE R_VALUE                         VARCHAR(2000);

    SELECT TITLE_CN
    INTO   R_VALUE
    FROM   TB_SYS_TITLE
    WHERE  TITLE_CODE = I_TITLE_CODE
    AND    TITLE_LOCALE = I_USER_LOCALE
    ;

    IF R_VALUE IS NOT NULL AND R_VALUE <> '' THEN
        RETURN R_VALUE;
    END IF;

    IF I_USER_LOCALE <> I_DEFAULT_LOCALE THEN

        SELECT TITLE_CN
        INTO   R_VALUE
        FROM   TB_SYS_TITLE
        WHERE  TITLE_CODE = I_TITLE_CODE
        AND    TITLE_LOCALE = I_DEFAULT_LOCALE
        ;

        IF R_VALUE IS NOT NULL AND R_VALUE <> '' THEN
            RETURN R_VALUE;
        END IF;
    END IF;

    RETURN IFNULL(I_DEFAULT_TEXT, I_TITLE_CODE);

END```
        * FN_UID
          * ```sql
CREATE DEFINER=`root`@`%` FUNCTION `bokv`.`FN_UID`(
    I_TYPE                          VARCHAR(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
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
        * TN_USER_NAME
          * ```sql
CREATE DEFINER=`root`@`%` FUNCTION `bokv`.`FN_USER_NAME`(
    I_USER_ID                       VARCHAR(18)  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
    I_USER_LOCALE                   VARCHAR(5)  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
) RETURNS varchar(100) CHARSET utf8mb4
    NO SQL
    DETERMINISTIC
BEGIN

    DECLARE R_VALUE VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

    SELECT CASE WHEN TCPU.PERSON_ID IS NULL THEN
                TSU.LOGIN_NM
           ELSE
                FN_PERSON_NAME(TCPU.PERSON_ID, I_USER_LOCALE)
           END
    INTO R_VALUE
    FROM TB_SYS_USER TSU
    LEFT JOIN TB_COM_PERSON_USER TCPU ON TCPU.USER_ID = TSU.USER_ID
    WHERE TSU.USER_ID = I_USER_ID;

    RETURN R_VALUE;

END```
  * 테이블 연결관계 확실하게 구성 시작.
    * tb_vouch_mastr에 의뢰기관(tb_vouch_instt) 키를 foreign key로 지정. coin_mastr 키는 그냥 일반 칼럼으로.
    * tb_vouch_isu_mastr의 user_id를 cstmr_id로 변경. 소스도 마찬가지. 그 외 foreign key로 cstmr_id와 vouch_id 설정.
    * 14:43 foreign key cascade 설정 포함해서 tb_vouch_mastr와 tb_vouch_isu_mastr 테이블 재생성 완료
  * [x] 15:25 의뢰기관에서 바우처 관리한다고 할 때,
    * C: prt_cmpny_id가 같이 들어가도록. -> RequestBody에 prt_cmpny_id 항목 있음.
    * R: prt_cmpny_id로 조회하도록. myBatis mapper.xml에 if (prt_cmpny_id exists)문 추가
    * U: vouch_id와 prt_cmpy_id를 수정할 수 있게 하면 안 된다.
    * D: vouch_id만 있으면 된다. 작업 X
  * 15:33 메뉴에 url 삽입 시작
    * 메뉴 url 명명 규칙을 생각해봐야 할 듯. backend와 연결 방식 구분 기준.
  * 16:39 모집대상도 DB에 저장.
    * TB_CSTMR_MASTR 복사해서 TB_CSTMR_RCRIT
    * 모르겠다. TB_CSTMR_RCRIT에 바우처 ID를 넣자.
  * 17:23 yarn install할 때 repository 연결 에러가 나면 yarn.lock을 지워야 한다. 중요!!!!
    * 빌드도 되고 실행도 되었지만 로그인에서 에러 발생.
```plain text
[HPM] Error occurred while proxying request localhost:3001/common/config/readConfig to http://10.200.66.28:8080/ [ETIMEDOUT] (https://nodejs.org/api/errors.html#errors_common_system_errors)
```
      * [x] env 파일에 REACT_APP_PROXY_HOST를 우분투 서버 포트로 변경. 아래 파일 용도 파악 필요.
```plain text
REACT_APP_API_URL='/'
REACT_APP_PROXY_HOST='http://000.000.000.000:8085/'
PUBLIC_URL='/'
REACT_APP_DEV_TYPE='dev'
GENERATE_SOURCEMAP=false
```
      * 이후 로그인 할 때 OPT 번호를 또 입력해야 한다.
        * Google Authenticator에 내 OPT KEY를 등록.
          * chrome 확장 프로그램 google authenticator를 브라우저에 추가
          * 수동 입력을 선택해서 OTP KEY를 입력하면 OPT 번호를 받을 수 있다.
          * 이후 QR 코드를 생성하고서 내 핸드폰의 Google Authenticator로 QR를 읽으면 다음부터는 핸드폰에 OTP 번호가 뜬다.
  * 18:48 일단 menu_path를 db에 저장했다. 만일을 위해 TB_SYS_MENU를 csv로 백업.
  * 19:26 지급이 가장 어려울 것 같은데...
    * 이용자 목록을 for loop 돌면서 TB_VOUCH_ISU_MASTR에 하나씩 저장해야 한다.