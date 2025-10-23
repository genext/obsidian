---
title: "September 4th, 2024"
created: 2024-09-04 06:04:51
updated: 2025-01-27 08:57:03
---
  * # 수요일
  * 06:01 출근
  * 오늘 할 일
    * 업무 메일 확인
    * 바우처 배포 승인 요청 시 constructor param 값을 DB에 저장하는 것도 추가
    * 바우처 update 테스트
  * 명경지수 -> 명징한 생각
  * 06:40 바우처 배포 승인 요청 시 초기화 값 테이블 저장 추가 개발
  * [x] Global Exception handler도 다른 endpoint와 구조가 동일하다. AOP와 연결해서 다시 파악.
  * 06:57 unchecked Exceptions는 RuntimeException과 그 하위 클래스이며 이들은 따로 throw를 쓸 필요 없다.
  * 07:35 1개비
  * 08:07 바우처 배포 승인 요청 보완 개발
  * 08:13 바우처 배포 생성 화면 조회 테스트 중 에러
    * sql error
      * sql
        * ```sql
 SELECT
            (
                SELECT GROUP_CONCAT(tcvvr.template_name SEPARATOR ',')
                FROM tb_ca_vc_verification_result tcvvr2
                WHERE company_id = #{companyId}
            ) AS template_names,
            tcvvr.template_type,
            tccei.wallet_address,
            (
                SELECT deployed_address
                FROM tb_ca_oracle_mgt_info
            ) AS deployed_address,
           (
                SELECT GROUP_CONCAT(tscv.cd_value_nm ORDER BY tscv.sort_ordr SEPARATOR ',')
                FROM TB_SYS_CODE_VALUE tscv
                WHERE tscv.cd_group_id = ''
            ) AS cd_value_nms
        FROM tb_ca_company tcc
        LEFT JOIN tb_ca_vc_verification_result tcvvr ON tcvvr.company_id = tcc.company_id
        LEFT JOIN tb_ca_central_eoa_info tccei ON tccei.company_id = tcc.company_id
        WHERE tcc.company_id = #{companyId}```
      * ```plain text
Caused by: java.sql.SQLSyntaxErrorException: In aggregated query without GROUP BY, expression #2 of SELECT list contains nonaggregated column 'bok-cbdc-voucher.tcvvr.template_type'; this is incompatible with sql_mode=only_full_group_by```
      * 조치: 쓸데없이 tcvvr를 붙였다. 괄호 안에 묶은 것은 독립된 sql 이므로 바깥쪽 테이블 alias를 쓸 필요 없다.
  * 09:09 지금까지 바우처 배포 생성 관련 CRUD 테스트 완료. 화면과 비교 시작.
  * 09:57 바우처 승인 현황 목록 상세 화면에서 Initializer인 스마트계약 배포 정보(은행코드, 권한 주소, 오라클 배포 주소, 바우처 관리 주소)를 다른 테이블에서 조회하도록 sql 수정.
    * 기존 sql
      * ```sql
 SELECT
            tcvdr.deploy_request_id,
            tcvdr.voucher_name,
            tcvvr.template_name,
            GET_CODE_NM(tcvvr.template_type),
            tcvdr.voucher_requested_agency,
            GET_CODE_NM(tcvdr.status),
            tcvdr.abi_info,
            tcvdr.bytecode_info,
            tcvdr.deployed_address,
            tcvdr.deployed_transaction_hash,
            tcvdr.deployed_transaction_status,
            tcvdr.rejected_reason,
            tcvdr.approved_at,
            tcvdr.approved_by,
            tcvdr.rejected_at,
            tcvdr.rejected_by,
            tcvdr.deployed_at,
            tcvdr.deployed_by,
            tcvdr.template_id,
            tcvdr.created_at,
            tcvdr.created_by,
            tcvdr.updated_at,
            tcvdr.updated_by,
        FROM tb_ca_vc_deploy_request tcvdr
        INNER JOIN tb_ca_vc_verification_result tcvvr on tcvvr.template_id = tcvdr.template_id
        INNER JOIN tb_ca_company tcc on tcc.company_id = tcvvr.company_id
        LEFT JOIN tb_ca_initl_factor_value tcifv on tcifv.deploy_request_id = tcvdr.deploy_request_id 
        LEFT JOIN tb_ca_central_eoa_info tccei on tccei.company_id = tcc.company_id
        WHERE 1 = 1;```
    * tb_ca_initl_factor_value 테이블이 이상한 것이 factor_name이 항목이고 variable_name이 값이다. 그래서 한 deploy_request_id로 조회하면 항목이 4개면 결과가 4개가 나온다. 즉 가로로 칼럼이 펼쳐지는 것이 아니고 세로로 펼쳐진다. 따라서 rest controller의 return type은 BaseMapList이다. --> 이정주 팀장에게 문의한 결과, variable_name은 스마트계약에서 말하는 변수명이고 실제로 배포할 때는 변수명을 쓰지 않고 그냥 값만 json의 constructor param에 넣는다.
      * [[json]]_ARRAYAGG를 이용한 sql.
        * ```sql
 SELECT
            tcvdr.deploy_request_id,
            tcvdr.voucher_name,
            tcvvr.template_name,
            GET_CODE_NM(tcvvr.template_type),
            tcvdr.voucher_requested_agency,
            GET_CODE_NM(tcvdr.status),
            tcvdr.abi_info,
            tcvdr.bytecode_info,
            tcvdr.deployed_address,
            tcvdr.deployed_transaction_hash,
            tcvdr.deployed_transaction_status,
            tcvdr.rejected_reason,
            tcvdr.approved_at,
            tcvdr.approved_by,
            tcvdr.rejected_at,
            tcvdr.rejected_by,
            tcvdr.deployed_at,
            tcvdr.deployed_by,
            tcvdr.template_id,
            tcvdr.created_at,
            tcvdr.created_by,
            tcvdr.updated_at,
            tcvdr.updated_by,
            JSON_ARRAYAGG(
		        JSON_OBJECT(
		            'factor_name', tcifv.factor_name,
		            'variable_name', tcifv.variable_name
		        )
		    ) AS factor_values
        FROM tb_ca_vc_deploy_request tcvdr
        INNER JOIN tb_ca_vc_verification_result tcvvr on tcvvr.template_id = tcvdr.template_id
        INNER JOIN tb_ca_company tcc on tcc.company_id = tcvvr.company_id
        LEFT JOIN tb_ca_initl_factor_value tcifv on tcifv.deploy_request_id = tcvdr.deploy_request_id 
        LEFT JOIN tb_ca_central_eoa_info tccei on tccei.company_id = tcc.company_id
        WHERE 1 = 1
        GROUP BY tcvdr.deploy_request_id;```
  * 10:47 바우처 배포 생성 화면용 sql 수정
  * 11:19 바우처 배포 승인 신청과 실행 수정 개발 
  * 11:36 선택상자용 참가기관 조회 개발 --> 이미 있는 것 같은데..
  * 12:20 4개비
  * 13:55 5개비
  * 13:55 오라클 관리 개발
  * 15:45 6개비
  * 16:04 verification contract info 데이터를 새로 만들었다고 이걸로 바우처 배포 테스트 해보라고 해서 시도해보았는데...abi쪽에 문제가 있는 듯? ^Ggcuc5-aQ
    * ```plain text
{
  "status": "400",
  "message": "[requestId: VCD20240904000001] [ErrorCode: BWS101] wallet sdk error: Length mismatch between input parameters: 3 and abi definition inputs: 5",
  "success": false,
  "data": null
}```