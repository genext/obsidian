---
title: "September 5th, 2024"
created: 2024-09-04 09:19:26
updated: 2024-10-24 12:44:51
---
  * # 목요일
  * 06:01 출근
  * 오늘 할 일
    * 업무 메일 확인
    * daas 접속
    * 흐름도 재확인
  * 명경지수 -> 명징한 생각
  * 블록체인(blockchain) sdk 호출 정리(바우처 한정)
    * 호출 종류
      * 배포
        * ContractManager.deployContract(requestId, signer, abi, bytecode, constructorParam)
      * 거래
        * mint?
        * EoaWalletManager.signAndSendTx(requestId, walletType("central"), signer, contractAddr, contractAddr, function, function param(toAddress, amount))
      * 조회
        * QueryHandler.callQueryFn(requestId, walletType("central"), contractAddr, contractAddr, balanceOfFnName, function param(fromAddress))
  * 이정주 팀장 문의 사항
    * [[September 4th, 2024#^Ggcuc5-aQ|16:04 verification contract info 데이터를 새로 만들었다고 이걸로 바우처 배포 테스트 해보라고 해서 시도해보았는데...abi쪽에 문제가 있는 듯?]]
      * abi를 보면 input parameter를 정의한 부분이 있고 마지막에 constructorParams가 있다. 
        * constructor parameter용 매개변수가 5개 정의되었는데 내가 constructorParam에 세 개만 줘서 에러가 발생한 것이었다.
        * ```plain text
{
  "requestId": "con-dep-002",
    "signer": {
        "walletAddress": "0xDeEbda439aEC0983a21363B8b0bDcf9EC4230CF6",
        "hdKeyId": "9915c5d6-0985-36a4-920f-3293e3eea3de",
        "hdKeyAccToken": "eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJCS01TIiwiaWF0IjoxNzI1MjYyMTM0LCJzdWIiOiJCS01TX0hEX0tFWV9BQ0NfVE9LRU4iLCJhdWQiOiJXQVMiLCJleHAiOjE3NTY3OTgxMzQsImhkS2V5SWQiOiI5OTE1YzVkNi0wOTg1LTM2YTQtOTIwZi0zMjkzZTNlZWEzZGUifQ.qCm_R6JCekBve8ctC0pQqxdeW_L6Jan7IKNDRcoRZQ4"
    },
  "abi": [
    {
      "inputs": [
        {"internalType":"address","name":"defaultAdmin","type":"address"},
        {"internalType":"address","name":"manager","type":"address"},
        {"internalType":"string","name":"partId","type":"string"},
        {"internalType":"uint256","name":"expiry","type":"uint256"},
        {"internalType":"address","name":"voucherOracle","type":"address"}
      ],
      "stateMutability":"nonpayable",
      "type":"constructor"
      ...],
  "bytecode": ".....",
      "constructorParams": [
        "MyToken",
        "MYT",
        "0x05F3E96DB03b376a861FC74CE5A5D02D06B2ACd3"
      ]
    }```
    * [x] 바우처 배포 생성 화면 표시할 때 바우처 관리 주소 추가하도록
      * 나: 본사업에서 이미 관리 주소를 만들었다니 이걸 받아서 현재 테이블에 저장하고 연결 테이블에도 저장하면 되지 않나?
      * 이정주 팀장: 그래도 되는데 본사업은 proxy를 써서 배포를 두 번 했다. 그래서 나중에 테이블 구조가 바뀔 수도 있고 결정되면 알려주겠다.
    * [x] 바우처 배포 승인 요청 보낼 때 DTO에 abi와 bytecode를 어떻게 넣어야 하는지 문의. sol 컴파일 관련 전체 흐름 정리 필요.
      * front 파일 올리기 -> 서버에서 파일 받아서 컴파일 -> abi, bytes 획득 -> DB 저장 순으로 일괄 처리? 아니면?
      * 이정주 팀장:
        * 바우처 배포는 검증 의뢰 컨트랙트 정보(tb_ca_verification_contract_info)에 있는 abi, bytescode를 그대로 갖다가 쓰면 된다. 그리고 바우처 배포 생성 화면에 있는 큰 상자에는 content에 있는 것을 넣으면 된다.
        * 오라클 배포는 순서를 정해야 하는데 일단 한 번에 하는 것을 생각 중.
    * [x] front 개발을 언제쯤? 내일 아니면 다음주 월요일
  * 08:35 3개비
  * 08:45 DaaS 테이블(contract_address_abi)에 pbm(캐시백) 스마트계약 주소가 있지만 다른 주소는 뭔지 모르겠다.
  * 08:49 DaaS gitlab 접속해서 소스 확인
  * [x] 디자인 패턴 중 proxy 패턴 --> [[Design pattern]]에 정리
  * 09:21 배포 승인 요청 시 abi, bytecode 저장하는 부분 코딩 시작
    * 10:07 template_name 만 GROUP_CONCAT했는데 template_id와 template_type도 같이 쌍으로 묶어야 해서 GROUP_CONCAT안에 CONCAT 함수를 사용.
    * 11:08 content 길이가 너무 길어서 GROUP_CONCAT를 쓰면 content가 잘린다. 그래서 sql을 두 개로 분리하고 서비스에서 결과를 합치는 것으로 수정.
  * [x] 스마트계약 컴파일을 테스트해보고 통합해보기
  * 11:16 바우처 배포 승인 요청할 때 abi, bytecode를 tb_ca_verification_contract_info에서 읽어서 저장하도록 수정.
  * 13:13 sql insert 할 때 primary key가 생성된다. 이 값을 얻어서 다음 작업이 진행될 수 있게 하려면 insert 문 속성을 다음과 같이 해야 한다.
    * 키가 자동생성될 경우
      * ```sql
 <insert id="insertDeployRequest" useGeneratedKeys="true" keyProperty="deployRequestId">
  ...```
    * 하지만 이건 primary key가 auto increment를 통해 생성될 때만 사용하는 것이며 그렇게 속성을 정하면 myBatis가 자동생성된 키를 DTO에 저장한다. 이 프로젝트에서 하는 것처럼 GENERATE_ID 함수를 만들어서 쓰면 myBatis가 DTO에 키를 넣어주지 못함.
    * 키를 함수를 사용해서 만들 경우(mysql에서는 지원되지 않는다.)
      * ```sql
<insert id="insertDeployRequest">
 ...);
SELECT LAST_INSERT_ID(); -- Fetch the generated id
</insert>```
    * mysql에서 가능한 방법
      * parameterType, useGenerateKeys 속성 정하고 selectKey 태그를 사용.
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
        #{createdAt},
        #{createdBy},
        #{updatedAt},
        #{updatedBy}
        )
    </insert>
```
    * 이에 맞춰 변경한 service
      * ```java
@Transactional
    public void insertDeployRequest(VcDeployRequestInsertDTO vcDeployRequestInsert) {

        BaseMap abiAndBytecodeInfo = deployMapper.selectAbiAndBytecode(vcDeployRequestInsert.getTemplateId());
        vcDeployRequestInsert.setAbiInfo((String) abiAndBytecodeInfo.get("abi_info"));
        vcDeployRequestInsert.setBytecodeInfo((String) abiAndBytecodeInfo.get("bytecode_info"));

        deployMapper.insertDeployRequest(vcDeployRequestInsert);

        // DTO에서 key를 얻은다.
        String generatedDeployRequestId = vcDeployRequestInsert.getDeployRequestId();

        for (VcDeployRequestInsertDTO.InitializerDTO initializerDTO : vcDeployRequestInsert.getInitializer()) {
            deployMapper.insertInitializer(
                    initializerDTO.getFactorName(),
                    initializerDTO.getVariableName(),
                    initializerDTO.getDataType(),
                    initializerDTO.getDataValue(),
                    generatedDeployRequestId,
                    vcDeployRequestInsert.getCreatedAt(),
                    vcDeployRequestInsert.getCreatedBy(),
                    vcDeployRequestInsert.getUpdatedAt(),
                    vcDeployRequestInsert.getUpdatedBy()
            );
        }
    }```
  * 14:04 진짜로 배포가 되었다. abi constructor parameter 값을 제대로 주고 했더니 잘 되었다.
    * 성공한 json
      * ```json
{
    "requestId": "con-dep-002",
    "signer": {
        "walletAddress": "0xDeEbda439aEC0983a21363B8b0bDcf9EC4230CF6",
        "hdKeyId": "9915c5d6-0985-36a4-920f-3293e3eea3de",
        "hdKeyAccToken": "eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJCS01TIiwiaWF0IjoxNzI1MjYyMTM0LCJzdWIiOiJCS01TX0hEX0tFWV9BQ0NfVE9LRU4iLCJhdWQiOiJXQVMiLCJleHAiOjE3NTY3OTgxMzQsImhkS2V5SWQiOiI5OTE1YzVkNi0wOTg1LTM2YTQtOTIwZi0zMjkzZTNlZWEzZGUifQ.qCm_R6JCekBve8ctC0pQqxdeW_L6Jan7IKNDRcoRZQ4"
    },
    "abi": [{
      "inputs": [
        {"internalType":"address","name":"defaultAdmin","type":"address"},
        {"internalType":"address","name":"manager","type":"address"},
        {"internalType":"string","name":"partId","type":"string"},
        {"internalType":"uint256","name":"expiry","type":"uint256"},
        {"internalType":"address","name":"voucherOracle","type":"address"}
      ],
      "stateMutability":"nonpayable",
      "type":"constructor"
    },...{"inputs":[],"name":"vcExpiry","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}],
    "bytecode": "600818560208601613e50565b80840191505092......736f6c63430008180033",
    "constructorParams": [
        "0x10908341980F81985d3198a073aD803eB03ecb1B",
        "0x10908341980F81985d3198a073aD803eB03ecb1B",
        "partId",
        "2041088477",
        "0x10908341980F81985d3198a073aD803eB03ecb1B"

    ]
}```
  * 17:13 디버그를 제대로 해야지. 엉뚱하게 디렉토리 생성이 안 된다고 잘못 봤다가 나만 이상한 사람이 되겠다.