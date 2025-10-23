---
title: "SQL"
created: 2024-02-25 10:37:40
updated: 2025-02-15 16:46:08
---
  * Visualizing a SQL Query
    * ![[100. media/image/2Pj1P3BNhC.png]]
  * sql 구성요소 ^5KW2fzI1_
    * ![[100. media/image/L_6rjrmQMa.png]]
  * sql 응용 사례
    * JOIN
      * JOIN의 중요한 특징 두 개
        * 왼쪽 테이블 모든 데이터 가져온다.
        * ON 조건으로 두 테이블의 cartesian product 중에서 일부만 추려낸다.
      * [[October 17th, 2024#^2UCcotfoi|16:36 두 개을 조인해서 조회할 때 한 쪽 테이블에 없는 데이터를 조회하려면 LEFT JOIN을 통해 특정 필드가 null인 것을 찾으면 된다.]]
    * CamelCase
      * [[October 17th, 2024#^lhCsMFJMo|17:10 서버에서 내려줄 때 CamelCase로 내려줘야 하면 sql의 AS를 써서 column명을 CamelCase로 바꾸면 간단하게 된다. ]]
    * Pagination
      * application layer에서 offset을 계산
        * PageDataDTO
          * ```javascript
package kr.or.cbdc.config.paging;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.SuperBuilder;

@Data
@SuperBuilder
@NoArgsConstructor
public class PagingDTO {

	@Schema(description = "페이지", example = "1")
	public Integer page;

	@Schema(description = "조회할 최대 행 수", example = "1000000")
	public Integer limit;

	@Schema(hidden = true)
	public Integer getOffset() {
		return (page - 1) * limit;
	}
}```
        * 다른 DTO가 pageDataDO 상속
          * ```javascript
package kr.or.cbdc.application.voucherManage.vc.oracle.dto;

import kr.or.cbdc.config.paging.PagingDTO;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

@Data
@EqualsAndHashCode(callSuper = false)
@NoArgsConstructor
public class VcOracleInfoSearchDTO extends PagingDTO {
    private String oracleId;
    private String oracleName;
    private String createdAt;
    private String updatedAt;
    private int createdBy;
    private int updatedBy;
}```
      * sql 작성 시 total count를 잊지 말 것. 아래 방식 말고 total count를 구하는 sql을 별도로 작성해서 쓰는 것도 가능.
        * 간단한 예
          * ```sql
    <select id="selectAllMgt" resultType="kr.or.cbdc.infrastructure.framework.core.support.collection.BaseMap">
        SELECT mgt_id,
        mgt_name,
        transaction_status,
        (SELECT count(*)
        FROM tb_ca_register_vc_deployed_address tcogb
        WHERE tcogb.mgt_id = tcomi.mgt_id) as authority_count,
        `usage`,
        GET_USER_EMAIL(created_by) as created_by,
        created_at,
        deployed_at,
        GET_USER_EMAIL(deployed_by) as deployed_by,
        updated_at,
        (
            SELECT COUNT(*)
            FROM tb_ca_vc_mgt_info
            WHERE 1= 1
            <if test="query.mgtName != null and query.mgtName != ''">
                AND mgt_name LIKE CONCAT('%', #{query.mgtName}, '%')
            </if>
        ) As totalCount
        FROM tb_ca_vc_mgt_info tcomi
        WHERE 1 = 1
        <if test="query.mgtName != null and query.mgtName != ''">
            AND tcomi.mgt_name LIKE CONCAT('%', #{query.mgtName}, '%')
        </if>
        ORDER BY `usage` DESC, updated_at DESC
        <if test='query.offset != null and query.limit != null'>
            <![CDATA[
        LIMIT #{query.limit} OFFSET #{query.offset}
        ]]>
        </if>
    </select>
```
        * 복잡한 예
          * ```sql
 <select id="searchDeployRequests"  resultType="kr.or.cbdc.infrastructure.framework.core.support.collection.BaseMap">
        SELECT
            tcvdr.deploy_request_id,
            tcc.company_name,
            tcvdr.voucher_name,
            tcvvr.template_name,
            GET_CODE_NM(tcvvr.template_type) AS template_type_name,
            GET_CODE_NM(tcvdr.status) AS status_name,
            tcvdr.status,
            tcvdr.created_at,
            GET_USER_EMAIL(tcvdr.created_by) as created_by,
            tcvdr.approved_at,
            GET_USER_EMAIL(tcvdr.approved_by) as approved_by,
            tcvdr.deployed_at,
            GET_USER_EMAIL(tcvdr.deployed_by) as deployed_by,
            tcvdr.rejected_at,
            GET_USER_EMAIL(tcvdr.rejected_by) as rejected_by,
            tcvdr.template_id,
        (SELECT COUNT(*) FROM tb_ca_vc_deploy_request tcvdr
        INNER JOIN tb_ca_vc_verification_result tcvvr on tcvvr.template_id = tcvdr.template_id
        INNER JOIN tb_ca_company tcc on tcc.company_id = tcvvr.company_id
        LEFT JOIN tb_ca_central_eoa_info tccei on tccei.company_id = tcc.company_id AND tccei.usage_type = 'C0110002'
        WHERE 1 = 1
        <if test="query.companyId != null and query.companyId != ''">
            AND tcvvr.company_id = #{query.companyId}
        </if>
        <if test="query.voucherName != null and query.voucherName != ''">
            AND tcvdr.voucher_name LIKE CONCAT('%', #{query.voucherName}, '%')
        </if>
        <if test='query.templateType != null and query.templateType != ""'>
            AND template_type = #{query.templateType}
        </if>
        <if test="query.createdAtStart != null and query.createdAtStart != ''">
            AND tcvdr.created_at &gt;= STR_TO_DATE(#{query.createdAtStart}, '%Y-%m-%d %H:%i:%s')
        </if>
        <if test="query.createdAtEnd != null and query.createdAtEnd != ''">
            AND tcvdr.created_at &lt;= STR_TO_DATE(#{query.createdAtEnd}, '%Y-%m-%d %H:%i:%s')
        </if>
        <if test="query.status != null and query.status != ''">
            AND tcvdr.status = #{query.status}
        </if>
        ) AS totalCount
        FROM tb_ca_vc_deploy_request tcvdr
        INNER JOIN tb_ca_vc_verification_result tcvvr on tcvvr.template_id = tcvdr.template_id
        INNER JOIN tb_ca_company tcc on tcc.company_id = tcvvr.company_id
        LEFT JOIN tb_ca_central_eoa_info tccei on tccei.company_id = tcc.company_id AND tccei.usage_type = 'C0110002'
        WHERE 1 = 1
        <if test="query.companyId != null and query.companyId != ''">
            AND tcvvr.company_id = #{query.companyId}
        </if>
        <if test="query.voucherName != null and query.voucherName != ''">
            AND tcvdr.voucher_name LIKE CONCAT('%', #{query.voucherName}, '%')
        </if>
        <if test='query.templateType != null and query.templateType != ""'>
            AND template_type = #{query.templateType}
        </if>
        <if test="query.createdAtStart != null and query.createdAtStart != ''">
            AND tcvdr.created_at &gt;= STR_TO_DATE(#{query.createdAtStart}, '%Y-%m-%d %H:%i:%s')
        </if>
        <if test="query.createdAtEnd != null and query.createdAtEnd != ''">
            AND tcvdr.created_at &lt;= STR_TO_DATE(#{query.createdAtEnd}, '%Y-%m-%d %H:%i:%s')
        </if>
        <if test="query.status != null and query.status != ''">
            AND tcvdr.status = #{query.status}
        </if>
        GROUP BY tcvdr.deploy_request_id
        ORDER BY tcvdr.created_at
        <choose>
            <when test="query.order != null and query.order.toLowerCase() == 'asc'">
                ASC
            </when>
            <otherwise>
                DESC
            </otherwise>
        </choose>
        <if test='query.offset != null and query.limit != null'>
            <![CDATA[
        LIMIT #{query.limit} OFFSET #{query.offset}
        ]]>
        </if>
    </select>```
    * 기본키(primary key) 생성할 때 Auto increment를 안 쓰고 mysql procedure 영역에 함수 정해놓고 쓸 때 기본키값을 미리 얻어서 그것으로 저장할 때.
      * myBatis sql
        * ```sql
 <insert id="insertDeployRequest" parameterType="kr.or.cbdc.application.voucherManage.vc.deploy.dto.VcDeployRequestInsertDTO" useGeneratedKeys="false">
        <selectKey resultType="String" keyProperty="deployRequestId" order="BEFORE">
            SELECT GENERATE_ID('VCD') AS deployRequestId;
        </selectKey>

       INSERT INTO tb_ca_vc_deploy_request (
        deploy_request_id,
        voucher_name,
        voucher_requested_agency,
        status,
        abi_info,
        bytecode_info,
        template_id,
        created_at,
        created_by,
        updated_at,
        updated_by
       ) VALUES (
        #{deployRequestId},
        #{voucherName},
        #{voucherRequestedAgency},
        #{status},
        #{abiInfo},
        #{bytecodeInfo},
        #{templateId},
        NOW(),
        #{createdBy},
        NOW(),
        #{updatedBy}
        )
    </insert>
```
    * UPDATE 동적 sql myBatis
      * ```sql
<update id = "updateDeployRequestStatus">
        UPDATE tb_ca_vc_deploy_request
        <set>
            status = #{status},
            updated_at = NOW(),
            updated_by = #{updatedBy}
            <if test="approvedBy != null">
                , approved_at = NOW(),
                approved_by = #{approvedBy}
            </if>
            <if test="rejectedBy != null">
                , rejected_at = NOW(),
                rejected_reason = #{rejectedReason},
                rejected_by = #{rejectedBy}
            </if>
            <if test="deployedBy != null">
                , deployed_at = NOW(),
                deployed_by = #{deployedBy}
            </if>
        </set>
        WHERE deploy_request_id = #{deployRequestId}
    </update>```
    * sql 질의 결과가 HashMap<String, Object>일 때 속성명과 값 한 쌍이 보통이지만 특수한 경우에 값에 해당하는 곳에 배열을 넣을 수 있다. mysql
      * 아래 보인 ront에게 보내는 [[json]] 응답 중 factor_values 속성은 배열이다. 테이블에서 얻은 값(속성명:값)을 배열로 만들기 위해서 [[json]]_ARRAYAGG 함수 사용
        * ```json
{
  "status": "200",
  "message": "상세 조회 완료",
  "success": true,
  "data": {
    "deploy_request_id": "VCD20241016000007",
    "voucher_name": "배포다시테스트1",
    "requestor_company_name": "신한은행",
    "voucher_requested_agency": "배포다시테스트1",
    "wallet_address": "0x10908341980F81985d3198a073aD803eB03ecb1B",
    "oracle_deployed_address": "0xb830d00ee4421b052930e7eceef667de2bf9d472",
    "mgt_address": "0x85e5797c6afdd62d275105e01909cf753ff0e639",
    "template_name": "서울시 청년 지원 바우처1",
    "template_type_name": "캐시백형",
    "status_name": "배포 완료",
    "status": "C0090004",
    "abi_info": "[{\"inputs\":[{\"internalType\":\"add...\"type\":\"function\"}]",
    "bytecode_info": "6080604052348...008180033\r\n",
    "deployed_address": "0x446f2e14a813f81f29653d00eef11cd8b806bb22",
    "deployed_transaction_hash": "0x0e5eb97aba70ecd877d7f98ff01edae851e4e12114124ff8effe16c1625713bb",
    "deployed_at": [
      2024,
      10,
      16,
      8,
      25,
      41
    ],
    "deployed_by": "jkoh5@hanmail.net",
    "rejected_reason": null,
    "approved_at": [
      2024,
      10,
      16,
      8,
      25,
      10
    ],
    "approved_by": "jkoh5@hanmail.net",
    "template_id": "VCT20241004000001",
    "factor_values": "[
		{
			\"data_type\": \"address\", 
			\"data_value\": \"0xDeEbda439aEC0983a21363B8b0bDcf9EC4230CF6\", 
			\"factor_name\": \"defaultAdmin\", 
			\"variable_name\": \"defaultAdmin\"
		}, 
		{
			\"data_type\": \"address\", 
			\"data_value\": \"0x10908341980F81985d3198a073aD803eB03ecb1B\", 
			\"factor_name\": \"manager\", 
			\"variable_name\": \"manager\"
		}, 
		{
			\"data_type\": \"string\", 
			\"data_value\": \"088\", 
			\"factor_name\": \"partId\", 
			\"variable_name\": \"partId\"}, 
		{
			\"data_type\": \"uint256\", 
			\"data_value\": \"4884740697\", 
			\"factor_name\": \"expiry\", 
			\"variable_name\": \"expiry\"
		}, 
		{
			\"data_type\": \"address\", 
			\"data_value\": \"0xb830d00ee4421b052930e7eceef667de2bf9d472\", 
			\"factor_name\": \"voucherOracle\", 
			\"variable_name\": \"voucherOracle\"
		}
	]",
    "file_name": "PBMWrapper.sol"
  }
}```
      * sql
        * ```sql
<select id="deployRequestDetail"  parameterType="string" resultType="kr.or.cbdc.infrastructure.framework.core.support.collection.BaseMap">
        SELECT
            tcvdr.deploy_request_id,
            tcvdr.voucher_name,
            tcc.company_name AS requestor_company_name,
            tcvdr.voucher_requested_agency,
            tccei.wallet_address,
            (
                SELECT deployed_address
                FROM tb_ca_oracle_mgt_info
                WHERE `usage` = 1
                LIMIT 1
            ) AS oracle_deployed_address,
            (
                SELECT deployed_address
                FROM tb_ca_vc_mgt_info
                WHERE `usage` = 1
            ) AS mgt_address,
            tcvvr.template_name,
            GET_CODE_NM(tcvvr.template_type) AS template_type_name,
            GET_CODE_NM(tcvdr.status) AS status_name,
            tcvdr.status,
            tcvdr.abi_info,
            tcvdr.bytecode_info,
            tcvdr.deployed_address,
            tcvdr.deployed_transaction_hash,
            tcvdr.deployed_at,
            GET_USER_EMAIL(tcvdr.deployed_by) as deployed_by,
            tcvdr.rejected_reason,
            tcvdr.approved_at,
            GET_USER_EMAIL(tcvdr.approved_by) as approved_by,
            tcvdr.template_id,
            (
                SELECT JSON_ARRAYAGG(
                    JSON_OBJECT(
                        'factor_name', ordered_factors.factor_name,
                        'variable_name', ordered_factors.variable_name,
                        'data_type', ordered_factors.data_type,
                        'data_value', ordered_factors.data_value
                    )
                )
                FROM (
                    SELECT tcifv.factor_name, tcifv.variable_name, tcifv.data_type, tcifv.data_value
                    FROM tb_ca_initl_factor_value tcifv
                    WHERE tcifv.deploy_request_id = tcvdr.deploy_request_id
                    ORDER BY tcifv.factor_id ASC  -- Order the data by factor_id
                ) AS ordered_factors
            ) AS factor_values,
            tcvci.file_name
        FROM tb_ca_vc_deploy_request tcvdr
        INNER JOIN tb_ca_vc_verification_result tcvvr on tcvvr.template_id = tcvdr.template_id
        INNER JOIN tb_ca_verification_contract_info tcvci ON tcvci.contract_id = tcvvr.contract_id
        INNER JOIN tb_ca_company tcc on tcc.company_id = tcvvr.company_id
        LEFT JOIN tb_ca_central_eoa_info tccei on tccei.company_id = tcc.company_id and tccei.usage_type = 'C0110002'
        WHERE tcvdr.deploy_request_id = #{deployRequestId}
        GROUP BY
            tcvdr.deploy_request_id,
            tcvdr.voucher_name,
            tcvdr.voucher_requested_agency,
            tccei.wallet_address,
            tcvvr.template_name,
            tcvvr.template_type,
            tcvdr.status,
            tcvdr.abi_info,
            tcvdr.bytecode_info,
            tcvdr.deployed_address,
            tcvdr.deployed_transaction_hash,
            tcvdr.deployed_at,
            tcvdr.deployed_by,
            tcvdr.rejected_reason,
            tcvdr.approved_at,
            tcvdr.approved_by,
            tcvdr.template_id;
    </select>```
      * rest controller
        * ```java
@Operation(summary = "0.1.3.5 바우처 승인 요청 상세", description = "바우처 승인 요청 상세")
    @GetMapping(path = "/deployRequestDetail")
    public ResponseEntity<ApiResponse<BaseMap>> deployRequestDetail(
            @RequestParam("deployRequestId") String deployRequestId) {
        if (deployRequestId == null || deployRequestId.trim().isEmpty()) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(ApiResponse.error(
                    String.valueOf(HttpStatus.BAD_REQUEST.value()), "바우처 ID가 없습니다."));
        }

        BaseMap results = vcDeployService.deployRequestDetail(deployRequestId);

        if (results != null && !results.isEmpty()) {
            return ResponseEntity.ok(ApiResponse.success(String.valueOf(HttpStatus.OK.value()), "상세 조회 완료", results));
        } else {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(ApiResponse.error(String.valueOf(HttpStatus.NOT_FOUND.value()), "일치하는 데이터가 없습니다."));
        }
    }```
    * MAX 사용례
      * 한 테이블의 동일한 속성이지만 code에 따라 여러 값이 있을 수 있다. 이 때 MAX를 안 쓰면 원하는 결과가 안 나온다.
      * MAX 안 쓴 경우
        * ```sql
 SELECT
            CASE WHEN tccei.usage_type = 'C0110001' THEN tccei.wallet_address END AS defaultAdmin,
            CASE WHEN tccei.usage_type = 'C0110002' THEN tccei.wallet_address END AS manager,
            (SELECT deployed_address
                FROM tb_ca_oracle_mgt_info
                WHERE `usage` = 1
                LIMIT 1) AS voucherOracle,
            (SELECT bank_code FROM tb_ca_company WHERE company_id = 'COMP000000003') as partId
        FROM tb_ca_central_eoa_info tccei
        WHERE tccei.company_id = 'COMP000000003';```
        * 결과
          * ```plain text
defaultAdmin                              |manager                                   |voucherOracle                             |partId|
------------------------------------------+------------------------------------------+------------------------------------------+------+
0xDeEbda439aEC0983a21363B8b0bDcf9EC4230CF6|                                          |0xb830d00ee4421b052930e7eceef667de2bf9d472|088   |
                                          |0x10908341980F81985d3198a073aD803eB03ecb1B|0xb830d00ee4421b052930e7eceef667de2bf9d472|088   |```
      * MAX를 쓴 경우, 한 행으로 결과를 얻음.
        * ```sql
<select id="getInitializerValue" parameterType="string"  resultType="kr.or.cbdc.infrastructure.framework.core.support.collection.BaseMap">
        SELECT
            MAX(CASE WHEN tccei.usage_type = 'C0110001' THEN tccei.wallet_address END) AS defaultAdmin,
            MAX(CASE WHEN tccei.usage_type = 'C0110002' THEN tccei.wallet_address END) AS manager,
            (SELECT deployed_address
                FROM tb_ca_oracle_mgt_info
                WHERE `usage` = 1
                LIMIT 1) AS voucherOracle,
            (SELECT bank_code FROM tb_ca_company WHERE company_id = #{companyId}) as partId
        FROM tb_ca_central_eoa_info tccei
        WHERE tccei.company_id = #{companyId}
    </select>```
        * 결과
          * ```plain text
defaultAdmin                              |manager                                   |voucherOracle                             |partId|
------------------------------------------+------------------------------------------+------------------------------------------+------+
0xDeEbda439aEC0983a21363B8b0bDcf9EC4230CF6|0x10908341980F81985d3198a073aD803eB03ecb1B|0xb830d00ee4421b052930e7eceef667de2bf9d472|088   |```
    * CASE 사용례
      * ```sql
SELECT
            CASE
                WHEN deployed_address IS NOT NULL AND deployed_address &lt;&gt; ''
                THEN 1
                ELSE 0
            END
        FROM tb_ca_vc_deploy_request
        WHERE deploy_request_id = #{deployRequestId}```
    * 기존 테이블에 칼럼 추가
      * ```sql
ALTER TABLE TB_VOUCH_RAMP_MASTR
ADD CBS_TRN_ACNO VARCHAR(100),
ADD CBS_TRN_DT DATETIME,
ADD MCA_GUID VARCHAR(100),
ADD CBS_TRN_SRNO VARCHAR(100);```
  * procedure/function
    * [[October 15th, 2024#^lFUU2FPCq|sql에서 사용 하는 DB function]]
