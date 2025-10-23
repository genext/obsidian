---
title: "September 12th, 2024"
created: 2024-09-12 00:00:09
updated: 2024-10-03 14:27:42
---
  * 06:02 출근
  * 오늘 할 일
    * 업무 메일 확인
    * 로그인 문제? 개발?
    * cbdc-bok kafka thread 구동 확인
    * front로 날짜 정보 전달할 때 String이 아닌 LocalDateTime으로 문제가 없을지?
  * 명경지수 -> 명징한 생각
  * 명경지수라는 것은 단순한 고요가 아니다. 모든 마음이 가라앉은 상태다. 요즘 내가 디버그를 제대로 못하는 까닭은 그동안 내가 너무 성급하고 쫓기듯이 디버그했고 그래서 그게 습관화되어 기본적인 사항을 확인하지 않고 그냥 단지 휙휙 바쁘게 이것저것 살펴보기만 한 때문이다.
  * 금융결제원 스마트계약 관리시스템 로그인 안 되는 현상
    * 서버(application-voucher.yml)에 기동 포트 8085 및 프론트(.env.development)의 SYSTEM_SERVER_PORT 8085 확인.
    * 그런데 로그인 버튼 누르면 서버로 요청이 가지 않는다. 이게 정상?
    * export const EMAIL_PATTERN = /^[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,}$/;
      * 이메일을 제대로 입력해도 여기서 false를 돌려줌.
      * const EMAIL_PATTERN = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;로 수정했지만 여전히 에러.
    * 일단 어제 됐던 것은 이충렬 매니저가 정규표현식을 해결해서 된 것이 아니라 일단 그 부분을 막아서 된 것임.
  * 06:43 이제 로그인 안 되는 원인을 알았으니 DB 다시 생성해서 한글이 제대로 보이도록...
  * [x] 이정주 팀장에게 문의
    * tb_ca_vc_verification_result의 company_id는 참가기관이 되어야 하는 것이 아닌지?
  * 08:03 Datagrip이라는 DB 툴도 있다.
  * 08:24 테스트 데이터를 tb_ca_vc_verification_result에 추가했더니 바우처 배포 생성 실행 시 select에서 에러가 남. 
    * 에러
      * ```plain text
Caused by: org.apache.ibatis.exceptions.TooManyResultsException: Expected one result (or null) to be returned by selectOne(), but found: 2```
    * 원인:
      * 이 쿼리는 시스템에 로그인한 사람의 속한 은행의 권한지갑주소, 오라클 배포 주소, 관리주소를 얻는 것이기 때문에 은행별로 하나만 나와야 하는 것이 맞다. 그래서 바꿈.
        * ```sql
 SELECT
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
            tcc.bank_code
        FROM tb_ca_company tcc
        LEFT JOIN tb_ca_vc_verification_result tcvvr ON tcvvr.company_id = tcc.company_id
        INNER JOIN tb_ca_central_eoa_info tccei ON tccei.company_id = tcc.company_id AND tccei.usage_type = 'C0110002' --> LEFT를 INNER로 변경.
        WHERE tcc.company_id = #{companyId}```
  * [x] created_by, updated_by을 매개변수가 아닌 스프링 시스템에서 myBatis와 연계해서 자동으로 넣을 수 없나?
    * jwtUtil을 사용.
      * ```java
package kr.or.cbdc.infrastructure.framework.core.support.security;

import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

import javax.crypto.SecretKey;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Component;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.Jws;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import kr.or.cbdc.application.voucherManage.common.auth.mapper.AuthMapper;
import lombok.extern.slf4j.Slf4j;

@Component
@Slf4j
public class JwtUtil {

	private final SecretKey key;

	// Access Token 유효 시간: 1시간 (3600000)
	private final long ACCESS_TOKEN_VALIDITY = 3600000;
	// Refresh Token 유효 시간: 24시간 (86400000)
	private final long REFRESH_TOKEN_VALIDITY = 86400000;

	private final ZoneId zoneId;

	@Autowired
	private AuthMapper authMapper;

	public JwtUtil(ZoneId zoneId, @Qualifier("environment") Environment env) {
		this.zoneId = zoneId;
		// 환경 변수에서 SECRET_KEY 로드
		String secretKey = env.getProperty("SECRET_KEY");
		if (secretKey == null || secretKey.isEmpty()) {
			throw new IllegalArgumentException("SECRET_KEY is not set in the environment variables.");
		}
		this.key = Keys.hmacShaKeyFor(secretKey.getBytes());
	}

	public String createAccessToken(Integer userId) {
		LocalDateTime issuedAt = LocalDateTime.now(zoneId);
		LocalDateTime expiration = issuedAt.plusSeconds(ACCESS_TOKEN_VALIDITY / 1000);

		Map<String, Object> authDetails = authMapper.getUserDetailsById(userId);

		Map<String, Object> claims = new HashMap<>();
		claims.put("userId", userId);
		claims.put("companyId", authDetails.get("companyId"));
		claims.put("companyType", authDetails.get("companyType"));
		claims.put("bankCode", authDetails.get("bankCode"));
		claims.put("phone", authDetails.get("phone"));
		claims.put("grantId", authDetails.get("grantId"));
		claims.put("email", authDetails.get("email"));

		return Jwts.builder().claim("userInfo", claims)
			.subject(String.valueOf(userId))
			.issuedAt(convertToDate(issuedAt))
			.expiration(convertToDate(expiration))
			.signWith(key)
			.compact();
	}

	public String createRefreshToken(Integer userId) {
		LocalDateTime issuedAt = LocalDateTime.now(zoneId);
		LocalDateTime expiration = issuedAt.plusSeconds(REFRESH_TOKEN_VALIDITY / 1000);

		Map<String, Object> authDetails = authMapper.getUserDetailsById(userId);

		Map<String, Object> claims = new HashMap<>();
		claims.put("userId", userId);
		claims.put("companyId", authDetails.get("companyId"));
		claims.put("companyType", authDetails.get("companyType"));
		claims.put("bankCode", authDetails.get("bankCode"));
		claims.put("phone", authDetails.get("phone"));
		claims.put("grantId", authDetails.get("grantId"));
		claims.put("email", authDetails.get("email"));

		return Jwts.builder()
			.subject(String.valueOf(userId))
			.issuedAt(convertToDate(issuedAt))
			.expiration(convertToDate(expiration))
			.signWith(key)
			.compact();
	}

	private Date convertToDate(LocalDateTime dateTime) {
		return Date.from(dateTime.atZone(zoneId).toInstant());
	}

	public SecretKey getKey() {
		return this.key;
	}

	public Integer extractUserIdFromToken(String bearerToken) {
		try {
			return Jwts.parser()
				.verifyWith(key)
				.build()
				.parseSignedClaims(bearerToken)
				.getPayload()
				.get("userId", Integer.class);
		} catch (ExpiredJwtException e) {
			return e.getClaims().get("userId", Integer.class);
		} catch (Exception e) {
			log.error("[extractUserIdFromToken] Failed to extract userId from token: ", e);
			return null;
		}
	}

	public Map<String, Object> extractClaimsFromToken(String bearerToken) {
		try {
			Jws<Claims> jwsClaims = Jwts.parser()
				.verifyWith(key)
				.build()
				.parseSignedClaims(bearerToken);
			return jwsClaims.getPayload().get("userInfo", Map.class);
		} catch (ExpiredJwtException e) {
			log.error("[extractClaimsFromToken] Token has expired: ", e);
			return e.getClaims().get("userInfo", Map.class);
		} catch (Exception e) {
			log.error("[extractClaimsFromToken] Failed to extract claims from token: ", e);
			return null;
		}
	}

}```
      * rest controller에서 사용.
        * ```java
import kr.or.cbdc.infrastructure.framework.core.support.security.JwtUtil;

@Operation(summary = "0.1.8.0 오라클 배포주소 배포 실행")
    @PostMapping(path = "/deploy")
    public ResponseEntity<ApiResponse<String>> manageDeploy(@RequestBody ManageDeployRequest requestBody, HttpServletRequest httpRequest) {
        String authorizationHeader = httpRequest.getHeader("Authorization");
        if (authorizationHeader == null || !authorizationHeader.startsWith("Bearer ")) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST )
                    .body(ApiResponse.error(String.valueOf(HttpStatus.BAD_REQUEST.value()), "인증 정보가 없습니다."));
        }
        String bearerToken = authorizationHeader.startsWith("Bearer ")
                ? authorizationHeader.substring(7)
                : authorizationHeader;

        Map userInfo = jwtUtil.extractClaimsFromToken(bearerToken);

        Map<String, Object> result = this.dashboardService.select(userInfo);
        DeployRequestDTO req = manageService.prepareDeploy(requestBody.getMgtId());
        req.setCompanyId((String) userInfo.get("companyId"));
        KafkaMessagesFromCore response = contractDeploymentService.deployContract(req);

        DeploymentResultDTO deploymentResult = contractDeploymentService.handleDeploymentResult(response, req, manageDeployResultService);

        if (deploymentResult.isSuccess()) {
            // Return success response
            String successMessage = "Mgt Management deployed successfully";
            return ResponseEntity.ok(ApiResponse.success(String.valueOf(HttpStatus.OK.value()), successMessage, deploymentResult.getTransactionHash()));
        } else {
            // Return error response
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(ApiResponse.error(String.valueOf(HttpStatus.INTERNAL_SERVER_ERROR.value()), deploymentResult.getMessage()));
        }
    }```
  * 11:56 5개비
  * 15:34 바우처 승인 목록 조회를 상세조회와 단순 목록 조회로 나누기 작업 시작.
    * 일단 기존 조회 엔드포인트는 상세용으로 돌리고 목록 조회용 엔드포인트 개발 필요.
    * 15:35 서버 작업
      * sql, mapper, service, endpoint
    * 15:59 sql 분리하는 데에만 25분을 썼다.
  * 16:35 목록 조회, 상세 조회 분리 작업 완료
  * 16:35 프론트 분리 작업 시작