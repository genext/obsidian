---
title: "October 15th, 2024"
created: 2024-10-15 00:00:06
updated: 2024-10-22 17:48:55
---
  * 06:01 출근
  * 오늘 할 일
    * 업무 메일 확인
    * 에러 표시 창 확인 테스트 --> OK
    * 에러 유발 테스트
  * 명경지수 -> 명징한 생각
  * 07:53 이정주 팀장 회의
    * 배포주소 관리에서 몇 가지 개선할 점.
      * ~~파일 업로드 후 바로 배포하지 않고 나중에 배포할 때 배포실행 버튼이 안 나타남.~~
      * ~~배포 실행 후 화면 데이터 재표시~~
      * ~~파일 업로드 전까지 배포 실행 버튼 비활성화~~
      * ~~관리목록에서 최신 데이터 desc로~~
  * 09:26 배포주소, 오라클 개선 작업 중 휴식
  * source 수집
    * frontend(React) ^3FmLBEtEd
      * git: ![[100. media/archives/jiiU9ROLA3.zip]]
    * backend([[Spring boot]])
      * git: ![[100. media/archives/w_8RmawuZ9.zip]]
      * sql에서 사용 하는 DB function ^lFUU2FPCq
        * FN_UID
          * ```sql
CREATE DEFINER=`root`@`%` FUNCTION `bok-cbdc-voucher`.`FN_UID`(
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
        * GENERATE_ID
          * ```sql
CREATE DEFINER=`root`@`localhost` FUNCTION `bok-cbdc-voucher`.`GENERATE_ID`(prefix VARCHAR(5)) RETURNS varchar(18) CHARSET utf8mb4 COLLATE utf8mb4_general_ci
    READS SQL DATA
BEGIN
    DECLARE new_id VARCHAR(18);
    DECLARE today_date VARCHAR(8);
    DECLARE max_id INT;

    SET today_date = DATE_FORMAT(CURDATE(), '%Y%m%d');

    CASE prefix
        WHEN 'REQ' THEN
            SELECT IFNULL(MAX(CAST(SUBSTRING(req_id, 12) AS UNSIGNED)), 0) + 1
            INTO max_id
            FROM `bok-cbdc-voucher`.tb_ca_vc_verification_request
            WHERE req_id LIKE CONCAT(prefix, today_date, '%');
        WHEN 'ORA' THEN
            SELECT IFNULL(MAX(CAST(SUBSTRING(oracle_id, 12) AS UNSIGNED)), 0) + 1
            INTO max_id
            FROM `bok-cbdc-voucher`.tb_ca_oracle_mgt_info
            WHERE oracle_id LIKE CONCAT(prefix, today_date, '%');
        WHEN 'MGT' THEN
            SELECT IFNULL(MAX(CAST(SUBSTRING(mgt_id, 12) AS UNSIGNED)), 0) + 1
            INTO max_id
            FROM `bok-cbdc-voucher`.tb_ca_vc_mgt_info
            WHERE mgt_id LIKE CONCAT(prefix, today_date, '%');
        WHEN 'VCD' THEN
            SELECT IFNULL(MAX(CAST(SUBSTRING(deploy_request_id, 12) AS UNSIGNED)), 0) + 1
            INTO max_id
            FROM `bok-cbdc-voucher`.tb_ca_vc_deploy_request
            WHERE deploy_request_id LIKE CONCAT(prefix, today_date, '%');
        WHEN 'VCT' THEN
            SELECT IFNULL(MAX(CAST(SUBSTRING(template_id, 12) AS UNSIGNED)), 0) + 1
            INTO max_id
            FROM `bok-cbdc-voucher`.tb_ca_vc_verification_result
            WHERE template_id LIKE CONCAT(prefix, today_date, '%');
        WHEN 'GR' THEN
            SELECT IFNULL(MAX(CAST(SUBSTRING(grant_id, 3) AS UNSIGNED)), 0) + 1
            INTO max_id
            FROM `bok-cbdc-voucher`.tb_ca_grant
            WHERE grant_id LIKE CONCAT(prefix, '%');
        WHEN 'COMP' THEN
            SELECT IFNULL(MAX(CAST(SUBSTRING(company_id, 5) AS UNSIGNED)), 0) + 1
            INTO max_id
            FROM `bok-cbdc-voucher`.tb_ca_company
            WHERE company_id LIKE CONCAT(prefix, '%');
        ELSE
            SET max_id = 1;
    END CASE;

    IF prefix = 'COMP' THEN
        SET new_id = CONCAT(prefix, LPAD(max_id, 9, '0')); -- COMP000000001
    ELSE
        SET new_id = CONCAT(prefix, today_date, LPAD(max_id, 6, '0')); -- For other prefixes
    END IF;

    RETURN new_id;
END```
        * GET_CODE_NM
          * ```sql
CREATE DEFINER=`root`@`localhost` FUNCTION `bok-cbdc-voucher`.`GET_CODE_NM`(code_input VARCHAR(18)) RETURNS varchar(100) CHARSET utf8mb4 COLLATE utf8mb4_general_ci
    READS SQL DATA
BEGIN
    DECLARE code_name_result VARCHAR(100);

    SELECT code_name INTO code_name_result
    FROM `bok-cbdc-voucher`.tb_ca_code
    WHERE code = code_input;

    RETURN code_name_result;
END```
        * GET_USER_EMAIL
          * ```sql
CREATE FUNCTION GET_USER_EMAIL(p_user_id INT)
RETURNS VARCHAR(255)
DETERMINISTIC
BEGIN
	DECLARE v_email VARCHAR(255);

	SELECT email
	INTO v_email
	FROM tb_ca_user
	WHERE user_id = p_user_id
	LIMIT 1;

	RETURN v_email;
END
```
  * 12:02 로그인 ID를 이메일로 바꾸는 작업 시작.
  * 15:17 오라클 항목추가하기에서 자꾸 transactionHash 값이 없다고 나온다. 이거는 다른 에러인 듯. 내 소스는 정상처리한다.
  * 17:01 사용상태 변경을 하다보면 사용 중이 두 개가 될 때가 있다.