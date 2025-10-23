---
title: "September 3rd, 2024"
created: 2024-09-03 00:00:05
updated: 2024-10-07 11:28:42
---
  * 화요일
  * 06:01 출근
  * 오늘 할 일
    * 업무 메일 확인
    * 바우처 배포 실행 endpoint 개발
    * 배포 실행 트랜잭션 조회가 무엇이지 파악.
  * 명경지수 -> 명징한 생각
  * 06:18 DBeaver에서 한글이 깨지는 원인 추적 중.
    * /docker/data/mysql 지우고 docker 다시 실행해도 마찬가지
    * sql script 창에서 select 해도 한글이 다 깨짐.
    * 마지막 수단으로 엑셀로 export -> 역시 한글이 깨짐.
    * comment에 있는 한글은 정상인데 데이터에 있는 한글이 깨지는 것도 만들어짐. 이건 encoding이 어느 한 쪽에서 제대로 안 되는 것 같은데..
    * 수호쪽에서 쓴 mysql 버전이 오래됐다. 5.6 버전. 한글에 관해서는 하위호환성이 보장되지 않나?
    * mysql driver version 5.1.x를 받아서 설치했지만 그래도 안 된다.
  * 08:35 이정주 팀장에게 개발 관련 문의
  * 09:03 3개비
  * 10:10 이정주 팀장이 mysql procedure에 함수를 정의했다.
    * [x] GENERATE_ID
      * ```sql
CREATE DEFINER=`root`@`localhost` FUNCTION `bok-cbdc-voucher`.`GENERATE_ID`(prefix VARCHAR(5)) RETURNS varchar(18) CHARSET utf8mb4
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
    * [x] GET_CODE_NM
      * ```sql
CREATE DEFINER=`root`@`localhost` FUNCTION `bok-cbdc-voucher`.`GET_CODE_NM`(code_input VARCHAR(18)) RETURNS varchar(100) CHARSET utf8mb4
BEGIN
    DECLARE code_name_result VARCHAR(100);

    SELECT code_name INTO code_name_result
    FROM `bok-cbdc-voucher`.tb_ca_code
    WHERE code = code_input;

    RETURN code_name_result;
END```
    * 사용할 때는 sql안에서 함수 호출하듯이 매개변수를 넣어서 그냥 호출하면 된다.
  * 11:00 updateDeployRequest 작성 중.
  * 13:12 insertDeployRequest 테스트 OK
  * 13:23 deploy 실행 테스트 일단 OK. HD Key가 없다고 했지만 그래도 wallet sdk를 통해서 제대로 호출이 되었다는 뜻이리라.
  * 15:52 간단한 조회인데 이상하게 에러가 나서 한참을 헤맸다.
    * Caused by: org.apache.ibatis.reflection.ReflectionException: There is no getter for property named '_SELECT_QUERY_WRAPPER_' in 'class kr.or.cbdc.application.voucherManage.vc.deploy.dto.VcDeployRequestSearchDTO'
    * 알고 보니 mapper class에서 BaseMapList searchDeployRequests(VcDeployRequestSearchDTO vcDeployRequests); 이렇게 하면 에러가 나고 BaseMapList searchDeployRequests(@Param("query") VcDeployRequestSearchDTO vcDeployRequests); 이렇게 하면 에러가 안 난다.
    * http request url에 query string으로 전달된 DTO 매개변수가 sql xml에 **@Param이 필요**한 것 같다.
  * 16:51 이정주 팀장에게 문의한 결과
    * 바우처 배포 constructor param ^FWjHFBcc_
      * 항목: tb_ca_initl_factor.factor_name(tb_ca_vc_verification_result.contract_id로 찾아서 조회)
      * 값: 바우처 배포 승인 요청할 때 tb_ca_initl_factor_value에 있는 값
    * 오라클 배포 constructor param은 미정
  * [x] 16:56 이정주 팀장이 질문한 것은 AuthGuard 관련해서 jwt를 가지고 token별로 api 호출 권한을 따로 가져갈 수 있는 annotation이 있지 않냐는 것이었다.
  * 17:53 기간 비교를 겨우 해결했다.
    * DTO에서 날짜 부분을 LocalDateTime으로 했는데 이게 문제가 있다. front에서 보낼 때는 String 타입이다. 그래서 자꾸 안 되는데 이걸 아예 String 타입으로 해서 query에서 비교할 때만 STR_TO_DATE 함수로 바꿔서 해결했다.