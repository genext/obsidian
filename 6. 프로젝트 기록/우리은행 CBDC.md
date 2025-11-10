---
title: "우리은행 CBDC "
created: 2025-01-27 13:13:49
updated: 2025-09-07 12:49:42
---
## 2024.11.18. ~ 2025.4.30.
## 한 일
### 계정계/ 블록체인 조회 포함한 TD on/offRamp(개인, 사업자) 순서도 작성
### CBDC 시스템과 계정계 gw 역할을 하는 계정계 연결 API 호출 공통 모듈(apiService, umsGateway) 작성
### kafka listener(saga 테이블 이용) 수정.
### 탈회 대상자(사망,압류 포함) spring boot scheduler 처리
## JwtTokenFilter
### Source
#### build error?
```plain text
Build error. C:\develop\backend\org_back_end\src\main\java\kr\or\cbdc\application\common\user\filter\JwtTokenFilter.java:125: error: local variables referenced from a lambda expression must be final or effectively final
                    if ( PAYMENT_URL.stream().anyMatch(paymentUrl -> httpServletRequest.getRequestURL().toString().contains(paymentUrl))) {
```
```java
package kr.or.cbdc.application.common.user.filter;

import com.fasterxml.jackson.core.JsonProcessingException;
import io.jsonwebtoken.ExpiredJwtException;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import kr.or.cbdc.application.common.user.model.RequestModel;
import kr.or.cbdc.application.common.user.service.IpService;
import kr.or.cbdc.application.common.user.service.UserLoginServiceImpl;
import kr.or.cbdc.domain.main.model.sys.log.TbSysLog;
import kr.or.cbdc.domain.main.model.sys.user.TbSysUser;
import kr.or.cbdc.infrastructure.error.model.ErrorMessage;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.BizException;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.ErrorAssert;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.ErrorCode;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.InputParamException;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.SysException;
import kr.or.cbdc.infrastructure.framework.core.support.wrapper.BokContentCachingResponseWrapper;
import kr.or.cbdc.infrastructure.framework.web.context.request.RequestContextUtil;
import kr.or.cbdc.infrastructure.framework.web.servlet.http.HttpServletRequestUtil;
import kr.or.cbdc.infrastructure.logging.service.LoggingServiceImpl;
import kr.or.cbdc.infrastructure.user.AnonymousUser;
import kr.or.cbdc.infrastructure.util.TokenInfo;
import kr.or.cbdc.infrastructure.util.TokenUtils;
import kr.or.cbdc.interfaces.RequestIdCache;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.MDC;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.util.ObjectUtils;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;
import org.springframework.web.util.WebUtils;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.Date;
import java.util.List;
import java.util.UUID;

@Slf4j
@Component
@RequiredArgsConstructor
public class JwtTokenFilter extends OncePerRequestFilter {

    @Value("${spring.jwt.refresh-expired}")
    private Long refreshTokenExpired;

    private final TokenUtils jwtTokenProvider;
    private @Autowired UserLoginServiceImpl userLoginServiceImpl;
    private @Autowired LoggingServiceImpl loggingService;
    private final RequestIdCache<String, RequestModel> requestCache;
    private final IpService ipService;

    private List<String> PAYMENT_URL = List.of("/ewa/pay/payment","/ewa/acnut/depositConv","/ewa/acnut/convDeposit");

    @Override
    protected void doFilterInternal(HttpServletRequest httpServletRequest, HttpServletResponse httpServletResponse,
            FilterChain filterChain) throws ServletException, IOException {
    	httpServletRequest = HttpServletRequestUtil.getHttpServletRequest(httpServletRequest);
        String loginUser = AnonymousUser.USER_ID;
        String token = jwtTokenProvider.resolveToken(httpServletRequest);
        BokContentCachingResponseWrapper wrapperResponse = new BokContentCachingResponseWrapper(httpServletResponse);

        try {
            String requestBody = HttpServletRequestUtil.getRequestBody(httpServletRequest);
            TbSysLog tbSysLog = loggingService.create(requestBody, null);

            int check = 0;
            if (token != null && (check = jwtTokenProvider.isValidToken(token,
                    httpServletRequest.getRequestURL().toString())) > 0) {
                if (check != TokenUtils.OPT_CHECK && check != TokenUtils.BANK_ROLE_ONLY ) {

                    Cookie cookieRequestId = WebUtils.getCookie(httpServletRequest, "requestId");

                    String requestId = cookieRequestId.getValue();
                    if ( requestCache.get(requestId) == null ) {
                        log.error("{},{}",requestId, ErrorCode.UNAUTHORIZED_REQUESTiD.getMessage());
                        throw new BizException(ErrorCode.UNAUTHORIZED_REQUESTiD);
                    }
                    
                    LocalDateTime now = LocalDateTime.now();
                    Long time = now.toEpochSecond(ZoneOffset.UTC);
                    String requestHash = generateHash(requestId, httpServletRequest.getRequestURL().toString());
                    RequestModel past = requestCache.get(requestHash);
                    log.debug(" request id : [{}],  requestHash : [{}], body : []", requestId, requestHash, httpServletRequest.getRequestURL().toString());

                    if ( ObjectUtils.isEmpty(past)) {
                        requestCache.put(requestHash, RequestModel.builder().time(time).count(1).build());
                    } else {
                        throw new BizException(ErrorCode.SESSION_EXPIRED_ERROR);
                    } 

                    Cookie refreshToken = WebUtils.getCookie(httpServletRequest, "refreshToken");
                    if(refreshToken != null) {
//                        if (ObjectUtils.isEmpty(refreshToken)) {
//                            throw new BizException(ErrorCode.WRONG_REQUIRED);
//                        }

	                    TbSysUser userEntity = userLoginServiceImpl.refreshTokenRotation(refreshToken.getValue());
	                    if (ObjectUtils.isEmpty(userEntity)) {
                            log.info("BizException 3 refreshToken.getValue()=[{}]",refreshToken.getValue());
	                        throw new BizException(ErrorCode.DUPLICATE_USER_ID_OR_ERROR);
	                    }

					}

                    TbSysUser userEntity = userLoginServiceImpl.refreshTokenRotation(refreshToken.getValue());
                    if (ObjectUtils.isEmpty(userEntity)) {
                        throw new BizException(ErrorCode.DUPLICATE_USER_ID_OR_ERROR);
                    }

                    // 핀번호 인증 후 처리 
                    if ( PAYMENT_URL.stream().anyMatch(paymentUrl -> httpServletRequest.getRequestURL().toString().contains(paymentUrl))) {
                        jwtTokenProvider.validateOneTimeToken(token);                        
                    }

                } else if (check == TokenUtils.BANK_ROLE_ONLY ) {
                    String ip = ipService.getClientIP(httpServletRequest);
                    validateIp(ip, ipService.getIpList());
                }

                loginUser = TokenUtils.getCIFromToken(TokenUtils.USER_ID);
                Authentication auth = jwtTokenProvider.getAuthentication(token);
                SecurityContextHolder.getContext().setAuthentication(auth);
            }

            filterChain.doFilter(httpServletRequest, wrapperResponse);

        } catch (ExpiredJwtException eJwt) {

            log.debug("ExpiredJwtException");
            Date expire = eJwt.getClaims().getExpiration();
            ErrorAssert.notNull(expire, ErrorCode.ACCESS_DENIED);

            if ( eJwt.getClaims().get(TokenUtils.USER_DIV).toString().startsWith(TokenUtils.ROLE_BANK) ) {
                sendErrorResponse(httpServletResponse, HttpServletResponse.SC_UNAUTHORIZED,
                        " 타 시스템 접근 토큰이 오래됐습니다.");
                return;                
            }

            log.debug("reissueAccessToken start");
            Cookie refreshToken = WebUtils.getCookie(httpServletRequest, "refreshToken");
            // log.info("[before refreshToken]: {}", refreshToken.getValue());

            if (refreshToken == null) {
                sendErrorResponse(httpServletResponse, HttpServletResponse.SC_UNAUTHORIZED,
                        "비정상 접근입니다 토큰이 존재하지 않거나 오래됐습니다.");
                return;
            }

            final TokenInfo responseJson = userLoginServiceImpl.reissue(refreshToken.getValue());

            if (ObjectUtils.isEmpty(responseJson)) {
                sendErrorResponse(httpServletResponse, HttpServletResponse.SC_UNAUTHORIZED,
                        "일정시간 서비스 미사용으로 자동 로그아웃 되었습니다.");
                return;
            }

            loginUser = responseJson.getUserId();

            Authentication auth = jwtTokenProvider.getAuthentication(responseJson.getAccessToken());
            SecurityContextHolder.getContext().setAuthentication(auth);

            filterChain.doFilter(httpServletRequest, wrapperResponse);

            log.info("[after refreshToken]: {}", responseJson.getRefreshToken());
            if (responseJson instanceof TokenInfo) {
                TokenInfo tokenInfo = (TokenInfo) responseJson;
                wrapperResponse.setHeader("Set-Cookie",
                        "refreshToken=" + tokenInfo.getRefreshToken() + "; Path=/; HttpOnly; Max-Age="
                                + refreshTokenExpired);
                wrapperResponse.setHeader("Authorization",
                        "Bearer " + tokenInfo.getAccessToken());
            }

        } catch (InputParamException ex) {
            log.error("{}", ex.getMessage());
            sendErrorResponse(httpServletResponse, (ex.getErrorCode() != null ) ? ex.getErrorCode().getHttpCode() : HttpServletResponse.SC_UNAUTHORIZED ,
                    (ex.getMessage() != null) ? ex.getMessage() : ErrorCode.UNAUTHORIZED_ACCESS.getMessage());
            return;

        } catch (BizException eBiz) {
            log.error("{}", eBiz.getMessage());
            sendErrorResponse(httpServletResponse, (eBiz.getErrorCode() != null ) ? eBiz.getErrorCode().getHttpCode() : HttpServletResponse.SC_UNAUTHORIZED ,
                    (eBiz.getMessage() != null) ? eBiz.getMessage() : ErrorCode.UNAUTHORIZED_ACCESS.getMessage());
            return;

        } catch (Exception ex) {
            // this is very important, since it guarantees the user is not authenticated at
            // all
            log.error("{}", ex.getMessage());
            SecurityContextHolder.clearContext();
            sendErrorResponse(httpServletResponse, ErrorCode.UNAUTHORIZED_ACCESS.getHttpCode(), ErrorCode.UNAUTHORIZED_ACCESS.getMessage());
            return;
        } finally {
            MDC.put("userInfo", loginUser + "-" + RequestContextUtil.getClientIpAddress());

            if (!httpServletRequest.getServletPath().startsWith("/static")
                    && !httpServletRequest.getServletPath().endsWith("html")
                    && !httpServletRequest.getServletPath().endsWith("png")) {

                loggingService.updateRspnsSttusCode(httpServletResponse.getStatus(),
                        new String(wrapperResponse.getContentAsByteArray(),
                                wrapperResponse.getCharacterEncoding()));
            } else {
                loggingService.updateRspnsSttusCode(httpServletResponse.getStatus(), null);

            }

            String newRequestId = UUID.randomUUID().toString();
            requestCache.put(newRequestId, RequestModel.builder().count(0).build());

            wrapperResponse.addHeader("Set-Cookie",
            "requestId=" + newRequestId + "; Path=/; HttpOnly; Max-Age="
                    + refreshTokenExpired);            

            wrapperResponse.copyBodyToResponse();
        }
    }

    private void validateIp(String ip, List<String> ipList) {
        if (StringUtils.hasLength(ip) && !ObjectUtils.isEmpty(ipList)) {
            if (!ipList.contains(IpService.ALL_IP_ALLOWED) && !ipList.contains(ip)) {
                log.error(ErrorCode.IP_ADDRESS_UNAVAILABLE.getFormat(ip));
                throw new BizException(ErrorCode.IP_ADDRESS_UNAVAILABLE, null, ip);
            }
        } else {
            log.error(ErrorCode.IP_INITIALIZATION_FAILED.getMessage());
            throw new BizException(ErrorCode.IP_INITIALIZATION_FAILED);
        }
    }    

    private void sendErrorResponse(HttpServletResponse httpServletResponse, int status, String message)
            throws JsonProcessingException, IOException {
        httpServletResponse.setCharacterEncoding("UTF-8");
        httpServletResponse.setContentType("application/json");
        httpServletResponse.setStatus(status);
        httpServletResponse.getWriter()
                .write(ErrorMessage.builder().status(String.valueOf(status))
                        .message(message).build().toJson());

    }

        // Method to generate a hash from requestId and url
    public String generateHash(String requestId, String request)  {

        try {
            // 해시 생성
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hashBytes = digest.digest( (requestId + request).getBytes(StandardCharsets.UTF_8 ));
            StringBuilder hexString = new StringBuilder();
            for (byte b : hashBytes) {
                hexString.append(String.format("%02x", b));
            }
            return hexString.toString();

        } catch (NoSuchAlgorithmException e) {
            throw new SysException(ErrorCode.REQUEST_HASH_GENERATION_ERROR, e);
        }

    }

}
```
## sftp + job scheduler 구현
### dependency
#### ```xml
<dependency>
    <groupId>org.springframework.integration</groupId>
    <artifactId>spring-integration-sftp</artifactId>
</dependency>```
### config class
#### Instead of direct config values, you can use configuration class with better type safe
```java
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.integration.sftp.session.DefaultSftpSessionFactory;
import org.springframework.integration.sftp.session.SftpRemoteFileTemplate;

@Configuration
public class SftpConfig {
    @Value("${sftp.host}")
    private String sftpHost;
    
    @Value("${sftp.port}")
    private int sftpPort;
    
    @Value("${sftp.username}")
    private String sftpUser;
    
    @Value("${sftp.password}")
    private String sftpPassword;
    
    @Bean
    public DefaultSftpSessionFactory sftpSessionFactory() {
        DefaultSftpSessionFactory factory = new DefaultSftpSessionFactory(true);
        factory.setHost(sftpHost);
        factory.setPort(sftpPort);
        factory.setUser(sftpUser);
        factory.setPassword(sftpPassword);
        factory.setAllowUnknownKeys(true);
        return factory;
    }
    
    @Bean
    public SftpRemoteFileTemplate sftpRemoteFileTemplate() {
        return new SftpRemoteFileTemplate(sftpSessionFactory());
    }
}
```
### job scheduler
```java
package kr.or.cbdc.application.common.scheduler;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

import org.apache.commons.codec.binary.Base64;
import org.quartz.JobExecutionContext;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;

import kr.or.cbdc.application.ewa.cstmr.dto.DeactivateCstmrDto;
import kr.or.cbdc.application.ewa.cstmr.mapper.EwaDeactivateCstmrMapper;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.BaseException;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.ErrorCode;
import kr.or.cbdc.infrastructure.framework.core.support.scheduling.AnyJob;
import kr.or.cbdc.infrastructure.framework.core.support.scheduling.model.JobDetailTrigger;
import kr.or.cbdc.infrastructure.framework.core.support.scheduling.model.SchedulerJobConfig;
import kr.or.cbdc.infrastructure.util.CryptUtils;
import lombok.extern.slf4j.Slf4j;
import java.io.IOException;
import java.io.InputStream;
import org.apache.commons.io.IOUtils;
import org.springframework.integration.sftp.session.SftpRemoteFileTemplate;

@Slf4j
public class EwaDeactivateCstmrJob extends AnyJob {
    
    public static final String DataProcessing = "DeactivateCstmr";

    @Autowired
    private EwaDeactivateCstmrMapper ewaDeactivateCstmrMapper;
    
    private String fileBaseName = "DEDPESZPELIST";
    
    // @Value("${config.file.deactivate-customer.directory}")
    // private String fileDirectory = "/upload/RECV/";
    
    @Autowired
    private CryptUtils cryptUtils;

    @Autowired
    private SftpRemoteFileTemplate sftpRemoteFileTemplate;
    // @Value("${sftp.remote.directory}")
    private String remoteDirectory = "/upload/RECV/";

    // TODO 암호화 적용 후 아래 함수 뺄 것.
    private boolean isBase64Encrypted(String text) {
        try {
            return Base64.isBase64(text.getBytes());
        } catch (Exception e) {
            return false;
        }
    }
    private DeactivateCstmrDto parseLine(String line) throws Exception {
        // Validate basic format
        // Minimum length(test): D(1) + seqNo(10) + csno(11) + date(8) + code(2)
        // Minimum length(prd): D(1) + seqNo(10) + csno(24) + date(8) + code(2)
        if (line == null || line.length() < 32) {
            log.error("데이터가 잘못되었습니다. {}", line);
            throw new IllegalArgumentException("Invalid line length");
        }

        if (!line.startsWith("D")) {
            throw new IllegalArgumentException("Invalid line format - must start with 'D'");
        }
    
        int dateLength = 8;
        int codeLength = 2;
        
        String cusDscd = line.substring(line.length() - codeLength);
        String cusStsDtm = line.substring(line.length() - (codeLength + dateLength), line.length() - codeLength);
        
        // SEQ 10자리 이후부터, 줄 끝에서 날짜(8자리) + code(2자리)만큼 앞으로 이동한 자리 이전까지가 통합고객번호
        String encryptedItcsno = line.substring(11, line.length() - (codeLength + dateLength));
        
        String itCsno;
        if (isBase64Encrypted(encryptedItcsno)) {
            itCsno = cryptUtils.decrypt(encryptedItcsno);
            if (itCsno == null) {
                log.error("고객번호 복호화 실패: {}", encryptedItcsno);
                throw new IllegalStateException("Failed to decrypt customer number");
            }
        } else {
            log.warn("고객번호가 암호화되지 않았습니다: {}", encryptedItcsno);
            itCsno = encryptedItcsno;  // Use as-is if not encrypted
        }

        DeactivateCstmrDto customer = new DeactivateCstmrDto();
        customer.setItcsno(itCsno);
        customer.setCusDscd(cusDscd);
        customer.setCusStsDtm(cusStsDtm);
        
        return customer;
    }
    
    private int parseTrailerCount(String trailerLine) {
        if (trailerLine == null || !trailerLine.startsWith("T")) {
            throw new IllegalArgumentException("Invalid trailer line format");
        }
        try {
            return Integer.parseInt(trailerLine.substring(1).trim());
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("Invalid count in trailer line", e);
        }
    }


    @Override
    public void executeJob(SchedulerJobConfig jobConfig, JobDetailTrigger jobDetailTrigger,
        JobExecutionContext context) {
    
        log.info("Starting Deactivate Customer file processing job");

        // Check SFTP connection first
        try {
            sftpRemoteFileTemplate.execute(session -> {
                log.info("Successfully connected to SFTP server");
                return null;
            });
        } catch (Exception e) {
            log.error("Failed to connect to SFTP server: ", e);
            throw new BaseException(ErrorCode.SERVER_ERROR, e);
        }
      
        try {
            LocalDate yesterday = LocalDate.now().minusDays(1);
            String dateSuffix = yesterday.format(DateTimeFormatter.ofPattern("yyyyMMdd"));
            
            String fileName = fileBaseName + "." + dateSuffix;
            String remotePath = remoteDirectory + fileName;
            
/*             Path path = Paths.get(fileDirectory, fileName);
            log.info("Looking for file: {}", path);
            if (!Files.exists(path)) {
                log.warn("사망자/압류자 파일이 약속된 디렉토리에 없습니다. {}", path);
                return;
            }

            List<String> lines = Files.readAllLines(path, StandardCharsets.UTF_8);
            */
            byte[] fileContent = sftpRemoteFileTemplate.execute(session -> {
                try {
                    if (!session.exists(remotePath)) {
                        log.warn("사망자/압류자 파일이 SFTP 서버에 없습니다. {}", remotePath);
                        return null;
                    }
                    
                    try (InputStream is = session.readRaw(remotePath)) {
                        return IOUtils.toByteArray(is);
                    }
                } catch (IOException e) {
                    log.error("sFTP 서버로부터 사망자/압류자 파일을 읽는 데에 실패했습니다.: ", e);
                    throw new BaseException(ErrorCode.FILE_DOWNLOAD_ERROR, e);
                }
            });

            if (fileContent == null) {
                return;
            }
            
            List<String> lines = new String(fileContent, StandardCharsets.UTF_8)
                                    .lines()
                                    .collect(Collectors.toList());

            if (lines.isEmpty()) {
                log.warn("파일이 비었습니다.: {}", fileName);
                return;
            }
 
            if (lines.size() < 3) {
                log.error("파일은 헤더부 한 줄, 데이터부 최소 한 줄, 트레일러부 한 줄이 있어야 합니다. {}", fileName);
                return;
            }

            String header = lines.get(0);
            if (!validateHeader(header, dateSuffix)) {
                log.error("헤더 형식이 잘못되었습니다. {}", header);
                return; 
            }

            String trailerLine = lines.get(lines.size() - 1);
            int expectedCount;
            try {
                expectedCount = parseTrailerCount(trailerLine);
                log.info("Expected number of records from trailer: {}", expectedCount);
            } catch (IllegalArgumentException e) {
                log.error("트레일러부 형식이 잘못 되었습니다. {}", trailerLine);
                return;
            }

            List<DeactivateCstmrDto> customers = new ArrayList<>();
            
            for (int i = 1; i < lines.size(); i++) {
                String line = lines.get(i);
                if (!line.startsWith("D")) continue;

                try {
                    DeactivateCstmrDto customer = parseLine(line);
                    customers.add(customer);
                } catch (Exception e) {
                    log.error("Error processing line {}: {}", i + 1, e.getMessage());
                }
                
            }
            
            if (customers.size() != expectedCount) {
                log.warn("실제 처리 숫자와 트레일러부 총 건수가 일치하지 않습니다. 총 건수: {}, 실제 처리수: {}", 
                    expectedCount, customers.size());
            }

            if (!customers.isEmpty()) {
                ewaDeactivateCstmrMapper.insertList(customers);
                log.info("Successfully processed {} customer records from file {}", 
                        customers.size(), fileName);
            } else {
                log.warn("No records found in the file {}", fileName);
            }
            
        } catch (Exception e) {
            log.error("Error processing deactivate customer file: ", e);
            throw new BaseException(ErrorCode.SERVER_ERROR, e);
        }
    }
    
    private boolean validateHeader(String header, String expectedDate) {
        if (header == null || header.length() < 9 || !header.startsWith("H")) {
            log.debug("null or Invalid header");
            return false;
        }
        
        String headerDate = header.substring(1);
        return headerDate.equals(expectedDate);
    }
}
```
## AI 대화록
### Deposit Token 발행 메소드에 발행이력 데이터 기본키값 파라미터 추가
#### 질문: issueDepositToken 변경해라
```java
package kr.or.cbdc.application.ewa.cstmr.service;

import kr.or.bok.wallet.sdk.errorhandling.WalletSdkException;
import kr.or.bok.wallet.sdk.model.common.Signer;
import kr.or.cbdc.application.common.alias.mapper.BlockListManageMapper;
import kr.or.cbdc.application.common.alias.model.AliasResponse;
import kr.or.cbdc.application.common.alias.model.AliasSearchInfo;
import kr.or.cbdc.application.common.alias.service.BaseBlockListServiceImpl;
import kr.or.cbdc.application.common.alias.service.BaseBlockListServiceImpl;
import kr.or.cbdc.application.ewa.alias.service.AliasEwaBanksServiceImpl;
import kr.or.cbdc.application.ewa.common.dto.GwRampDto;
import kr.or.cbdc.application.ewa.common.dto.GwRampFailDto;
import kr.or.cbdc.application.ewa.common.service.EwaGWServiceImpl;
import kr.or.cbdc.application.ewa.common.dto.CbsAcnoResponseDto;
import kr.or.cbdc.application.ewa.common.dto.CbsAcnoResponseGridDto;
import kr.or.cbdc.application.ewa.common.dto.CbsErrorDto;
import kr.or.cbdc.application.ewa.common.dto.CbsRampResponseDto;
import kr.or.cbdc.application.ewa.common.dto.GwAcnoDto;
import kr.or.cbdc.application.ewa.cstmr.model.AcnutManageModel;
import kr.or.cbdc.application.ewa.policy.service.EwaPolicyManageServiceImpl;
import kr.or.cbdc.application.ewa.wallet.service.EwaWalletManageServiceImpl;
import kr.or.cbdc.config.props.ConfigProperties;
import kr.or.cbdc.domain.main.mapper.ewa.cstmr.TbEwaAcnutMastrMapper;
import kr.or.cbdc.domain.main.mapper.ewa.cstmr.TbEwaCstmrMastrMapper;
import kr.or.cbdc.domain.main.mapper.ewa.dc1.EwaDc1IsuMastrMapper;
import kr.or.cbdc.domain.main.mapper.ewa.dc1.EwaDc1RedempMastrMapper;
import kr.or.cbdc.domain.main.mapper.ewa.wallet.TbEwaWalletMastrMapper;
import kr.or.cbdc.domain.main.model.com.wallet.TbWalletMastr;
import kr.or.cbdc.domain.main.model.ewa.cstmr.TbCstmrMastr;
import kr.or.cbdc.domain.main.model.ewa.dc1.Dc1IsuMastr;
import kr.or.cbdc.domain.main.model.ewa.dc1.Dc1RedempMastr;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.BizException;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.CBSException;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.ErrorAssert;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.ErrorCode;
import kr.or.cbdc.infrastructure.idgen.util.IdGenerationUtil;
import kr.or.cbdc.infrastructure.mybatis.GenericMapperService;
import kr.or.cbdc.infrastructure.mybatis.GenericMapperService;
import kr.or.cbdc.infrastructure.profile.EwaProfileCondition;
import kr.or.cbdc.infrastructure.queue.KafkaProducer;
import kr.or.cbdc.infrastructure.queue.TxMessage;
import kr.or.cbdc.infrastructure.util.TokenUtils;
import kr.or.cbdc.interfaces.blockchain.BlockChainHelper;
import kr.or.cbdc.interfaces.blockchain.CoinType;
import kr.or.cbdc.interfaces.blockchain.CommandType;
import kr.or.cbdc.interfaces.blockchain.SupportCallback;
import kr.or.cbdc.interfaces.blockchain.TrnscType;
import kr.or.cbdc.interfaces.blockchain.WalletType;
import kr.or.cbdc.interfaces.blockchain.BlockChainHelper;
import kr.or.cbdc.interfaces.blockchain.CoinType;
import kr.or.cbdc.interfaces.blockchain.CommandType;
import kr.or.cbdc.interfaces.blockchain.SupportCallback;
import kr.or.cbdc.interfaces.blockchain.TrnscType;
import kr.or.cbdc.interfaces.blockchain.WalletType;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Conditional;
import org.springframework.dao.DataAccessException;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.HttpServerErrorException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.stereotype.Service;

import com.hazelcast.core.HazelcastInstance;
import com.hazelcast.cp.lock.FencedLock;
import com.hazelcast.sql.impl.expression.BiExpression;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Random;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;

import kr.or.cbdc.interfaces.ApiCallHelper;
import kr.or.cbdc.config.props.ConfigProperties;
import java.util.function.Supplier;
import org.springframework.http.HttpMethod;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import io.grpc.netty.shaded.io.netty.util.internal.ObjectUtil;

import java.util.HashMap;

/**
##### 계좌 관리 Service
 */
@Slf4j
@Service
@Conditional(EwaProfileCondition.class)
public class EwaAcnutManageServiceImpl extends SupportCallback {

    private @Autowired TbEwaCstmrMastrMapper tbEwaCstmrMastrMapper;
    private @Autowired TbEwaAcnutMastrMapper tbEwaAcnutMastrMapper;
    private @Autowired TbEwaWalletMastrMapper tbEwaWalletMastrMapper;
    private @Autowired EwaPolicyManageServiceImpl ewaPolicyManageService;
    private @Autowired EwaWalletManageServiceImpl ewaWalletManageService;
    private @Autowired AliasEwaBanksServiceImpl aliasEwaBanksService;
    private @Autowired BlockListManageMapper blockListManageMapper;
    private @Autowired BlockChainHelper _blockChain;
    private @Autowired KafkaProducer kafkaProducer;
    private @Autowired GenericMapperService genericMapperService;
    private @Autowired ConfigProperties config;
    private @Autowired BaseBlockListServiceImpl blockListService;
    private @Autowired ApiCallHelper apiCallHelper;
    private @Autowired ConfigProperties configProperties;
    private @Autowired EwaDc1IsuMastrMapper ewaDc1IsuMastrMapper;
    private @Autowired HazelcastInstance hazelcastInstance;
    private @Autowired EwaGWServiceImpl ewaGWService;
    private int baseNo = 2;

    private static final Random rand = new Random();
    private static final ObjectMapper objectMapper = new ObjectMapper();

    private void validateInput(AcnutManageModel model) {
        ErrorAssert.notNull(model, ErrorCode.MISSING_REQUIRED_FIELD);
        ErrorAssert.notNull(model.getTbAcnutMastr(), ErrorCode.MISSING_REQUIRED_FIELD);
        ErrorAssert.notNull(model.getTbAcnutMastr().getTrnscAmt(), ErrorCode.MISSING_REQUIRED_FIELD);
    }
    
    private TbCstmrMastr validateCustomer(String cstmrNo) {
        ErrorAssert.hasLength(cstmrNo, ErrorCode.CUSTOMER_ID_REQUIRED);
        TbCstmrMastr customer = tbEwaCstmrMastrMapper.select(cstmrNo);
        ErrorAssert.notNull(customer, ErrorCode.CUSTOMER_NOT_FOUND, cstmrNo);
        ErrorAssert.isTrue(!StringUtils.equals(customer.getCstmrSttusCd(), "1"), ErrorCode.INVALID_CUSTOMER_STATE);
        return customer;
    }
    
    private BigDecimal validateAmount(BigDecimal amount) {
        ErrorAssert.notNull(amount, ErrorCode.INVALID_TRANSACTION_AMOUNT);
        ErrorAssert.isTrue(amount.compareTo(BigDecimal.ZERO) > 0, ErrorCode.INVALID_TRANSACTION_AMOUNT);
        ErrorAssert.isTrue(amount.compareTo(new BigDecimal("999999999999.99")) <= 0, 
                     ErrorCode.INVALID_TRANSACTION_AMOUNT);
        return amount;
    }

    public TbWalletMastr validateWallet(WalletType walletType, TbCstmrMastr tbCstmrMastr, ErrorCode walletNotFoundError) {
        TbWalletMastr tbWalletMastr = tbEwaWalletMastrMapper.selectWalletSe(walletType.toString());
        log.debug("[jkoh] I1 wallet: {} cstmr's wallte address: {}", tbWalletMastr, tbCstmrMastr.getWalletAdres());
        ErrorAssert.notNull(tbWalletMastr, walletNotFoundError);
        ErrorAssert.hasLength(tbCstmrMastr.getWalletAdres(), ErrorCode.WALLET_MISSING);
        return tbWalletMastr;
    }
    
    public GwRampDto createRampParams(String internalTxId, TbCstmrMastr tbCstmrMastr, BigDecimal trnscAmt, BigInteger toBalance) {
        return GwRampDto.builder()
            .internalTxId(internalTxId)
            .customerId(tbCstmrMastr.getCstmrNo())
            .acnutNo(tbCstmrMastr.getAcnutno())
            .amount(trnscAmt)
            .beforeTdBalance(toBalance)
            .build();
    }

    public GwRampFailDto createRampFailParams(String internalTxId, String guid, String accountNo, BigDecimal amount) {
        return GwRampFailDto.builder()
            .internalTxId(internalTxId)
            .oriId(guid)
            .customerId(accountNo)
            .amount(amount)
            .build();
    }

    // Operation type enum
    public enum BalanceOperationType {
        ADD, SUBTRACT
    }

    public void updateCustomerBalance(String cstmrNo, BigDecimal balance, BigDecimal trnscAmt, BalanceOperationType operationType) {
        if (cstmrNo == null || trnscAmt == null || operationType == null) {
            throw new IllegalArgumentException("Customer, transaction amount, or operation type cannot be null");
        }
        
        BigDecimal newBalance = (operationType == BalanceOperationType.ADD)
                                ? balance.add(trnscAmt)
                                : balance.subtract(trnscAmt);
        TbCstmrMastr tbCstmrMastrUpdate = new TbCstmrMastr();
        tbCstmrMastrUpdate.setCstmrNo(cstmrNo);
        tbCstmrMastrUpdate.setAcnutnoBlce(newBalance);
        try {
            // Perform database update
            genericMapperService.updateModel(tbCstmrMastrUpdate,
                            TbCstmrMastr.class,
                            TbEwaAcnutMastrMapper.class,
                            "updateBlce");
        } catch (DataAccessException e) {
            log.error("고객 계좌({}) 잔액 변경({} -> {}) 중 에러가 발생했습니다. 에러 내용: {}"
                            , cstmrNo
                            , balance
                            , (operationType == BalanceOperationType.ADD) ? balance.add(trnscAmt) : balance.subtract(trnscAmt)
                            , e.getMessage());
            throw new BizException(ErrorCode.DATA_ACCESS_ERROR, e.getMessage());
        } catch (Exception e) {
            log.error("고객 계좌({}) 잔액 변경({} -> {}) 중 에러가 발생했습니다. 에러 내용: {}"
                            , cstmrNo
                            , balance
                            , (operationType == BalanceOperationType.ADD) ? balance.add(trnscAmt) : balance.subtract(trnscAmt)
                            , e.getMessage());
            throw new BizException(ErrorCode.SERVER_ERROR, e.getMessage());
        }
    }
    
    private void handleOnRampFailure(String wGuid, String acnutno, BigDecimal trnscAmt) {
        GwRampFailDto paramOnRampFail = createRampFailParams("internalTxId", wGuid, acnutno, trnscAmt);
        try {
            JsonNode respOnRampFail = apiCallHelper.callURL(configProperties.getGateway().getOnRampFail().getUrl(),
                                        null,
                                        objectMapper.valueToTree(paramOnRampFail),
                                        HttpMethod.POST);
            CbsRampResponseDto onRampFailResponse = parseGatewayResponse(respOnRampFail, "onRampFail");
            checkGWResponse(onRampFailResponse, null);
        } catch (ResourceAccessException e) {
            // We don't rethrow here as this is already in an error handling path
            log.error("GlobalID({}) account({}) OnRampFail API timeout or connection error: {}", wGuid, acnutno, e.getMessage());
        } catch (HttpClientErrorException e) {
            log.error("GlobalID({}) account({}) OnRampFail API client error (4xx): Status {}, Response {}", wGuid, acnutno, e.getStatusCode(), e.getResponseBodyAsString());
        } catch (HttpServerErrorException e) {
            log.error("GlobalID({}) account({}) OnRampFail API server error (5xx): Status {}, Response {}", wGuid, acnutno, e.getStatusCode(), e.getResponseBodyAsString());
        } catch (Exception e) {
            log.error("GlobalID({}) account({}) Unexpected error calling OnRampFail API: {}", wGuid, acnutno, e.getMessage(), e);
        }
    }

    /**
##### 계정계에 onRamp 요청하고 거래 키를 돌려준다.
##### @return wGuid from Gateway response for onRamp cancel
     */
    private CbsRampResponseDto onRampCoreBanking(String cstmrNo, TbCstmrMastr tbCstmrMastr, 
            BigDecimal acnutnoBlce, BigDecimal trnscAmt, BigInteger toBalance) {
        
        log.debug("[jkoh] 계정계 gateway onRamp 호출 시작");
        GwRampDto paramOnRamp = createRampParams("internalTxId", tbCstmrMastr, trnscAmt, toBalance);
        JsonNode respOnRamp = null;
        try {
            respOnRamp = apiCallHelper.callURL(configProperties.getGateway().getOnRamp().getUrl(),
                    null,
                    objectMapper.valueToTree(paramOnRamp),
                    HttpMethod.POST);
        } catch (ResourceAccessException e) {
            updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
            log.error("Account: {}, OnRamp API timeout or connection error: {}", 
                    tbCstmrMastr.getAcnutno(), e.getMessage());
            throw new BizException(ErrorCode.BRIDGE_CALL_ERROR, e);
        } catch (HttpClientErrorException e) {
            updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
            log.error("Account: {}, OnRamp API client error (4xx): Status {}, Response {}", 
                    tbCstmrMastr.getAcnutno(), e.getStatusCode(), e.getResponseBodyAsString());
            throw new BizException(ErrorCode.BRIDGE_CALL_ERROR, e);
        } catch (HttpServerErrorException e) {
            updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
            log.error("Account: {}, OnRamp API server error (5xx): Status {}, Response {}", 
                    tbCstmrMastr.getAcnutno(), e.getStatusCode(), e.getResponseBodyAsString());
            throw new BizException(ErrorCode.BRIDGE_CALL_ERROR, e);
        } catch (Exception e) {
            updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
            log.error("Unexpected error calling OnRamp API for account: {}, error: {}", 
                    tbCstmrMastr.getAcnutno(), e.getMessage(), e);
            throw new BizException(ErrorCode.BRIDGE_CALL_ERROR, e);
        }
        
        CbsRampResponseDto onRampResponse = parseGatewayResponse(respOnRamp, "onRamp");
        checkGWResponse(onRampResponse, () -> updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, 
                BalanceOperationType.ADD));
        log.debug("[jkoh] OnRamp step 3 계정계 onRamp 요청 완료");
        
        return onRampResponse;
    }

    /**
##### 전환 입금 (예금토큰 발행)
     *
##### @param model
##### @return
##### @throws WalletSdkException
     */
    public String convDeposit(AcnutManageModel model) throws WalletSdkException {
        if (lock(TokenUtils.getToken())) {
            try {
        		// step0 입력값 검증
        		validateInput(model);
        		
                String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));
        		TbCstmrMastr tbCstmrMastr = validateCustomer(cstmrNo);
        		BigDecimal trnscAmt = validateAmount(model.getTbAcnutMastr().getTrnscAmt());
        		log.debug("[jkoh] convDeposit start cstmrNo: {} trnsAmt {}", cstmrNo, trnscAmt);
        		log.debug("[jkoh] tbCstmrMastr: {}", tbCstmrMastr);

        		ErrorAssert.isNull(blockListManageMapper.selectBlclstWallet(bankCd, cstmrNo), ErrorCode.BLACKLIST_TARGET);
                blockListService.findBlockStatus(bankCd);
        		
                BigInteger toBalance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);

        		// IF-GWS-O-006 참가기관 이용자 Core Banking(계정계) 연계 계좌의 잔액 조회 --> 이건 20250207_Source에서 추가된 것. TODO??
                validateAccountWithdrawal(cstmrNo, trnscAmt);
                // 위에서 계정계 계좌 잔액 조회를 통해 검증하므로 아래 줄은 주석 처리
        		// ErrorAssert.isTrue(!(trnscAmt.compareTo(acnutnoBlce) > 0),ErrorCode.INSUFFICIENT_ACCOUNT_BALANCE);

                // step 2-1 통화정책 한도검증 (보유)
                ewaPolicyManageService.policyLimit(null, null, toBalance.add(trnscAmt.toBigInteger()),
                        trnscAmt.toBigInteger(), cstmrNo);

                return issueDepositToken(cstmrNo, trnscAmt);

            } finally {
                unlock(TokenUtils.getToken());
            }
        } else {
            throw new BizException(ErrorCode.DISTRIBUTED_LOCK_ERROR);
        }
    }

    /**
##### IF-GWS-O-004 예외발생시 예금토큰 재 발행
     *
##### @param model
##### @return
##### @throws WalletSdkException
     */
    public String depositTokenReissue(TxMessage message) throws WalletSdkException {

        String cstmrNo = tbEwaAcnutMastrMapper.selectByAccount(message.getFromAcnutno());
        TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(cstmrNo);        

        ErrorAssert.notNull(tbEwaCstmrMastrMapper.select(cstmrNo), ErrorCode.CUSTOMER_NOT_FOUND, cstmrNo);
        ErrorAssert.isTrue(!StringUtils.equals(tbEwaCstmrMastrMapper.select(cstmrNo).getCstmrSttusCd(), "1"),
                ErrorCode.INVALID_CUSTOMER_STATE);
        BigDecimal trnscAmt = BigDecimal.valueOf( message.getAmount() );

        // step1 지갑 검증
        TbWalletMastr tbWalletMastr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.I1.toString());
        ErrorAssert.notNull(tbWalletMastr, ErrorCode.EMPTY_PREP_WALLET);
        ErrorAssert.hasLength(tbCstmrMastr.getWalletAdres(), ErrorCode.WALLET_MISSING);

        // step 2 계좌 예치금 검증 (예금 >= 전환입금),(발행준비 >= 전환입금)
        BigInteger fromBalance = _blockChain.getBalance(tbWalletMastr.getWalletAdres(), bankCd, CoinType.DC1);
        BigInteger toBalance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);

        ErrorAssert.isTrue(
                trnscAmt.compareTo(BigDecimal.ZERO) > 0 && trnscAmt.stripTrailingZeros().scale() <= 0,
                ErrorCode.INVALID_AMOUNT);

        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0),
                ErrorCode.INSUFFICIENT_ISU_ACCOUNT_BALANCE);

        // step4 DC1 발행 생성
        Dc1IsuMastr dc1IsuMastr = Dc1IsuMastr.builder().dc1IsuSttus("W")
                .trgetInstt(bankCd)
                .dc1IsuAmount(trnscAmt.longValue())
                .applcntId(cstmrNo)
                .build().newId();
        // ewaDc1IsuMastrMapper.insert(dc1IsuMastr);
        genericMapperService.insertModel(dc1IsuMastr, Dc1IsuMastr.class, EwaDc1IsuMastrMapper.class, "insert");

        // kafka message 생성
        TxMessage txMessage = TxMessage.builder().command(CommandType.I1)
                .txDbId(dc1IsuMastr.getDc1IsuId())
                .from(tbWalletMastr.getWalletAdres())
                .to(tbCstmrMastr.getWalletAdres())
                .fromWalletDpstr(tbWalletMastr.getWalletNm())
                .walletDpstr(tbCstmrMastr.getKoreanNm())
                .fromBankCode(bankCd)
                .toBankCode(bankCd)
                .timestamp(new Date())
                .amount(trnscAmt.longValue())
                .trnscAfterBlce(toBalance.add(trnscAmt.toBigInteger()).longValue())
                .acnutno(tbCstmrMastr.getAcnutno())
                .personId(cstmrNo)
                .coin(CoinType.DC1)
                .txType(TrnscType.DEPOSIT.getValue())
                .retry(0).build();

        String requestId = kafkaProducer.setSaga(List.of(txMessage));

        // step 5 카프카 등록및 오류처리
        try {
            kafkaProc(List.of(txMessage), requestId, "W");

            // step 6 예금토큰 발행 DC1 발행준비 > 이용자 : 분산원장 Call , 참가기관 단일서명
            String result = _blockChain.sendTransaction(requestId, tbWalletMastr.getOwner(),
                    tbCstmrMastr.getWalletAdres(),
                    trnscAmt.toBigInteger(), bankCd, CoinType.DC1,
                    getCallBack(List.of(txMessage), CoinType.DC1.name()));
            ErrorAssert.hasLength(result, ErrorCode.BLOCKCHAIN_CALL_FAILURE);

        } catch (Exception e) {
            kafkaProc(List.of(txMessage), requestId, "R");
            throw new BizException(ErrorCode.SERVER_ERROR, requestId, e.getMessage());
        }

        return requestId;

    }

    /**
##### 계정계로 잔액 조회를 요청해서 검증
##### @param accountNo Account number to check
##### @param amount Amount to validate
##### @throws BizException if validation fails
     */
    private void validateAccountWithdrawal(String accountNo, BigDecimal amount) {
        GwAcnoDto acnoParam = GwAcnoDto.builder()
                .inqDscd("01")  // 보유계좌잔액조회
                .dpsAcno(accountNo)
                .build();
        
        JsonNode acnoResponse = ewaGWService.acno(acnoParam);
        try {
            CbsAcnoResponseDto acnoResponseDto = objectMapper.treeToValue(acnoResponse, CbsAcnoResponseDto.class);
            
            if (acnoResponseDto.getErrorlist() != null && !acnoResponseDto.getErrorlist().isEmpty()) {
                log.error("계정계 잔액조회 에러: {}", acnoResponseDto.getErrorlist().get(0).getMainMsgTxt());
                throw new BizException(ErrorCode.INVALID_BALANCE_REQUIRED);
            }

            if (acnoResponseDto.getGrid() == null || acnoResponseDto.getGrid().isEmpty()) {
                log.error("계정계 계좌 정보 없음: {}", accountNo);
                throw new BizException(ErrorCode.INVALID_ACNUTNO);
            }

            CbsAcnoResponseGridDto accountInfo = acnoResponseDto.getGrid().get(0);
            if (accountInfo.getWdrAvlAm() < amount.intValue()) {
                log.error("계정계 출금가능금액 부족. 계좌: {}, 출금가능금액: {}, 요청금액: {}", 
                        accountNo, accountInfo.getWdrAvlAm(), amount.intValue());
                throw new BizException(ErrorCode.INSUFFICIENT_ACCOUNT_BALANCE);
            }
        } catch (JsonProcessingException e) {
            log.error("계정계 잔액조회 응답 파싱 에러: {}", e.getMessage());
            throw new BizException(ErrorCode.PARSING_ERROR);
        }
    }

    /**
##### offRamp 원복하기 위해서 호출할 수 있도록 convDeposit에서 onRamp 핵심 로직을 추려낸 것.
##### convDeposit과 offRamp 원복 양쪽에서 호출할 수 있음.
     */
    public String issueDepositToken(String cstmrNo, BigDecimal trnscAmt) throws WalletSdkException {
        TbCstmrMastr tbCstmrMastr = validateCustomer(cstmrNo);
		BigDecimal acnutnoBlce = tbCstmrMastr.getAcnutnoBlce();
        validateAmount(trnscAmt);
        
        // step1 지갑 검증
        TbWalletMastr tbWalletMastr = validateWallet(WalletType.I1, tbCstmrMastr, ErrorCode.INVALID_TD_ISSUANCE_WALLET);
        
        // step 2 계좌 예치금 검증 (예금 >= 전환입금),(발행준비 >= 전환입금)
        BigInteger fromBalance = _blockChain.getBalance(tbWalletMastr.getWalletAdres(), bankCd, CoinType.DC1);
        BigInteger toBalance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);
		log.debug("[jkoh] TD 발행 준비지갑 잔액 fromBalance: {}", fromBalance);
		log.debug("[jkoh] 이용자 지갑 잔액 toBalance: {}", toBalance);
        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.INSUFFICIENT_ISU_ACCOUNT_BALANCE);
		log.debug("[jkoh] OnRamp step 2 지갑, 잔액 검증 완료");

        // step 3-1 계정계 출금 요청 Gateway 호출
		CbsRampResponseDto onRampResponse = onRampCoreBanking(cstmrNo, tbCstmrMastr, acnutnoBlce, trnscAmt, toBalance);
        String wGuid = onRampResponse.getTrnLogKeyVal();

		// step4 계정계에서 출금이 정상적으로 되면 DC1 발행 기록
        Dc1IsuMastr dc1IsuMastr = Dc1IsuMastr.builder()
                .dc1IsuSttus("W")
                .trgetInstt(bankCd)
                .dc1IsuAmount(trnscAmt.longValue())
                .applcntId(cstmrNo)
                .mcaGuid(onRampResponse.getTrnLogKeyVal())
                .cbsTrnAcno(onRampResponse.getDpsInpAcno())
                .cbsTrnDt(onRampResponse.getTrnDt())
                .cbsTrnSrno(onRampResponse.getTrnSrno())
                .build()
                .newId();
        
		log.debug("[jkoh] dc1IsuMaster data to save: {}", dc1IsuMastr);
        try {
            genericMapperService.insertModel(dc1IsuMastr, Dc1IsuMastr.class, 
                    EwaDc1IsuMastrMapper.class, "insert");
            log.debug("[jkoh] onRamp 예금토큰 발행 내역 저장 {}", dc1IsuMastr);
        } catch (Exception e) {
            log.error("계좌({}) 거래키({}) 거래일련번호({})에 대한 예금토큰 발행 내역 신규저장 에러: {}", tbCstmrMastr.getAcnutno(), onRampResponse.getTrnLogKeyVal(), onRampResponse.getTrnSrno(), e.getMessage());
            updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
            // 계정계에 취소 거래 보내기
            handleOnRampFailure(wGuid, tbCstmrMastr.getAcnutno(), trnscAmt);
            throw new BizException(ErrorCode.DATA_ACCESS_ERROR, e.getMessage(), e);
        }
        log.debug("[jkoh] OnRamp step 4 TD 발행 이력 저장 완료");

        // Create and send Kafka message
        TxMessage txMessage = TxMessage.builder()
                .command(CommandType.I1)
                .txDbId(dc1IsuMastr.getDc1IsuId())
                .from(tbWalletMastr.getWalletAdres())
                .to(tbCstmrMastr.getWalletAdres())
                .fromWalletDpstr(tbWalletMastr.getWalletNm())
                .walletDpstr(tbCstmrMastr.getKoreanNm())
                .fromBankCode(bankCd)
                .toBankCode(bankCd)
                .amount(trnscAmt.longValue())
                .timestamp(new Date())
                .trnscAfterBlce(toBalance.add(trnscAmt.toBigInteger()).longValue())
                .acnutno(tbCstmrMastr.getAcnutno())
                .personId(cstmrNo)
                .coin(CoinType.DC1)
                .txType(TrnscType.DEPOSIT.getValue())
                .retry(0)
                .build();

		log.debug("[jkoh] issueDepositToken kafka message: {}", txMessage);

        String requestId = null;
        try {
            requestId = kafkaProducer.setSaga(List.of(txMessage));
            log.debug("[jkoh] issueDepositToken requestId from setSage: {}", requestId);
        } catch (Exception e) {
            log.error("onRamp 트랜잭션 관리용 Saga requestId for txMessage {} 생성 에러: {}", txMessage, e);
            updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
            // 계정계에 취소 거래 보내기
            handleOnRampFailure(wGuid, tbCstmrMastr.getAcnutno(), trnscAmt);
            throw e;
        }

        // step 5 카프카 등록및 오류처리
        try {
            kafkaProc(List.of(txMessage), requestId, "W");
            log.debug("[jkoh] issueDepositToken After kafka send and before call Blockchain sendTransaction");
        } catch (BizException e) {
            log.error("onRamp Kafka 메시지[{}] 송신 에러: {}", requestId, e.getMessage());
            updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
            // 계정계에 취소 거래 보내기
            handleOnRampFailure(wGuid, tbCstmrMastr.getAcnutno(), trnscAmt);
            throw e;
        }
        log.debug("[jkoh] OnRamp step 5 kafka 전송 완료");
        
        try {
            // step 6 예금토큰 발행 DC1 발행준비 > 이용자 : 분산원장 Call , 참가기관 단일서명
            String result = _blockChain.sendTransaction(requestId, tbWalletMastr.getOwner(), tbCstmrMastr.getWalletAdres(),
                    trnscAmt.toBigInteger(), bankCd, CoinType.DC1, getCallBack(List.of(txMessage), CoinType.DC1.name()));
            ErrorAssert.hasLength(result, ErrorCode.BLOCKCHAIN_CALL_FAILURE);
        } catch (Exception e) {
            log.error("예금토큰 발행({} -> {}) 블록체인 호출 에러 {}", tbWalletMastr.getWalletAdres(), tbCstmrMastr.getWalletAdres(), e.getMessage());
            // 계좌 증액 처리 (계좌잔액= 계좌잔액 + 전환입금액, DC1 = DC1잔액 - 전환입금액)
            updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
            // TODO 위에서 TB_DC1_ISU_MASTR1에 insert한 것은 트랜잭션 상태가 변했는지 확인 필요.

            kafkaProc(List.of(txMessage), requestId, "R");
            handleOnRampFailure(wGuid, tbCstmrMastr.getAcnutno(), trnscAmt);
            throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
        }
		log.debug("[jkoh] OnRamp step 6 블록체인 요청 완료.");
		return txMessage.getTxDbId();
    }

    /**
##### 예금 전환(예금토큰 환수)
     *
##### @param model
##### @return
##### @throws WalletSdkException
     */
    public String depositConv(AcnutManageModel model) throws WalletSdkException {
        if (lock(TokenUtils.getToken())) {
            try {
        		// step0 입력값 검증
        		validateInput(model);

                String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));
        		TbCstmrMastr tbCstmrMastr = validateCustomer(cstmrNo);
        		BigDecimal acnutnoBlce = tbCstmrMastr.getAcnutnoBlce();
        		
        		BigDecimal trnscAmt = validateAmount(model.getTbAcnutMastr().getTrnscAmt());

        		// blockListService.chkBlockStatus(cstmrNo, bankCd); 20250106_Source merge할 때 이 부분 막고 20250106_Source의 코드로 바꿈.
                blockListService.findBlockStatus(bankCd);

                // step1 지갑 검증
        		TbWalletMastr tbWalletMastr = validateWallet(WalletType.R1, tbCstmrMastr, ErrorCode.INVALID_TD_REDEMPTION_WALET);

                // step 2 예금전환액 검증
                BigInteger balance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);
                ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(balance) > 0), ErrorCode.INSUFFICIENT_BALANCE);
        		ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(balance) > 0), ErrorCode.INSUFFICIENT_BALANCE);
        		log.debug("[jkoh] OffRamp step 2 지갑, 잔액 검증 완료");
        		
        		// step3 계좌증액
        		updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
        		log.debug("[jkoh] OffRamp step 3 계좌 증액 완료");

                // step4 DC1 환수 생성
                Dc1RedempMastr dc1RedempMastr = Dc1RedempMastr.builder().dc1RedempSttus("W")
                        .trgetInstt(bankCd)
                        .dc1RedempAmount(trnscAmt.longValue())
                        .applcntId(cstmrNo)
                        .build().newId();
                // ewaDc1RedempMastrMapper.insert(dc1RedempMastr);
        		try {
                genericMapperService.insertModel(dc1RedempMastr, Dc1RedempMastr.class, EwaDc1RedempMastrMapper.class,
                        "insert");
        		} catch (Exception e) {
        			log.error("계좌({}에 대한 예금토큰 환수 내역 신규저장 에러: {}", tbCstmrMastr.getAcnutno(), e.getMessage());
        			updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.SUBTRACT);
        			throw new BizException(ErrorCode.DATA_ACCESS_ERROR, e.getMessage(), e);
        		}
        		log.debug("[jkoh] OffRamp step 4 TD 환수 이력 저장 완료");

                // kafka message 생성
                TxMessage txMessage = TxMessage.builder().command(CommandType.R1)
                        .txDbId(dc1RedempMastr.getDc1RedempId())
                        .from(tbCstmrMastr.getWalletAdres())
                        .to(tbWalletMastr.getWalletAdres())
                        .fromBankCode(bankCd)
                        .toBankCode(bankCd)
                        .amount(trnscAmt.longValue())
                        .timestamp(new Date())
                        .fromTrnscAfterBlce(balance.subtract(trnscAmt.toBigInteger()).longValue())
                        .fromAcnutno(tbCstmrMastr.getAcnutno())
                        .fromWalletDpstr(tbCstmrMastr.getKoreanNm())
                        .walletDpstr(tbWalletMastr.getWalletNm())
                        .personId(cstmrNo)
                        .coin(CoinType.DC1)
                        .txType(TrnscType.CONVERS.getValue())
                        .retry(0).build();
                List<TxMessage> txMessages = new ArrayList<>();
                txMessages.add(txMessage);
        		
        		String requestId = null;
        		try {
        			requestId = kafkaProducer.setSaga(txMessages);
        			log.debug("[jkoh] depositConv requestId from setSage: {}", requestId);
        		} catch (Exception e) {
        			updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.SUBTRACT);
        			log.error("offRamp 트랜잭션 관리용 Saga requestId for txMessage {} 생성 에러: {}", txMessage, e);
        			throw e;
        		}

                // step 5 카프카 등록및 오류처리
                try {
                    kafkaProc(List.of(txMessage), requestId, "W");
        		} catch (BizException e) {
        			updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.SUBTRACT);
        			log.error("offRamp Kafka 메시지[SagaID({})] 송신 에러: {}", requestId, e.getMessage());
        			throw e;
        		} 
        		log.debug("[jkoh] OffRamp step 5 kafka 전송 완료");
        		
        		try {

                    // step 6 이용자지갑 > 환수지갑 : 분산원장 Call , 참가기관 단일서명
        			String result = _blockChain.sendTransaction(requestId, tbCstmrMastr.getOwner(), tbWalletMastr.getWalletAdres(),
        					trnscAmt.toBigInteger(), this.bankCd, CoinType.DC1, getCallBack(txMessages,CoinType.DC1.name()));
                    ErrorAssert.hasLength(result, ErrorCode.KAFKA_PRODUCE_ERROR);
        		} catch (WalletSdkException e) {
        			log.error("SagaId({}) 예금토큰 환수({} -> {}) 블록체인 호출 에러 {}", requestId, tbCstmrMastr.getWalletAdres(), tbWalletMastr.getWalletAdres(), e.getMessage());
                    kafkaProc(List.of(txMessage), requestId, "R");
        			// 계좌 차감 처리 (계좌잔액= 계좌잔액 - 전환입금액, DC1 = DC1잔액 + 전환입금액)
        			updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.SUBTRACT);
        			throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
        		}
        		log.debug("[jkoh] OffRamp step 6 블록체인 요청 완료.");
        		
        		/*
            	Dc1RedempMastr dc1RedempMastrUpdate = Dc1RedempMastr.builder()
	                                                .dc1RedempId(dc1RedempMastr.getDc1RedempId())
	                                                .build();
	
	            try {
	                genericMapperService.updateModel(dc1RedempMastrUpdate, Dc1RedempMastr.class, EwaDc1RedempMastrMapper.class, "update");
	            } catch (Exception e) {
	                log.error("SagaID({}) 계좌({}) 예금토큰 환수 내역 저장 에러: {}", requestId, tbCstmrMastr.getAcnutno(), e.getMessage());
	                throw new BizException(ErrorCode.DATA_ACCESS_ERROR, e.getMessage(), e);
	            }
        		 */
        		return txMessage.getTxDbId();
            } finally {
                unlock(TokenUtils.getToken());
            }
        } else {
            throw new BizException(ErrorCode.DISTRIBUTED_LOCK_ERROR);
        }
    }

    /**
##### 예금 토큰 송금 (DC1 당,타행 이체)
     *
##### @param model
##### @return
##### @throws WalletSdkException
     */
    public String depositTrans(AcnutManageModel model) throws WalletSdkException {

        String result = "";
        String requestId = "";
        String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));

        ErrorAssert.notNull(tbEwaCstmrMastrMapper.select(cstmrNo),ErrorCode.USER_ID_NOT_FOUND);
        ErrorAssert.isTrue(!StringUtils.equals(tbEwaCstmrMastrMapper.select(cstmrNo).getCstmrSttusCd() ,"1"), ErrorCode.INVALID_CUSTOMER_STATE);
        String aliasNm = model.getTbAcnutMastr().getAliasNm();
        String walletInsttCd = model.getTbAcnutMastr().getWalletInsttCd();
        BigDecimal trnscAmt = model.getTbAcnutMastr().getTrnscAmt();
        boolean extYn = StringUtils.equals(walletInsttCd, bankCd);

        // step0 입력값 검증
        ErrorAssert.hasLength(cstmrNo, ErrorCode.CUSTOMER_ID_REQUIRED);
        ErrorAssert.hasLength(aliasNm, ErrorCode.INVALID_ALIAS);
        ErrorAssert.hasLength(trnscAmt.toString(), ErrorCode.EMPTY_TRANSACTION_AMOUNT);
        ErrorAssert.isNull(blockListManageMapper.selectBlclstWallet(bankCd, cstmrNo), ErrorCode.BLACKLIST_TARGET);
        blockListService.findBlockStatus(bankCd);

        // step1 수취인조회및 검증(수취인 지갑여부)
        AliasSearchInfo aliasSearchInfo = AliasSearchInfo.builder().aliasNm(aliasNm).trgetInstt(walletInsttCd).build();

        AliasResponse response = extYn ? aliasEwaBanksService.readFromLocal(aliasSearchInfo)
                : aliasEwaBanksService.read(aliasSearchInfo);

        // step2 이용자 지갑 검증
        TbWalletMastr tbWalletMastrA = this.tbEwaWalletMastrMapper.selectWalletByWalletSe("A");
        Signer signerA = Signer.builder().walletAddress(tbWalletMastrA.getWalletAdres())
                .hdKeyAccToken(tbWalletMastrA.getHdKeyaccToken())
                .hdKeyId(tbWalletMastrA.getHdKeyid()).build();
        TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(cstmrNo);
        ErrorAssert.hasLength(tbCstmrMastr.getWalletAdres(), ErrorCode.WALLET_MISSING);
        ErrorAssert.hasLength(response.getWalletAdres(), ErrorCode.WALLET_INFO_NOT_FOUND);
        ErrorAssert.isTrue(!StringUtils.equals(tbCstmrMastr.getWalletAdres(), response.getWalletAdres()), ErrorCode.WRONG_TRANSFER_REQUIRED);
        ErrorAssert.hasLength(tbCstmrMastr.getWalletAdres(), ErrorCode.WALLET_MISSING);
        ErrorAssert.hasLength(response.getWalletAdres(), ErrorCode.WALLET_INFO_NOT_FOUND);
        ErrorAssert.isTrue(!StringUtils.equals(tbCstmrMastr.getWalletAdres(), response.getWalletAdres()), ErrorCode.WRONG_TRANSFER_REQUIRED);


        // step3 DC1 차감(송금자) > DC1 증액(수취인)
        BigInteger fromBalance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);
        BigInteger toBalance = _blockChain.getBalance(response.getWalletAdres(), bankCd, CoinType.DC1);
        ErrorAssert.isTrue(fromBalance.compareTo(BigInteger.ZERO) > 0, ErrorCode.INSUFFICIENT_BALANCE);
        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.TRANS_AMOUNT_EXCEEDS_BALANCE);
        ErrorAssert.isTrue(fromBalance.compareTo(BigInteger.ZERO) > 0, ErrorCode.INSUFFICIENT_BALANCE);
        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.TRANS_AMOUNT_EXCEEDS_BALANCE);


        // step 3-1 통화정책 한도검증 (1회 , 1일)
        ewaPolicyManageService.policyLimit(trnscAmt, ewaWalletManageService.selectAmtPerDay(cstmrNo), null);
        ewaPolicyManageService.policyTransferLimit(ewaWalletManageService.selectAmtCntPerDay(cstmrNo));

        /*
##### kafka message 생성
##### (당,티헹)
##### kafka message 0 이용자 >> 이용자 (거래내역용)
##### (티헹)
##### kafka message 1 이용자 >> TD환수
##### kafka message 2 출금은행 당좌 >> 입금은행 당좌
##### kafka message 3 출금은행 TD 발행 >> 이용자
         */
        List<TxMessage> txMessages = new ArrayList<>();
        TxMessage txMessage = TxMessage.builder().command(CommandType.T1)
                .txDbId(IdGenerationUtil.createUid("TB_DC_TRANS_MASTR"))
                .from(tbCstmrMastr.getWalletAdres())
                .to(response.getWalletAdres())
                .fromBankCode(bankCd)
                .toBankCode(walletInsttCd)
                .amount(trnscAmt.longValue())
                .timestamp(new Date())
                .fromTrnscAfterBlce(fromBalance.subtract(trnscAmt.toBigInteger()).longValue())
                .personId(cstmrNo)
                .coin(CoinType.DC1)
                .retry(0).build();
        txMessages.add(txMessage);

        // kafka message 0 이용자 >> 이용자 (거래내역용)
        txMessages.get(0).setFromAcnutno(tbCstmrMastr.getAcnutno());
        txMessages.get(0).setAcnutno(response.getAcnutno());
        txMessages.get(0).setAliasNm(tbCstmrMastr.getAliasNm());
        txMessages.get(0).setFromAliasNm(aliasNm);
        txMessages.get(0).setWalletDpstr(response.getPersonNm());
        txMessages.get(0).setFromWalletDpstr(tbCstmrMastr.getKoreanNm());
        txMessages.get(0).setTxType(TrnscType.TRANSFER.getValue());

        // step 5 당행 송금
        if (extYn) {
            requestId = kafkaProducer.setSaga(txMessages);

            // step 5 카프카 등록및 오류처리
            try {
                kafkaProc(txMessages, requestId, "W");

                txMessage.setTrnscAfterBlce(toBalance.add(trnscAmt.toBigInteger()).longValue());
                result = _blockChain.sendLimitTransaction(requestId, tbCstmrMastr.getOwner(), response.getWalletAdres(),
                        trnscAmt.toBigInteger(), bankCd, CoinType.DC1, getCallBack(txMessages, CoinType.DC1.name()));

            } catch (Exception e) {
                kafkaProc(txMessages, requestId, "R");
                throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
            }

        } else {// 타행 송금

            txMessages.add(txMessage.clone());
            txMessages.add(txMessage.clone());
            txMessages.add(txMessage.clone());

            // kafka message 1 이용자 >> TD환수
            String tdRedempWalletAddr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.R1.name()).getWalletAdres();
            txMessages.get(1).setCommand(CommandType.R1);
            txMessages.get(1).setTo(tdRedempWalletAddr);
            txMessages.get(1).setToBankCode(bankCd);

            // kafka message 2 출금은행 당좌 >> 입금은행 당좌
            String cWalletAddr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.C.name()).getWalletAdres();
            BigInteger cBlce = _blockChain.getPrivateBalance(signerA, cWalletAddr, bankCd, CoinType.CBDC);
            ErrorAssert.isTrue(cBlce.compareTo(BigInteger.valueOf(trnscAmt.longValue()))>=0, ErrorCode.INSUFFICIENT_BALANCE);

            String toCWalletAddr = ewaWalletManageService.selectExtWalletAddr(WalletType.C.name(), walletInsttCd);
            txMessages.get(2).setCommand(CommandType.T);
            txMessages.get(2).setFrom(cWalletAddr);
            txMessages.get(2).setTo(toCWalletAddr);
            txMessages.get(2).setFromBankCode(config.getBokCode());
            txMessages.get(2).setToBankCode(config.getBokCode());
            txMessages.get(2).setFromTrnscAfterBlce(0);
            txMessages.get(2).setCoin(CoinType.CBDC);
            txMessages.get(2).setTretInstt(bankCd);
            txMessages.get(2).setTxType(TrnscType.CBDCTRANS.getValue());

            // kafka message 3 출금은행 TD 발행 >> 이용자
            String toIWalletAddr = ewaWalletManageService.selectExtWalletAddr(WalletType.I1.name(), walletInsttCd);
            txMessages.get(3).setCommand(CommandType.I1);
            txMessages.get(3).setFrom(toIWalletAddr);
            txMessages.get(3).setFromBankCode(walletInsttCd);
            txMessages.get(3).setTretInstt(bankCd);
            txMessages.get(3).setFromTrnscAfterBlce(0);

            requestId = kafkaProducer.setSaga(txMessages);

            // step 5 카프카 등록및 오류처리
            try {
                kafkaProc(txMessages, requestId, "W");

                result = _blockChain.sendExtLimitTransaction(requestId, tbCstmrMastr.getOwner(), bankCd,
                        walletInsttCd,
                        response.getWalletAdres(), trnscAmt.toBigInteger(),
                        getCallBack(txMessages, CoinType.DC1.name()));

            } catch (Exception e) {
                kafkaProc(txMessages, requestId, "R");
                throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
            }
        }

        ErrorAssert.hasLength(result, ErrorCode.BLOCKCHAIN_TRANSFER_ERROR);
        ErrorAssert.hasLength(result, ErrorCode.BLOCKCHAIN_TRANSFER_ERROR);

        return requestId;
    }

    /**
##### 예금 토큰 결제 (DC1 예금 토큰 결제)
     *
##### @param model
##### @return
##### @throws WalletSdkException
     */
    public String payment(AcnutManageModel model) throws WalletSdkException {

        String result = "";
        String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));
        ErrorAssert.notNull(tbEwaCstmrMastrMapper.select(cstmrNo), ErrorCode.CUSTOMER_NOT_FOUND,cstmrNo);
        ErrorAssert.isTrue(!StringUtils.equals(tbEwaCstmrMastrMapper.select(cstmrNo).getCstmrSttusCd() ,"1"), ErrorCode.INVALID_CUSTOMER_STATE);
        String aliasNm = model.getTbAcnutMastr().getAliasNm();
        String walletInsttCd = model.getTbAcnutMastr().getWalletInsttCd();
        BigDecimal trnscAmt = model.getTbAcnutMastr().getTrnscAmt();
        boolean extYn = StringUtils.equals(walletInsttCd, bankCd);

        // step0 입력값 검증
        ErrorAssert.hasLength(cstmrNo, ErrorCode.CUSTOMER_ID_REQUIRED);
        ErrorAssert.hasLength(aliasNm, ErrorCode.INVALID_ALIAS);
        ErrorAssert.hasLength(trnscAmt.toString(), ErrorCode.INVALID_AMOUNT);
        ErrorAssert.isNull(blockListManageMapper.selectBlclstWallet(bankCd, cstmrNo), ErrorCode.BLACKLIST_TARGET);
        blockListService.findBlockStatus(bankCd);

        // step1 수취인조회및 검증(수취인 지갑여부)
        AliasSearchInfo aliasSearchInfo = AliasSearchInfo.builder().aliasNm(aliasNm).trgetInstt(walletInsttCd).build();

        AliasResponse response = extYn ? aliasEwaBanksService.readFromLocal(aliasSearchInfo)
                : aliasEwaBanksService.read(aliasSearchInfo);

        // step2 이용자 지갑 검증
        TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(cstmrNo);
        ErrorAssert.hasLength(tbCstmrMastr.getWalletAdres(), ErrorCode.WALLET_MISSING);
        ErrorAssert.hasLength(response.getWalletAdres(), ErrorCode.INVALID_WALLET_INFO_ERROR);
        ErrorAssert.isTrue(!StringUtils.equals(tbCstmrMastr.getWalletAdres(), response.getWalletAdres()),ErrorCode.WRONG_PAYMENT_REQUIRED);


        // step3 DC1 차감(송금자) > DC1 증액(결제처)
        BigInteger fromBalance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);
        BigInteger toBalance = _blockChain.getBalance(response.getWalletAdres(), bankCd, CoinType.DC1);
        ErrorAssert.isTrue(fromBalance.compareTo(BigInteger.ZERO) > 0, ErrorCode.INSUFFICIENT_BALANCE);
        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.PAYMENT_AMOUNT_EXCEEDS_BALANCE);
        ErrorAssert.isTrue(fromBalance.compareTo(BigInteger.ZERO) > 0, ErrorCode.INSUFFICIENT_BALANCE);
        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.PAYMENT_AMOUNT_EXCEEDS_BALANCE);



        /*
##### kafka message 생성
##### (당,티헹)
##### kafka message 0 이용자 >> 이용자 (거래내역용)
##### (티헹)
##### kafka message 1 이용자 >> TD환수
##### kafka message 2 출금은행 당좌 >> 입금은행 당좌
##### kafka message 3 출금은행 TD 발행 >> 이용자
         */
        List<TxMessage> txMessages = new ArrayList<>();
        TxMessage txMessage = TxMessage.builder().command(CommandType.T1)
                .txDbId(IdGenerationUtil.createUid("TB_DC_TRANS_MASTR"))
                .from(tbCstmrMastr.getWalletAdres())
                .to(response.getWalletAdres())
                .fromBankCode(bankCd)
                .toBankCode(walletInsttCd)
                .amount(trnscAmt.longValue())
                .timestamp(new Date())
                .fromTrnscAfterBlce(fromBalance.subtract(trnscAmt.toBigInteger()).longValue())
                .personId(cstmrNo)
                .coin(CoinType.DC1)
                .retry(0).build();
        txMessages.add(txMessage);

        // kafka message 0 이용자 >> 이용자 (거래내역용)
        txMessages.get(0).setFromAcnutno(tbCstmrMastr.getAcnutno());
        txMessages.get(0).setAcnutno(response.getAcnutno());
        txMessages.get(0).setAliasNm(tbCstmrMastr.getAliasNm());
        txMessages.get(0).setFromAliasNm(aliasNm);
        txMessages.get(0).setWalletDpstr(response.getPersonNm());
        txMessages.get(0).setFromWalletDpstr(tbCstmrMastr.getKoreanNm());
        txMessages.get(0).setTxType(TrnscType.PAYMENT.getValue());

        String requestId = "";

        // step 5 당행 결제
        if (extYn) {
            requestId = kafkaProducer.setSaga(txMessages);

            // step 5 카프카 등록및 오류처리
            try {
                kafkaProc(txMessages, requestId, "W");

                txMessage.setTrnscAfterBlce(toBalance.add(trnscAmt.toBigInteger()).longValue());
                result = _blockChain.sendTransaction(requestId, tbCstmrMastr.getOwner(), response.getWalletAdres(),
                        trnscAmt.toBigInteger(), bankCd, CoinType.DC1, getCallBack(txMessages, CoinType.DC1.name()));
            } catch (Exception e) {
                kafkaProc(List.of(txMessage), requestId, "R");
                throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
            }

        } else {// 타행 결제

            txMessages.add(txMessage.clone());
            txMessages.add(txMessage.clone());
            txMessages.add(txMessage.clone());

            // kafka message 1 이용자 >> TD환수
            String tdRedempWalletAddr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.R1.name()).getWalletAdres();
            txMessages.get(1).setCommand(CommandType.R1);
            txMessages.get(1).setTo(tdRedempWalletAddr);
            txMessages.get(1).setToBankCode(bankCd);

            // kafka message 2 출금은행 당좌 >> 입금은행 당좌
            String cWalletAddr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.C.name()).getWalletAdres();
            String toCWalletAddr = ewaWalletManageService.selectExtWalletAddr(WalletType.C.name(), walletInsttCd);
            txMessages.get(2).setCommand(CommandType.T);
            txMessages.get(2).setFrom(cWalletAddr);
            txMessages.get(2).setTo(toCWalletAddr);
            txMessages.get(2).setFromBankCode(config.getBokCode());
            txMessages.get(2).setToBankCode(config.getBokCode());
            txMessages.get(2).setTretInstt(bankCd);
            txMessages.get(2).setFromTrnscAfterBlce(0);
            txMessages.get(2).setTxType(TrnscType.CBDCTRANS.getValue());
            txMessages.get(2).setCoin(CoinType.CBDC);

            // kafka message 3 출금은행 TD 발행 >> 이용자
            String toIWalletAddr = ewaWalletManageService.selectExtWalletAddr(WalletType.I1.name(), walletInsttCd);
            txMessages.get(3).setCommand(CommandType.I1);
            txMessages.get(3).setFrom(toIWalletAddr);
            txMessages.get(3).setFromBankCode(walletInsttCd);
            txMessages.get(3).setTretInstt(bankCd);
            txMessages.get(3).setFromTrnscAfterBlce(0);

            requestId = kafkaProducer.setSaga(txMessages);

            // step 5 카프카 등록및 오류처리
            try {
                kafkaProc(txMessages, requestId, "W");

                result = _blockChain.sendExtTransaction(requestId, tbCstmrMastr.getOwner(), bankCd, walletInsttCd,
                        response.getWalletAdres(), trnscAmt.toBigInteger(),
                        getCallBack(txMessages, CoinType.DC1.name()));

            } catch (Exception e) {
                kafkaProc(txMessages, requestId, "R");
                throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
            }
        }

        ErrorAssert.hasLength(result, ErrorCode.KAFKA_PRODUCE_ERROR);

        return requestId;
    }

    private void kafkaProc(List<TxMessage> txMessages, String requestId, String trnscSttusCd) {

        txMessages.forEach(tx -> {
            tx.setTrnscSttusCd(trnscSttusCd);
            tx.setRequestId(requestId);
        });

        try {
            kafkaProducer.send(topicTxRequest, txMessages);
        } catch (InterruptedException | ExecutionException e) {
            throw new BizException(ErrorCode.SERVER_ERROR  ,  requestId ,  e);
        } catch (Exception e) {
            throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);

        }
        ErrorAssert.hasLength(requestId, ErrorCode.KAFKA_PRODUCE_ERROR);
    }

    /**
##### 계좌인증정보입력(검증) 워드3+난수3 자리생성
     *
##### @param model
##### @return
     */
    public String accountValid(AcnutManageModel model) {

        String[] words = { "송아리", "도사리", "미리내", "가루비", "도둑눈", "산돌림", "나비잠", "흰여울", "그루잠", "희나리" };

        StringBuilder result = new StringBuilder();
        result.append(words[rand.nextInt(words.length)]);

        ErrorAssert.isTrue(tbEwaAcnutMastrMapper.accountValid(model.getTbAcnutMastr()) != null,
                ErrorCode.WALLET_INFO_NOT_FOUND);

        // [Mockup][IF-GWS-O-007
        // ewaBridgeServiceImpl.validityCheck();

        return result.append(rand.nextInt(900) + 100).toString();
    }

    /**
##### 계좌 상세 조회
     *
##### @param cstmrNo
##### @return
     */
    public AcnutManageModel read(String cstmrNo) {

        AcnutManageModel model = new AcnutManageModel();
        model.setTbAcnutMastr(tbEwaAcnutMastrMapper.select(cstmrNo));
        return model;
    }

    public boolean lock(String userId) {
    	log.error("hazelcastInstance lock ::: {}", userId);
        FencedLock lock = hazelcastInstance.getCPSubsystem().getLock("lock:" + userId);
        return lock.tryLock(10, TimeUnit.SECONDS);
    }

    public void unlock(String userId) {
    	log.error("hazelcastInstance unlock :::: {}", userId);
        FencedLock lock = hazelcastInstance.getCPSubsystem().getLock("lock:" + userId);
        lock.unlock();
    }
 
    /**
##### 보유계좌 잔액 조회
     *
##### @param model
##### @return
     */
    /* 사용하지 않는 코드 주석처리. 2025.02.05 오재경
    public JsonNode balance(AcnutManageModel model) {
        // step0 입력값 검증
        validateInput(model);

        String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));
        TbCstmrMastr tbCstmrMastr = validateCustomer(cstmrNo);
        
        // 보유계좌 잔액 조회 Gateway 호출.
        HashMap<String, Object> paramBalance = new HashMap<>();
        paramBalance.put("inqDscd", "01");
        paramBalance.put("dpsAcno", tbCstmrMastr.getAcnutno());
        return apiCallHelper.callURL(configProperties.getGateway().getBalance().getUrl(),
                                            null,
                                            (new ObjectMapper()).valueToTree(paramBalance),
                                            HttpMethod.POST);
    } */
    
    /**
##### Checks gateway response for errors. If error exists, throws CBSException.
##### @param response Gateway response DTO
##### @param errorHandler Optional handler to execute before throwing exception
##### @return true if no error (errcode is null), false if there is an error
##### @throws CBSException if error is found
     */
    private void checkGWResponse(CbsRampResponseDto response, Runnable errorHandler) {
        String errcode = response.getErrcode();
        if (errcode != null) {
            
            if (errorHandler != null) {
                errorHandler.run();
            }

            String errmsg = response.getErrusrmsg();
            List<CbsErrorDto> errlist = response.getErrorlist();
            if (errlist != null && !errlist.isEmpty()) {
                errcode = errlist.get(0).getMsgCd();
                errmsg = errlist.get(0).getMainMsgTxt();
            }
            log.error("계정계 호출 에러 {} {}", errcode, errmsg);
            throw new CBSException(errcode, errmsg);
        }
    }
    
    private CbsRampResponseDto parseGatewayResponse(JsonNode response, String errorContext) throws BizException {
        try {
            return objectMapper.treeToValue(response, CbsRampResponseDto.class);
        } catch (JsonProcessingException e) {
            log.error("계정계 " + errorContext + " 응답[{}] 파싱 에러: {}", response.toPrettyString(), e.getMessage());
            throw new BizException(ErrorCode.PARSING_ERROR, e);
        }
    }
    
}
Now I need to change issueDepositToken.
1. add a parameter named 'TxDbId' which is nullable.
Then there are 2 cases.
1. TxDbId is null, then just do everything in issueDepositToken.
2. TxDbId is not null, then skip 3-1, 4 and set kafka message's TxDbId with the parameter.
```
#### 답
```java
/**
##### 계정계를 포함한 전체 onRamp 로직을 실행.
##### convDeposit에서 호출
 */
public String issueDepositToken(String cstmrNo, BigDecimal trnscAmt) throws WalletSdkException {
    return issueDepositTokenInternal(cstmrNo, trnscAmt, true);
}

/**
##### 계정계 호출을 건너뛰고 토큰 발행만 수행.
##### offRamp 원복이나 onRamp 대사 불일치 처리에서 호출
 */
public String reissueDepositToken(String cstmrNo, BigDecimal trnscAmt, String txDbId) throws WalletSdkException {
    return issueDepositTokenInternal(cstmrNo, trnscAmt, false, txDbId);
}

private String issueDepositTokenInternal(String cstmrNo, BigDecimal trnscAmt, boolean withCoreBanking) throws WalletSdkException {
    return issueDepositTokenInternal(cstmrNo, trnscAmt, withCoreBanking, null);
}

/**
##### 예금토큰 발행의 내부 구현
##### @param cstmrNo 고객번호
##### @param trnscAmt 거래금액
##### @param withCoreBanking true면 계정계 호출 포함, false면 계정계 호출 제외
##### @param txDbId 재발행시 사용할 거래ID (withCoreBanking가 false일 때만 사용)
 */
private String issueDepositTokenInternal(String cstmrNo, BigDecimal trnscAmt, boolean withCoreBanking, String txDbId) 
        throws WalletSdkException {
    TbCstmrMastr tbCstmrMastr = validateCustomer(cstmrNo);
    BigDecimal acnutnoBlce = tbCstmrMastr.getAcnutnoBlce();
    validateAmount(trnscAmt);
    
    // step1 지갑 검증
    TbWalletMastr tbWalletMastr = validateWallet(WalletType.I1, tbCstmrMastr, ErrorCode.INVALID_TD_ISSUANCE_WALLET);
    
    // step 2 계좌 예치금 검증 (예금 >= 전환입금),(발행준비 >= 전환입금)
    BigInteger fromBalance = _blockChain.getBalance(tbWalletMastr.getWalletAdres(), bankCd, CoinType.DC1);
    BigInteger toBalance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);
    log.debug("[jkoh] TD 발행 준비지갑 잔액 fromBalance: {}", fromBalance);
    log.debug("[jkoh] 이용자 지갑 잔액 toBalance: {}", toBalance);
    ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.INSUFFICIENT_ISU_ACCOUNT_BALANCE);
    log.debug("[jkoh] step 2 지갑, 잔액 검증 완료");

    String wGuid = null;
    String finalTxDbId = txDbId;
    Dc1IsuMastr dc1IsuMastr = null;

    // Core banking and DB record creation only if requested
    if (withCoreBanking) {
        // step 3-1 계정계 출금 요청 Gateway 호출
        CbsRampResponseDto onRampResponse = onRampCoreBanking(cstmrNo, tbCstmrMastr, acnutnoBlce, trnscAmt, toBalance);
        wGuid = onRampResponse.getTrnLogKeyVal();

        // step4 계정계에서 출금이 정상적으로 되면 DC1 발행 기록
        dc1IsuMastr = Dc1IsuMastr.builder()
                .dc1IsuSttus("W")
                .trgetInstt(bankCd)
                .dc1IsuAmount(trnscAmt.longValue())
                .applcntId(cstmrNo)
                .mcaGuid(onRampResponse.getTrnLogKeyVal())
                .cbsTrnAcno(onRampResponse.getDpsInpAcno())
                .cbsTrnDt(onRampResponse.getTrnDt())
                .cbsTrnSrno(onRampResponse.getTrnSrno())
                .build()
                .newId();
        
        log.debug("[jkoh] dc1IsuMaster data to save: {}", dc1IsuMastr);
        try {
            genericMapperService.insertModel(dc1IsuMastr, Dc1IsuMastr.class, 
                    EwaDc1IsuMastrMapper.class, "insert");
            log.debug("[jkoh] 예금토큰 발행 내역 저장 완료 {}", dc1IsuMastr);
            finalTxDbId = dc1IsuMastr.getDc1IsuId();
        } catch (Exception e) {
            log.error("계좌({}) 거래키({}) 거래일련번호({})에 대한 예금토큰 발행 내역 신규저장 에러: {}", 
                    tbCstmrMastr.getAcnutno(), onRampResponse.getTrnLogKeyVal(), 
                    onRampResponse.getTrnSrno(), e.getMessage());
            handleBankingFailure(cstmrNo, acnutnoBlce, trnscAmt, wGuid, tbCstmrMastr.getAcnutno());
            throw new BizException(ErrorCode.DATA_ACCESS_ERROR, e.getMessage(), e);
        }
    }

    // Create Kafka message
    TxMessage txMessage = TxMessage.builder()
            .command(CommandType.I1)
            .txDbId(finalTxDbId)
            .from(tbWalletMastr.getWalletAdres())
            .to(tbCstmrMastr.getWalletAdres())
            .fromWalletDpstr(tbWalletMastr.getWalletNm())
            .walletDpstr(tbCstmrMastr.getKoreanNm())
            .fromBankCode(bankCd)
            .toBankCode(bankCd)
            .amount(trnscAmt.longValue())
            .timestamp(new Date())
            .trnscAfterBlce(toBalance.add(trnscAmt.toBigInteger()).longValue())
            .acnutno(tbCstmrMastr.getAcnutno())
            .personId(cstmrNo)
            .coin(CoinType.DC1)
            .txType(TrnscType.DEPOSIT.getValue())
            .retry(0)
            .build();

    log.debug("[jkoh] Kafka message created: {}", txMessage);

    String requestId = null;
    try {
        requestId = kafkaProducer.setSaga(List.of(txMessage));
        log.debug("[jkoh] Saga requestId created: {}", requestId);
    } catch (Exception e) {
        log.error("Saga requestId 생성 에러: {}", e.getMessage());
        if (withCoreBanking) {
            handleBankingFailure(cstmrNo, acnutnoBlce, trnscAmt, wGuid, tbCstmrMastr.getAcnutno());
        }
        throw e;
    }

    try {
        kafkaProc(List.of(txMessage), requestId, "W");
        log.debug("[jkoh] Kafka message sent successfully");
    } catch (BizException e) {
        log.error("Kafka 메시지[{}] 송신 에러: {}", requestId, e.getMessage());
        if (withCoreBanking) {
            handleBankingFailure(cstmrNo, acnutnoBlce, trnscAmt, wGuid, tbCstmrMastr.getAcnutno());
        }
        throw e;
    }
    
    try {
        // 예금토큰 발행 DC1 발행준비 > 이용자 : 분산원장 Call , 참가기관 단일서명
        String result = _blockChain.sendTransaction(requestId, tbWalletMastr.getOwner(), 
                tbCstmrMastr.getWalletAdres(),
                trnscAmt.toBigInteger(), bankCd, CoinType.DC1, 
                getCallBack(List.of(txMessage), CoinType.DC1.name()));
        ErrorAssert.hasLength(result, ErrorCode.BLOCKCHAIN_CALL_FAILURE);
    } catch (Exception e) {
        log.error("예금토큰 발행({} -> {}) 블록체인 호출 에러 {}", 
                tbWalletMastr.getWalletAdres(), tbCstmrMastr.getWalletAdres(), e.getMessage());
        if (withCoreBanking) {
            handleBankingFailure(cstmrNo, acnutnoBlce, trnscAmt, wGuid, tbCstmrMastr.getAcnutno());
        }
        kafkaProc(List.of(txMessage), requestId, "R");
        throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
    }
    
    log.debug("[jkoh] 블록체인 요청 완료");
    return finalTxDbId;
}

/**
##### 계정계 관련 실패 처리를 한 곳에서 처리
 */
private void handleBankingFailure(String cstmrNo, BigDecimal acnutnoBlce, BigDecimal trnscAmt, 
        String wGuid, String acnutno) {
    updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
    if (wGuid != null) {
        handleOnRampFailure(wGuid, acnutno, trnscAmt);
    }
}
```
### issueDepositToken을 활용하여 변경하기 전 소스와 변경 후 소스 비교 점검
#### 질문: 소스를 비교하고 업무 처리흐름이 동일한지 판별
```java
package kr.or.cbdc.application.ewa.cstmr.service;

import kr.or.bok.wallet.sdk.errorhandling.WalletSdkException;
import kr.or.bok.wallet.sdk.model.common.Signer;
import kr.or.cbdc.application.common.alias.mapper.BlockListManageMapper;
import kr.or.cbdc.application.common.alias.model.AliasResponse;
import kr.or.cbdc.application.common.alias.model.AliasSearchInfo;
import kr.or.cbdc.application.common.alias.service.BaseBlockListServiceImpl;
import kr.or.cbdc.application.common.alias.service.BaseBlockListServiceImpl;
import kr.or.cbdc.application.ewa.alias.service.AliasEwaBanksServiceImpl;
import kr.or.cbdc.application.ewa.common.dto.GwRampDto;
import kr.or.cbdc.application.ewa.common.dto.GwRampFailDto;
import kr.or.cbdc.application.ewa.common.dto.CbsErrorDto;
import kr.or.cbdc.application.ewa.common.dto.CbsRampResponseDto;
import kr.or.cbdc.application.ewa.cstmr.model.AcnutManageModel;
import kr.or.cbdc.application.ewa.policy.service.EwaPolicyManageServiceImpl;
import kr.or.cbdc.application.ewa.wallet.service.EwaWalletManageServiceImpl;
import kr.or.cbdc.config.props.ConfigProperties;
import kr.or.cbdc.domain.main.mapper.ewa.cstmr.TbEwaAcnutMastrMapper;
import kr.or.cbdc.domain.main.mapper.ewa.cstmr.TbEwaCstmrMastrMapper;
import kr.or.cbdc.domain.main.mapper.ewa.dc1.EwaDc1IsuMastrMapper;
import kr.or.cbdc.domain.main.mapper.ewa.dc1.EwaDc1RedempMastrMapper;
import kr.or.cbdc.domain.main.mapper.ewa.wallet.TbEwaWalletMastrMapper;
import kr.or.cbdc.domain.main.model.com.wallet.TbWalletMastr;
import kr.or.cbdc.domain.main.model.ewa.cstmr.TbCstmrMastr;
import kr.or.cbdc.domain.main.model.ewa.dc1.Dc1IsuMastr;
import kr.or.cbdc.domain.main.model.ewa.dc1.Dc1RedempMastr;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.BizException;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.CBSException;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.ErrorAssert;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.ErrorCode;
import kr.or.cbdc.infrastructure.idgen.util.IdGenerationUtil;
import kr.or.cbdc.infrastructure.mybatis.GenericMapperService;
import kr.or.cbdc.infrastructure.mybatis.GenericMapperService;
import kr.or.cbdc.infrastructure.profile.EwaProfileCondition;
import kr.or.cbdc.infrastructure.queue.KafkaProducer;
import kr.or.cbdc.infrastructure.queue.TxMessage;
import kr.or.cbdc.infrastructure.util.TokenUtils;
import kr.or.cbdc.interfaces.blockchain.BlockChainHelper;
import kr.or.cbdc.interfaces.blockchain.CoinType;
import kr.or.cbdc.interfaces.blockchain.CommandType;
import kr.or.cbdc.interfaces.blockchain.SupportCallback;
import kr.or.cbdc.interfaces.blockchain.TrnscType;
import kr.or.cbdc.interfaces.blockchain.WalletType;
import kr.or.cbdc.interfaces.blockchain.BlockChainHelper;
import kr.or.cbdc.interfaces.blockchain.CoinType;
import kr.or.cbdc.interfaces.blockchain.CommandType;
import kr.or.cbdc.interfaces.blockchain.SupportCallback;
import kr.or.cbdc.interfaces.blockchain.TrnscType;
import kr.or.cbdc.interfaces.blockchain.WalletType;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Conditional;
import org.springframework.dao.DataAccessException;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.HttpServerErrorException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.stereotype.Service;

import com.hazelcast.core.HazelcastInstance;
import com.hazelcast.cp.lock.FencedLock;
import com.hazelcast.sql.impl.expression.BiExpression;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Random;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;

import kr.or.cbdc.interfaces.ApiCallHelper;
import kr.or.cbdc.config.props.ConfigProperties;
import java.util.function.Supplier;
import org.springframework.http.HttpMethod;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import io.grpc.netty.shaded.io.netty.util.internal.ObjectUtil;

import java.util.HashMap;

/**
##### 계좌 관리 Service
 */
@Slf4j
@Service
@Conditional(EwaProfileCondition.class)
public class EwaAcnutManageServiceImpl extends SupportCallback {

    private @Autowired TbEwaCstmrMastrMapper tbEwaCstmrMastrMapper;
    private @Autowired TbEwaAcnutMastrMapper tbEwaAcnutMastrMapper;
    private @Autowired TbEwaWalletMastrMapper tbEwaWalletMastrMapper;
    private @Autowired EwaPolicyManageServiceImpl ewaPolicyManageService;
    private @Autowired EwaWalletManageServiceImpl ewaWalletManageService;
    private @Autowired AliasEwaBanksServiceImpl aliasEwaBanksService;
    private @Autowired BlockListManageMapper blockListManageMapper;
    private @Autowired BlockChainHelper _blockChain;
    private @Autowired KafkaProducer kafkaProducer;
    private @Autowired GenericMapperService genericMapperService;
    private @Autowired ConfigProperties config;
    private @Autowired BaseBlockListServiceImpl blockListService;
    private @Autowired ApiCallHelper apiCallHelper;
    private @Autowired ConfigProperties configProperties;
    private @Autowired EwaDc1IsuMastrMapper ewaDc1IsuMastrMapper;
    private @Autowired HazelcastInstance hazelcastInstance;
    private int baseNo = 2;

    private static final Random rand = new Random();
    private static final ObjectMapper objectMapper = new ObjectMapper();

    private void validateInput(AcnutManageModel model) {
        ErrorAssert.notNull(model, ErrorCode.MISSING_REQUIRED_FIELD);
        ErrorAssert.notNull(model.getTbAcnutMastr(), ErrorCode.MISSING_REQUIRED_FIELD);
        ErrorAssert.notNull(model.getTbAcnutMastr().getTrnscAmt(), ErrorCode.MISSING_REQUIRED_FIELD);
    }
    
    private TbCstmrMastr validateCustomer(String cstmrNo) {
        ErrorAssert.hasLength(cstmrNo, ErrorCode.CUSTOMER_ID_REQUIRED);
        TbCstmrMastr customer = tbEwaCstmrMastrMapper.select(cstmrNo);
        ErrorAssert.notNull(customer, ErrorCode.CUSTOMER_NOT_FOUND, cstmrNo);
        ErrorAssert.isTrue(!StringUtils.equals(customer.getCstmrSttusCd(), "1"), ErrorCode.INVALID_CUSTOMER_STATE);
        return customer;
    }
    
    private BigDecimal validateAmount(BigDecimal amount) {
        ErrorAssert.notNull(amount, ErrorCode.INVALID_TRANSACTION_AMOUNT);
        ErrorAssert.isTrue(amount.compareTo(BigDecimal.ZERO) > 0, ErrorCode.INVALID_TRANSACTION_AMOUNT);
        ErrorAssert.isTrue(amount.compareTo(new BigDecimal("999999999999.99")) <= 0, 
                     ErrorCode.INVALID_TRANSACTION_AMOUNT);
        return amount;
    }

    public TbWalletMastr validateWallet(WalletType walletType, TbCstmrMastr tbCstmrMastr, ErrorCode walletNotFoundError) {
        TbWalletMastr tbWalletMastr = tbEwaWalletMastrMapper.selectWalletSe(walletType.toString());
        log.debug("[jkoh] I1 wallet: {} cstmr's wallte address: {}", tbWalletMastr, tbCstmrMastr.getWalletAdres());
        ErrorAssert.notNull(tbWalletMastr, walletNotFoundError);
        ErrorAssert.hasLength(tbCstmrMastr.getWalletAdres(), ErrorCode.WALLET_MISSING);
        return tbWalletMastr;
    }
    
    public GwRampDto createRampParams(String internalTxId, TbCstmrMastr tbCstmrMastr, BigDecimal trnscAmt, BigInteger toBalance) {
        return GwRampDto.builder()
            .internalTxId(internalTxId)
            .customerId(tbCstmrMastr.getCstmrNo())
            .acnutNo(tbCstmrMastr.getAcnutno())
            .amount(trnscAmt)
            .beforeTdBalance(toBalance)
            .build();
    }

    public GwRampFailDto createRampFailParams(String internalTxId, String guid, String accountNo, BigDecimal amount) {
        return GwRampFailDto.builder()
            .internalTxId(internalTxId)
            .oriId(guid)
            .customerId(accountNo)
            .amount(amount)
            .build();
    }

    // Operation type enum
    public enum BalanceOperationType {
        ADD, SUBTRACT
    }

    public void updateCustomerBalance(String cstmrNo, BigDecimal balance, BigDecimal trnscAmt, BalanceOperationType operationType) {
        if (cstmrNo == null || trnscAmt == null || operationType == null) {
            throw new IllegalArgumentException("Customer, transaction amount, or operation type cannot be null");
        }
        
        BigDecimal newBalance = (operationType == BalanceOperationType.ADD)
                                ? balance.add(trnscAmt)
                                : balance.subtract(trnscAmt);
        TbCstmrMastr tbCstmrMastrUpdate = new TbCstmrMastr();
        tbCstmrMastrUpdate.setCstmrNo(cstmrNo);
        tbCstmrMastrUpdate.setAcnutnoBlce(newBalance);
        try {
            // Perform database update
            genericMapperService.updateModel(tbCstmrMastrUpdate,
                            TbCstmrMastr.class,
                            TbEwaAcnutMastrMapper.class,
                            "updateBlce");
        } catch (DataAccessException e) {
            log.error("고객 계좌({}) 잔액 변경({} -> {}) 중 에러가 발생했습니다. 에러 내용: {}"
                            , cstmrNo
                            , balance
                            , (operationType == BalanceOperationType.ADD) ? balance.add(trnscAmt) : balance.subtract(trnscAmt)
                            , e.getMessage());
            throw new BizException(ErrorCode.DATA_ACCESS_ERROR, e.getMessage());
        } catch (Exception e) {
            log.error("고객 계좌({}) 잔액 변경({} -> {}) 중 에러가 발생했습니다. 에러 내용: {}"
                            , cstmrNo
                            , balance
                            , (operationType == BalanceOperationType.ADD) ? balance.add(trnscAmt) : balance.subtract(trnscAmt)
                            , e.getMessage());
            throw new BizException(ErrorCode.SERVER_ERROR, e.getMessage());
        }
    }
    
    private void handleOnRampFailure(String wGuid, String acnutno, BigDecimal trnscAmt) {
        GwRampFailDto paramOnRampFail = createRampFailParams("internalTxId", wGuid, acnutno, trnscAmt);
        try {
            JsonNode respOnRampFail = apiCallHelper.callURL(configProperties.getGateway().getOnRampFail().getUrl(),
                                        null,
                                        objectMapper.valueToTree(paramOnRampFail),
                                        HttpMethod.POST);
            CbsRampResponseDto onRampFailResponse = parseGatewayResponse(respOnRampFail, "onRampFail");
            checkGWResponse(onRampFailResponse, null);
        } catch (ResourceAccessException e) {
            // We don't rethrow here as this is already in an error handling path
            log.error("GlobalID({}) account({}) OnRampFail API timeout or connection error: {}", wGuid, acnutno, e.getMessage());
        } catch (HttpClientErrorException e) {
            log.error("GlobalID({}) account({}) OnRampFail API client error (4xx): Status {}, Response {}", wGuid, acnutno, e.getStatusCode(), e.getResponseBodyAsString());
        } catch (HttpServerErrorException e) {
            log.error("GlobalID({}) account({}) OnRampFail API server error (5xx): Status {}, Response {}", wGuid, acnutno, e.getStatusCode(), e.getResponseBodyAsString());
        } catch (Exception e) {
            log.error("GlobalID({}) account({}) Unexpected error calling OnRampFail API: {}", wGuid, acnutno, e.getMessage(), e);
        }
    }

    /**
##### 전환 입금 (예금토큰 발행)
     *
##### @param model
##### @return
##### @throws WalletSdkException
     */
    public String convDeposit(AcnutManageModel model) throws WalletSdkException {
        if (lock(TokenUtils.getToken())) {
            try {
        		// step0 입력값 검증
        		validateInput(model);
        		
                String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));
        		TbCstmrMastr tbCstmrMastr = validateCustomer(cstmrNo);
        		BigDecimal acnutnoBlce = tbCstmrMastr.getAcnutnoBlce();
        		BigDecimal trnscAmt = validateAmount(model.getTbAcnutMastr().getTrnscAmt());
        		log.debug("[jkoh] convDeposit start cstmrNo: {} trnsAmt {}", cstmrNo, trnscAmt);
        		log.debug("[jkoh] tbCstmrMastr: {}", tbCstmrMastr);

                // step0 입력값 검증
        		ErrorAssert.isNull(blockListManageMapper.selectBlclstWallet(bankCd, cstmrNo), ErrorCode.BLACKLIST_TARGET);
                blockListService.findBlockStatus(bankCd);
        		

                // step1 지갑 검증
        		TbWalletMastr tbWalletMastr = validateWallet(WalletType.I1, tbCstmrMastr, ErrorCode.INVALID_TD_ISSUANCE_WALLET);

                // step 2 계좌 예치금 검증 (예금 >= 전환입금),(발행준비 >= 전환입금)
                BigInteger fromBalance = _blockChain.getBalance(tbWalletMastr.getWalletAdres(), bankCd, CoinType.DC1);
        		log.debug("[jkoh] TD 발행 준비지갑 잔액 fromBalance: {}", fromBalance);
                BigInteger toBalance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);
        		log.debug("[jkoh] 이용자 지갑 잔액 toBalance: {}", toBalance);

        		// IF-GWS-O-006 참가기관 이용자 Core Banking(계정계) 연계 계좌의 잔액 조회 --> 이건 20250207_Source에서 추가된 것. TODO??
                // ErrorAssert.isTrue(!(trnscAmt.compareTo(ewaBridgeServiceImpl.balance()) > 0),
                // ErrorCode.INSUFFICIENT_ACCOUNT_BALANCE);

        		ErrorAssert.isTrue(!(trnscAmt.compareTo(acnutnoBlce) > 0),ErrorCode.INSUFFICIENT_ACCOUNT_BALANCE);
        		ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.INSUFFICIENT_ISU_ACCOUNT_BALANCE);

                // step 2-1 통화정책 한도검증 (보유)
                ewaPolicyManageService.policyLimit(null, null, toBalance.add(trnscAmt.toBigInteger()),
                        trnscAmt.toBigInteger(), cstmrNo);
        		log.debug("[jkoh] OnRamp step 2 지갑, 잔액 검증 완료");
        		// step 3 계좌차감 처리 (계좌잔액 = 계좌잔액 - 전환입금액, DC1 = DC1잔액 + 전환입금액)
        		updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.SUBTRACT);
        		
        		// step 3-1 계정계 출금 요청 Gateway 호출.
        		// TODO 전자지갑 앱에서 internalTxId 보내주는지 확인하고 변경
        		log.debug("[jkoh] 계정계 gateway onRamp 호출 시작");
        		GwRampDto paramOnRamp = createRampParams("internalTxId", tbCstmrMastr, trnscAmt, toBalance);
        		JsonNode respOnRamp = null;
        		try {
        			respOnRamp = apiCallHelper.callURL(configProperties.getGateway().getOnRamp().getUrl(),
        					null,
        					objectMapper.valueToTree(paramOnRamp),
        					HttpMethod.POST);
        		} catch (ResourceAccessException e) {
        			updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
        			log.error("Account: {}, OnRamp API timeout or connection error: {}", tbCstmrMastr.getAcnutno(), e.getMessage());
        			throw new BizException(ErrorCode.BRIDGE_CALL_ERROR, e);
        		} catch (HttpClientErrorException e) {
        			updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
        			log.error("Account: {}, OnRamp API client error (4xx): Status {}, Response {}", tbCstmrMastr.getAcnutno(), e.getStatusCode(), e.getResponseBodyAsString());
        			throw new BizException(ErrorCode.BRIDGE_CALL_ERROR, e);
        		} catch (HttpServerErrorException e) {
        			updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
        			log.error("Account: {}, OnRamp API server error (5xx): Status {}, Response {}", tbCstmrMastr.getAcnutno(), e.getStatusCode(), e.getResponseBodyAsString());
        			throw new BizException(ErrorCode.BRIDGE_CALL_ERROR, e);
        		} catch (Exception e) {
        			updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
        			log.error("Unexpected error calling OnRamp API for account: {}, error: {}", tbCstmrMastr.getAcnutno(), e.getMessage(), e);
        			throw new BizException(ErrorCode.BRIDGE_CALL_ERROR, e);
        		}
        		
        		CbsRampResponseDto onRampResponse = parseGatewayResponse(respOnRamp, "onRamp");
        		checkGWResponse(onRampResponse, () -> updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD));
        		log.debug("[jkoh] OnRamp step 3 계정계 onRamp 요청 완료");
        		String wGuid = onRampResponse.getTrnLogKeyVal();
        		// step4 계정계에서 출금이 정상적으로 되면 DC1 발행 기록
                Dc1IsuMastr dc1IsuMastr = Dc1IsuMastr.builder().dc1IsuSttus("W")
                        .trgetInstt(bankCd)
                        .dc1IsuAmount(trnscAmt.longValue())
                        .applcntId(cstmrNo)
        				.mcaGuid(onRampResponse.getTrnLogKeyVal())
        				.cbsTrnAcno(onRampResponse.getDpsInpAcno())
        				.cbsTrnDt(onRampResponse.getTrnDt())
        				.cbsTrnSrno(onRampResponse.getTrnSrno())
                        .build().newId();
        		//ewaDc1IsuMastrMapper.insert(dc1IsuMastr);
        		log.debug("[jkoh] dc1IsuMaster data to save: {}", dc1IsuMastr);
        		try {
                genericMapperService.insertModel(dc1IsuMastr, Dc1IsuMastr.class, EwaDc1IsuMastrMapper.class, "insert");
        			log.debug("[jkoh] onRamp 예금토큰 발행 내역 저장 {}", dc1IsuMastr);
        		} catch (Exception e) {
        			log.error("계좌({}) 거래키({}) 거래일련번호({})에 대한 예금토큰 발행 내역 신규저장 에러: {}", tbCstmrMastr.getAcnutno(), onRampResponse.getTrnLogKeyVal(), onRampResponse.getTrnSrno(), e.getMessage());
        			updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
        			// 계정계에 취소 거래 보내기
        			handleOnRampFailure(wGuid, tbCstmrMastr.getAcnutno(), trnscAmt);
        			throw new BizException(ErrorCode.DATA_ACCESS_ERROR, e.getMessage(), e);
        		}
        		log.debug("[jkoh] OnRamp step 4 TD 발행 이력 저장 완료");

                // kafka message 생성
                TxMessage txMessage = TxMessage.builder().command(CommandType.I1)
                        .txDbId(dc1IsuMastr.getDc1IsuId())
                        .from(tbWalletMastr.getWalletAdres())
                        .to(tbCstmrMastr.getWalletAdres())
                        .fromWalletDpstr(tbWalletMastr.getWalletNm())
                        .walletDpstr(tbCstmrMastr.getKoreanNm())
                        .fromBankCode(bankCd)
                        .toBankCode(bankCd)
                        .amount(trnscAmt.longValue())
                        .timestamp(new Date())
                        .trnscAfterBlce(toBalance.add(trnscAmt.toBigInteger()).longValue())
                        .acnutno(tbCstmrMastr.getAcnutno())
                        .personId(cstmrNo)
                        .coin(CoinType.DC1)
                        .txType(TrnscType.DEPOSIT.getValue())
                        .retry(0).build();

        		log.debug("[jkoh] convDeposit kafka message: {}", txMessage);
        		String requestId = null;
        		try {
        			requestId = kafkaProducer.setSaga(List.of(txMessage));
        			log.debug("[jkoh] convDeposit requestId from setSage: {}", requestId);
        		} catch (Exception e) {
        			log.error("onRamp 트랜잭션 관리용 Saga requestId for txMessage {} 생성 에러: {}", txMessage, e);
        			updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
        			// 계정계에 취소 거래 보내기
        			handleOnRampFailure(wGuid, tbCstmrMastr.getAcnutno(), trnscAmt);
        			throw e;
        		}

                // step 5 카프카 등록및 오류처리
                try {
                    kafkaProc(List.of(txMessage), requestId, "W");
        			log.debug("[jkoh] convDeposit After kafka send and before call Blockchain sendTransaction");
        		} catch (BizException e) {
        			log.error("onRamp Kafka 메시지[{}] 송신 에러: {}", requestId, e.getMessage());
        			updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
        			// 계정계에 취소 거래 보내기
        			handleOnRampFailure(wGuid, tbCstmrMastr.getAcnutno(), trnscAmt);
        			throw e;
        		}
        		log.debug("[jkoh] OnRamp step 5 kafka 전송 완료");
        		
        		try {
                    // step 6 예금토큰 발행 DC1 발행준비 > 이용자 : 분산원장 Call , 참가기관 단일서명
        			String result = _blockChain.sendTransaction(requestId, tbWalletMastr.getOwner(), tbCstmrMastr.getWalletAdres(),
        					trnscAmt.toBigInteger(), bankCd, CoinType.DC1, getCallBack(List.of(txMessage), CoinType.DC1.name()));
                    ErrorAssert.hasLength(result, ErrorCode.BLOCKCHAIN_CALL_FAILURE);
        		} catch (Exception e) {
        			log.error("예금토큰 발행({} -> {}) 블록체인 호출 에러 {}", tbWalletMastr.getWalletAdres(), tbCstmrMastr.getWalletAdres(), e.getMessage());
        			// 계좌 증액 처리 (계좌잔액= 계좌잔액 + 전환입금액, DC1 = DC1잔액 - 전환입금액)
        			updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
        			// TODO 위에서 TB_DC1_ISU_MASTR1에 insert한 것은 트랜잭션 상태가 변했는지 확인 필요.

                    kafkaProc(List.of(txMessage), requestId, "R");
        			handleOnRampFailure(wGuid, tbCstmrMastr.getAcnutno(), trnscAmt);
        			throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
                }

        		log.debug("[jkoh] OnRamp step 6 블록체인 요청 완료.");
        		return txMessage.getTxDbId();
            } finally {
                unlock(TokenUtils.getToken());
            }
        } else {
            throw new BizException(ErrorCode.DISTRIBUTED_LOCK_ERROR);
        }
    }

        /**
##### IF-GWS-O-004 예외발생시 예금토큰 재 발행
     *
##### @param model
##### @return
##### @throws WalletSdkException
     */
    public String depositTokenReissue(TxMessage message) throws WalletSdkException {

        String cstmrNo = tbEwaAcnutMastrMapper.selectByAccount(message.getFromAcnutno());
        TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(cstmrNo);        

        ErrorAssert.notNull(tbEwaCstmrMastrMapper.select(cstmrNo), ErrorCode.CUSTOMER_NOT_FOUND, cstmrNo);
        ErrorAssert.isTrue(!StringUtils.equals(tbEwaCstmrMastrMapper.select(cstmrNo).getCstmrSttusCd(), "1"),
                ErrorCode.INVALID_CUSTOMER_STATE);
        BigDecimal trnscAmt = BigDecimal.valueOf( message.getAmount() );

        // step1 지갑 검증
        TbWalletMastr tbWalletMastr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.I1.toString());
        ErrorAssert.notNull(tbWalletMastr, ErrorCode.EMPTY_PREP_WALLET);
        ErrorAssert.hasLength(tbCstmrMastr.getWalletAdres(), ErrorCode.WALLET_MISSING);

        // step 2 계좌 예치금 검증 (예금 >= 전환입금),(발행준비 >= 전환입금)
        BigInteger fromBalance = _blockChain.getBalance(tbWalletMastr.getWalletAdres(), bankCd, CoinType.DC1);
        BigInteger toBalance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);

        ErrorAssert.isTrue(
                trnscAmt.compareTo(BigDecimal.ZERO) > 0 && trnscAmt.stripTrailingZeros().scale() <= 0,
                ErrorCode.INVALID_AMOUNT);

        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0),
                ErrorCode.INSUFFICIENT_ISU_ACCOUNT_BALANCE);

        // step4 DC1 발행 생성
        Dc1IsuMastr dc1IsuMastr = Dc1IsuMastr.builder().dc1IsuSttus("W")
                .trgetInstt(bankCd)
                .dc1IsuAmount(trnscAmt.longValue())
                .applcntId(cstmrNo)
                .build().newId();
        // ewaDc1IsuMastrMapper.insert(dc1IsuMastr);
        genericMapperService.insertModel(dc1IsuMastr, Dc1IsuMastr.class, EwaDc1IsuMastrMapper.class, "insert");

        // kafka message 생성
        TxMessage txMessage = TxMessage.builder().command(CommandType.I1)
                .txDbId(dc1IsuMastr.getDc1IsuId())
                .from(tbWalletMastr.getWalletAdres())
                .to(tbCstmrMastr.getWalletAdres())
                .fromWalletDpstr(tbWalletMastr.getWalletNm())
                .walletDpstr(tbCstmrMastr.getKoreanNm())
                .fromBankCode(bankCd)
                .toBankCode(bankCd)
                .timestamp(new Date())
                .amount(trnscAmt.longValue())
                .trnscAfterBlce(toBalance.add(trnscAmt.toBigInteger()).longValue())
                .acnutno(tbCstmrMastr.getAcnutno())
                .personId(cstmrNo)
                .coin(CoinType.DC1)
                .txType(TrnscType.DEPOSIT.getValue())
                .retry(0).build();

        String requestId = kafkaProducer.setSaga(List.of(txMessage));

        // step 5 카프카 등록및 오류처리
        try {
            kafkaProc(List.of(txMessage), requestId, "W");

            // step 6 예금토큰 발행 DC1 발행준비 > 이용자 : 분산원장 Call , 참가기관 단일서명
            String result = _blockChain.sendTransaction(requestId, tbWalletMastr.getOwner(),
                    tbCstmrMastr.getWalletAdres(),
                    trnscAmt.toBigInteger(), bankCd, CoinType.DC1,
                    getCallBack(List.of(txMessage), CoinType.DC1.name()));
            ErrorAssert.hasLength(result, ErrorCode.BLOCKCHAIN_CALL_FAILURE);

        } catch (Exception e) {
            kafkaProc(List.of(txMessage), requestId, "R");
            throw new BizException(ErrorCode.SERVER_ERROR, requestId, e.getMessage());
        }

        return requestId;

    }

    /**
##### 예금 전환(예금토큰 환수)
     *
##### @param model
##### @return
##### @throws WalletSdkException
     */
    public String depositConv(AcnutManageModel model) throws WalletSdkException {
        if (lock(TokenUtils.getToken())) {
            try {
        		// step0 입력값 검증
        		validateInput(model);

                String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));
        		TbCstmrMastr tbCstmrMastr = validateCustomer(cstmrNo);
        		BigDecimal acnutnoBlce = tbCstmrMastr.getAcnutnoBlce();
        		
        		BigDecimal trnscAmt = validateAmount(model.getTbAcnutMastr().getTrnscAmt());

        		// blockListService.chkBlockStatus(cstmrNo, bankCd); 20250106_Source merge할 때 이 부분 막고 20250106_Source의 코드로 바꿈.
                blockListService.findBlockStatus(bankCd);

                // step1 지갑 검증
        		TbWalletMastr tbWalletMastr = validateWallet(WalletType.R1, tbCstmrMastr, ErrorCode.INVALID_TD_REDEMPTION_WALET);

                // step 2 예금전환액 검증
                BigInteger balance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);
                ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(balance) > 0), ErrorCode.INSUFFICIENT_BALANCE);
        		ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(balance) > 0), ErrorCode.INSUFFICIENT_BALANCE);
        		log.debug("[jkoh] OffRamp step 2 지갑, 잔액 검증 완료");
        		
        		// step3 계좌증액
        		updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
        		log.debug("[jkoh] OffRamp step 3 계좌 증액 완료");

                // step4 DC1 환수 생성
                Dc1RedempMastr dc1RedempMastr = Dc1RedempMastr.builder().dc1RedempSttus("W")
                        .trgetInstt(bankCd)
                        .dc1RedempAmount(trnscAmt.longValue())
                        .applcntId(cstmrNo)
                        .build().newId();
                // ewaDc1RedempMastrMapper.insert(dc1RedempMastr);
        		try {
                genericMapperService.insertModel(dc1RedempMastr, Dc1RedempMastr.class, EwaDc1RedempMastrMapper.class,
                        "insert");
        		} catch (Exception e) {
        			log.error("계좌({}에 대한 예금토큰 환수 내역 신규저장 에러: {}", tbCstmrMastr.getAcnutno(), e.getMessage());
        			updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.SUBTRACT);
        			throw new BizException(ErrorCode.DATA_ACCESS_ERROR, e.getMessage(), e);
        		}
        		log.debug("[jkoh] OffRamp step 4 TD 환수 이력 저장 완료");

                // kafka message 생성
                TxMessage txMessage = TxMessage.builder().command(CommandType.R1)
                        .txDbId(dc1RedempMastr.getDc1RedempId())
                        .from(tbCstmrMastr.getWalletAdres())
                        .to(tbWalletMastr.getWalletAdres())
                        .fromBankCode(bankCd)
                        .toBankCode(bankCd)
                        .amount(trnscAmt.longValue())
                        .timestamp(new Date())
                        .fromTrnscAfterBlce(balance.subtract(trnscAmt.toBigInteger()).longValue())
                        .fromAcnutno(tbCstmrMastr.getAcnutno())
                        .fromWalletDpstr(tbCstmrMastr.getKoreanNm())
                        .walletDpstr(tbWalletMastr.getWalletNm())
                        .personId(cstmrNo)
                        .coin(CoinType.DC1)
                        .txType(TrnscType.CONVERS.getValue())
                        .retry(0).build();
                List<TxMessage> txMessages = new ArrayList<>();
                txMessages.add(txMessage);
        		
        		String requestId = null;
        		try {
        			requestId = kafkaProducer.setSaga(txMessages);
        			log.debug("[jkoh] depositConv requestId from setSage: {}", requestId);
        		} catch (Exception e) {
        			updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.SUBTRACT);
        			log.error("offRamp 트랜잭션 관리용 Saga requestId for txMessage {} 생성 에러: {}", txMessage, e);
        			throw e;
        		}

                // step 5 카프카 등록및 오류처리
                try {
                    kafkaProc(List.of(txMessage), requestId, "W");
        		} catch (BizException e) {
        			updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.SUBTRACT);
        			log.error("offRamp Kafka 메시지[SagaID({})] 송신 에러: {}", requestId, e.getMessage());
        			throw e;
        		} 
        		log.debug("[jkoh] OffRamp step 5 kafka 전송 완료");
        		
        		try {

                    // step 6 이용자지갑 > 환수지갑 : 분산원장 Call , 참가기관 단일서명
        			String result = _blockChain.sendTransaction(requestId, tbCstmrMastr.getOwner(), tbWalletMastr.getWalletAdres(),
        					trnscAmt.toBigInteger(), this.bankCd, CoinType.DC1, getCallBack(txMessages,CoinType.DC1.name()));
                    ErrorAssert.hasLength(result, ErrorCode.KAFKA_PRODUCE_ERROR);
        		} catch (WalletSdkException e) {
        			log.error("SagaId({}) 예금토큰 환수({} -> {}) 블록체인 호출 에러 {}", requestId, tbCstmrMastr.getWalletAdres(), tbWalletMastr.getWalletAdres(), e.getMessage());
                    kafkaProc(List.of(txMessage), requestId, "R");
        			// 계좌 차감 처리 (계좌잔액= 계좌잔액 - 전환입금액, DC1 = DC1잔액 + 전환입금액)
        			updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.SUBTRACT);
        			throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
        		}
        		log.debug("[jkoh] OffRamp step 6 블록체인 요청 완료.");
        		
        		/*
            	Dc1RedempMastr dc1RedempMastrUpdate = Dc1RedempMastr.builder()
	                                                .dc1RedempId(dc1RedempMastr.getDc1RedempId())
	                                                .build();
	
	            try {
	                genericMapperService.updateModel(dc1RedempMastrUpdate, Dc1RedempMastr.class, EwaDc1RedempMastrMapper.class, "update");
	            } catch (Exception e) {
	                log.error("SagaID({}) 계좌({}) 예금토큰 환수 내역 저장 에러: {}", requestId, tbCstmrMastr.getAcnutno(), e.getMessage());
	                throw new BizException(ErrorCode.DATA_ACCESS_ERROR, e.getMessage(), e);
	            }
        		 */
        		return txMessage.getTxDbId();
            } finally {
                unlock(TokenUtils.getToken());
            }
        } else {
            throw new BizException(ErrorCode.DISTRIBUTED_LOCK_ERROR);
        }
    }

    /**
##### 예금 토큰 송금 (DC1 당,타행 이체)
     *
##### @param model
##### @return
##### @throws WalletSdkException
     */
    public String depositTrans(AcnutManageModel model) throws WalletSdkException {

        String result = "";
        String requestId = "";
        String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));

        ErrorAssert.notNull(tbEwaCstmrMastrMapper.select(cstmrNo),ErrorCode.USER_ID_NOT_FOUND);
        ErrorAssert.isTrue(!StringUtils.equals(tbEwaCstmrMastrMapper.select(cstmrNo).getCstmrSttusCd() ,"1"), ErrorCode.INVALID_CUSTOMER_STATE);
        String aliasNm = model.getTbAcnutMastr().getAliasNm();
        String walletInsttCd = model.getTbAcnutMastr().getWalletInsttCd();
        BigDecimal trnscAmt = model.getTbAcnutMastr().getTrnscAmt();
        boolean extYn = StringUtils.equals(walletInsttCd, bankCd);

        // step0 입력값 검증
        ErrorAssert.hasLength(cstmrNo, ErrorCode.CUSTOMER_ID_REQUIRED);
        ErrorAssert.hasLength(aliasNm, ErrorCode.INVALID_ALIAS);
        ErrorAssert.hasLength(trnscAmt.toString(), ErrorCode.EMPTY_TRANSACTION_AMOUNT);
        ErrorAssert.isNull(blockListManageMapper.selectBlclstWallet(bankCd, cstmrNo), ErrorCode.BLACKLIST_TARGET);
        blockListService.findBlockStatus(bankCd);

        // step1 수취인조회및 검증(수취인 지갑여부)
        AliasSearchInfo aliasSearchInfo = AliasSearchInfo.builder().aliasNm(aliasNm).trgetInstt(walletInsttCd).build();

        AliasResponse response = extYn ? aliasEwaBanksService.readFromLocal(aliasSearchInfo)
                : aliasEwaBanksService.read(aliasSearchInfo);

        // step2 이용자 지갑 검증
        TbWalletMastr tbWalletMastrA = this.tbEwaWalletMastrMapper.selectWalletByWalletSe("A");
        Signer signerA = Signer.builder().walletAddress(tbWalletMastrA.getWalletAdres())
                .hdKeyAccToken(tbWalletMastrA.getHdKeyaccToken())
                .hdKeyId(tbWalletMastrA.getHdKeyid()).build();
        TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(cstmrNo);
        ErrorAssert.hasLength(tbCstmrMastr.getWalletAdres(), ErrorCode.WALLET_MISSING);
        ErrorAssert.hasLength(response.getWalletAdres(), ErrorCode.WALLET_INFO_NOT_FOUND);
        ErrorAssert.isTrue(!StringUtils.equals(tbCstmrMastr.getWalletAdres(), response.getWalletAdres()), ErrorCode.WRONG_TRANSFER_REQUIRED);
        ErrorAssert.hasLength(tbCstmrMastr.getWalletAdres(), ErrorCode.WALLET_MISSING);
        ErrorAssert.hasLength(response.getWalletAdres(), ErrorCode.WALLET_INFO_NOT_FOUND);
        ErrorAssert.isTrue(!StringUtils.equals(tbCstmrMastr.getWalletAdres(), response.getWalletAdres()), ErrorCode.WRONG_TRANSFER_REQUIRED);


        // step3 DC1 차감(송금자) > DC1 증액(수취인)
        BigInteger fromBalance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);
        BigInteger toBalance = _blockChain.getBalance(response.getWalletAdres(), bankCd, CoinType.DC1);
        ErrorAssert.isTrue(fromBalance.compareTo(BigInteger.ZERO) > 0, ErrorCode.INSUFFICIENT_BALANCE);
        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.TRANS_AMOUNT_EXCEEDS_BALANCE);
        ErrorAssert.isTrue(fromBalance.compareTo(BigInteger.ZERO) > 0, ErrorCode.INSUFFICIENT_BALANCE);
        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.TRANS_AMOUNT_EXCEEDS_BALANCE);


        // step 3-1 통화정책 한도검증 (1회 , 1일)
        ewaPolicyManageService.policyLimit(trnscAmt, ewaWalletManageService.selectAmtPerDay(cstmrNo), null);
        ewaPolicyManageService.policyTransferLimit(ewaWalletManageService.selectAmtCntPerDay(cstmrNo));

        /*
##### kafka message 생성
##### (당,티헹)
##### kafka message 0 이용자 >> 이용자 (거래내역용)
##### (티헹)
##### kafka message 1 이용자 >> TD환수
##### kafka message 2 출금은행 당좌 >> 입금은행 당좌
##### kafka message 3 출금은행 TD 발행 >> 이용자
         */
        List<TxMessage> txMessages = new ArrayList<>();
        TxMessage txMessage = TxMessage.builder().command(CommandType.T1)
                .txDbId(IdGenerationUtil.createUid("TB_DC_TRANS_MASTR"))
                .from(tbCstmrMastr.getWalletAdres())
                .to(response.getWalletAdres())
                .fromBankCode(bankCd)
                .toBankCode(walletInsttCd)
                .amount(trnscAmt.longValue())
                .timestamp(new Date())
                .fromTrnscAfterBlce(fromBalance.subtract(trnscAmt.toBigInteger()).longValue())
                .personId(cstmrNo)
                .coin(CoinType.DC1)
                .retry(0).build();
        txMessages.add(txMessage);

        // kafka message 0 이용자 >> 이용자 (거래내역용)
        txMessages.get(0).setFromAcnutno(tbCstmrMastr.getAcnutno());
        txMessages.get(0).setAcnutno(response.getAcnutno());
        txMessages.get(0).setAliasNm(tbCstmrMastr.getAliasNm());
        txMessages.get(0).setFromAliasNm(aliasNm);
        txMessages.get(0).setWalletDpstr(response.getPersonNm());
        txMessages.get(0).setFromWalletDpstr(tbCstmrMastr.getKoreanNm());
        txMessages.get(0).setTxType(TrnscType.TRANSFER.getValue());

        // step 5 당행 송금
        if (extYn) {
            requestId = kafkaProducer.setSaga(txMessages);

            // step 5 카프카 등록및 오류처리
            try {
                kafkaProc(txMessages, requestId, "W");

                txMessage.setTrnscAfterBlce(toBalance.add(trnscAmt.toBigInteger()).longValue());
                result = _blockChain.sendLimitTransaction(requestId, tbCstmrMastr.getOwner(), response.getWalletAdres(),
                        trnscAmt.toBigInteger(), bankCd, CoinType.DC1, getCallBack(txMessages, CoinType.DC1.name()));

            } catch (Exception e) {
                kafkaProc(txMessages, requestId, "R");
                throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
            }

        } else {// 타행 송금

            txMessages.add(txMessage.clone());
            txMessages.add(txMessage.clone());
            txMessages.add(txMessage.clone());

            // kafka message 1 이용자 >> TD환수
            String tdRedempWalletAddr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.R1.name()).getWalletAdres();
            txMessages.get(1).setCommand(CommandType.R1);
            txMessages.get(1).setTo(tdRedempWalletAddr);
            txMessages.get(1).setToBankCode(bankCd);

            // kafka message 2 출금은행 당좌 >> 입금은행 당좌
            String cWalletAddr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.C.name()).getWalletAdres();
            BigInteger cBlce = _blockChain.getPrivateBalance(signerA, cWalletAddr, bankCd, CoinType.CBDC);
            ErrorAssert.isTrue(cBlce.compareTo(BigInteger.valueOf(trnscAmt.longValue()))>=0, ErrorCode.INSUFFICIENT_BALANCE);

            String toCWalletAddr = ewaWalletManageService.selectExtWalletAddr(WalletType.C.name(), walletInsttCd);
            txMessages.get(2).setCommand(CommandType.T);
            txMessages.get(2).setFrom(cWalletAddr);
            txMessages.get(2).setTo(toCWalletAddr);
            txMessages.get(2).setFromBankCode(config.getBokCode());
            txMessages.get(2).setToBankCode(config.getBokCode());
            txMessages.get(2).setFromTrnscAfterBlce(0);
            txMessages.get(2).setCoin(CoinType.CBDC);
            txMessages.get(2).setTretInstt(bankCd);
            txMessages.get(2).setTxType(TrnscType.CBDCTRANS.getValue());

            // kafka message 3 출금은행 TD 발행 >> 이용자
            String toIWalletAddr = ewaWalletManageService.selectExtWalletAddr(WalletType.I1.name(), walletInsttCd);
            txMessages.get(3).setCommand(CommandType.I1);
            txMessages.get(3).setFrom(toIWalletAddr);
            txMessages.get(3).setFromBankCode(walletInsttCd);
            txMessages.get(3).setTretInstt(bankCd);
            txMessages.get(3).setFromTrnscAfterBlce(0);

            requestId = kafkaProducer.setSaga(txMessages);

            // step 5 카프카 등록및 오류처리
            try {
                kafkaProc(txMessages, requestId, "W");

                result = _blockChain.sendExtLimitTransaction(requestId, tbCstmrMastr.getOwner(), bankCd,
                        walletInsttCd,
                        response.getWalletAdres(), trnscAmt.toBigInteger(),
                        getCallBack(txMessages, CoinType.DC1.name()));

            } catch (Exception e) {
                kafkaProc(txMessages, requestId, "R");
                throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
            }
        }

        ErrorAssert.hasLength(result, ErrorCode.BLOCKCHAIN_TRANSFER_ERROR);
        ErrorAssert.hasLength(result, ErrorCode.BLOCKCHAIN_TRANSFER_ERROR);

        return requestId;
    }

    /**
##### 예금 토큰 결제 (DC1 예금 토큰 결제)
     *
##### @param model
##### @return
##### @throws WalletSdkException
     */
    public String payment(AcnutManageModel model) throws WalletSdkException {

        String result = "";
        String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));
        ErrorAssert.notNull(tbEwaCstmrMastrMapper.select(cstmrNo), ErrorCode.CUSTOMER_NOT_FOUND,cstmrNo);
        ErrorAssert.isTrue(!StringUtils.equals(tbEwaCstmrMastrMapper.select(cstmrNo).getCstmrSttusCd() ,"1"), ErrorCode.INVALID_CUSTOMER_STATE);
        String aliasNm = model.getTbAcnutMastr().getAliasNm();
        String walletInsttCd = model.getTbAcnutMastr().getWalletInsttCd();
        BigDecimal trnscAmt = model.getTbAcnutMastr().getTrnscAmt();
        boolean extYn = StringUtils.equals(walletInsttCd, bankCd);

        // step0 입력값 검증
        ErrorAssert.hasLength(cstmrNo, ErrorCode.CUSTOMER_ID_REQUIRED);
        ErrorAssert.hasLength(aliasNm, ErrorCode.INVALID_ALIAS);
        ErrorAssert.hasLength(trnscAmt.toString(), ErrorCode.INVALID_AMOUNT);
        ErrorAssert.isNull(blockListManageMapper.selectBlclstWallet(bankCd, cstmrNo), ErrorCode.BLACKLIST_TARGET);
        blockListService.findBlockStatus(bankCd);

        // step1 수취인조회및 검증(수취인 지갑여부)
        AliasSearchInfo aliasSearchInfo = AliasSearchInfo.builder().aliasNm(aliasNm).trgetInstt(walletInsttCd).build();

        AliasResponse response = extYn ? aliasEwaBanksService.readFromLocal(aliasSearchInfo)
                : aliasEwaBanksService.read(aliasSearchInfo);

        // step2 이용자 지갑 검증
        TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(cstmrNo);
        ErrorAssert.hasLength(tbCstmrMastr.getWalletAdres(), ErrorCode.WALLET_MISSING);
        ErrorAssert.hasLength(response.getWalletAdres(), ErrorCode.INVALID_WALLET_INFO_ERROR);
        ErrorAssert.isTrue(!StringUtils.equals(tbCstmrMastr.getWalletAdres(), response.getWalletAdres()),ErrorCode.WRONG_PAYMENT_REQUIRED);


        // step3 DC1 차감(송금자) > DC1 증액(결제처)
        BigInteger fromBalance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);
        BigInteger toBalance = _blockChain.getBalance(response.getWalletAdres(), bankCd, CoinType.DC1);
        ErrorAssert.isTrue(fromBalance.compareTo(BigInteger.ZERO) > 0, ErrorCode.INSUFFICIENT_BALANCE);
        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.PAYMENT_AMOUNT_EXCEEDS_BALANCE);
        ErrorAssert.isTrue(fromBalance.compareTo(BigInteger.ZERO) > 0, ErrorCode.INSUFFICIENT_BALANCE);
        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.PAYMENT_AMOUNT_EXCEEDS_BALANCE);



        /*
##### kafka message 생성
##### (당,티헹)
##### kafka message 0 이용자 >> 이용자 (거래내역용)
##### (티헹)
##### kafka message 1 이용자 >> TD환수
##### kafka message 2 출금은행 당좌 >> 입금은행 당좌
##### kafka message 3 출금은행 TD 발행 >> 이용자
         */
        List<TxMessage> txMessages = new ArrayList<>();
        TxMessage txMessage = TxMessage.builder().command(CommandType.T1)
                .txDbId(IdGenerationUtil.createUid("TB_DC_TRANS_MASTR"))
                .from(tbCstmrMastr.getWalletAdres())
                .to(response.getWalletAdres())
                .fromBankCode(bankCd)
                .toBankCode(walletInsttCd)
                .amount(trnscAmt.longValue())
                .timestamp(new Date())
                .fromTrnscAfterBlce(fromBalance.subtract(trnscAmt.toBigInteger()).longValue())
                .personId(cstmrNo)
                .coin(CoinType.DC1)
                .retry(0).build();
        txMessages.add(txMessage);

        // kafka message 0 이용자 >> 이용자 (거래내역용)
        txMessages.get(0).setFromAcnutno(tbCstmrMastr.getAcnutno());
        txMessages.get(0).setAcnutno(response.getAcnutno());
        txMessages.get(0).setAliasNm(tbCstmrMastr.getAliasNm());
        txMessages.get(0).setFromAliasNm(aliasNm);
        txMessages.get(0).setWalletDpstr(response.getPersonNm());
        txMessages.get(0).setFromWalletDpstr(tbCstmrMastr.getKoreanNm());
        txMessages.get(0).setTxType(TrnscType.PAYMENT.getValue());

        String requestId = "";

        // step 5 당행 결제
        if (extYn) {
            requestId = kafkaProducer.setSaga(txMessages);

            // step 5 카프카 등록및 오류처리
            try {
                kafkaProc(txMessages, requestId, "W");

                txMessage.setTrnscAfterBlce(toBalance.add(trnscAmt.toBigInteger()).longValue());
                result = _blockChain.sendTransaction(requestId, tbCstmrMastr.getOwner(), response.getWalletAdres(),
                        trnscAmt.toBigInteger(), bankCd, CoinType.DC1, getCallBack(txMessages, CoinType.DC1.name()));
            } catch (Exception e) {
                kafkaProc(List.of(txMessage), requestId, "R");
                throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
            }

        } else {// 타행 결제

            txMessages.add(txMessage.clone());
            txMessages.add(txMessage.clone());
            txMessages.add(txMessage.clone());

            // kafka message 1 이용자 >> TD환수
            String tdRedempWalletAddr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.R1.name()).getWalletAdres();
            txMessages.get(1).setCommand(CommandType.R1);
            txMessages.get(1).setTo(tdRedempWalletAddr);
            txMessages.get(1).setToBankCode(bankCd);

            // kafka message 2 출금은행 당좌 >> 입금은행 당좌
            String cWalletAddr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.C.name()).getWalletAdres();
            String toCWalletAddr = ewaWalletManageService.selectExtWalletAddr(WalletType.C.name(), walletInsttCd);
            txMessages.get(2).setCommand(CommandType.T);
            txMessages.get(2).setFrom(cWalletAddr);
            txMessages.get(2).setTo(toCWalletAddr);
            txMessages.get(2).setFromBankCode(config.getBokCode());
            txMessages.get(2).setToBankCode(config.getBokCode());
            txMessages.get(2).setTretInstt(bankCd);
            txMessages.get(2).setFromTrnscAfterBlce(0);
            txMessages.get(2).setTxType(TrnscType.CBDCTRANS.getValue());
            txMessages.get(2).setCoin(CoinType.CBDC);

            // kafka message 3 출금은행 TD 발행 >> 이용자
            String toIWalletAddr = ewaWalletManageService.selectExtWalletAddr(WalletType.I1.name(), walletInsttCd);
            txMessages.get(3).setCommand(CommandType.I1);
            txMessages.get(3).setFrom(toIWalletAddr);
            txMessages.get(3).setFromBankCode(walletInsttCd);
            txMessages.get(3).setTretInstt(bankCd);
            txMessages.get(3).setFromTrnscAfterBlce(0);

            requestId = kafkaProducer.setSaga(txMessages);

            // step 5 카프카 등록및 오류처리
            try {
                kafkaProc(txMessages, requestId, "W");

                result = _blockChain.sendExtTransaction(requestId, tbCstmrMastr.getOwner(), bankCd, walletInsttCd,
                        response.getWalletAdres(), trnscAmt.toBigInteger(),
                        getCallBack(txMessages, CoinType.DC1.name()));

            } catch (Exception e) {
                kafkaProc(txMessages, requestId, "R");
                throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
            }
        }

        ErrorAssert.hasLength(result, ErrorCode.KAFKA_PRODUCE_ERROR);

        return requestId;
    }

    private void kafkaProc(List<TxMessage> txMessages, String requestId, String trnscSttusCd) {

        txMessages.forEach(tx -> {
            tx.setTrnscSttusCd(trnscSttusCd);
            tx.setRequestId(requestId);
        });

        try {
            kafkaProducer.send(topicTxRequest, txMessages);
        } catch (InterruptedException | ExecutionException e) {
            throw new BizException(ErrorCode.SERVER_ERROR  ,  requestId ,  e);
        } catch (Exception e) {
            throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);

        }
        ErrorAssert.hasLength(requestId, ErrorCode.KAFKA_PRODUCE_ERROR);
    }

    /**
##### 계좌인증정보입력(검증) 워드3+난수3 자리생성
     *
##### @param model
##### @return
     */
    public String accountValid(AcnutManageModel model) {

        String[] words = { "송아리", "도사리", "미리내", "가루비", "도둑눈", "산돌림", "나비잠", "흰여울", "그루잠", "희나리" };

        StringBuilder result = new StringBuilder();
        result.append(words[rand.nextInt(words.length)]);

        ErrorAssert.isTrue(tbEwaAcnutMastrMapper.accountValid(model.getTbAcnutMastr()) != null,
                ErrorCode.WALLET_INFO_NOT_FOUND);

        // [Mockup][IF-GWS-O-007
        // ewaBridgeServiceImpl.validityCheck();

        return result.append(rand.nextInt(900) + 100).toString();
    }

    /**
##### 계좌 상세 조회
     *
##### @param cstmrNo
##### @return
     */
    public AcnutManageModel read(String cstmrNo) {

        AcnutManageModel model = new AcnutManageModel();
        model.setTbAcnutMastr(tbEwaAcnutMastrMapper.select(cstmrNo));
        return model;
    }

    public boolean lock(String userId) {
    	log.error("hazelcastInstance lock ::: {}", userId);
        FencedLock lock = hazelcastInstance.getCPSubsystem().getLock("lock:" + userId);
        return lock.tryLock(10, TimeUnit.SECONDS);
    }

    public void unlock(String userId) {
    	log.error("hazelcastInstance unlock :::: {}", userId);
        FencedLock lock = hazelcastInstance.getCPSubsystem().getLock("lock:" + userId);
        lock.unlock();
    }
 
    /**
##### 보유계좌 잔액 조회
     *
##### @param model
##### @return
     */
    /* 사용하지 않는 코드 주석처리. 2025.02.05 오재경
    public JsonNode balance(AcnutManageModel model) {
        // step0 입력값 검증
        validateInput(model);

        String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));
        TbCstmrMastr tbCstmrMastr = validateCustomer(cstmrNo);
        
        // 보유계좌 잔액 조회 Gateway 호출.
        HashMap<String, Object> paramBalance = new HashMap<>();
        paramBalance.put("inqDscd", "01");
        paramBalance.put("dpsAcno", tbCstmrMastr.getAcnutno());
        return apiCallHelper.callURL(configProperties.getGateway().getBalance().getUrl(),
                                            null,
                                            (new ObjectMapper()).valueToTree(paramBalance),
                                            HttpMethod.POST);
    } */
    
    /**
##### Checks gateway response for errors. If error exists, throws CBSException.
##### @param response Gateway response DTO
##### @param errorHandler Optional handler to execute before throwing exception
##### @return true if no error (errcode is null), false if there is an error
##### @throws CBSException if error is found
     */
    private void checkGWResponse(CbsRampResponseDto response, Runnable errorHandler) {
        String errcode = response.getErrcode();
        if (errcode != null) {
            
            if (errorHandler != null) {
                errorHandler.run();
            }

            String errmsg = response.getErrusrmsg();
            List<CbsErrorDto> errlist = response.getErrorlist();
            if (errlist != null && !errlist.isEmpty()) {
                errcode = errlist.get(0).getMsgCd();
                errmsg = errlist.get(0).getMainMsgTxt();
            }
            log.error("계정계 호출 에러 {} {}", errcode, errmsg);
            throw new CBSException(errcode, errmsg);
        }
    }
    
    private CbsRampResponseDto parseGatewayResponse(JsonNode response, String errorContext) throws BizException {
        try {
            return objectMapper.treeToValue(response, CbsRampResponseDto.class);
        } catch (JsonProcessingException e) {
            log.error("계정계 " + errorContext + " 응답[{}] 파싱 에러: {}", response.toPrettyString(), e.getMessage());
            throw new BizException(ErrorCode.PARSING_ERROR, e);
        }
    }
    
}


package kr.or.cbdc.infrastructure.queue;

import kr.or.bok.wallet.sdk.errorhandling.WalletSdkException;
import kr.or.cbdc.application.common.bridge.service.BridgeServiceInterface;
import kr.or.cbdc.config.props.ConfigProperties;
import kr.or.cbdc.application.common.bridge.service.BridgeServiceImpl;
import kr.or.cbdc.application.common.encryption.interfae.EncryptionService;
import kr.or.cbdc.application.ewa.common.dto.CbsErrorDto;
import kr.or.cbdc.application.ewa.common.dto.CbsRampResponseDto;
import kr.or.cbdc.application.ewa.common.dto.GwRampDto;
import kr.or.cbdc.application.ewa.cstmr.service.EwaAcnutManageServiceImpl.BalanceOperationType;
import kr.or.cbdc.domain.main.mapper.ewa.cstmr.TbEwaAcnutMastrMapper;
import kr.or.cbdc.domain.main.mapper.transaction.TransactionMirrorRecordMapper;
import kr.or.cbdc.domain.main.mapper.transaction.TransactionRecordMapper;
import kr.or.cbdc.domain.main.mapper.transaction.TransactionSagaMapper;
import kr.or.cbdc.domain.main.model.ewa.cstmr.TbCstmrMastr;
import kr.or.cbdc.domain.main.model.transaction.TransactionRecord;
import kr.or.cbdc.domain.main.service.push.SetPushDataService;
import kr.or.cbdc.interfaces.blockchain.CommandType;
import kr.or.cbdc.interfaces.blockchain.TransactionMapping;
import kr.or.cbdc.interfaces.blockchain.TrnscType;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.ObjectUtils;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.exception.ExceptionUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.dao.DataAccessException;
import org.springframework.http.HttpMethod;
import org.springframework.kafka.annotation.DltHandler;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.annotation.RetryableTopic;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.retrytopic.DltStrategy;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.kafka.support.KafkaHeaders;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.retry.annotation.Backoff;
import org.springframework.stereotype.Component;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.HttpServerErrorException;
import org.springframework.web.client.ResourceAccessException;

import java.util.Arrays;
import java.util.Date;
import java.util.concurrent.ExecutionException;

import jakarta.annotation.PostConstruct;

import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.function.Supplier;

import kr.or.cbdc.domain.main.mapper.ewa.cstmr.TbEwaCstmrMastrMapper;
import kr.or.cbdc.domain.main.mapper.ewa.dc1.EwaDc1IsuMastrMapper;
import kr.or.cbdc.infrastructure.mybatis.GenericMapperService;
import kr.or.cbdc.infrastructure.util.TokenUtils;
import kr.or.cbdc.interfaces.ApiCallHelper;
import kr.or.cbdc.interfaces.InterfaceMap;
import kr.or.cbdc.interfaces.InterfaceSend;
import kr.or.cbdc.config.props.ConfigProperties;
import com.fasterxml.jackson.databind.ObjectMapper;

@Slf4j
@Component
public class MessageListener {

    @Autowired
    private KafkaTemplate<String, TxMessage> kafkaTemplate;

    @Value(value = "${spring.kafka.topicTxRequest}")
    public String[] topicTxRequest;

    @Value(value = "${spring.kafka.topicTxResponse}")
    private String topicTxResponse;

    @Value(value = "${config.bank-code}")
    private String bankCode;

    @Value(value = "${spring.kafka.group}")
    public String group;
    @Value(value = "${spring.kafka.bc-group}")
    public String bcGroup;

    private @Autowired TransactionSagaMapper transactionSagaMapper;
    private @Autowired TransactionRecordMapper transactionRecordMapper;
    private @Autowired TransactionMapping transactionMapping;

    private @Autowired SetPushDataService setPushData;
    private @Autowired KafkaProducer kafkaProducer;
    private @Autowired ConfigProperties config;
    private @Autowired BridgeServiceImpl bridgeService;
    private @Autowired TbEwaCstmrMastrMapper tbEwaCstmrMastrMapper;
    private @Autowired  GenericMapperService genericMapperService;
    private @Autowired ApiCallHelper apiCallHelper;
    private @Autowired ConfigProperties configProperties;
    private @Autowired EwaDc1IsuMastrMapper ewaDc1IsuMastrMapper;
    private @Autowired EwaDc1IsuMastrMapper ewaDc1RedemMastrMapper;
    private @Autowired InterfaceSend interfaceSend;
    private static final ObjectMapper objectMapper = new ObjectMapper();

    public String[] dynamicTopics;

    @PostConstruct
    public void initializeTopics() {
        // 각 원소에 "_${config.bank-code}"를 추가
        dynamicTopics = Arrays.stream(topicTxRequest)
                .map(topic -> topic + "_" + bankCode)
                .toArray(String[]::new);

        log.info("Dynamic Topics Initialized: {}", Arrays.toString(dynamicTopics));
    }    

    private boolean vouchTranSactionData(TxMessage message) {

        switch (message.getCommand()) {
            case PM: //바우처 연계 : 결제 요청
                transactionMapping.setTransactionComplete( message.getCommand(),message.getTxDbId(),message.getPersonId(),"", message);
                return true;
            case TX, TR: //바우처 연계 : 거래번호 생성및 요청
                transactionMapping.setTransactionComplete( message.getCommand(),message.getTxDbId(),message.getPersonId(),"", message);
                return true;
            case PR, PF: // 바우처 연계 승인정보전달 Update 후 종료 , 승인 Update key 'TX_CD' , 결제승인번호는 '리퀘스트ID'
                transactionRecordMapper.updatePr(message);
                return true;
            case RR, RF: // 바우처 연계 환불정보전달 Update 후 종료 , 환불 Update key 'TX_CD' , 환불승인번호는 '리퀘스트ID'
                transactionRecordMapper.updateRr(message);
                return true;
            case CR: // 바우처 연계 캐쉬백정보전달 Update 후 종료 , 캐쉬백 Update key 'TX_CD' , 캐쉬백승인번호는 '리퀘스트ID'
                transactionRecordMapper.updateCr(message);
                return true;
            default:
                return false;
        }
    }

    public GwRampDto createRampParams(String internalTxId, TbCstmrMastr tbCstmrMastr, BigDecimal trnscAmt, BigInteger toBalance) {
        return GwRampDto.builder()
            .internalTxId(internalTxId)
            .customerId(tbCstmrMastr.getCstmrNo())
            .acnutNo(tbCstmrMastr.getAcnutno())
            .amount(trnscAmt)
            .beforeTdBalance(toBalance)
            .build();
    }

    private Optional<CbsRampResponseDto> parseGatewayResponse(JsonNode response, String errorContext) {
        try {
            return Optional.of(objectMapper.treeToValue(response, CbsRampResponseDto.class));
        } catch (JsonProcessingException e) {
            log.error("계정계 " + errorContext + " 응답[{}] 파싱 에러: {}", response.toPrettyString(), e.getMessage());
            return Optional.empty();
        }
    }

    private void checkGWResponse(Optional<CbsRampResponseDto> responseOpt, Runnable errorHandler) {
        if (responseOpt.isPresent()) {
            CbsRampResponseDto response = responseOpt.get();
            String errcode = response.getErrcode();
            if (errcode != null) {
                
                if (errorHandler != null) {
                    errorHandler.run();
                }

                String errmsg = response.getErrusrmsg();
                List<CbsErrorDto> errlist = response.getErrorlist();
                if (errlist != null && !errlist.isEmpty()) {
                    errcode = errlist.get(0).getMsgCd();
                    errmsg = errlist.get(0).getMainMsgTxt();
                }
                log.error("계정계 호출 에러 {} {}", errcode, errmsg);
            }
            log.debug("[jkoh] OffRamp step 7 계정계 offRamp 요청 완료");
        }
        else {
            errorHandler.run();
        }
    }

    public void subtractCustomerBalance(TxMessage message) {
        log.debug("[jkoh] OffRamp step 7-1 계좌 복구(감액 처리)");
        // 계좌 차감 처리 (계좌잔액= 계좌잔액 - 전환입금액, DC1 = DC1잔액 + 전환입금액)
        TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(message.getPersonId());
        BigDecimal trnscAmt = BigDecimal.valueOf(message.getAmount());
        tbCstmrMastr.setAcnutnoBlce(tbCstmrMastr.getAcnutnoBlce().subtract(trnscAmt));

        try {
            // Perform database update
            genericMapperService.updateModel(tbCstmrMastr, TbCstmrMastr.class, TbEwaAcnutMastrMapper.class, "updateBlce");
        } catch (DataAccessException e) {
            log.error("고객 {} 잔액 변경 중 에러가 발생했습니다. 에러 내용: {}", tbCstmrMastr.getCstmrNo(), e.getMessage());
        } catch (Exception e) {
            log.error("고객 {} 잔액 변경 중 에러가 발생했습니다. 에러 내용: {}", tbCstmrMastr.getCstmrNo(), e.getMessage());
        }
    }

    public void updateTransactionComplete(TxMessage message) {
        String messageSttus = "";
        switch (message.getCommand()) {
            case M, I, B, R, M1, M2, D1, D2, I1, I2, R1, R2:
                messageSttus = "S".equals(message.getTrnscSttusCd()) ? "C" : "F";
                break;
            case D:
                messageSttus = "S".equals(message.getTrnscSttusCd()) ? "A" : "F";
                break;
            default:
                messageSttus = "S".equals(message.getTrnscSttusCd()) ? "C" : "F";
                return;
        }
        transactionMapping.setTransactionComplete(message.getCommand(), message.getTxDbId(), message.getPersonId(),
                messageSttus, message);
    }

    @RetryableTopic(attempts = "3", backoff = @Backoff(  delay = 1000, maxDelay = 5000, multiplier = 2), kafkaTemplate = "kafkaTemplate", dltStrategy = DltStrategy.FAIL_ON_ERROR, listenerContainerFactory = "retryContainerFactory")
    @KafkaListener(id = "txRequest", topics = "#{@messageListener.dynamicTopics}", containerFactory = "kafkaListenerContainerFactory", groupId = "${spring.kafka.group}" )
    public void listenTxRequest(TxMessage message, Acknowledgment acknowledgment) throws WalletSdkException, InterruptedException, ExecutionException {

    	// log.info("txRequest message {} : {}", message.getRequestId(), message.toString());
        log.debug("[jkoh] txRequest message {} : {}", message.getRequestId(), message.toString());
        String trnscSttusCd = message.getTrnscSttusCd();
        String trnscType = message.getTxType();

        //바우처 연계
        try {
            if(vouchTranSactionData(message)){
                acknowledgment.acknowledge();
                return;
               }
        }catch (Exception e){
            acknowledgment.acknowledge();
            log.error("바우처 연계정보 DB 수정 에러 vouchTranSactionData: {}", ExceptionUtils.getMessage(e));
            return;
        }

        // 지갑으로 기록할 거래 장부를 판단하고 기록
        kafkaProducer.insertTransactionData(1, message);

        if ("S".equals(trnscSttusCd) || "F".equals(trnscSttusCd)) {
            if ((config.getBokCode().equals(message.getFromBankCode()) && config.getBokCode().equals(message.getToBankCode())) ||
                    ((bankCode.equals(message.getFromBankCode()) || "END".equals(message.getFromBankCode()))&& message.getNum() == 0)) {
                log.debug("[jkoh] call updateTransactionComplete");
                updateTransactionComplete(message);
            }

            try {
            setPushData.setPushData(message);
                log.debug("[jkoh] call setPushData");
            } catch (Exception e) {
                log.error("setPushData error in MessageListener.listenTxRequest: {}", e.getMessage());
            }


            // 바우처 연계 : 결제 거래 성공후 승인정보전달
            if(ObjectUtils.equals(CommandType.T1 , message.getCommand()) && StringUtils.equals(bankCode , message.getFromBankCode())){
                if (StringUtils.equals(TrnscType.PAYMENT.getValue(), message.getTxType())){
                    message.setCommand(CommandType.PR);
                    message.setMessage("3 group:"+group+"  bcGroup:"+bcGroup);
                    message.setApprovalCd(message.getRequestId());
                    kafkaProducer.sendMessage(String.join(",", topicTxRequest), message);

                }else if(StringUtils.equals(TrnscType.ONLINE_PAYMENT.getValue(), message.getTxType())){
                    message.setCommand(CommandType.PF);
                    message.setMessage("4 group:"+group+"  bcGroup:"+bcGroup);
                    message.setApprovalCd(message.getRequestId());
                    kafkaProducer.sendMessage(String.join(",", topicTxRequest), message);
                }
            }

            /*
##### [ GateWay ] [IF-GWS-O-010] CBDC On/Off Ramp 내역 전송
##### 중앙은행에서 CBDC 발행 결과 전달받은 후 실행
##### 
##### pdm > G/W CBDC On-Ramp 내역 전송
##### */
            if ("S".equals(trnscSttusCd)
					&& "I".equals(message.getCommand().toString())
					&& "CBDC".equals(message.getCoin().toString())) {
            //    bridgeService.sendOnOffRampData(message, "1");
               InterfaceMap param = new InterfaceMap();
               param.put("trnDscd", "01");
               param.put("trnAm", message.getAmount());
               try {
                interfaceSend.api_E_001(param);
               } catch (Exception e) {
                log.error("api_E_001 call param: {}, error: {}", param, e.getMessage());
               }
            }

            // onRamp 처리
            if (Objects.equals(trnscType, TrnscType.DEPOSIT.getValue())) {
                // 블록체인 거래 성공 -> 로그
                if (trnscSttusCd.equals("S")) {
                    try {
                        TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(message.getPersonId());
                        log.info("계좌({}) 전환 입금(onRamp) 거래 완료", tbCstmrMastr.getAcnutno());
                    } catch (DataAccessException e) {
                        log.error("고객 정보 조회 데이터베이스 에러: {}", ExceptionUtils.getMessage(e));
                    } catch (Exception e) {
                        log.error("고객 정보 조회 에러 : {}", ExceptionUtils.getMessage(e));
                    }
                    log.debug("[jkoh] OnRamp step 7 onRamp 거래 최종 완료");
                }
                // 블록체인 거래 실패 -> 계좌 차감, 계정계 취소
                else if (trnscSttusCd.equals("F")) {
                    // OnRamp 실패 처리
                    // Step 1. NCP DB 계좌 증액 처리
                    // 계좌 증액 처리 (계좌잔액= 계좌잔액 + 전환입금액, DC1 = DC1잔액 - 전환입금액)
                    log.debug("[jkoh] OnRamp step 7 onRamp 실패");
                    try {
                        TbCstmrMastr tbCstmrMastr = null;
                        try {
                            tbCstmrMastr = tbEwaCstmrMastrMapper.select(message.getPersonId());
                            BigDecimal trnscAmt = BigDecimal.valueOf(message.getAmount());
                            tbCstmrMastr.setAcnutnoBlce(tbCstmrMastr.getAcnutnoBlce().add(trnscAmt));
                            try {
                                genericMapperService.updateModel(tbCstmrMastr, TbCstmrMastr.class, TbEwaAcnutMastrMapper.class, "updateBlce");
                            } catch (Exception e) {
                                log.error("계좌({}) 증액 처리 에러: {}", tbCstmrMastr.getAcnutno(), e.getMessage());
                            }
                            log.debug("[jkoh] OnRamp step 7-1 계좌 복구(증액 처리)");
                        } catch (DataAccessException e) {
                            log.error("고객 정보 조회 데이터베이스 에러: {}", ExceptionUtils.getMessage(e));
                        } catch (Exception e) {
                            log.error("고객 정보 조회 에러 : {}", ExceptionUtils.getMessage(e));
                        }
                    } catch (DataAccessException e) {
                        log.error("GlobalID 조회 데이터베이스 에러: {}", ExceptionUtils.getMessage(e));
                    } catch (Exception e) {
                        log.error("GlobalID 조회 에러 : {}", ExceptionUtils.getMessage(e));
                    }

                    // Step 2. 계정계 onRamp 거래 취소 통지
                    // Step 1이 실패해도 계정계 계좌 onRamp 실패 통지는 해야 한다.
                    // 블록체인 거래 실패로 전자지갑으로 돈이 들어가지 않았으므로.
                    String wGuid = null;
                    wGuid = ewaDc1IsuMastrMapper.selectGuid(message.getTxDbId());
                    if (wGuid != null) {
                        HashMap<String, Object> param = new HashMap<>();
                        param.put("internalTxId", "internalTxId");
                        param.put("oriId", wGuid);
                        param.put("customerId", message.getAcnutno());
                        log.debug("[jkoh] onRamp Fail send to CBS: {}", param);
                        JsonNode response = null;
                        try {
                            response = apiCallHelper.callURL(configProperties.getGateway().getOnRampFail().getUrl(),
                                                                null,
                                                                (new ObjectMapper()).valueToTree(param),
                                                                HttpMethod.POST);
                            try {
                                CbsRampResponseDto onRampFailResponse = new ObjectMapper().treeToValue(response, CbsRampResponseDto.class);
                                String errcode = onRampFailResponse.getErrcode();
                                if (errcode != null) {
                                    String errmsg = onRampFailResponse.getErrusrmsg();
                                    List<CbsErrorDto> errlist = onRampFailResponse.getErrorlist();
                                    if (errlist.size() > 0) {
                                        errcode = errlist.get(0).getMsgCd();
                                        errmsg = errlist.get(0).getMainMsgTxt();
                                    }
                                    log.error("GlobalID({}) 계정계 호출 에러 {} {}", wGuid, errcode, errmsg);
                                }
                            } catch (JsonProcessingException e) {
                                log.error("GlobalID({}) Json response({}) 파싱 에러: ", wGuid, response.toPrettyString(), e.getMessage());
                            }
                        } catch (ResourceAccessException e) {
                            log.error("onRampFail API timeout or connection error: {}", e.getMessage());
                        } catch (HttpClientErrorException e) {
                            log.error("onRampFail API client error (4xx): Status {}, Response {}", e.getStatusCode(), e.getResponseBodyAsString());
                        } catch (HttpServerErrorException e) {
                            log.error("onRampFail API server error (5xx): Status {}, Response {}", e.getStatusCode(), e.getResponseBodyAsString());
                        } catch (Exception e) {
                            log.error("Unexpected error calling onRampFail API: {}", e.getMessage(), e);
                        }
                        log.debug("[jkoh] OnRamp step 7-2 계정계 거래 취소 요청 완료");
                    }
                    else {
                        log.error("{}값에 대응되는 키값이 DB에 없어서 계정계에 취소 거래를 보낼 수 없습니다.", message.getTxDbId());
                    }
                }
            }
            // offRamp 처리
            else if (Objects.equals(trnscType, TrnscType.CONVERS.getValue())) {
                // 블록체인 거래 성공 -> 계정계 offRamp 전송 및 에러 처리
                if (trnscSttusCd.equals("S")) {
                    Optional<CbsRampResponseDto> offRampResponse;
                    TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(message.getPersonId());
                    BigDecimal trnscAmt = BigDecimal.valueOf(message.getAmount());

                    // step 7 계정계 입금 요청 Gateway 호출
                    GwRampDto paramOffRamp = createRampParams("internalTxId"
                                                            , tbCstmrMastr
                                                            , trnscAmt
                                                            , BigInteger.valueOf(message.getFromTrnscAfterBlce()).add(trnscAmt.toBigInteger()));
                    JsonNode respOffRamp = null;
                    try {
                        respOffRamp = apiCallHelper.callURL(configProperties.getGateway().getOffRamp().getUrl(),
                                                        null,
                                                        objectMapper.valueToTree(paramOffRamp),
                                                        HttpMethod.POST);
                        offRampResponse = parseGatewayResponse(respOffRamp, "offRamp");
                        checkGWResponse(offRampResponse, () -> {
                            // TODO 블록체인 거래 취소 API 호출하는 것 넣기. 한국은행에서 API 만들면 수정.
                            subtractCustomerBalance(message);

                        });
                    } catch (ResourceAccessException e) {
                        subtractCustomerBalance(message);
                        log.error("OffRamp API timeout or connection error: {}", e.getMessage());
                    } catch (HttpClientErrorException e) {
                        subtractCustomerBalance(message);
                        log.error("OffRamp API client error (4xx): Status {}, Response {}", e.getStatusCode(), e.getResponseBodyAsString());
                    } catch (HttpServerErrorException e) {
                        subtractCustomerBalance(message);
                        log.error("OffRamp API server error (5xx): Status {}, Response {}", e.getStatusCode(), e.getResponseBodyAsString());
                    } catch (Exception e) {
                        subtractCustomerBalance(message);
                        log.error("Unexpected error calling OffRamp API: {}", e.getMessage(), e);
                    }
                }
                // 블록체인 거래 실패 -> 계좌 차감 
                else if (trnscSttusCd.equals("F")) {
                    subtractCustomerBalance(message);
                }
            }
        }
        else if (trnscSttusCd.equals("R")) {
            log.debug("[jkoh] trnscSttusCd is R. Decide what to do.");
            // TODO jkoh 블록체인 호출할 때 실패하면 trnscSttusCd를 'R'로 설정하는데 실제 R이 오는지 확인
            // 여기서 특별히 할 일은? 
        }

        //SAGA테이블 적재
        if (!"W".equals(trnscSttusCd)) {
            TxMessage returnMessage = TxMessage.builder()
                    .command(message.getCommand())
                    .txDbId(message.getTxDbId())
                    .txSagaId(message.getTxSagaId())
                    .toBankCode(message.getFromBankCode())
                    .fromBankCode(message.getToBankCode())
                    .coinBankCode(message.getCoinBankCode())
                    .txType(message.getTxType())
                    .personId(message.getPersonId())
                    .amount(message.getAmount())
                    .timestamp(new Date())
                    .acnutno(message.getAcnutno())
                    .fromAcnutno(message.getFromAcnutno())
                    .walletDpstr(message.getWalletDpstr())
                    .fromWalletDpstr(message.getFromWalletDpstr())
                    .aliasNm(message.getAliasNm())
                    .trnscSttusCd(message.getTrnscSttusCd())
                    .txHash(message.getTxHash()).retry(0).tretInstt(bankCode)
                    .build();

            if (config.getBokCode().equals(message.getFromBankCode()) && config.getBokCode().equals(message.getToBankCode())) {
                if (StringUtils.isNotEmpty(message.getTretInstt()) && message.getTretInstt().length() == 3) {

                    returnMessage.setToBankCode(message.getTretInstt());
                    log.debug("[jkoh] TretInstt not empty Return Message : {}", returnMessage);
                    kafkaTemplate.send(topicTxResponse + "_" + returnMessage.getToBankCode(), returnMessage.getRequestId(), returnMessage);

                }

            } else if (!bankCode.equals(message.getFromBankCode())) {
                // save Transaction information to DB
                returnMessage.setToBankCode("END".equals(message.getFromBankCode()) ? message.getToBankCode()
                        : message.getTretInstt());
                log.debug("[jkoh] Return Message to other bank: {}", returnMessage);
                kafkaTemplate.send(topicTxResponse + "_" + returnMessage.getToBankCode(), returnMessage.getRequestId(), returnMessage);

            } else if (!bankCode.equals(message.getTretInstt()) &&
                    StringUtils.isNotEmpty(message.getTretInstt()) && message.getTretInstt().length() == 3) {
                returnMessage.setToBankCode(message.getTretInstt());
                log.debug("[jkoh] Last Return Message : {}", returnMessage);
                kafkaTemplate.send(topicTxResponse  + "_" + returnMessage.getToBankCode(), returnMessage.getRequestId(), returnMessage);
            } else {
                // 트랜잭션 SAGA 테이블 동기화 상태 변경
                log.debug("[jkoh] Just update saga table?");
                transactionSagaMapper.updateStatus(message.getTxSagaId(),
                        message.getTrnscSttusCd(), message.getTxHash(), message.getTretInstt(), null);
            }
        }

        acknowledgment.acknowledge();

    }

    @RetryableTopic(attempts = "3", backoff = @Backoff(delay = 1000, maxDelay = 5000, multiplier = 2), kafkaTemplate = "kafkaTemplate", dltStrategy = DltStrategy.FAIL_ON_ERROR, listenerContainerFactory = "retryContainerFactory")
    @KafkaListener(id = "txResponse", topics = "${spring.kafka.topicTxResponse}" + "_" + "${config.bank-code}", containerFactory = "kafkaListenerContainerFactory", groupId = "${spring.kafka.group}" )
    public void listenTxResponse(TxMessage message, Acknowledgment acknowledgment) {

        log.debug("[jkoh] txResponse message {} : {}", message.getRequestId(), message.toString());

        if (bankCode.equals(message.getToBankCode())) {

            // 트랜잭션 SAGA 테이블 동기화 상태 변경
            try {
            transactionSagaMapper.updateStatus(message.getTxSagaId(),
                    message.getTrnscSttusCd(), message.getTxHash(), message.getTretInstt(), null);
            } catch (Exception e) {
                log.error("transactionSagaMapper.updateStatus error: {}", e.getMessage());
            }

        }

        acknowledgment.acknowledge();

    }

    @DltHandler
    public void handleDltMessge(TxMessage message, @Header(KafkaHeaders.RECEIVED_TOPIC) String topic) {
        log.info("Event dlt topic topic={}, paylod={}", topic, message.toString());

    }


}
Above is old version.
------------------------------
Below is new version. I added offRamp recovery processing. To do that I extracted some common business logic into a function issueDepositToken.
If an error happens in calling offRamp API call, performOffRampRecovery will be executed.

/**
##### 계좌 관리 Service
 */
@Slf4j
@Service
@Conditional(EwaProfileCondition.class)
public class EwaAcnutManageServiceImpl extends SupportCallback {

    private @Autowired TbEwaCstmrMastrMapper tbEwaCstmrMastrMapper;
    private @Autowired TbEwaAcnutMastrMapper tbEwaAcnutMastrMapper;
    private @Autowired TbEwaWalletMastrMapper tbEwaWalletMastrMapper;
    private @Autowired EwaPolicyManageServiceImpl ewaPolicyManageService;
    private @Autowired EwaWalletManageServiceImpl ewaWalletManageService;
    private @Autowired AliasEwaBanksServiceImpl aliasEwaBanksService;
    private @Autowired BlockListManageMapper blockListManageMapper;
    private @Autowired BlockChainHelper _blockChain;
    private @Autowired KafkaProducer kafkaProducer;
    private @Autowired GenericMapperService genericMapperService;
    private @Autowired ConfigProperties config;
    private @Autowired BaseBlockListServiceImpl blockListService;
    private @Autowired ApiCallHelper apiCallHelper;
    private @Autowired ConfigProperties configProperties;
    private @Autowired EwaDc1IsuMastrMapper ewaDc1IsuMastrMapper;
    private @Autowired HazelcastInstance hazelcastInstance;
    private @Autowired EwaGWServiceImpl ewaGWService;
    private int baseNo = 2;

    private static final Random rand = new Random();
    private static final ObjectMapper objectMapper = new ObjectMapper();

    private void validateInput(AcnutManageModel model) {
        ErrorAssert.notNull(model, ErrorCode.MISSING_REQUIRED_FIELD);
        ErrorAssert.notNull(model.getTbAcnutMastr(), ErrorCode.MISSING_REQUIRED_FIELD);
        ErrorAssert.notNull(model.getTbAcnutMastr().getTrnscAmt(), ErrorCode.MISSING_REQUIRED_FIELD);
    }
    
    private TbCstmrMastr validateCustomer(String cstmrNo) {
        ErrorAssert.hasLength(cstmrNo, ErrorCode.CUSTOMER_ID_REQUIRED);
        TbCstmrMastr customer = tbEwaCstmrMastrMapper.select(cstmrNo);
        ErrorAssert.notNull(customer, ErrorCode.CUSTOMER_NOT_FOUND, cstmrNo);
        ErrorAssert.isTrue(!StringUtils.equals(customer.getCstmrSttusCd(), "1"), ErrorCode.INVALID_CUSTOMER_STATE);
        return customer;
    }
    
    private BigDecimal validateAmount(BigDecimal amount) {
        ErrorAssert.notNull(amount, ErrorCode.INVALID_TRANSACTION_AMOUNT);
        ErrorAssert.isTrue(amount.compareTo(BigDecimal.ZERO) > 0, ErrorCode.INVALID_TRANSACTION_AMOUNT);
        ErrorAssert.isTrue(amount.compareTo(new BigDecimal("999999999999.99")) <= 0, 
                     ErrorCode.INVALID_TRANSACTION_AMOUNT);
        return amount;
    }

    public TbWalletMastr validateWallet(WalletType walletType, TbCstmrMastr tbCstmrMastr, ErrorCode walletNotFoundError) {
        TbWalletMastr tbWalletMastr = tbEwaWalletMastrMapper.selectWalletSe(walletType.toString());
        log.debug("[jkoh] I1 wallet: {} cstmr's wallte address: {}", tbWalletMastr, tbCstmrMastr.getWalletAdres());
        ErrorAssert.notNull(tbWalletMastr, walletNotFoundError);
        ErrorAssert.hasLength(tbCstmrMastr.getWalletAdres(), ErrorCode.WALLET_MISSING);
        return tbWalletMastr;
    }
    
    public GwRampDto createRampParams(String internalTxId, TbCstmrMastr tbCstmrMastr, BigDecimal trnscAmt, BigInteger toBalance) {
        return GwRampDto.builder()
            .internalTxId(internalTxId)
            .customerId(tbCstmrMastr.getCstmrNo())
            .acnutNo(tbCstmrMastr.getAcnutno())
            .amount(trnscAmt)
            .beforeTdBalance(toBalance)
            .build();
    }

    public GwRampFailDto createRampFailParams(String internalTxId, String guid, String accountNo, BigDecimal amount) {
        return GwRampFailDto.builder()
            .internalTxId(internalTxId)
            .oriId(guid)
            .customerId(accountNo)
            .amount(amount)
            .build();
    }

    // Operation type enum
    public enum BalanceOperationType {
        ADD, SUBTRACT
    }

    public void updateCustomerBalance(String cstmrNo, BigDecimal balance, BigDecimal trnscAmt, BalanceOperationType operationType) {
        if (cstmrNo == null || trnscAmt == null || operationType == null) {
            throw new IllegalArgumentException("Customer, transaction amount, or operation type cannot be null");
        }
        
        BigDecimal newBalance = (operationType == BalanceOperationType.ADD)
                                ? balance.add(trnscAmt)
                                : balance.subtract(trnscAmt);
        TbCstmrMastr tbCstmrMastrUpdate = new TbCstmrMastr();
        tbCstmrMastrUpdate.setCstmrNo(cstmrNo);
        tbCstmrMastrUpdate.setAcnutnoBlce(newBalance);
        try {
            // Perform database update
            genericMapperService.updateModel(tbCstmrMastrUpdate,
                            TbCstmrMastr.class,
                            TbEwaAcnutMastrMapper.class,
                            "updateBlce");
        } catch (DataAccessException e) {
            log.error("고객 계좌({}) 잔액 변경({} -> {}) 중 에러가 발생했습니다. 에러 내용: {}"
                            , cstmrNo
                            , balance
                            , (operationType == BalanceOperationType.ADD) ? balance.add(trnscAmt) : balance.subtract(trnscAmt)
                            , e.getMessage());
            throw new BizException(ErrorCode.DATA_ACCESS_ERROR, e.getMessage());
        } catch (Exception e) {
            log.error("고객 계좌({}) 잔액 변경({} -> {}) 중 에러가 발생했습니다. 에러 내용: {}"
                            , cstmrNo
                            , balance
                            , (operationType == BalanceOperationType.ADD) ? balance.add(trnscAmt) : balance.subtract(trnscAmt)
                            , e.getMessage());
            throw new BizException(ErrorCode.SERVER_ERROR, e.getMessage());
        }
    }
    
    private void handleOnRampFailure(String wGuid, String acnutno, BigDecimal trnscAmt) {
        GwRampFailDto paramOnRampFail = createRampFailParams("internalTxId", wGuid, acnutno, trnscAmt);
        try {
            JsonNode respOnRampFail = apiCallHelper.callURL(configProperties.getGateway().getOnRampFail().getUrl(),
                                        null,
                                        objectMapper.valueToTree(paramOnRampFail),
                                        HttpMethod.POST);
            CbsRampResponseDto onRampFailResponse = parseGatewayResponse(respOnRampFail, "onRampFail");
            checkGWResponse(onRampFailResponse, null);
        } catch (ResourceAccessException e) {
            // We don't rethrow here as this is already in an error handling path
            log.error("GlobalID({}) account({}) OnRampFail API timeout or connection error: {}", wGuid, acnutno, e.getMessage());
        } catch (HttpClientErrorException e) {
            log.error("GlobalID({}) account({}) OnRampFail API client error (4xx): Status {}, Response {}", wGuid, acnutno, e.getStatusCode(), e.getResponseBodyAsString());
        } catch (HttpServerErrorException e) {
            log.error("GlobalID({}) account({}) OnRampFail API server error (5xx): Status {}, Response {}", wGuid, acnutno, e.getStatusCode(), e.getResponseBodyAsString());
        } catch (Exception e) {
            log.error("GlobalID({}) account({}) Unexpected error calling OnRampFail API: {}", wGuid, acnutno, e.getMessage(), e);
        }
    }

    /**
##### 계정계에 onRamp 요청하고 거래 키를 돌려준다.
##### @return wGuid from Gateway response for onRamp cancel
     */
    private CbsRampResponseDto onRampCoreBanking(String cstmrNo, TbCstmrMastr tbCstmrMastr, 
            BigDecimal acnutnoBlce, BigDecimal trnscAmt, BigInteger toBalance) {
        
        log.debug("[jkoh] 계정계 gateway onRamp 호출 시작");
        GwRampDto paramOnRamp = createRampParams("internalTxId", tbCstmrMastr, trnscAmt, toBalance);
        JsonNode respOnRamp = null;
        try {
            respOnRamp = apiCallHelper.callURL(configProperties.getGateway().getOnRamp().getUrl(),
                    null,
                    objectMapper.valueToTree(paramOnRamp),
                    HttpMethod.POST);
        } catch (ResourceAccessException e) {
            updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
            log.error("Account: {}, OnRamp API timeout or connection error: {}", 
                    tbCstmrMastr.getAcnutno(), e.getMessage());
            throw new BizException(ErrorCode.BRIDGE_CALL_ERROR, e);
        } catch (HttpClientErrorException e) {
            updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
            log.error("Account: {}, OnRamp API client error (4xx): Status {}, Response {}", 
                    tbCstmrMastr.getAcnutno(), e.getStatusCode(), e.getResponseBodyAsString());
            throw new BizException(ErrorCode.BRIDGE_CALL_ERROR, e);
        } catch (HttpServerErrorException e) {
            updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
            log.error("Account: {}, OnRamp API server error (5xx): Status {}, Response {}", 
                    tbCstmrMastr.getAcnutno(), e.getStatusCode(), e.getResponseBodyAsString());
            throw new BizException(ErrorCode.BRIDGE_CALL_ERROR, e);
        } catch (Exception e) {
            updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
            log.error("Unexpected error calling OnRamp API for account: {}, error: {}", 
                    tbCstmrMastr.getAcnutno(), e.getMessage(), e);
            throw new BizException(ErrorCode.BRIDGE_CALL_ERROR, e);
        }
        
        CbsRampResponseDto onRampResponse = parseGatewayResponse(respOnRamp, "onRamp");
        checkGWResponse(onRampResponse, () -> updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, 
                BalanceOperationType.ADD));
        log.debug("[jkoh] OnRamp step 3 계정계 onRamp 요청 완료");
        
        return onRampResponse;
    }

    /**
##### 전환 입금 (예금토큰 발행)
     *
##### @param model
##### @return
##### @throws WalletSdkException
     */
    public String convDeposit(AcnutManageModel model) throws WalletSdkException {
        if (lock(TokenUtils.getToken())) {
            try {
        		// step0 입력값 검증
        		validateInput(model);
        		
                String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));
        		TbCstmrMastr tbCstmrMastr = validateCustomer(cstmrNo);
        		BigDecimal trnscAmt = validateAmount(model.getTbAcnutMastr().getTrnscAmt());
        		log.debug("[jkoh] convDeposit start cstmrNo: {} trnsAmt {}", cstmrNo, trnscAmt);
        		log.debug("[jkoh] tbCstmrMastr: {}", tbCstmrMastr);

        		ErrorAssert.isNull(blockListManageMapper.selectBlclstWallet(bankCd, cstmrNo), ErrorCode.BLACKLIST_TARGET);
                blockListService.findBlockStatus(bankCd);
        		
                BigInteger toBalance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);

        		// IF-GWS-O-006 참가기관 이용자 Core Banking(계정계) 연계 계좌의 잔액 조회 --> 이건 20250207_Source에서 추가된 것. TODO??
                validateAccountWithdrawal(cstmrNo, trnscAmt);
                // 위에서 계정계 계좌 잔액 조회를 통해 검증하므로 아래 줄은 주석 처리
        		// ErrorAssert.isTrue(!(trnscAmt.compareTo(acnutnoBlce) > 0),ErrorCode.INSUFFICIENT_ACCOUNT_BALANCE);

                // step 2-1 통화정책 한도검증 (보유)
                ewaPolicyManageService.policyLimit(null, null, toBalance.add(trnscAmt.toBigInteger()),
                        trnscAmt.toBigInteger(), cstmrNo);

                return issueDepositToken(cstmrNo, trnscAmt);

            } finally {
                unlock(TokenUtils.getToken());
            }
        } else {
            throw new BizException(ErrorCode.DISTRIBUTED_LOCK_ERROR);
        }
    }

    /**
##### IF-GWS-O-004 예외발생시 예금토큰 재 발행
     *
##### @param model
##### @return
##### @throws WalletSdkException
     */
    public String depositTokenReissue(TxMessage message) throws WalletSdkException {

        String cstmrNo = tbEwaAcnutMastrMapper.selectByAccount(message.getFromAcnutno());
        TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(cstmrNo);        

        ErrorAssert.notNull(tbEwaCstmrMastrMapper.select(cstmrNo), ErrorCode.CUSTOMER_NOT_FOUND, cstmrNo);
        ErrorAssert.isTrue(!StringUtils.equals(tbEwaCstmrMastrMapper.select(cstmrNo).getCstmrSttusCd(), "1"),
                ErrorCode.INVALID_CUSTOMER_STATE);
        BigDecimal trnscAmt = BigDecimal.valueOf( message.getAmount() );

        // step1 지갑 검증
        TbWalletMastr tbWalletMastr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.I1.toString());
        ErrorAssert.notNull(tbWalletMastr, ErrorCode.EMPTY_PREP_WALLET);
        ErrorAssert.hasLength(tbCstmrMastr.getWalletAdres(), ErrorCode.WALLET_MISSING);

        // step 2 계좌 예치금 검증 (예금 >= 전환입금),(발행준비 >= 전환입금)
        BigInteger fromBalance = _blockChain.getBalance(tbWalletMastr.getWalletAdres(), bankCd, CoinType.DC1);
        BigInteger toBalance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);

        ErrorAssert.isTrue(
                trnscAmt.compareTo(BigDecimal.ZERO) > 0 && trnscAmt.stripTrailingZeros().scale() <= 0,
                ErrorCode.INVALID_AMOUNT);

        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0),
                ErrorCode.INSUFFICIENT_ISU_ACCOUNT_BALANCE);

        // step4 DC1 발행 생성
        Dc1IsuMastr dc1IsuMastr = Dc1IsuMastr.builder().dc1IsuSttus("W")
                .trgetInstt(bankCd)
                .dc1IsuAmount(trnscAmt.longValue())
                .applcntId(cstmrNo)
                .build().newId();
        // ewaDc1IsuMastrMapper.insert(dc1IsuMastr);
        genericMapperService.insertModel(dc1IsuMastr, Dc1IsuMastr.class, EwaDc1IsuMastrMapper.class, "insert");

        // kafka message 생성
        TxMessage txMessage = TxMessage.builder().command(CommandType.I1)
                .txDbId(dc1IsuMastr.getDc1IsuId())
                .from(tbWalletMastr.getWalletAdres())
                .to(tbCstmrMastr.getWalletAdres())
                .fromWalletDpstr(tbWalletMastr.getWalletNm())
                .walletDpstr(tbCstmrMastr.getKoreanNm())
                .fromBankCode(bankCd)
                .toBankCode(bankCd)
                .timestamp(new Date())
                .amount(trnscAmt.longValue())
                .trnscAfterBlce(toBalance.add(trnscAmt.toBigInteger()).longValue())
                .acnutno(tbCstmrMastr.getAcnutno())
                .personId(cstmrNo)
                .coin(CoinType.DC1)
                .txType(TrnscType.DEPOSIT.getValue())
                .retry(0).build();

        String requestId = kafkaProducer.setSaga(List.of(txMessage));

        // step 5 카프카 등록및 오류처리
        try {
            kafkaProc(List.of(txMessage), requestId, "W");

            // step 6 예금토큰 발행 DC1 발행준비 > 이용자 : 분산원장 Call , 참가기관 단일서명
            String result = _blockChain.sendTransaction(requestId, tbWalletMastr.getOwner(),
                    tbCstmrMastr.getWalletAdres(),
                    trnscAmt.toBigInteger(), bankCd, CoinType.DC1,
                    getCallBack(List.of(txMessage), CoinType.DC1.name()));
            ErrorAssert.hasLength(result, ErrorCode.BLOCKCHAIN_CALL_FAILURE);

        } catch (Exception e) {
            kafkaProc(List.of(txMessage), requestId, "R");
            throw new BizException(ErrorCode.SERVER_ERROR, requestId, e.getMessage());
        }

        return requestId;

    }

    /**
##### 계정계로 잔액 조회를 요청해서 검증
##### @param accountNo Account number to check
##### @param amount Amount to validate
##### @throws BizException if validation fails
     */
    private void validateAccountWithdrawal(String accountNo, BigDecimal amount) {
        GwAcnoDto acnoParam = GwAcnoDto.builder()
                .inqDscd("01")  // 보유계좌잔액조회
                .dpsAcno(accountNo)
                .build();
        
        JsonNode acnoResponse = ewaGWService.acno(acnoParam);
        try {
            CbsAcnoResponseDto acnoResponseDto = objectMapper.treeToValue(acnoResponse, CbsAcnoResponseDto.class);
            
            if (acnoResponseDto.getErrorlist() != null && !acnoResponseDto.getErrorlist().isEmpty()) {
                log.error("계정계 잔액조회 에러: {}", acnoResponseDto.getErrorlist().get(0).getMainMsgTxt());
                throw new BizException(ErrorCode.INVALID_BALANCE_REQUIRED);
            }

            if (acnoResponseDto.getGrid() == null || acnoResponseDto.getGrid().isEmpty()) {
                log.error("계정계 계좌 정보 없음: {}", accountNo);
                throw new BizException(ErrorCode.INVALID_ACNUTNO);
            }

            CbsAcnoResponseGridDto accountInfo = acnoResponseDto.getGrid().get(0);
            if (accountInfo.getWdrAvlAm() < amount.intValue()) {
                log.error("계정계 출금가능금액 부족. 계좌: {}, 출금가능금액: {}, 요청금액: {}", 
                        accountNo, accountInfo.getWdrAvlAm(), amount.intValue());
                throw new BizException(ErrorCode.INSUFFICIENT_ACCOUNT_BALANCE);
            }
        } catch (JsonProcessingException e) {
            log.error("계정계 잔액조회 응답 파싱 에러: {}", e.getMessage());
            throw new BizException(ErrorCode.PARSING_ERROR);
        }
    }

    /**
##### offRamp 원복하기 위해서 호출할 수 있도록 convDeposit에서 onRamp 핵심 로직을 추려낸 것.
##### convDeposit과 offRamp 원복 양쪽에서 호출할 수 있음.
     */
    public String issueDepositToken(String cstmrNo, BigDecimal trnscAmt) throws WalletSdkException {
        TbCstmrMastr tbCstmrMastr = validateCustomer(cstmrNo);
		BigDecimal acnutnoBlce = tbCstmrMastr.getAcnutnoBlce();
        validateAmount(trnscAmt);
        
        // step1 지갑 검증
        TbWalletMastr tbWalletMastr = validateWallet(WalletType.I1, tbCstmrMastr, ErrorCode.INVALID_TD_ISSUANCE_WALLET);
        
        // step 2 계좌 예치금 검증 (예금 >= 전환입금),(발행준비 >= 전환입금)
        BigInteger fromBalance = _blockChain.getBalance(tbWalletMastr.getWalletAdres(), bankCd, CoinType.DC1);
        BigInteger toBalance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);
		log.debug("[jkoh] TD 발행 준비지갑 잔액 fromBalance: {}", fromBalance);
		log.debug("[jkoh] 이용자 지갑 잔액 toBalance: {}", toBalance);
        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.INSUFFICIENT_ISU_ACCOUNT_BALANCE);
		log.debug("[jkoh] OnRamp step 2 지갑, 잔액 검증 완료");

        // step 3-1 계정계 출금 요청 Gateway 호출
		CbsRampResponseDto onRampResponse = onRampCoreBanking(cstmrNo, tbCstmrMastr, acnutnoBlce, trnscAmt, toBalance);
        String wGuid = onRampResponse.getTrnLogKeyVal();

		// step4 계정계에서 출금이 정상적으로 되면 DC1 발행 기록
        Dc1IsuMastr dc1IsuMastr = Dc1IsuMastr.builder()
                .dc1IsuSttus("W")
                .trgetInstt(bankCd)
                .dc1IsuAmount(trnscAmt.longValue())
                .applcntId(cstmrNo)
                .mcaGuid(onRampResponse.getTrnLogKeyVal())
                .cbsTrnAcno(onRampResponse.getDpsInpAcno())
                .cbsTrnDt(onRampResponse.getTrnDt())
                .cbsTrnSrno(onRampResponse.getTrnSrno())
                .build()
                .newId();
        
		log.debug("[jkoh] dc1IsuMaster data to save: {}", dc1IsuMastr);
        try {
            genericMapperService.insertModel(dc1IsuMastr, Dc1IsuMastr.class, 
                    EwaDc1IsuMastrMapper.class, "insert");
            log.debug("[jkoh] onRamp 예금토큰 발행 내역 저장 {}", dc1IsuMastr);
        } catch (Exception e) {
            log.error("계좌({}) 거래키({}) 거래일련번호({})에 대한 예금토큰 발행 내역 신규저장 에러: {}", tbCstmrMastr.getAcnutno(), onRampResponse.getTrnLogKeyVal(), onRampResponse.getTrnSrno(), e.getMessage());
            updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
            // 계정계에 취소 거래 보내기
            handleOnRampFailure(wGuid, tbCstmrMastr.getAcnutno(), trnscAmt);
            throw new BizException(ErrorCode.DATA_ACCESS_ERROR, e.getMessage(), e);
        }
        log.debug("[jkoh] OnRamp step 4 TD 발행 이력 저장 완료");

        // Create and send Kafka message
        TxMessage txMessage = TxMessage.builder()
                .command(CommandType.I1)
                .txDbId(dc1IsuMastr.getDc1IsuId())
                .from(tbWalletMastr.getWalletAdres())
                .to(tbCstmrMastr.getWalletAdres())
                .fromWalletDpstr(tbWalletMastr.getWalletNm())
                .walletDpstr(tbCstmrMastr.getKoreanNm())
                .fromBankCode(bankCd)
                .toBankCode(bankCd)
                .amount(trnscAmt.longValue())
                .timestamp(new Date())
                .trnscAfterBlce(toBalance.add(trnscAmt.toBigInteger()).longValue())
                .acnutno(tbCstmrMastr.getAcnutno())
                .personId(cstmrNo)
                .coin(CoinType.DC1)
                .txType(TrnscType.DEPOSIT.getValue())
                .retry(0)
                .build();

		log.debug("[jkoh] issueDepositToken kafka message: {}", txMessage);

        String requestId = null;
        try {
            requestId = kafkaProducer.setSaga(List.of(txMessage));
            log.debug("[jkoh] issueDepositToken requestId from setSage: {}", requestId);
        } catch (Exception e) {
            log.error("onRamp 트랜잭션 관리용 Saga requestId for txMessage {} 생성 에러: {}", txMessage, e);
            updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
            // 계정계에 취소 거래 보내기
            handleOnRampFailure(wGuid, tbCstmrMastr.getAcnutno(), trnscAmt);
            throw e;
        }

        // step 5 카프카 등록및 오류처리
        try {
            kafkaProc(List.of(txMessage), requestId, "W");
            log.debug("[jkoh] issueDepositToken After kafka send and before call Blockchain sendTransaction");
        } catch (BizException e) {
            log.error("onRamp Kafka 메시지[{}] 송신 에러: {}", requestId, e.getMessage());
            updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
            // 계정계에 취소 거래 보내기
            handleOnRampFailure(wGuid, tbCstmrMastr.getAcnutno(), trnscAmt);
            throw e;
        }
        log.debug("[jkoh] OnRamp step 5 kafka 전송 완료");
        
        try {
            // step 6 예금토큰 발행 DC1 발행준비 > 이용자 : 분산원장 Call , 참가기관 단일서명
            String result = _blockChain.sendTransaction(requestId, tbWalletMastr.getOwner(), tbCstmrMastr.getWalletAdres(),
                    trnscAmt.toBigInteger(), bankCd, CoinType.DC1, getCallBack(List.of(txMessage), CoinType.DC1.name()));
            ErrorAssert.hasLength(result, ErrorCode.BLOCKCHAIN_CALL_FAILURE);
        } catch (Exception e) {
            log.error("예금토큰 발행({} -> {}) 블록체인 호출 에러 {}", tbWalletMastr.getWalletAdres(), tbCstmrMastr.getWalletAdres(), e.getMessage());
            // 계좌 증액 처리 (계좌잔액= 계좌잔액 + 전환입금액, DC1 = DC1잔액 - 전환입금액)
            updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
            // TODO 위에서 TB_DC1_ISU_MASTR1에 insert한 것은 트랜잭션 상태가 변했는지 확인 필요.

            kafkaProc(List.of(txMessage), requestId, "R");
            handleOnRampFailure(wGuid, tbCstmrMastr.getAcnutno(), trnscAmt);
            throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
        }
		log.debug("[jkoh] OnRamp step 6 블록체인 요청 완료.");
		return txMessage.getTxDbId();
    }

    /**
##### 예금 전환(예금토큰 환수)
     *
##### @param model
##### @return
##### @throws WalletSdkException
     */
    public String depositConv(AcnutManageModel model) throws WalletSdkException {
        if (lock(TokenUtils.getToken())) {
            try {
        		// step0 입력값 검증
        		validateInput(model);

                String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));
        		TbCstmrMastr tbCstmrMastr = validateCustomer(cstmrNo);
        		BigDecimal acnutnoBlce = tbCstmrMastr.getAcnutnoBlce();
        		
        		BigDecimal trnscAmt = validateAmount(model.getTbAcnutMastr().getTrnscAmt());

        		// blockListService.chkBlockStatus(cstmrNo, bankCd); 20250106_Source merge할 때 이 부분 막고 20250106_Source의 코드로 바꿈.
                blockListService.findBlockStatus(bankCd);

                // step1 지갑 검증
        		TbWalletMastr tbWalletMastr = validateWallet(WalletType.R1, tbCstmrMastr, ErrorCode.INVALID_TD_REDEMPTION_WALET);

                // step 2 예금전환액 검증
                BigInteger balance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);
                ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(balance) > 0), ErrorCode.INSUFFICIENT_BALANCE);
        		ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(balance) > 0), ErrorCode.INSUFFICIENT_BALANCE);
        		log.debug("[jkoh] OffRamp step 2 지갑, 잔액 검증 완료");
        		
        		// step3 계좌증액
        		updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
        		log.debug("[jkoh] OffRamp step 3 계좌 증액 완료");

                // step4 DC1 환수 생성
                Dc1RedempMastr dc1RedempMastr = Dc1RedempMastr.builder().dc1RedempSttus("W")
                        .trgetInstt(bankCd)
                        .dc1RedempAmount(trnscAmt.longValue())
                        .applcntId(cstmrNo)
                        .build().newId();
                // ewaDc1RedempMastrMapper.insert(dc1RedempMastr);
        		try {
                genericMapperService.insertModel(dc1RedempMastr, Dc1RedempMastr.class, EwaDc1RedempMastrMapper.class,
                        "insert");
        		} catch (Exception e) {
        			log.error("계좌({}에 대한 예금토큰 환수 내역 신규저장 에러: {}", tbCstmrMastr.getAcnutno(), e.getMessage());
        			updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.SUBTRACT);
        			throw new BizException(ErrorCode.DATA_ACCESS_ERROR, e.getMessage(), e);
        		}
        		log.debug("[jkoh] OffRamp step 4 TD 환수 이력 저장 완료");

                // kafka message 생성
                TxMessage txMessage = TxMessage.builder().command(CommandType.R1)
                        .txDbId(dc1RedempMastr.getDc1RedempId())
                        .from(tbCstmrMastr.getWalletAdres())
                        .to(tbWalletMastr.getWalletAdres())
                        .fromBankCode(bankCd)
                        .toBankCode(bankCd)
                        .amount(trnscAmt.longValue())
                        .timestamp(new Date())
                        .fromTrnscAfterBlce(balance.subtract(trnscAmt.toBigInteger()).longValue())
                        .fromAcnutno(tbCstmrMastr.getAcnutno())
                        .fromWalletDpstr(tbCstmrMastr.getKoreanNm())
                        .walletDpstr(tbWalletMastr.getWalletNm())
                        .personId(cstmrNo)
                        .coin(CoinType.DC1)
                        .txType(TrnscType.CONVERS.getValue())
                        .retry(0).build();
                List<TxMessage> txMessages = new ArrayList<>();
                txMessages.add(txMessage);
        		
        		String requestId = null;
        		try {
        			requestId = kafkaProducer.setSaga(txMessages);
        			log.debug("[jkoh] depositConv requestId from setSage: {}", requestId);
        		} catch (Exception e) {
        			updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.SUBTRACT);
        			log.error("offRamp 트랜잭션 관리용 Saga requestId for txMessage {} 생성 에러: {}", txMessage, e);
        			throw e;
        		}

                // step 5 카프카 등록및 오류처리
                try {
                    kafkaProc(List.of(txMessage), requestId, "W");
        		} catch (BizException e) {
        			updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.SUBTRACT);
        			log.error("offRamp Kafka 메시지[SagaID({})] 송신 에러: {}", requestId, e.getMessage());
        			throw e;
        		} 
        		log.debug("[jkoh] OffRamp step 5 kafka 전송 완료");
        		
        		try {

                    // step 6 이용자지갑 > 환수지갑 : 분산원장 Call , 참가기관 단일서명
        			String result = _blockChain.sendTransaction(requestId, tbCstmrMastr.getOwner(), tbWalletMastr.getWalletAdres(),
        					trnscAmt.toBigInteger(), this.bankCd, CoinType.DC1, getCallBack(txMessages,CoinType.DC1.name()));
                    ErrorAssert.hasLength(result, ErrorCode.KAFKA_PRODUCE_ERROR);
        		} catch (WalletSdkException e) {
        			log.error("SagaId({}) 예금토큰 환수({} -> {}) 블록체인 호출 에러 {}", requestId, tbCstmrMastr.getWalletAdres(), tbWalletMastr.getWalletAdres(), e.getMessage());
                    kafkaProc(List.of(txMessage), requestId, "R");
        			// 계좌 차감 처리 (계좌잔액= 계좌잔액 - 전환입금액, DC1 = DC1잔액 + 전환입금액)
        			updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.SUBTRACT);
        			throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
        		}
        		log.debug("[jkoh] OffRamp step 6 블록체인 요청 완료.");
        		
        		/*
            	Dc1RedempMastr dc1RedempMastrUpdate = Dc1RedempMastr.builder()
	                                                .dc1RedempId(dc1RedempMastr.getDc1RedempId())
	                                                .build();
	
	            try {
	                genericMapperService.updateModel(dc1RedempMastrUpdate, Dc1RedempMastr.class, EwaDc1RedempMastrMapper.class, "update");
	            } catch (Exception e) {
	                log.error("SagaID({}) 계좌({}) 예금토큰 환수 내역 저장 에러: {}", requestId, tbCstmrMastr.getAcnutno(), e.getMessage());
	                throw new BizException(ErrorCode.DATA_ACCESS_ERROR, e.getMessage(), e);
	            }
        		 */
        		return txMessage.getTxDbId();
            } finally {
                unlock(TokenUtils.getToken());
            }
        } else {
            throw new BizException(ErrorCode.DISTRIBUTED_LOCK_ERROR);
        }
    }

    /**
##### 예금 토큰 송금 (DC1 당,타행 이체)
     *
##### @param model
##### @return
##### @throws WalletSdkException
     */
    public String depositTrans(AcnutManageModel model) throws WalletSdkException {

        String result = "";
        String requestId = "";
        String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));

        ErrorAssert.notNull(tbEwaCstmrMastrMapper.select(cstmrNo),ErrorCode.USER_ID_NOT_FOUND);
        ErrorAssert.isTrue(!StringUtils.equals(tbEwaCstmrMastrMapper.select(cstmrNo).getCstmrSttusCd() ,"1"), ErrorCode.INVALID_CUSTOMER_STATE);
        String aliasNm = model.getTbAcnutMastr().getAliasNm();
        String walletInsttCd = model.getTbAcnutMastr().getWalletInsttCd();
        BigDecimal trnscAmt = model.getTbAcnutMastr().getTrnscAmt();
        boolean extYn = StringUtils.equals(walletInsttCd, bankCd);

        // step0 입력값 검증
        ErrorAssert.hasLength(cstmrNo, ErrorCode.CUSTOMER_ID_REQUIRED);
        ErrorAssert.hasLength(aliasNm, ErrorCode.INVALID_ALIAS);
        ErrorAssert.hasLength(trnscAmt.toString(), ErrorCode.EMPTY_TRANSACTION_AMOUNT);
        ErrorAssert.isNull(blockListManageMapper.selectBlclstWallet(bankCd, cstmrNo), ErrorCode.BLACKLIST_TARGET);
        blockListService.findBlockStatus(bankCd);

        // step1 수취인조회및 검증(수취인 지갑여부)
        AliasSearchInfo aliasSearchInfo = AliasSearchInfo.builder().aliasNm(aliasNm).trgetInstt(walletInsttCd).build();

        AliasResponse response = extYn ? aliasEwaBanksService.readFromLocal(aliasSearchInfo)
                : aliasEwaBanksService.read(aliasSearchInfo);

        // step2 이용자 지갑 검증
        TbWalletMastr tbWalletMastrA = this.tbEwaWalletMastrMapper.selectWalletByWalletSe("A");
        Signer signerA = Signer.builder().walletAddress(tbWalletMastrA.getWalletAdres())
                .hdKeyAccToken(tbWalletMastrA.getHdKeyaccToken())
                .hdKeyId(tbWalletMastrA.getHdKeyid()).build();
        TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(cstmrNo);
        ErrorAssert.hasLength(tbCstmrMastr.getWalletAdres(), ErrorCode.WALLET_MISSING);
        ErrorAssert.hasLength(response.getWalletAdres(), ErrorCode.WALLET_INFO_NOT_FOUND);
        ErrorAssert.isTrue(!StringUtils.equals(tbCstmrMastr.getWalletAdres(), response.getWalletAdres()), ErrorCode.WRONG_TRANSFER_REQUIRED);
        ErrorAssert.hasLength(tbCstmrMastr.getWalletAdres(), ErrorCode.WALLET_MISSING);
        ErrorAssert.hasLength(response.getWalletAdres(), ErrorCode.WALLET_INFO_NOT_FOUND);
        ErrorAssert.isTrue(!StringUtils.equals(tbCstmrMastr.getWalletAdres(), response.getWalletAdres()), ErrorCode.WRONG_TRANSFER_REQUIRED);


        // step3 DC1 차감(송금자) > DC1 증액(수취인)
        BigInteger fromBalance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);
        BigInteger toBalance = _blockChain.getBalance(response.getWalletAdres(), bankCd, CoinType.DC1);
        ErrorAssert.isTrue(fromBalance.compareTo(BigInteger.ZERO) > 0, ErrorCode.INSUFFICIENT_BALANCE);
        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.TRANS_AMOUNT_EXCEEDS_BALANCE);
        ErrorAssert.isTrue(fromBalance.compareTo(BigInteger.ZERO) > 0, ErrorCode.INSUFFICIENT_BALANCE);
        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.TRANS_AMOUNT_EXCEEDS_BALANCE);


        // step 3-1 통화정책 한도검증 (1회 , 1일)
        ewaPolicyManageService.policyLimit(trnscAmt, ewaWalletManageService.selectAmtPerDay(cstmrNo), null);
        ewaPolicyManageService.policyTransferLimit(ewaWalletManageService.selectAmtCntPerDay(cstmrNo));

        /*
##### kafka message 생성
##### (당,티헹)
##### kafka message 0 이용자 >> 이용자 (거래내역용)
##### (티헹)
##### kafka message 1 이용자 >> TD환수
##### kafka message 2 출금은행 당좌 >> 입금은행 당좌
##### kafka message 3 출금은행 TD 발행 >> 이용자
         */
        List<TxMessage> txMessages = new ArrayList<>();
        TxMessage txMessage = TxMessage.builder().command(CommandType.T1)
                .txDbId(IdGenerationUtil.createUid("TB_DC_TRANS_MASTR"))
                .from(tbCstmrMastr.getWalletAdres())
                .to(response.getWalletAdres())
                .fromBankCode(bankCd)
                .toBankCode(walletInsttCd)
                .amount(trnscAmt.longValue())
                .timestamp(new Date())
                .fromTrnscAfterBlce(fromBalance.subtract(trnscAmt.toBigInteger()).longValue())
                .personId(cstmrNo)
                .coin(CoinType.DC1)
                .retry(0).build();
        txMessages.add(txMessage);

        // kafka message 0 이용자 >> 이용자 (거래내역용)
        txMessages.get(0).setFromAcnutno(tbCstmrMastr.getAcnutno());
        txMessages.get(0).setAcnutno(response.getAcnutno());
        txMessages.get(0).setAliasNm(tbCstmrMastr.getAliasNm());
        txMessages.get(0).setFromAliasNm(aliasNm);
        txMessages.get(0).setWalletDpstr(response.getPersonNm());
        txMessages.get(0).setFromWalletDpstr(tbCstmrMastr.getKoreanNm());
        txMessages.get(0).setTxType(TrnscType.TRANSFER.getValue());

        // step 5 당행 송금
        if (extYn) {
            requestId = kafkaProducer.setSaga(txMessages);

            // step 5 카프카 등록및 오류처리
            try {
                kafkaProc(txMessages, requestId, "W");

                txMessage.setTrnscAfterBlce(toBalance.add(trnscAmt.toBigInteger()).longValue());
                result = _blockChain.sendLimitTransaction(requestId, tbCstmrMastr.getOwner(), response.getWalletAdres(),
                        trnscAmt.toBigInteger(), bankCd, CoinType.DC1, getCallBack(txMessages, CoinType.DC1.name()));

            } catch (Exception e) {
                kafkaProc(txMessages, requestId, "R");
                throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
            }

        } else {// 타행 송금

            txMessages.add(txMessage.clone());
            txMessages.add(txMessage.clone());
            txMessages.add(txMessage.clone());

            // kafka message 1 이용자 >> TD환수
            String tdRedempWalletAddr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.R1.name()).getWalletAdres();
            txMessages.get(1).setCommand(CommandType.R1);
            txMessages.get(1).setTo(tdRedempWalletAddr);
            txMessages.get(1).setToBankCode(bankCd);

            // kafka message 2 출금은행 당좌 >> 입금은행 당좌
            String cWalletAddr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.C.name()).getWalletAdres();
            BigInteger cBlce = _blockChain.getPrivateBalance(signerA, cWalletAddr, bankCd, CoinType.CBDC);
            ErrorAssert.isTrue(cBlce.compareTo(BigInteger.valueOf(trnscAmt.longValue()))>=0, ErrorCode.INSUFFICIENT_BALANCE);

            String toCWalletAddr = ewaWalletManageService.selectExtWalletAddr(WalletType.C.name(), walletInsttCd);
            txMessages.get(2).setCommand(CommandType.T);
            txMessages.get(2).setFrom(cWalletAddr);
            txMessages.get(2).setTo(toCWalletAddr);
            txMessages.get(2).setFromBankCode(config.getBokCode());
            txMessages.get(2).setToBankCode(config.getBokCode());
            txMessages.get(2).setFromTrnscAfterBlce(0);
            txMessages.get(2).setCoin(CoinType.CBDC);
            txMessages.get(2).setTretInstt(bankCd);
            txMessages.get(2).setTxType(TrnscType.CBDCTRANS.getValue());

            // kafka message 3 출금은행 TD 발행 >> 이용자
            String toIWalletAddr = ewaWalletManageService.selectExtWalletAddr(WalletType.I1.name(), walletInsttCd);
            txMessages.get(3).setCommand(CommandType.I1);
            txMessages.get(3).setFrom(toIWalletAddr);
            txMessages.get(3).setFromBankCode(walletInsttCd);
            txMessages.get(3).setTretInstt(bankCd);
            txMessages.get(3).setFromTrnscAfterBlce(0);

            requestId = kafkaProducer.setSaga(txMessages);

            // step 5 카프카 등록및 오류처리
            try {
                kafkaProc(txMessages, requestId, "W");

                result = _blockChain.sendExtLimitTransaction(requestId, tbCstmrMastr.getOwner(), bankCd,
                        walletInsttCd,
                        response.getWalletAdres(), trnscAmt.toBigInteger(),
                        getCallBack(txMessages, CoinType.DC1.name()));

            } catch (Exception e) {
                kafkaProc(txMessages, requestId, "R");
                throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
            }
        }

        ErrorAssert.hasLength(result, ErrorCode.BLOCKCHAIN_TRANSFER_ERROR);
        ErrorAssert.hasLength(result, ErrorCode.BLOCKCHAIN_TRANSFER_ERROR);

        return requestId;
    }

    /**
##### 예금 토큰 결제 (DC1 예금 토큰 결제)
     *
##### @param model
##### @return
##### @throws WalletSdkException
     */
    public String payment(AcnutManageModel model) throws WalletSdkException {

        String result = "";
        String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));
        ErrorAssert.notNull(tbEwaCstmrMastrMapper.select(cstmrNo), ErrorCode.CUSTOMER_NOT_FOUND,cstmrNo);
        ErrorAssert.isTrue(!StringUtils.equals(tbEwaCstmrMastrMapper.select(cstmrNo).getCstmrSttusCd() ,"1"), ErrorCode.INVALID_CUSTOMER_STATE);
        String aliasNm = model.getTbAcnutMastr().getAliasNm();
        String walletInsttCd = model.getTbAcnutMastr().getWalletInsttCd();
        BigDecimal trnscAmt = model.getTbAcnutMastr().getTrnscAmt();
        boolean extYn = StringUtils.equals(walletInsttCd, bankCd);

        // step0 입력값 검증
        ErrorAssert.hasLength(cstmrNo, ErrorCode.CUSTOMER_ID_REQUIRED);
        ErrorAssert.hasLength(aliasNm, ErrorCode.INVALID_ALIAS);
        ErrorAssert.hasLength(trnscAmt.toString(), ErrorCode.INVALID_AMOUNT);
        ErrorAssert.isNull(blockListManageMapper.selectBlclstWallet(bankCd, cstmrNo), ErrorCode.BLACKLIST_TARGET);
        blockListService.findBlockStatus(bankCd);

        // step1 수취인조회및 검증(수취인 지갑여부)
        AliasSearchInfo aliasSearchInfo = AliasSearchInfo.builder().aliasNm(aliasNm).trgetInstt(walletInsttCd).build();

        AliasResponse response = extYn ? aliasEwaBanksService.readFromLocal(aliasSearchInfo)
                : aliasEwaBanksService.read(aliasSearchInfo);

        // step2 이용자 지갑 검증
        TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(cstmrNo);
        ErrorAssert.hasLength(tbCstmrMastr.getWalletAdres(), ErrorCode.WALLET_MISSING);
        ErrorAssert.hasLength(response.getWalletAdres(), ErrorCode.INVALID_WALLET_INFO_ERROR);
        ErrorAssert.isTrue(!StringUtils.equals(tbCstmrMastr.getWalletAdres(), response.getWalletAdres()),ErrorCode.WRONG_PAYMENT_REQUIRED);


        // step3 DC1 차감(송금자) > DC1 증액(결제처)
        BigInteger fromBalance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);
        BigInteger toBalance = _blockChain.getBalance(response.getWalletAdres(), bankCd, CoinType.DC1);
        ErrorAssert.isTrue(fromBalance.compareTo(BigInteger.ZERO) > 0, ErrorCode.INSUFFICIENT_BALANCE);
        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.PAYMENT_AMOUNT_EXCEEDS_BALANCE);
        ErrorAssert.isTrue(fromBalance.compareTo(BigInteger.ZERO) > 0, ErrorCode.INSUFFICIENT_BALANCE);
        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.PAYMENT_AMOUNT_EXCEEDS_BALANCE);



        /*
##### kafka message 생성
##### (당,티헹)
##### kafka message 0 이용자 >> 이용자 (거래내역용)
##### (티헹)
##### kafka message 1 이용자 >> TD환수
##### kafka message 2 출금은행 당좌 >> 입금은행 당좌
##### kafka message 3 출금은행 TD 발행 >> 이용자
         */
        List<TxMessage> txMessages = new ArrayList<>();
        TxMessage txMessage = TxMessage.builder().command(CommandType.T1)
                .txDbId(IdGenerationUtil.createUid("TB_DC_TRANS_MASTR"))
                .from(tbCstmrMastr.getWalletAdres())
                .to(response.getWalletAdres())
                .fromBankCode(bankCd)
                .toBankCode(walletInsttCd)
                .amount(trnscAmt.longValue())
                .timestamp(new Date())
                .fromTrnscAfterBlce(fromBalance.subtract(trnscAmt.toBigInteger()).longValue())
                .personId(cstmrNo)
                .coin(CoinType.DC1)
                .retry(0).build();
        txMessages.add(txMessage);

        // kafka message 0 이용자 >> 이용자 (거래내역용)
        txMessages.get(0).setFromAcnutno(tbCstmrMastr.getAcnutno());
        txMessages.get(0).setAcnutno(response.getAcnutno());
        txMessages.get(0).setAliasNm(tbCstmrMastr.getAliasNm());
        txMessages.get(0).setFromAliasNm(aliasNm);
        txMessages.get(0).setWalletDpstr(response.getPersonNm());
        txMessages.get(0).setFromWalletDpstr(tbCstmrMastr.getKoreanNm());
        txMessages.get(0).setTxType(TrnscType.PAYMENT.getValue());

        String requestId = "";

        // step 5 당행 결제
        if (extYn) {
            requestId = kafkaProducer.setSaga(txMessages);

            // step 5 카프카 등록및 오류처리
            try {
                kafkaProc(txMessages, requestId, "W");

                txMessage.setTrnscAfterBlce(toBalance.add(trnscAmt.toBigInteger()).longValue());
                result = _blockChain.sendTransaction(requestId, tbCstmrMastr.getOwner(), response.getWalletAdres(),
                        trnscAmt.toBigInteger(), bankCd, CoinType.DC1, getCallBack(txMessages, CoinType.DC1.name()));
            } catch (Exception e) {
                kafkaProc(List.of(txMessage), requestId, "R");
                throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
            }

        } else {// 타행 결제

            txMessages.add(txMessage.clone());
            txMessages.add(txMessage.clone());
            txMessages.add(txMessage.clone());

            // kafka message 1 이용자 >> TD환수
            String tdRedempWalletAddr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.R1.name()).getWalletAdres();
            txMessages.get(1).setCommand(CommandType.R1);
            txMessages.get(1).setTo(tdRedempWalletAddr);
            txMessages.get(1).setToBankCode(bankCd);

            // kafka message 2 출금은행 당좌 >> 입금은행 당좌
            String cWalletAddr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.C.name()).getWalletAdres();
            String toCWalletAddr = ewaWalletManageService.selectExtWalletAddr(WalletType.C.name(), walletInsttCd);
            txMessages.get(2).setCommand(CommandType.T);
            txMessages.get(2).setFrom(cWalletAddr);
            txMessages.get(2).setTo(toCWalletAddr);
            txMessages.get(2).setFromBankCode(config.getBokCode());
            txMessages.get(2).setToBankCode(config.getBokCode());
            txMessages.get(2).setTretInstt(bankCd);
            txMessages.get(2).setFromTrnscAfterBlce(0);
            txMessages.get(2).setTxType(TrnscType.CBDCTRANS.getValue());
            txMessages.get(2).setCoin(CoinType.CBDC);

            // kafka message 3 출금은행 TD 발행 >> 이용자
            String toIWalletAddr = ewaWalletManageService.selectExtWalletAddr(WalletType.I1.name(), walletInsttCd);
            txMessages.get(3).setCommand(CommandType.I1);
            txMessages.get(3).setFrom(toIWalletAddr);
            txMessages.get(3).setFromBankCode(walletInsttCd);
            txMessages.get(3).setTretInstt(bankCd);
            txMessages.get(3).setFromTrnscAfterBlce(0);

            requestId = kafkaProducer.setSaga(txMessages);

            // step 5 카프카 등록및 오류처리
            try {
                kafkaProc(txMessages, requestId, "W");

                result = _blockChain.sendExtTransaction(requestId, tbCstmrMastr.getOwner(), bankCd, walletInsttCd,
                        response.getWalletAdres(), trnscAmt.toBigInteger(),
                        getCallBack(txMessages, CoinType.DC1.name()));

            } catch (Exception e) {
                kafkaProc(txMessages, requestId, "R");
                throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
            }
        }

        ErrorAssert.hasLength(result, ErrorCode.KAFKA_PRODUCE_ERROR);

        return requestId;
    }

    private void kafkaProc(List<TxMessage> txMessages, String requestId, String trnscSttusCd) {

        txMessages.forEach(tx -> {
            tx.setTrnscSttusCd(trnscSttusCd);
            tx.setRequestId(requestId);
        });

        try {
            kafkaProducer.send(topicTxRequest, txMessages);
        } catch (InterruptedException | ExecutionException e) {
            throw new BizException(ErrorCode.SERVER_ERROR  ,  requestId ,  e);
        } catch (Exception e) {
            throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);

        }
        ErrorAssert.hasLength(requestId, ErrorCode.KAFKA_PRODUCE_ERROR);
    }

    /**
##### 계좌인증정보입력(검증) 워드3+난수3 자리생성
     *
##### @param model
##### @return
     */
    public String accountValid(AcnutManageModel model) {

        String[] words = { "송아리", "도사리", "미리내", "가루비", "도둑눈", "산돌림", "나비잠", "흰여울", "그루잠", "희나리" };

        StringBuilder result = new StringBuilder();
        result.append(words[rand.nextInt(words.length)]);

        ErrorAssert.isTrue(tbEwaAcnutMastrMapper.accountValid(model.getTbAcnutMastr()) != null,
                ErrorCode.WALLET_INFO_NOT_FOUND);

        // [Mockup][IF-GWS-O-007
        // ewaBridgeServiceImpl.validityCheck();

        return result.append(rand.nextInt(900) + 100).toString();
    }

    /**
##### 계좌 상세 조회
     *
##### @param cstmrNo
##### @return
     */
    public AcnutManageModel read(String cstmrNo) {

        AcnutManageModel model = new AcnutManageModel();
        model.setTbAcnutMastr(tbEwaAcnutMastrMapper.select(cstmrNo));
        return model;
    }

    public boolean lock(String userId) {
    	log.error("hazelcastInstance lock :::: {}", userId);
        FencedLock lock = hazelcastInstance.getCPSubsystem().getLock("lock:" + userId);
        return lock.tryLock(10, TimeUnit.SECONDS);
    }

    public void unlock(String userId) {
    	log.error("hazelcastInstance unlock :::: {}", userId);
        FencedLock lock = hazelcastInstance.getCPSubsystem().getLock("lock:" + userId);
        lock.unlock();
    }
 
    /**
##### 보유계좌 잔액 조회
     *
##### @param model
##### @return
     */
    /* 사용하지 않는 코드 주석처리. 2025.02.05 오재경
    public JsonNode balance(AcnutManageModel model) {
        // step0 입력값 검증
        validateInput(model);

        String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));
        TbCstmrMastr tbCstmrMastr = validateCustomer(cstmrNo);
        
        // 보유계좌 잔액 조회 Gateway 호출.
        HashMap<String, Object> paramBalance = new HashMap<>();
        paramBalance.put("inqDscd", "01");
        paramBalance.put("dpsAcno", tbCstmrMastr.getAcnutno());
        return apiCallHelper.callURL(configProperties.getGateway().getBalance().getUrl(),
                                            null,
                                            (new ObjectMapper()).valueToTree(paramBalance),
                                            HttpMethod.POST);
    } */
    
    /**
##### Checks gateway response for errors. If error exists, throws CBSException.
##### @param response Gateway response DTO
##### @param errorHandler Optional handler to execute before throwing exception
##### @return true if no error (errcode is null), false if there is an error
##### @throws CBSException if error is found
     */
    private void checkGWResponse(CbsRampResponseDto response, Runnable errorHandler) {
        String errcode = response.getErrcode();
        if (errcode != null) {
            
            if (errorHandler != null) {
                errorHandler.run();
            }

            String errmsg = response.getErrusrmsg();
            List<CbsErrorDto> errlist = response.getErrorlist();
            if (errlist != null && !errlist.isEmpty()) {
                errcode = errlist.get(0).getMsgCd();
                errmsg = errlist.get(0).getMainMsgTxt();
            }
            log.error("계정계 호출 에러 {} {}", errcode, errmsg);
            throw new CBSException(errcode, errmsg);
        }
    }
    
    private CbsRampResponseDto parseGatewayResponse(JsonNode response, String errorContext) throws BizException {
        try {
            return objectMapper.treeToValue(response, CbsRampResponseDto.class);
        } catch (JsonProcessingException e) {
            log.error("계정계 " + errorContext + " 응답[{}] 파싱 에러: {}", response.toPrettyString(), e.getMessage());
            throw new BizException(ErrorCode.PARSING_ERROR, e);
        }
    }
    
}


@Slf4j
@Component
public class MessageListener {

    @Autowired
    private KafkaTemplate<String, TxMessage> kafkaTemplate;

    @Value(value = "${spring.kafka.topicTxRequest}")
    public String[] topicTxRequest;

    @Value(value = "${spring.kafka.topicTxResponse}")
    private String topicTxResponse;

    @Value(value = "${config.bank-code}")
    private String bankCode;

    @Value(value = "${spring.kafka.group}")
    public String group;
    @Value(value = "${spring.kafka.bc-group}")
    public String bcGroup;

    private @Autowired TransactionSagaMapper transactionSagaMapper;
    private @Autowired TransactionRecordMapper transactionRecordMapper;
    private @Autowired TransactionMapping transactionMapping;

    private @Autowired SetPushDataService setPushData;
    private @Autowired KafkaProducer kafkaProducer;
    private @Autowired ConfigProperties config;
    private @Autowired BridgeServiceImpl bridgeService;
    private @Autowired TbEwaCstmrMastrMapper tbEwaCstmrMastrMapper;
    private @Autowired  GenericMapperService genericMapperService;
    private @Autowired ApiCallHelper apiCallHelper;
    private @Autowired ConfigProperties configProperties;
    private @Autowired EwaDc1IsuMastrMapper ewaDc1IsuMastrMapper;
    private @Autowired InterfaceSend interfaceSend;
    private @Autowired EwaAcnutManageServiceImpl ewaAcnutManageService;
    private static final ObjectMapper objectMapper = new ObjectMapper();

    public String[] dynamicTopics;

    @PostConstruct
    public void initializeTopics() {
        // 각 원소에 "_${config.bank-code}"를 추가
        dynamicTopics = Arrays.stream(topicTxRequest)
                .map(topic -> topic + "_" + bankCode)
                .toArray(String[]::new);

        log.info("Dynamic Topics Initialized: {}", Arrays.toString(dynamicTopics));
    }    

    private boolean vouchTranSactionData(TxMessage message) {

        switch (message.getCommand()) {
            case PM: //바우처 연계 : 결제 요청
                transactionMapping.setTransactionComplete( message.getCommand(),message.getTxDbId(),message.getPersonId(),"", message);
                return true;
            case TX, TR: //바우처 연계 : 거래번호 생성및 요청
                transactionMapping.setTransactionComplete( message.getCommand(),message.getTxDbId(),message.getPersonId(),"", message);
                return true;
            case PR, PF: // 바우처 연계 승인정보전달 Update 후 종료 , 승인 Update key 'TX_CD' , 결제승인번호는 '리퀘스트ID'
                transactionRecordMapper.updatePr(message);
                return true;
            case RR, RF: // 바우처 연계 환불정보전달 Update 후 종료 , 환불 Update key 'TX_CD' , 환불승인번호는 '리퀘스트ID'
                transactionRecordMapper.updateRr(message);
                return true;
            case CR: // 바우처 연계 캐쉬백정보전달 Update 후 종료 , 캐쉬백 Update key 'TX_CD' , 캐쉬백승인번호는 '리퀘스트ID'
                transactionRecordMapper.updateCr(message);
                return true;
            default:
                return false;
        }
    }

    public GwRampDto createRampParams(String internalTxId, TbCstmrMastr tbCstmrMastr, BigDecimal trnscAmt, BigInteger toBalance) {
        return GwRampDto.builder()
            .internalTxId(internalTxId)
            .customerId(tbCstmrMastr.getCstmrNo())
            .acnutNo(tbCstmrMastr.getAcnutno())
            .amount(trnscAmt)
            .beforeTdBalance(toBalance)
            .build();
    }

    private Optional<CbsRampResponseDto> parseGatewayResponse(JsonNode response, String errorContext) {
        try {
            return Optional.of(objectMapper.treeToValue(response, CbsRampResponseDto.class));
        } catch (JsonProcessingException e) {
            log.error("계정계 " + errorContext + " 응답[{}] 파싱 에러: {}", response.toPrettyString(), e.getMessage());
            return Optional.empty();
        }
    }

    private void checkGWResponse(Optional<CbsRampResponseDto> responseOpt, Runnable errorHandler) {
        if (responseOpt.isPresent()) {
            CbsRampResponseDto response = responseOpt.get();
            String errcode = response.getErrcode();
            if (errcode != null) {
                
                if (errorHandler != null) {
                    errorHandler.run();
                }

                String errmsg = response.getErrusrmsg();
                List<CbsErrorDto> errlist = response.getErrorlist();
                if (errlist != null && !errlist.isEmpty()) {
                    errcode = errlist.get(0).getMsgCd();
                    errmsg = errlist.get(0).getMainMsgTxt();
                }
                log.error("계정계 호출 에러 {} {}", errcode, errmsg);
            }
            log.debug("[jkoh] OffRamp step 7 계정계 offRamp 요청 완료");
        }
        else {
            errorHandler.run();
        }
    }

    public void subtractCustomerBalance(TxMessage message) {
        log.debug("[jkoh] OffRamp step 7-1 계좌 복구(감액 처리)");
        // 계좌 차감 처리 (계좌잔액= 계좌잔액 - 전환입금액, DC1 = DC1잔액 + 전환입금액)
        TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(message.getPersonId());
        BigDecimal trnscAmt = BigDecimal.valueOf(message.getAmount());
        tbCstmrMastr.setAcnutnoBlce(tbCstmrMastr.getAcnutnoBlce().subtract(trnscAmt));

        try {
            // Perform database update
            genericMapperService.updateModel(tbCstmrMastr, TbCstmrMastr.class, TbEwaAcnutMastrMapper.class, "updateBlce");
        } catch (DataAccessException e) {
            log.error("고객 {} 잔액 변경 중 에러가 발생했습니다. 에러 내용: {}", tbCstmrMastr.getCstmrNo(), e.getMessage());
        } catch (Exception e) {
            log.error("고객 {} 잔액 변경 중 에러가 발생했습니다. 에러 내용: {}", tbCstmrMastr.getCstmrNo(), e.getMessage());
        }
    }

    public void updateTransactionComplete(TxMessage message) {
        String messageSttus = "";
        switch (message.getCommand()) {
            case M, I, B, R, M1, M2, D1, D2, I1, I2, R1, R2:
                messageSttus = "S".equals(message.getTrnscSttusCd()) ? "C" : "F";
                break;
            case D:
                messageSttus = "S".equals(message.getTrnscSttusCd()) ? "A" : "F";
                break;
            default:
                messageSttus = "S".equals(message.getTrnscSttusCd()) ? "C" : "F";
                return;
        }
        transactionMapping.setTransactionComplete(message.getCommand(), message.getTxDbId(), message.getPersonId(),
                messageSttus, message);
    }

    private void handleOffRampRecovery(TxMessage message) {
        try {
            // Try to reissue the deposit token using the common logic
            ewaAcnutManageService.issueDepositToken( message.getPersonId(), BigDecimal.valueOf(message.getAmount()));
            log.info("OffRamp 실패 후, 원복 거래 완료 {}", message.getTxDbId());
        } catch (Exception e) {
            log.error("OffRamp 실패 후, 원복 거래 실패 {}: {}", 
                message.getTxDbId(), e.getMessage());
            // Consider additional error handling or notification
        }
    }
    
    private void performOffRampRecovery(TxMessage message) {
        try {
            subtractCustomerBalance(message);
            handleOffRampRecovery(message);
        } catch (Exception e) {
            log.error("OffRamp 실패 후, 원복 거래 실패: {}", e.getMessage());
            throw new RuntimeException(e);
        }
    }
    
    @RetryableTopic(attempts = "3", backoff = @Backoff(  delay = 1000, maxDelay = 5000, multiplier = 2), kafkaTemplate = "kafkaTemplate", dltStrategy = DltStrategy.FAIL_ON_ERROR, listenerContainerFactory = "retryContainerFactory")
    @KafkaListener(id = "txRequest", topics = "#{@messageListener.dynamicTopics}", containerFactory = "kafkaListenerContainerFactory", groupId = "${spring.kafka.group}" )
    public void listenTxRequest(TxMessage message, Acknowledgment acknowledgment) throws WalletSdkException, InterruptedException, ExecutionException {

    	// log.info("txRequest message {} : {}", message.getRequestId(), message.toString());
        log.debug("[jkoh] txRequest message {} : {}", message.getRequestId(), message.toString());
        String trnscSttusCd = message.getTrnscSttusCd();
        String trnscType = message.getTxType();

        //바우처 연계
        try {
            if(vouchTranSactionData(message)){
                acknowledgment.acknowledge();
                return;
            }
        }catch (Exception e){
            acknowledgment.acknowledge();
            log.error("바우처 연계정보 DB 수정 에러 vouchTranSactionData: {}", ExceptionUtils.getMessage(e));
            return;
        }

        // 지갑으로 기록할 거래 장부를 판단하고 기록
        kafkaProducer.insertTransactionData(1, message);

        if ("S".equals(trnscSttusCd) || "F".equals(trnscSttusCd)) {
            if ((config.getBokCode().equals(message.getFromBankCode()) && config.getBokCode().equals(message.getToBankCode())) ||
                    ((bankCode.equals(message.getFromBankCode()) || "END".equals(message.getFromBankCode()))&& message.getNum() == 0)) {
                log.debug("[jkoh] call updateTransactionComplete");
                updateTransactionComplete(message);
            }

            try {
                setPushData.setPushData(message);
                log.debug("[jkoh] call setPushData");
            } catch (Exception e) {
                log.error("setPushData error in MessageListener.listenTxRequest: {}", e.getMessage());
            }


            // 바우처 연계 : 결제 거래 성공후 승인정보전달
            if(ObjectUtils.equals(CommandType.T1 , message.getCommand()) && StringUtils.equals(bankCode , message.getFromBankCode())){
                if (StringUtils.equals(TrnscType.PAYMENT.getValue(), message.getTxType())){
                    message.setCommand(CommandType.PR);
                    message.setMessage("3 group:"+group+"  bcGroup:"+bcGroup);
                    message.setApprovalCd(message.getRequestId());
                    kafkaProducer.sendMessage(String.join(",", topicTxRequest), message);

                }else if(StringUtils.equals(TrnscType.ONLINE_PAYMENT.getValue(), message.getTxType())){
                    message.setCommand(CommandType.PF);
                    message.setMessage("4 group:"+group+"  bcGroup:"+bcGroup);
                    message.setApprovalCd(message.getRequestId());
                    kafkaProducer.sendMessage(String.join(",", topicTxRequest), message);
                }
            }

            /*
##### [ GateWay ] [IF-GWS-O-010] CBDC On/Off Ramp 내역 전송
##### 중앙은행에서 CBDC 발행 결과 전달받은 후 실행
##### 
##### pdm > G/W CBDC On-Ramp 내역 전송
##### */
            if ("S".equals(trnscSttusCd)
					&& "I".equals(message.getCommand().toString())
					&& "CBDC".equals(message.getCoin().toString())) {
               InterfaceMap param = new InterfaceMap();
               param.put("trnDscd", "01");
               param.put("trnAm", message.getAmount());
               try {
                interfaceSend.api_E_001(param);
               } catch (Exception e) {
                log.error("api_E_001 call param: {}, error: {}", param, e.getMessage());
               }
            }

            // onRamp 처리
            if (Objects.equals(trnscType, TrnscType.DEPOSIT.getValue())) {
                // 블록체인 거래 성공 -> 로그
                if (trnscSttusCd.equals("S")) {
                    try {
                        TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(message.getPersonId());
                        log.info("계좌({}) 전환 입금(onRamp) 거래 완료", tbCstmrMastr.getAcnutno());
                    } catch (DataAccessException e) {
                        log.error("고객 정보 조회 데이터베이스 에러: {}", ExceptionUtils.getMessage(e));
                    } catch (Exception e) {
                        log.error("고객 정보 조회 에러 : {}", ExceptionUtils.getMessage(e));
                    }
                    log.debug("[jkoh] OnRamp step 7 onRamp 거래 최종 완료");
                }
                // 블록체인 거래 실패 -> 계좌 차감, 계정계 취소
                else if (trnscSttusCd.equals("F")) {
                    // OnRamp 실패 처리
                    // Step 1. NCP DB 계좌 증액 처리
                    // 계좌 증액 처리 (계좌잔액= 계좌잔액 + 전환입금액, DC1 = DC1잔액 - 전환입금액)
                    log.debug("[jkoh] OnRamp step 7 onRamp 실패");
                    try {
                        TbCstmrMastr tbCstmrMastr = null;
                        try {
                            tbCstmrMastr = tbEwaCstmrMastrMapper.select(message.getPersonId());
                            BigDecimal trnscAmt = BigDecimal.valueOf(message.getAmount());
                            tbCstmrMastr.setAcnutnoBlce(tbCstmrMastr.getAcnutnoBlce().add(trnscAmt));
                            try {
                                genericMapperService.updateModel(tbCstmrMastr, TbCstmrMastr.class, TbEwaAcnutMastrMapper.class, "updateBlce");
                            } catch (Exception e) {
                                log.error("계좌({}) 증액 처리 에러: {}", tbCstmrMastr.getAcnutno(), e.getMessage());
                            }
                            log.debug("[jkoh] OnRamp step 7-1 계좌 복구(증액 처리)");
                        } catch (DataAccessException e) {
                            log.error("고객 정보 조회 데이터베이스 에러: {}", ExceptionUtils.getMessage(e));
                        } catch (Exception e) {
                            log.error("고객 정보 조회 에러 : {}", ExceptionUtils.getMessage(e));
                        }
                    } catch (DataAccessException e) {
                        log.error("GlobalID 조회 데이터베이스 에러: {}", ExceptionUtils.getMessage(e));
                    } catch (Exception e) {
                        log.error("GlobalID 조회 에러 : {}", ExceptionUtils.getMessage(e));
                    }

                    // Step 2. 계정계 onRamp 거래 취소 통지
                    // Step 1이 실패해도 계정계 계좌 onRamp 실패 통지는 해야 한다.
                    // 블록체인 거래 실패로 전자지갑으로 돈이 들어가지 않았으므로.
                    String wGuid = null;
                    wGuid = ewaDc1IsuMastrMapper.selectGuid(message.getTxDbId());
                    if (wGuid != null) {
                        HashMap<String, Object> param = new HashMap<>();
                        param.put("internalTxId", "internalTxId");
                        param.put("oriId", wGuid);
                        param.put("customerId", message.getAcnutno());
                        log.debug("[jkoh] onRamp Fail send to CBS: {}", param);
                        JsonNode response = null;
                        try {
                            response = apiCallHelper.callURL(configProperties.getGateway().getOnRampFail().getUrl(),
                                                                null,
                                                                (new ObjectMapper()).valueToTree(param),
                                                                HttpMethod.POST);
                            try {
                                CbsRampResponseDto onRampFailResponse = new ObjectMapper().treeToValue(response, CbsRampResponseDto.class);
                                String errcode = onRampFailResponse.getErrcode();
                                if (errcode != null) {
                                    String errmsg = onRampFailResponse.getErrusrmsg();
                                    List<CbsErrorDto> errlist = onRampFailResponse.getErrorlist();
                                    if (errlist.size() > 0) {
                                        errcode = errlist.get(0).getMsgCd();
                                        errmsg = errlist.get(0).getMainMsgTxt();
                                    }
                                    log.error("GlobalID({}) 계정계 호출 에러 {} {}", wGuid, errcode, errmsg);
                                }
                            } catch (JsonProcessingException e) {
                                log.error("GlobalID({}) Json response({}) 파싱 에러: ", wGuid, response.toPrettyString(), e.getMessage());
                            }
                        } catch (ResourceAccessException e) {
                            log.error("onRampFail API timeout or connection error: {}", e.getMessage());
                        } catch (HttpClientErrorException e) {
                            log.error("onRampFail API client error (4xx): Status {}, Response {}", e.getStatusCode(), e.getResponseBodyAsString());
                        } catch (HttpServerErrorException e) {
                            log.error("onRampFail API server error (5xx): Status {}, Response {}", e.getStatusCode(), e.getResponseBodyAsString());
                        } catch (Exception e) {
                            log.error("Unexpected error calling onRampFail API: {}", e.getMessage(), e);
                        }
                        log.debug("[jkoh] OnRamp step 7-2 계정계 거래 취소 요청 완료");
                    }
                    else {
                        log.error("{}값에 대응되는 키값이 DB에 없어서 계정계에 취소 거래를 보낼 수 없습니다.", message.getTxDbId());
                    }
                }
            }
            // offRamp 처리
            else if (Objects.equals(trnscType, TrnscType.CONVERS.getValue())) {
                // 블록체인 거래 성공 -> 계정계 offRamp 전송 및 에러 처리
                if (trnscSttusCd.equals("S")) {
                    Optional<CbsRampResponseDto> offRampResponse;
                    TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(message.getPersonId());
                    BigDecimal trnscAmt = BigDecimal.valueOf(message.getAmount());

                    // step 7 계정계 입금 요청 Gateway 호출
                    GwRampDto paramOffRamp = createRampParams("internalTxId"
                                                            , tbCstmrMastr
                                                            , trnscAmt
                                                            , BigInteger.valueOf(message.getFromTrnscAfterBlce()).add(trnscAmt.toBigInteger()));
                    JsonNode respOffRamp = null;
                    try {
                        respOffRamp = apiCallHelper.callURL(configProperties.getGateway().getOffRamp().getUrl(),
                                                        null,
                                                        objectMapper.valueToTree(paramOffRamp),
                                                        HttpMethod.POST);
                        offRampResponse = parseGatewayResponse(respOffRamp, "offRamp");
                        checkGWResponse(offRampResponse, () -> performOffRampRecovery(message));
                    } catch (ResourceAccessException e) {
                        subtractCustomerBalance(message);
                        log.error("OffRamp API timeout or connection error: {}", e.getMessage());
                    } catch (HttpClientErrorException e) {
                        subtractCustomerBalance(message);
                        log.error("OffRamp API client error (4xx): Status {}, Response {}", e.getStatusCode(), e.getResponseBodyAsString());
                    } catch (HttpServerErrorException e) {
                        subtractCustomerBalance(message);
                        log.error("OffRamp API server error (5xx): Status {}, Response {}", e.getStatusCode(), e.getResponseBodyAsString());
                    } catch (Exception e) {
                        subtractCustomerBalance(message);
                        log.error("Unexpected error calling OffRamp API: {}", e.getMessage(), e);
                    }
                }
                // 블록체인 거래 실패 -> 계좌 차감 
                else if (trnscSttusCd.equals("F")) {
                    subtractCustomerBalance(message);
                }
            }
        }
        else if (trnscSttusCd.equals("R")) {
            log.debug("[jkoh] trnscSttusCd is R. Decide what to do.");
            // TODO jkoh 블록체인 호출할 때 실패하면 trnscSttusCd를 'R'로 설정하는데 실제 R이 오는지 확인
            // 여기서 특별히 할 일은? 
        }

        //SAGA테이블 적재
        if (!"W".equals(trnscSttusCd)) {
            TxMessage returnMessage = TxMessage.builder()
                    .command(message.getCommand())
                    .txDbId(message.getTxDbId())
                    .txSagaId(message.getTxSagaId())
                    .toBankCode(message.getFromBankCode())
                    .fromBankCode(message.getToBankCode())
                    .coinBankCode(message.getCoinBankCode())
                    .txType(message.getTxType())
                    .personId(message.getPersonId())
                    .amount(message.getAmount())
                    .timestamp(new Date())
                    .acnutno(message.getAcnutno())
                    .fromAcnutno(message.getFromAcnutno())
                    .walletDpstr(message.getWalletDpstr())
                    .fromWalletDpstr(message.getFromWalletDpstr())
                    .aliasNm(message.getAliasNm())
                    .trnscSttusCd(message.getTrnscSttusCd())
                    .txHash(message.getTxHash()).retry(0).tretInstt(bankCode)
                    .build();

            if (config.getBokCode().equals(message.getFromBankCode()) && config.getBokCode().equals(message.getToBankCode())) {
                if (StringUtils.isNotEmpty(message.getTretInstt()) && message.getTretInstt().length() == 3) {

                    returnMessage.setToBankCode(message.getTretInstt());
                    log.debug("[jkoh] TretInstt not empty Return Message : {}", returnMessage);
                    kafkaTemplate.send(topicTxResponse + "_" + returnMessage.getToBankCode(), returnMessage.getRequestId(), returnMessage);

                }

            } else if (!bankCode.equals(message.getFromBankCode())) {
                // save Transaction information to DB
                returnMessage.setToBankCode("END".equals(message.getFromBankCode()) ? message.getToBankCode()
                        : message.getTretInstt());
                log.debug("[jkoh] Return Message to other bank: {}", returnMessage);
                kafkaTemplate.send(topicTxResponse + "_" + returnMessage.getToBankCode(), returnMessage.getRequestId(), returnMessage);

            } else if (!bankCode.equals(message.getTretInstt()) &&
                    StringUtils.isNotEmpty(message.getTretInstt()) && message.getTretInstt().length() == 3) {
                returnMessage.setToBankCode(message.getTretInstt());
                log.debug("[jkoh] Last Return Message : {}", returnMessage);
                kafkaTemplate.send(topicTxResponse  + "_" + returnMessage.getToBankCode(), returnMessage.getRequestId(), returnMessage);
            } else {
                // 트랜잭션 SAGA 테이블 동기화 상태 변경
                log.debug("[jkoh] Just update saga table?");
                transactionSagaMapper.updateStatus(message.getTxSagaId(),
                        message.getTrnscSttusCd(), message.getTxHash(), message.getTretInstt(), null);
            }
        }

        acknowledgment.acknowledge();

    }

    @RetryableTopic(attempts = "3", backoff = @Backoff(delay = 1000, maxDelay = 5000, multiplier = 2), kafkaTemplate = "kafkaTemplate", dltStrategy = DltStrategy.FAIL_ON_ERROR, listenerContainerFactory = "retryContainerFactory")
    @KafkaListener(id = "txResponse", topics = "${spring.kafka.topicTxResponse}" + "_" + "${config.bank-code}", containerFactory = "kafkaListenerContainerFactory", groupId = "${spring.kafka.group}" )
    public void listenTxResponse(TxMessage message, Acknowledgment acknowledgment) {

        log.debug("[jkoh] txResponse message {} : {}", message.getRequestId(), message.toString());

        if (bankCode.equals(message.getToBankCode())) {

            // 트랜잭션 SAGA 테이블 동기화 상태 변경
            try {
                transactionSagaMapper.updateStatus(message.getTxSagaId(),
                        message.getTrnscSttusCd(), message.getTxHash(), message.getTretInstt(), null);
            } catch (Exception e) {
                log.error("transactionSagaMapper.updateStatus error: {}", e.getMessage());
            }

        }

        acknowledgment.acknowledge();

    }

    @DltHandler
    public void handleDltMessge(TxMessage message, @Header(KafkaHeaders.RECEIVED_TOPIC) String topic) {
        log.info("Event dlt topic topic={}, paylod={}", topic, message.toString());

    }
}

Compare old version and new version and check if business logic is identical.
Everything must be the same except when performOffRampRecovery should run.
```
#### 답
```plain text
The business logic remains identical except in the following scenarios:

When offRamp API call fails:


Old: Only subtracts customer balance
New: Subtracts customer balance AND attempts to reissue deposit tokens as recovery


When offRamp API returns error:


Old: Only subtracts customer balance
New: Executes full recovery process including token reissuance

The changes enhance error recovery by attempting to restore the system to its original state through token reissuance when offRamp operations fail, rather than just adjusting the customer balance.
All other business logic including account validation, blockchain interactions, transaction processing, and message handling remains functionally identical between versions.
These changes improve system resilience without altering the core business rules.
```
### sftp 환경변수 문제
#### 질문: 환경변수 사용이 일관되지 않다.
##### SftpConfig와 EwaDeactivateCstmrJob
```java
package kr.or.cbdc.config;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

import org.apache.sshd.sftp.client.SftpClient;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.expression.common.LiteralExpression;
import org.springframework.integration.channel.DirectChannel;
import org.springframework.integration.dsl.IntegrationFlow;
import org.springframework.integration.dsl.IntegrationFlows;
import org.springframework.integration.dsl.MessageChannels;
import org.springframework.integration.dsl.QueueChannelSpec;
import org.springframework.integration.file.remote.session.CachingSessionFactory;
import org.springframework.integration.file.remote.session.SessionFactory;
import org.springframework.integration.sftp.outbound.SftpMessageHandler;
import org.springframework.integration.sftp.session.DefaultSftpSessionFactory;
import org.springframework.integration.sftp.session.SftpRemoteFileTemplate;
import org.springframework.messaging.MessageChannel;
import org.springframework.messaging.MessageHandler;

@Configuration
public class SftpConfig {
    // @Value("${sftp.host}")
    private String sftpHost = "10.208.63.15";
    
    // @Value("${sftp.port}")
    private int sftpPort = 22;
    
    // @Value("${sftp.username}")
    private String sftpUser = "cbdcdev";
    
    // @Value("${sftp.password}")
    private String sftpPassword = "xxxxxxxxx";
    
    @Bean
    public SessionFactory<SftpClient.DirEntry> sftpSessionFactory() {
        DefaultSftpSessionFactory factory = new DefaultSftpSessionFactory(true);
        factory.setHost(sftpHost);
        factory.setPort(sftpPort);
        factory.setUser(sftpUser);
        factory.setPassword(sftpPassword);
        factory.setAllowUnknownKeys(true);
        return new CachingSessionFactory<>(factory);
    }

    @Bean
    public MessageHandler sftpMessageHandler() {
        SftpMessageHandler handler = new SftpMessageHandler(sftpSessionFactory());
        handler.setRemoteDirectoryExpression(new LiteralExpression("/upload/SEND"));
        handler.setFileNameGenerator(message -> {
            // 파일명 생성 로직 (예: 타임스탬프 사용)
            LocalDate date = LocalDate.now();
            String formattedDate = date.format(DateTimeFormatter.ofPattern("yyyyMMdd"));
            return "TDONOFFRAMPHISTORY." + formattedDate;
        });
        return handler;
    }

    @Bean
    public IntegrationFlow sftpOutboundFlow() {
        return IntegrationFlows.from("sftpChannel")
                .handle(sftpMessageHandler())
                .get();
    }
    
    @Bean
    public MessageChannel sftpChannel() {
        return new DirectChannel();
    }
    
    @Bean
    public SftpRemoteFileTemplate sftpRemoteFileTemplate() {
        return new SftpRemoteFileTemplate(sftpSessionFactory());
    }
}

package kr.or.cbdc.application.common.scheduler;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;

import org.apache.commons.codec.binary.Base64;
import org.quartz.JobExecutionContext;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;

import kr.or.cbdc.application.ewa.cstmr.dto.DeactivateCstmrDto;
import kr.or.cbdc.application.ewa.cstmr.mapper.EwaDeactivateCstmrMapper;
import kr.or.cbdc.config.props.ConfigProperties;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.BaseException;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.ErrorCode;
import kr.or.cbdc.infrastructure.framework.core.support.scheduling.AnyJob;
import kr.or.cbdc.infrastructure.framework.core.support.scheduling.model.JobDetailTrigger;
import kr.or.cbdc.infrastructure.framework.core.support.scheduling.model.SchedulerJobConfig;
import kr.or.cbdc.infrastructure.util.CryptUtils;
import lombok.extern.slf4j.Slf4j;
import java.io.IOException;
import java.io.InputStream;
import org.apache.commons.io.IOUtils;
import org.springframework.integration.sftp.session.SftpRemoteFileTemplate;

@Slf4j
public class EwaDeactivateCstmrJob extends AnyJob {
    @Autowired
    private EwaDeactivateCstmrMapper ewaDeactivateCstmrMapper;
    
    @Autowired
    private CryptUtils cryptUtils;

    @Autowired
    private SftpRemoteFileTemplate sftpRemoteFileTemplate;
    private @Autowired ConfigProperties configProperties;

    public static final String DataProcessing = "DeactivateCstmr";

    // Minimum length(test): D(1) + seqNo(10) + csno(11) + date(8) + code(2)
    // Minimum length(prd): D(1) + seqNo(10) + csno(24) + date(8) + code(2)
    private static final int headerLength = 9;
    private static final int maxLineLength = 45;
    private static final int dateLength = 8;
    private static final int codeLength = 2;
    private static final int itCsnoBeginIndex = 11; // SEQ 이후 itCsno가 시작하는 위치
    private static final int itCsnoLength = 24;
        

    private DeactivateCstmrDto parseLine(String line, String dateSuffix) {
        // Validate basic format
        int lineLength = line.length();
        if (line == null || lineLength < maxLineLength) {
            log.error("사망자/압류자 데이터가 잘못되었습니다. {}", line);
            return null;
        }


        String cusDscd = line.substring(lineLength - codeLength);

        String cusStsDtm = line.substring(lineLength - (codeLength + dateLength), lineLength - codeLength);
        if (!cusStsDtm.equals(dateSuffix)) {
            log.error("사망자/압류자 날짜 데이터가 잘못되었습니다. {}", line);
            return null;
        }

        String itCsno = line.substring(itCsnoBeginIndex, lineLength - (codeLength + dateLength));
        // SEQ 10자리 이후부터, 줄 끝에서 날짜(8자리) + code(2자리)만큼 앞으로 이동한 자리 이전까지가 통합고객번호
        String encryptedItcsno = line.substring(itCsnoBeginIndex, lineLength - (codeLength + dateLength));
        
        itCsno = cryptUtils.decrypt(encryptedItcsno);
        if (itCsno == null) {
            log.error("고객번호 복호화 실패: {}", encryptedItcsno);
            return null;
        }
        if (itCsno.length() > itCsnoLength) {
            log.error("ITCSNO 길이가 {}자리를 초과했습니다. ITCSNO: {}", itCsnoLength, itCsno);
            return null;
        }

        DeactivateCstmrDto customer = new DeactivateCstmrDto();
        customer.setItcsno(itCsno);
        customer.setCusDscd(cusDscd);
        customer.setCusStsDtm(cusStsDtm);
        
        return customer;
    }
    
    private int parseTrailerCount(String trailerLine) {
        if (trailerLine == null || !trailerLine.startsWith("T")) {
            throw new IllegalArgumentException("Invalid trailer line format");
        }
        try {
            return Integer.parseInt(trailerLine.substring(1).trim());
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("Invalid count in trailer line", e);
        }
    }

    @Override
    public void executeJob(SchedulerJobConfig jobConfig, JobDetailTrigger jobDetailTrigger,
        JobExecutionContext context) {
        final String remoteDirectory = configProperties.getSftp().getRemote().getDirectory();
        final String fileBaseName = configProperties.getSftp().getRemote().getFileBaseName();
    
        log.info("사망자/압류자 추출 작업 시작");
        
        try {
            sftpRemoteFileTemplate.execute(session -> {
                log.info("Successfully connected to SFTP server");
                return true;
            });
        } catch (Exception e) {
            log.error("SFTP 연결에 실패했습니다.: ", e);
            throw new BaseException(ErrorCode.SERVER_ERROR, e);
        }

        LocalDate yesterday = LocalDate.now().minusDays(1);
        String dateSuffix = yesterday.format(DateTimeFormatter.ofPattern("yyyyMMdd"));
        
        String fileName = fileBaseName + "." + dateSuffix;
        String remotePath = remoteDirectory + fileName;
        
        log.info("Looking for file in SFTP: {}", remotePath);
        try {
            byte[] fileContent = sftpRemoteFileTemplate.execute(session -> {
                try {
                    if (!session.exists(remotePath)) {
                        log.warn("{}일자 사망자/압류자 파일이 SFTP 서버에 없습니다. {}", dateSuffix, remotePath);
                        return null;
                    }
                    
                    try (InputStream is = session.readRaw(remotePath)) {
                        return IOUtils.toByteArray(is);
                    }
                } catch (IOException e) {
                    log.error("sFTP 서버로부터 {}일자 사망자/압류자 파일을 읽는 데에 실패했습니다.: ", dateSuffix, e);
                    throw new BaseException(ErrorCode.FILE_DOWNLOAD_ERROR, e);
                }
            });

            if (fileContent == null) {
                return;
            }
            
            List<String> lines = new String(fileContent, StandardCharsets.UTF_8)
                                    .lines()
                                    .collect(Collectors.toList());

            if (lines.isEmpty()) {
                log.warn("파일이 비었습니다.: {}", fileName);
                return;
            }
 
            if (lines.size() < 3) {
                log.error("파일은 헤더부 한 줄, 데이터부 최소 한 줄, 트레일러부 한 줄이 있어야 합니다. {}", fileName);
                return;
            }

            String header = lines.get(0);
            if (!validateHeader(header, dateSuffix)) {
                log.error("헤더 형식이 잘못되었습니다. {}", header);
                return; 
            }

            String trailerLine = lines.get(lines.size() - 1);
            int expectedCount;
            try {
                expectedCount = parseTrailerCount(trailerLine);
                log.info("Expected number of records from trailer: {}", expectedCount);
            } catch (IllegalArgumentException e) {
                log.error("트레일러부 형식이 잘못 되었습니다. {}", trailerLine);
                return;
            }

            // header와 trailer를 제외한 데이터 부분만 읽는다.
            lines = lines.subList(1, lines.size() - 1);

            List<DeactivateCstmrDto> customers = lines.stream()
                                                .filter(line -> line.startsWith("D"))
                                                .map(line -> parseLine(line, dateSuffix))
                                                .filter(Objects:nonNull)
                                                .collect(Collectors.toList());
            
            if (customers.size() != expectedCount) {
                log.warn("실제 처리 숫자와 트레일러부 총 건수가 일치하지 않습니다. 총 건수: {}, 실제 처리수: {}", expectedCount, customers.size());
            }

            if (!customers.isEmpty()) {
                ewaDeactivateCstmrMapper.insertList(customers);
                log.info("Successfully processed {} customer records from file {}", customers.size(), fileName);
            } else {
                log.warn("사망자/압류자 파일 {}에 정보가 없습니다.", fileName);
            }
            
        } catch (Exception e) {
            log.error("사망자/압류자 파일 처리 중 에러가 발생했습니다.: ", e);
            throw new BaseException(ErrorCode.SERVER_ERROR, e);
        }
    }
    
    private boolean validateHeader(String header, String expectedDate) {
        if (header == null || header.length() < headerLength || !header.startsWith("H")) {
            log.debug("null or Invalid header");
            return false;
        }
        
        String headerDate = header.substring(1);
        return headerDate.equals(expectedDate);
    }
}

These are code for sftp.
There is an inconsistency about config variables.
In SftpConfig, I commented out reading config variables. But in the DeactivateCstmrJob, I use configProperties.
```
##### ConfigProperties
```java
package kr.or.cbdc.config.props;

import java.io.IOException;
import java.util.List;
import java.util.Map;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

import kr.or.cbdc.domain.main.mapper.sys.schdul.SyncScheduleMapper;
import kr.or.cbdc.infrastructure.framework.core.support.scheduling.AnyJob;
import kr.or.cbdc.infrastructure.framework.core.support.scheduling.interceptor.AnyJobInterceptor;
import lombok.Data;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;

@Data
@Configuration
@ConfigurationProperties(prefix = "config")
public class ConfigProperties {

    private String systemTitle;
    private String bankCode;
    private String bokCode = "BOK";
    private String bokNm = "한국은행";
    private String bankNo;
    private String bankNm;
    private String iniFilePath;
    private String activeServer;
    private java.io.File logsDirectory;
    private java.io.File tempDirectory;
    private String defaultLocale;
    private Message message;
    private Log log;
    private File file;
    private Scheduler scheduler;
    private Login login;
    private DataCrypt dataCrypt;
    private Coopsystem coopsystem;
    private Report report;
    private BokCbdc bokCbdc;
    private Payment payment;
    private List<String> holidayList;
    @Valid private CoreBanking coreBanking;
    @Valid private Gateway gateway;
    private String serverId;
    @Valid private Sftp sftp;

    @Data
    public static class Message {

        private InvalidText invalidText;
        @Data
        public static class InvalidText {

            private String prefix;
            private String suffix;
        }
    }
    @Data
    public static class Log {

        private boolean enable;
        private Query query;
        private Error error;
        private Login login;
        private Menu menu;

        @Data
        public static class Query {

            private boolean enable;


        }
        @Data
        public static class Error {

            private boolean enable;
            private String serverCode;
        }
        @Data
        public static class Login {

            private boolean enable;
        }
        @Data
        public static class Menu {

            private boolean enable;

        }

    }
    @Data
    public static class File {

        private String contentTransferEncoding;
        private Boolean downloadFilenameUrlEncode;
        private Boolean downloadFilenameEncoding;
        private Repository repository;
        private String downloadDir;

        @Data
        public static class Repository {

            private boolean createIfNotExists;
            private Map<String, String> repositories;

            public boolean isCreateIfNotExists() {
                return this.createIfNotExists;
            }

            public void setCreateIfNotExists(boolean createIfNotExists) {
                this.createIfNotExists = createIfNotExists;
            }

        }

    }
    @Data
    public static class Scheduler {

        private Boolean enable;
        private Class<? extends AnyJobInterceptor> jobInterceptor;
        private Map<String, JobDetailConfig> jobDetails;
        private String[] clusteredProfiles;

        @Data
        public static class JobDetailConfig {

            private String name;
            private String targetSchema;
            private Class<? extends AnyJob> jobClass;
            private Class<SyncScheduleMapper> countClass;
            private Boolean holdingJobContinuouslyExecute;
            private List<String> cronExpressionList;
            private List<String> dateRangeList;
            private Integer startDelay;
            private Integer jobSplits;
            private String[] profiles;

        }
    }
    @Data
    public static class Login {

        private String defaultAuthorCode;
        private Admin admin;
        private Sso sso;
        private Fail fail;

        @Data
        public static class Admin {

            private boolean enable;
            private List<String> ipList;
            private String key;
            private String password;
        }

        @Data
        public static class Sso {

            private boolean enable;
            private String sApiKey;
            private String ssoToKenName;

        }
        @Data
        public static class Fail {

            private int availCount;
        }

    }

    @Data
    public static class DataCrypt {

        private String[] columnNames;
        private String[] onewayColumnNames;

    }

    @Data
    public static class Coopsystem {

        private String srmsUrl;
        private String dbUrl;
        private String mainUrl;

    }

    @Data
    public static class Report {

        private java.io.File jsonDirectory;
        private java.io.File jarDirectory;


        public void setJsonDirectory(java.io.File jsonDirectory) {
            try {
                this.jsonDirectory = jsonDirectory.getCanonicalFile();
            } catch (IOException e) {
                this.jsonDirectory = jsonDirectory;
            }
        }

        public void setJarDirectory(java.io.File jarDirectory) {
            try {
                this.jarDirectory = jarDirectory.getCanonicalFile();
            } catch (IOException e) {
                this.jarDirectory = jarDirectory;
            }
        }

    }

    @Data
    public static class BokCbdc {
        private String bokServerRpc;
        private String keyServerRpc;
        private String defaultPubKey;
        private String fromAdres;
        private String toAdres;

    }

    @Data
    public static class Payment {
        public String url;

    }


    @Data
    public static class CoreBanking {
        private String url;
        private String appKey;
        @Valid private Retry retry;
        @Valid private Timeout timeout;
        private Token token;
        @Valid private CbdcRamp cbdcRamp;
        @Valid private BalanceCore balanceCore;
        @Valid private TdRamp tdRamp;
        @Valid private DeactivateBulk deactivateBulk;
        @Valid private ReconCbdc reconCbdc;
        @Valid private ReconTd reconTd;
        @Valid private IssueCbdc issueCbdc;
        @Valid private BurnCbdc burnCbdc;
        @Valid private DeactivateAll deactivateAll;
        @Valid private AppPush appPush;
    }

    @Data
    public static class Gateway {
        private String url;
        @Valid private Retry retry;
        @Valid private Timeout timeout;
        @Valid private Balance balance;
        @Valid private OnRamp onRamp;
        @Valid private OnRampFail OnRampFail;
        @Valid private OffRamp offRamp;
        @Valid private OffRampFail offRampFail;
        @Valid private Cbdc cbdc;
        @Valid private Ums ums;
    }
    @Data
    public static class Retry {
        @Min(value = 1, message = "Retry count must be at least 1")
        @Max(value = 3, message = "Retry count cannot exceed 3")
        private int count;
        
        @Min(value = 100, message = "Retry delay must be at least 100ms")
        @Max(value = 1000, message = "Retry delay cannot exceed 1000ms")
        private int delay;
    }

    @Data
    public static class Timeout {
        @Min(value = 1000, message = "Connect timeout must be at least 1000ms")
        @Max(value = 60000, message = "Connect timeout cannot exceed 60000ms")
        private int connect;
        
        @Min(value = 1000, message = "Connect timeout must be at least 1000ms")
        @Max(value = 60000, message = "Connect timeout cannot exceed 60000ms")
        private int read;
    }

    @Data
    public static class Token {
        private String value;
    }

    @Data
    public static class BalanceCore {
        @NotBlank(message = "balanceCore openAPI(core-banking) url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }
    
    @Data
    public static class CbdcRamp {
        @NotBlank(message = "cbdcRamp openAPI(core-banking) url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class TdRamp {
        @NotBlank(message = "tdRamp openAPI(core-banking) url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class OffRampFailCore {
        @NotBlank(message = "onRampFail openAPI(core-banking) url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class DeactivateBulk {
        @NotBlank(message = "deactivateBulk openAPI url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class ReconCbdc {
        @NotBlank(message = "reconCbdc openAPI url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class ReconTd {
        @NotBlank(message = "reconTd openAPI url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class IssueCbdc {
        @NotBlank(message = "issueCbdc openAPI url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class BurnCbdc {
        @NotBlank(message = "burnCbdc openAPI url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class DeactivateAll {
        @NotBlank(message = "deactivateAll openAPI url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class AppPush {
        @NotBlank(message = "appPush openAPI url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class Balance {
        @NotBlank(message = "balance gateway url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class OnRamp {
        @NotBlank(message = "onRamp gateway url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class OnRampFail {
        @NotBlank(message = "OnRampFail gateway url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class OffRamp {
        @NotBlank(message = "offRamp gateway url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class OffRampFail {
        @NotBlank(message = "OffRampFail gateway url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class Cbdc {
        @NotBlank(message = "cbdc gateway url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }
    
    @Data
    public static class Ums {
    	@NotBlank(message = "cbdc gateway url이 없습니다.")
    	@Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
    	private String url;
    }

    @Data
    public static class Sftp {
        @Valid
        private Remote remote;
    }
    
    @Data
    public static class Remote {
        @NotBlank(message = "sftp 디렉토리가 없습니다.")
        private String directory;
        @NotBlank(message = "기본 파일명이 없습니다.")
        private String fileBaseName;
    }
}
```
#### 답
##### ConfigProperties 내 Sftp 클래스 변경
```java
@Data
public static class Sftp {
    @NotBlank(message = "SFTP host is required")
    private String host;
    
    @Min(value = 1, message = "Port must be greater than 0")
    @Max(value = 65535, message = "Port must be less than 65536")
    private int port;
    
    @NotBlank(message = "SFTP username is required")
    private String username;
    
    @NotBlank(message = "SFTP password is required")
    private String password;
    
    @Valid
    private Remote remote;
}
```
##### yaml 파일 수정
```plain text
config:
  sftp:
    host: 10.208.63.15
    port: 22
    username: cbdcdev
    password: xxxxxxxxxx
    remote:
      directory: /upload/SEND/
      file-base-name: TDONOFFRAMPHISTORY
```
##### SftpConfig 수정
```java
@Configuration
@RequiredArgsConstructor
public class SftpConfig {
    private final ConfigProperties configProperties;
    
    @Bean
    public SessionFactory<SftpClient.DirEntry> sftpSessionFactory() {
        DefaultSftpSessionFactory factory = new DefaultSftpSessionFactory(true);
        factory.setHost(configProperties.getSftp().getHost());
        factory.setPort(configProperties.getSftp().getPort());
        factory.setUser(configProperties.getSftp().getUsername());
        factory.setPassword(configProperties.getSftp().getPassword());
        factory.setAllowUnknownKeys(true);
        return new CachingSessionFactory<>(factory);
    }

    @Bean
    public MessageHandler sftpMessageHandler() {
        SftpMessageHandler handler = new SftpMessageHandler(sftpSessionFactory());
        handler.setRemoteDirectoryExpression(
            new LiteralExpression(configProperties.getSftp().getRemote().getDirectory())
        );
        handler.setFileNameGenerator(message -> {
            LocalDate date = LocalDate.now();
            String formattedDate = date.format(DateTimeFormatter.ofPattern("yyyyMMdd"));
            return configProperties.getSftp().getRemote().getFileBaseName() + "." + formattedDate;
        });
        return handler;
    }
}
```
### Optional을 이용한 UMS message refactory
#### 질문: 코드가 refactoring 된 것 같다. 비교
```java
This is old code. 
@Slf4j
@Service
@RequiredArgsConstructor
public class SetPushDataService {

    private @Autowired PushMessageMapper pushMessageMapper;
    private @Autowired FirebaseCloudMessageService firebaseCloudMessageService;
    private @Autowired ApiCallHelper apiCallHelper;

    @Value("${config.bank-code}")
    private String bankCd;

    @Value("${spring.profiles.active}")
    private String active;

	public void setPushData(TxMessage message) {
		try {
			// Push 메시지 전달(CBDC 발행 제외)
			if (CommandType.I == message.getCommand() && CoinType.CBDC == message.getCoin()) {
				return;
			}

			TbAppMssageMastr tbAppMssageMastr = TbAppMssageMastr.builder().build().newId();
			TbAppMssageMastr tbAppMssageMastrRec = TbAppMssageMastr.builder().build().newId();
			List<String> tokenList = new ArrayList<>();
			DecimalFormat decFormat = new DecimalFormat("###,###");
			String txType = "0";

			if (message.getPersonId() == null) {
				log.error("SetPushData Error Parameter. 메세지에 이용자 ID(personId)가 없습니다.");
				return;
			}

			CstmrModel userInfo = null;
			try {
				// Push 메시지 전달(CBDC 발행 제외)
				if (CommandType.RF == message.getCommand() && CoinType.DC1 == message.getCoin()) {
					userInfo = pushMessageMapper.getCstmrInfoByAcnutno(message.getAcnutno());
				} else {
					userInfo = pushMessageMapper.getCstmrInfoByCstmrNo(message.getPersonId());
				}
			} catch (Exception e) {
				log.error("고객 정보 조회 에러: " + message.getPersonId() + ", Error Msg : " + e.getMessage());
				throw new BizException(ErrorCode.SERVER_ERROR, e.getMessage());
			}

			// 알림수신여부 확인
			if (!"Y".equals(userInfo.getProcessNtcnYn()))
				return;

			if (message.getCommand() == CommandType.T1) {

				String fromTokenNm = pushMessageMapper.getCodeNm("COIN_TYPE", CoinType.DC1.toString());

				if (message.getTxType() != null)
					txType = message.getTxType();

				if (txType.equals(TrnscType.ONLINE_PAYMENT.getValue()) || txType.equals(TrnscType.PAYMENT.getValue())) {
					// 결제
					String recNm = message.getWalletDpstr();
					String amount = decFormat.format(message.getAmount());

					if ("S".equals(message.getTrnscSttusCd())) {
						String UMSTemplateMsg = amount + "원, " + recNm + "에서 결제되었습니다.";
						tbAppMssageMastr.setMssageTycd("TP");
						tbAppMssageMastr.setSj("결제");
						tbAppMssageMastr.setMssageCn(fromTokenNm);
						// tbAppMssageMastr.setSndngMssageCn(ErrorCode.PUSH_MSG_APPROVAL_S.getFormat(recNm,
						// fromTokenNm, amount));
						tbAppMssageMastr.setSndngMssageCn(UMSTemplateMsg);
						tbAppMssageMastr.setIndictYn("Y");
						tbAppMssageMastr.setCstmrNo(userInfo.getCstmrNo());
						tbAppMssageMastr.setPushToken(userInfo.getPushToken());

						GwUmsAppPushDto push = GwUmsAppPushDto.builder().umsTmplCd("RPWSTTPE0132438")
								.csno(userInfo.getCstmrNo()).stlAm(amount).mpng1(recNm).build();
						apiCallHelper.callUMSGateway(push);
						if (userInfo.getPushToken() != null && !userInfo.getPushToken().isEmpty())
							tokenList.add(userInfo.getPushToken());

					} else if ("F".equals(message.getTrnscSttusCd())) {
						// String UMSTemplateMsg = amount + "원 " + recNm + " 결제 실패되었습니다.";
						tbAppMssageMastr.setMssageTycd("TP");
						tbAppMssageMastr.setSj("결제");
						tbAppMssageMastr.setMssageCn(fromTokenNm);
						tbAppMssageMastr
								.setSndngMssageCn(ErrorCode.PUSH_MSG_APPROVAL_F.getFormat(recNm, fromTokenNm, amount));
						// tbAppMssageMastr.setSndngMssageCn(UMSTemplateMsg);
						tbAppMssageMastr.setIndictYn("Y");
						tbAppMssageMastr.setCstmrNo(userInfo.getCstmrNo());
						tbAppMssageMastr.setPushToken(userInfo.getPushToken());

						// apiCallHelper.callUMSGateway(tbAppMssageMastr);
						if (userInfo.getPushToken() != null && !userInfo.getPushToken().isEmpty())
							tokenList.add(userInfo.getPushToken());
					}
				} else if (txType.equals(TrnscType.REFUND.getValue())) {
					// 환불
					String recNm = message.getWalletDpstr();
					String amount = decFormat.format(message.getAmount());

					if ("S".equals(message.getTrnscSttusCd())) {
						String UMSTemplateMsg = amount + "원, " + recNm + "에서 환불되었습니다.";
						tbAppMssageMastr.setMssageTycd("TP");
						tbAppMssageMastr.setSj("환불");
						tbAppMssageMastr.setMssageCn(fromTokenNm);
						// tbAppMssageMastr.setSndngMssageCn(ErrorCode.PUSH_MSG_REFUND_S.getFormat(recNm,
						// fromTokenNm, amount));
						tbAppMssageMastr.setSndngMssageCn(UMSTemplateMsg);
						tbAppMssageMastr.setIndictYn("Y");
						tbAppMssageMastr.setCstmrNo(userInfo.getCstmrNo());
						tbAppMssageMastr.setPushToken(userInfo.getPushToken());

						GwUmsAppPushDto push = GwUmsAppPushDto.builder().umsTmplCd("RPWSTTPE0132439")
								.csno(userInfo.getCstmrNo()).stlAm(amount).mpng1(recNm).build();
						apiCallHelper.callUMSGateway(push);
						if (userInfo.getPushToken() != null && !userInfo.getPushToken().isEmpty())
							tokenList.add(userInfo.getPushToken());

					} else if ("F".equals(message.getTrnscSttusCd())) {
						// String UMSTemplateMsg = amount + "원 " + recNm + "환불 실패되었습니다.";
						tbAppMssageMastr.setMssageTycd("TP");
						tbAppMssageMastr.setSj("환불");
						tbAppMssageMastr.setMssageCn(fromTokenNm);
						tbAppMssageMastr
								.setSndngMssageCn(ErrorCode.PUSH_MSG_REFUND_F.getFormat(recNm, fromTokenNm, amount));
						// tbAppMssageMastr.setSndngMssageCn(UMSTemplateMsg);
						tbAppMssageMastr.setIndictYn("Y");
						tbAppMssageMastr.setCstmrNo(userInfo.getCstmrNo());
						tbAppMssageMastr.setPushToken(userInfo.getPushToken());

						// apiCallHelper.callUMSGateway(tbAppMssageMastr);
						if (userInfo.getPushToken() != null && !userInfo.getPushToken().isEmpty())
							tokenList.add(userInfo.getPushToken());
					}
				} else if (!message.getFromBankCode().equals(message.getToBankCode())) {
					// 타행 이체인 경우
					String amount = decFormat.format(message.getAmount());

					if (bankCd.equals(message.getToBankCode()) && "S".equals(message.getTrnscSttusCd())) {
						// 메시지의 목적지가 당행인 경우 : 수신자 메시지 생성
						// 성공인 경우에만 수신 메시지를 송신
						String receiverAcnutNo = message.getAcnutno();
						String senderNm = message.getFromWalletDpstr();
						CstmrModel receiverInfo = null;

						try {
							receiverInfo = pushMessageMapper.getCstmrInfoByAcnutNo(receiverAcnutNo);
							tbAppMssageMastr.setMssageTycd("TP");
							tbAppMssageMastr.setSj("받기");
							tbAppMssageMastr.setMssageCn(fromTokenNm);
							tbAppMssageMastr.setSndngMssageCn(
									ErrorCode.PUSH_MSG_RECEIVE_S.getFormat(senderNm, fromTokenNm, amount));
							tbAppMssageMastr.setIndictYn("Y");
							tbAppMssageMastr.setCstmrNo(receiverInfo.getCstmrNo());
							tbAppMssageMastr.setPushToken(receiverInfo.getPushToken());

							if (!receiverInfo.getPushToken().isEmpty())
								tokenList.add(receiverInfo.getPushToken());
						} catch (Exception e) {
							log.error("계좌번호로 고객 정보 조회 에러: " + receiverAcnutNo + ", Error Msg: " + e.getMessage());
						}
					} else if (bankCd.equals(message.getFromBankCode())) {
						// 메시지가 당행에서 송신된 경우 : 송신자 메시지 생성
						String recNm = message.getWalletDpstr();

						if ("S".equals(message.getTrnscSttusCd())) {
							tbAppMssageMastr.setMssageTycd("TP");
							tbAppMssageMastr.setSj("송금");
							tbAppMssageMastr.setMssageCn(fromTokenNm);
							tbAppMssageMastr.setSndngMssageCn(
									ErrorCode.PUSH_MSG_SENDER_S.getFormat(recNm, fromTokenNm, amount));
							tbAppMssageMastr.setIndictYn("Y");
							tbAppMssageMastr.setCstmrNo(userInfo.getCstmrNo());
							tbAppMssageMastr.setPushToken(userInfo.getPushToken());

							if (userInfo.getPushToken() != null && !userInfo.getPushToken().isEmpty())
								tokenList.add(userInfo.getPushToken());

						} else if ("F".equals(message.getTrnscSttusCd())) {
							tbAppMssageMastr.setMssageTycd("TP");
							tbAppMssageMastr.setSj("송금");
							tbAppMssageMastr.setMssageCn(fromTokenNm);
							tbAppMssageMastr.setSndngMssageCn(
									ErrorCode.PUSH_MSG_SENDER_F.getFormat(recNm, fromTokenNm, amount));
							tbAppMssageMastr.setIndictYn("Y");
							tbAppMssageMastr.setCstmrNo(userInfo.getCstmrNo());
							tbAppMssageMastr.setPushToken(userInfo.getPushToken());

							if (userInfo.getPushToken() != null && !userInfo.getPushToken().isEmpty())
								tokenList.add(userInfo.getPushToken());
						}
					}
				} else {
					// 당행 내부에서의 이체인 경우
					String amount = decFormat.format(message.getAmount());

					String senderAcnutNo = message.getFromAcnutno();
					String receiverAcnutNo = message.getAcnutno();
					String senderNm = message.getFromWalletDpstr();
					String recNm = message.getWalletDpstr();

					try {
						CstmrModel senderInfo = pushMessageMapper.getCstmrInfoByAcnutNo(senderAcnutNo);
						CstmrModel receiverInfo = pushMessageMapper.getCstmrInfoByAcnutNo(receiverAcnutNo);

						if ("S".equals(message.getTrnscSttusCd())) {
							// 성공인 경우
							tbAppMssageMastr.setMssageTycd("TP");
							tbAppMssageMastr.setSj("송금");
							tbAppMssageMastr.setMssageCn(fromTokenNm);
							tbAppMssageMastr.setSndngMssageCn(
									ErrorCode.PUSH_MSG_SENDER_S.getFormat(recNm, fromTokenNm, amount));
							tbAppMssageMastr.setIndictYn("Y");
							tbAppMssageMastr.setCstmrNo(senderInfo.getCstmrNo());
							tbAppMssageMastr.setPushToken(senderInfo.getPushToken());

							if (!senderInfo.getPushToken().isEmpty())
								tokenList.add(senderInfo.getPushToken());

							tbAppMssageMastrRec.setMssageTycd("TP");
							tbAppMssageMastrRec.setSj("받기");
							tbAppMssageMastrRec.setMssageCn(fromTokenNm);
							tbAppMssageMastrRec.setSndngMssageCn(
									ErrorCode.PUSH_MSG_RECEIVE_S.getFormat(senderNm, fromTokenNm, amount));
							tbAppMssageMastrRec.setIndictYn("Y");
							tbAppMssageMastrRec.setCstmrNo(receiverInfo.getCstmrNo());
							tbAppMssageMastrRec.setPushToken(receiverInfo.getPushToken());

							try {
								log.info("Active : " + active);
								pushMessageMapper.insert(tbAppMssageMastrRec);

								if (tbAppMssageMastrRec.getPushToken() != null) {
									this.firebaseCloudMessageService.sendMultiMessage(
											List.of(tbAppMssageMastrRec.getPushToken()), tbAppMssageMastrRec.getSj(),
											tbAppMssageMastrRec.getSndngMssageCn(), "");
								}
							} catch (BizException e) {
								throw new BizException(ErrorCode.SERVER_ERROR, e.getMessage());
							} catch (Exception e) {
								throw new BizException(ErrorCode.SERVER_ERROR, e.getMessage());
							}
						} else if ("F".equals(message.getTrnscSttusCd())) {
							// 실패한 경우
							tbAppMssageMastr.setMssageTycd("TP");
							tbAppMssageMastr.setSj("송금");
							tbAppMssageMastr.setMssageCn(fromTokenNm);
							tbAppMssageMastr.setSndngMssageCn(
									ErrorCode.PUSH_MSG_SENDER_F.getFormat(recNm, fromTokenNm, amount));
							tbAppMssageMastr.setIndictYn("Y");
							tbAppMssageMastr.setCstmrNo(senderInfo.getCstmrNo());
							tbAppMssageMastr.setPushToken(senderInfo.getPushToken());

							if (!senderInfo.getPushToken().isEmpty())
								tokenList.add(senderInfo.getPushToken());
						}
					} catch (Exception e) {
						log.error("SetPushData Error Parameter : " + message.getPersonId() + " Error Msg : "
								+ e.getMessage());
					}
				}
			} else if (message.getCommand() == CommandType.I1) {

				String toTokenNm = pushMessageMapper.getCodeNm("COIN_TYPE", CoinType.DC1.toString());
				String amount = decFormat.format(message.getAmount());

				tbAppMssageMastr.setCstmrNo(userInfo.getCstmrNo());

				if ("S".equals(message.getTrnscSttusCd())) {
					String UMSTemplateMsg = amount + "원, 예금 토큰으로 전환되었습니다.";
					tbAppMssageMastr.setMssageTycd("TP");
					tbAppMssageMastr.setSj("전환 입금");
					tbAppMssageMastr.setMssageCn(toTokenNm);
					// tbAppMssageMastr.setSndngMssageCn(ErrorCode.PUSH_MSG_TRN_TOKEN_S.getFormat(amount,
					// toTokenNm));
					tbAppMssageMastr.setSndngMssageCn(UMSTemplateMsg);
					tbAppMssageMastr.setIndictYn("Y");

					// 성공 시에만 UMS 메시지를 보낸다.
					GwUmsAppPushDto push = GwUmsAppPushDto.builder().umsTmplCd("RPWSTTPE0132436")
							.csno(userInfo.getCstmrNo()).stlAm(amount).build();
					apiCallHelper.callUMSGateway(push);
				} else if ("F".equals(message.getTrnscSttusCd())) {
					tbAppMssageMastr.setMssageTycd("TP");
					tbAppMssageMastr.setSj("전환 입금");
					tbAppMssageMastr.setMssageCn(toTokenNm);
					tbAppMssageMastr.setSndngMssageCn(ErrorCode.PUSH_MSG_TRN_TOKEN_F.getFormat(amount, toTokenNm));
					tbAppMssageMastr.setIndictYn("Y");
				}

				if (userInfo.getPushToken() != null && !userInfo.getPushToken().isEmpty()) {
					tokenList.add(userInfo.getPushToken());
				}
			} else if (message.getCommand() == CommandType.R1) {

				String toTokenNm = pushMessageMapper.getCodeNm("COIN_TYPE", CoinType.DC1.toString());
				String amount = decFormat.format(message.getAmount());

				tbAppMssageMastr.setCstmrNo(userInfo.getCstmrNo());

				if (txType.equals(TrnscType.QUIT.getValue())) {
					String koreanNm = userInfo.getKoreanNm();
					// 탈회하면서 발생하는 offRamp는 별도로 전송
					String UMSTemplateMsg = koreanNm + "님, 전자지갑이 해지되었습니다.";
					tbAppMssageMastr.setMssageTycd("TP");
					tbAppMssageMastr.setSj("전환");
					tbAppMssageMastr.setMssageCn(toTokenNm);
					tbAppMssageMastr.setSndngMssageCn(UMSTemplateMsg);
					tbAppMssageMastr.setIndictYn("Y");

					GwUmsAppPushDto push = GwUmsAppPushDto.builder().umsTmplCd("RPWSTTPE0132435")
							.csno(userInfo.getCstmrNo()).cusNm(koreanNm).build();
					apiCallHelper.callUMSGateway(push);
				} else {
					if ("S".equals(message.getTrnscSttusCd())) {
						String UMSTemplateMsg = amount + "원, 예금으로 전환되었습니다.";
						tbAppMssageMastr.setMssageTycd("TP");
						tbAppMssageMastr.setSj("전환");
						tbAppMssageMastr.setMssageCn(toTokenNm);
						// tbAppMssageMastr.setSndngMssageCn(ErrorCode.PUSH_MSG_TRN_DEPOSIT_S.getFormat(amount));
						tbAppMssageMastr.setSndngMssageCn(UMSTemplateMsg);
						tbAppMssageMastr.setIndictYn("Y");
						// 성공 시에만 UMS 메시지를 보낸다.
						GwUmsAppPushDto push = GwUmsAppPushDto.builder().umsTmplCd("RPWSTTPE0132437")
								.csno(userInfo.getCstmrNo()).stlAm(amount).build();
						apiCallHelper.callUMSGateway(push);
					} else if ("F".equals(message.getTrnscSttusCd())) {
						tbAppMssageMastr.setMssageTycd("TP");
						tbAppMssageMastr.setSj("전환");
						tbAppMssageMastr.setMssageCn(toTokenNm);
						tbAppMssageMastr.setSndngMssageCn(ErrorCode.PUSH_MSG_TRN_DEPOSIT_F.getFormat(amount));
						tbAppMssageMastr.setIndictYn("Y");
					}
				}

				if (userInfo.getPushToken() != null && !userInfo.getPushToken().isEmpty()) {
					tokenList.add(userInfo.getPushToken());
				}
			}

			try {
				pushMessageMapper.insert(tbAppMssageMastr);

				if (!tokenList.isEmpty()) {
					this.firebaseCloudMessageService.sendMultiMessage(tokenList, tbAppMssageMastr.getSj(),
							tbAppMssageMastr.getSndngMssageCn(), "");
				}
			} catch (BizException e) {
				log.error("SetPushData BizException. " + e.getMessage());
				throw new BizException(ErrorCode.SERVER_ERROR, e.getMessage());
			} catch (Exception e) {
				log.error("SetPushData Exception. " + e.getMessage());
				throw new BizException(ErrorCode.SERVER_ERROR, e.getMessage());
			}
		} catch (Exception e) {
			log.error("SetPushData Exception. " + e.getMessage());
		}
	}
}
--------------------
This is new version of the same class.
@Slf4j
@Service
@RequiredArgsConstructor
public class SetPushDataService {

    private final PushMessageMapper pushMessageMapper;
    private final FirebaseCloudMessageService firebaseCloudMessageService;
    private final BridgeServiceInterface bridgeService;

    @Value("${config.bank-code}")
    private String bankCd;

    @Value("${spring.profiles.active}")
    private String active;

    private static final DecimalFormat DECIMAL_FORMAT = new DecimalFormat("###,###");

    private String tokenNm;

    @PostConstruct
    private void init() {
        tokenNm = pushMessageMapper.getCodeNm("COIN_TYPE", CoinType.DC1.toString());
    }

    @Retryable(value = {BizException.class}, // 재시도할 예외
            maxAttempts = 3, // 최대 재시도 횟수
            backoff = @Backoff(delay = 2000) // 재시도 간격(밀리초)
    )


    public void sendPushNotification(List<String> tokens, String subject, String message) {
        try {
            //[필요 시 참가기관 별 푸쉬 서비스 적용] 푸쉬 데이터 전송
            //bridgeService.pushProcessing(tbAppMssageMastr);

            firebaseCloudMessageService.sendMultiMessage(tokens, subject, message, "");
        } catch (FirebaseMessagingException | IOException e) {
            // TODO Auto-generated catch block
            throw new BizException(ErrorCode.PUSH_SEND_ERROR, e);
        }
    }

    @Recover
    public void recover(Exception e, List<String> tokens, String subject, String message) {
        log.error("Failed to send push notification after retries: {}", e.getMessage());
        // 실패 메시지를 저장하거나 별도 처리
    }

    public void setPushData(TxMessage message) {
        try {
            Optional.ofNullable(processMessage(message))
                    .ifPresent(tbAppMssageMastrList -> tbAppMssageMastrList.stream()
                            .filter(tbAppMssageMastr -> Optional.ofNullable(tbAppMssageMastr.getPushToken())
                                    .isPresent())
                            .forEach(tbAppMssageMastr -> {
                                pushMessageMapper.insert(tbAppMssageMastr);
                                sendPushNotification(
                                        List.of(tbAppMssageMastr.getPushToken()),
                                        tbAppMssageMastr.getSj(),
                                        tbAppMssageMastr.getSndngMssageCn());
                            }));
        } catch (BizException e) {
            log.error("[{}] Error processing message: {}", message.getRequestId(), e.getMessage(), e);
        } catch (Exception e) {
            log.error("[{}] Error processing message: {}", message.getRequestId(), e.getMessage(), e);
        }
    }

    private List<TbAppMssageMastr> processMessage(TxMessage message) {
        String txType = Optional.ofNullable(message.getTxType()).orElse("0");

        return switch (message.getCommand()) {
            case T1 -> handleT1Command(message, txType);
            case I1 -> TrnscType.DEPOSIT.getValue().equals(txType) ? handleDepositCommand(message) : null;
            case R1 -> TrnscType.CONVERS.getValue().equals(txType) ? handleConversionCommand(message) : null;
            default -> {
                log.warn("Unknown command type: {}", message.getCommand());
                yield null;
            }
        };
    }

    private List<TbAppMssageMastr> handleT1Command(TxMessage message, String txType) {

        if (TrnscType.ONLINE_PAYMENT.getValue().equals(txType) || TrnscType.PAYMENT.getValue().equals(txType)) {
            return handlePaymentCommand(message);
        } else if (TrnscType.REFUND.getValue().equals(txType)) {
            return handleRefundCommand(message);
        } else if (!message.getFromBankCode().equals(message.getToBankCode())) {
            return handleExteralBankTransfer(message);
        } else {
            return handleInterBankTransfer(message);
        }
    }

    private List<TbAppMssageMastr> handlePaymentCommand(TxMessage message) {
        CstmrModel senderInfo = pushMessageMapper.getCstmrInfoByCstmrNo(message.getPersonId());
        String amount = DECIMAL_FORMAT.format(message.getAmount());

        if ("S".equals(message.getTrnscSttusCd())) {
            return createPushMessage(senderInfo, message, "결제", ErrorCode.PUSH_MSG_APPROVAL_S,
                    null, message.getWalletDpstr(), tokenNm, amount);
        } else {
            // 실패시 수신자명 데이터가 넘어오지 못하므로 수신자 명을 빼고 메시지 생성
            return createPushMessage(senderInfo, message, "결제", null,
                    ErrorCode.PUSH_MSG_APPROVAL_F, tokenNm, amount);
        }
    }

    private List<TbAppMssageMastr> handleRefundCommand(TxMessage message) {
        CstmrModel senderInfo = pushMessageMapper.getCstmrInfoByCstmrNo(message.getPersonId());
        String amount = DECIMAL_FORMAT.format(message.getAmount());
        return createPushMessage(senderInfo, message, "환불", ErrorCode.PUSH_MSG_REFUND_S,
                ErrorCode.PUSH_MSG_REFUND_F, message.getWalletDpstr(), tokenNm, amount);
    }

    private List<TbAppMssageMastr> handleDepositCommand(TxMessage message) {
        CstmrModel cstmrModel = pushMessageMapper.getCstmrInfoByCstmrNo(message.getPersonId());
        String amount = DECIMAL_FORMAT.format(message.getAmount());

        return createPushMessage(cstmrModel, message, "전환 입금", ErrorCode.PUSH_MSG_TRN_TOKEN_S,
                ErrorCode.PUSH_MSG_TRN_TOKEN_F, amount, tokenNm);
    }

    private List<TbAppMssageMastr> handleConversionCommand(TxMessage message) {
        CstmrModel cstmrModel = pushMessageMapper.getCstmrInfoByCstmrNo(message.getPersonId());
        String amount = DECIMAL_FORMAT.format(message.getAmount());

        return createPushMessage(cstmrModel, message, "전환", ErrorCode.PUSH_MSG_TRN_DEPOSIT_S,
                ErrorCode.PUSH_MSG_TRN_DEPOSIT_F, amount);
    }

    // 당행 내부에서의 이체인 경우
    private List<TbAppMssageMastr> handleInterBankTransfer(TxMessage message) {
        String amount = DECIMAL_FORMAT.format(message.getAmount());

        String senderAcnutNo = message.getFromAcnutno();
        String receiverAcnutNo = message.getAcnutno();
        CstmrModel senderInfo = pushMessageMapper.getCstmrInfoByAcnutNo(senderAcnutNo);
        CstmrModel receiverInfo = pushMessageMapper.getCstmrInfoByAcnutNo(receiverAcnutNo);

        if (bankCd.equals(message.getToBankCode()) && "S".equals(message.getTrnscSttusCd())) {
            return ListUtils.union(createPushMessage(receiverInfo, message, "받기", ErrorCode.PUSH_MSG_RECEIVE_S, null,
                            message.getFromWalletDpstr(), tokenNm, amount),
                    createPushMessage(senderInfo, message, "송금", ErrorCode.PUSH_MSG_SENDER_S, null,
                            message.getWalletDpstr(), tokenNm, amount));
        } else if (bankCd.equals(message.getFromBankCode())) {
            return createPushMessage(senderInfo, message, "송금", ErrorCode.PUSH_MSG_SENDER_S,
                    ErrorCode.PUSH_MSG_SENDER_F, message.getWalletDpstr(), tokenNm, amount);
        }
        return null;
    }

    private List<TbAppMssageMastr> createPushMessage(CstmrModel customerInfo, TxMessage message, String subject,
                                                     ErrorCode successCode,
                                                     ErrorCode failureCode, Object... params) {

        if (customerInfo == null) return List.of();

        return List.of(TbAppMssageMastr.builder()
                .cstmrNo(customerInfo.getCstmrNo())
                .pushToken(Optional.ofNullable(customerInfo.getPushToken()).orElse(""))
                .mssageTycd("TP")
                .sj(subject)
                .mssageCn(tokenNm)
                .sndngMssageCn(getTransferMessage(message.getTrnscSttusCd(), successCode, failureCode, params))
                .indictYn("Y").build()
                .newId());

    }

    // 타행 이체인 경우
    // 메시지의 목적지가 당행인 경우 : 수신자 메시지 생성
    // 성공인 경우에만 수신 메시지를 송신
    private List<TbAppMssageMastr> handleExteralBankTransfer(TxMessage message) {
        String amount = DECIMAL_FORMAT.format(message.getAmount());

        if (bankCd.equals(message.getToBankCode()) && "S".equals(message.getTrnscSttusCd())) {
            String receiverAcnutNo = message.getAcnutno();
            CstmrModel receiverInfo = getCustomerInfoByAccount(receiverAcnutNo);
            return createPushMessage(receiverInfo, message, "받기",
                    ErrorCode.PUSH_MSG_RECEIVE_S, null, message.getFromWalletDpstr(), tokenNm, amount);
        } else if (bankCd.equals(message.getFromBankCode())) {
            String senderAcnutNo = message.getFromAcnutno();
            CstmrModel senderInfo = getCustomerInfoByAccount(senderAcnutNo);
            return createPushMessage(senderInfo, message, "송금", ErrorCode.PUSH_MSG_SENDER_S,
                    ErrorCode.PUSH_MSG_SENDER_F, message.getWalletDpstr(), tokenNm, amount);
        }

        return null;
    }

    private CstmrModel getCustomerInfoByAccount(String accountNo) {
        try {
            return Optional.ofNullable(accountNo).map(pushMessageMapper:getCstmrInfoByAcnutNo).orElse(null);
        } catch (Exception e) {
            log.error("Error fetching customer info for accountNo {}: {}", accountNo, e.getMessage());
            return null;
        }
    }

    private String getTransferMessage(String statusCode, ErrorCode successCode, ErrorCode failureCode,
                                      Object... params) {
        // amount를 params 배열의 앞에 추가한 새로운 배열 생성
        return "S".equals(statusCode) ? successCode.getFormat(params) : failureCode.getFormat(params);
    }
}

It seems new code was refactored. 
Compare these 2 versions and check if the core logic is same.

I have to merge but new version changed too much. Another problem is I added some code to send messages to external system 
and set custome messages using UMSTemplateMsg variable. Can you merge it and make merged version works like old version?
FYI, this is added code to send messages.
GwUmsAppPushDto push = GwUmsAppPushDto.builder().umsTmplCd("RPWSTTPE0132438")
								.csno(userInfo.getCstmrNo()).stlAm(amount).mpng1(recNm).build();
						apiCallHelper.callUMSGateway(push);
						if (userInfo.getPushToken() != null && !userInfo.getPushToken().isEmpty())
							tokenList.add(userInfo.getPushToken());
```
### SecurityConfig 기능
#### 질문: SecurityConfig에 특정 url이 등록되어 있을 때 기능?
```java
This is security config file.

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Value(value="${spring.profiles.active}")
    private String active;
    private @Autowired SecuredResourceServiceImpl securedResourceService;
    private @Autowired ReloadableFilterInvocationSecurityMetadataSource filterInvocationSecurityMetadataSource;
    private @Autowired JwtTokenFilter jwtTokenFilter;
    private @Autowired UserAccessDeniedHandler userAccessDeniedHandler;
    private @Autowired UserLoginSuccessHandler userLoginSuccessHandler;

    private void configureCors(CorsConfigurer<HttpSecurity> cors) {
        if (  active.contains("live") ) {
            cors.disable();
        }else {
            cors.configurationSource(corsConfigurationSource());
        }
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                .cors(cors -> configureCors(cors) )
                .csrf(AbstractHttpConfigurer:disable)
                .authorizeHttpRequests(authorizeRequests -> authorizeRequests
                        .anyRequest().authenticated())
                .exceptionHandling(exceptionHandling -> exceptionHandling
                        .authenticationEntryPoint((request, response, authException) -> {
                            response.setCharacterEncoding("UTF-8");
                            response.setContentType("application/json");
                            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                            response.getWriter()
                                    .write(ErrorMessage.builder()
                                            .status(String.valueOf(HttpServletResponse.SC_UNAUTHORIZED))
                                            .message("접근 권한이 없습니다").build().toJson());
                        })
                        .accessDeniedHandler(userAccessDeniedHandler))
                .formLogin(formLogin -> formLogin
                        .loginProcessingUrl("/users/login")
                        .successHandler(userLoginSuccessHandler)
                        .failureHandler(new UserLoginFailureHandler())
                        .usernameParameter("loginNm")
                        .passwordParameter("loginPassword"));

        http.logout(logout -> logout.logoutSuccessHandler(new UserLogoutSuccessHandler()));

        configureCustomFilters(http);

        return http.build();
    }

    private void configureCustomFilters(HttpSecurity http) throws Exception {
        RoleHierarchyVoter roleHierarchyVoter = new RoleHierarchyVoter(roleHierarchy());

        List<AccessDecisionVoter<? extends Object>> accessDecisionVoterList = new ArrayList<>();
        accessDecisionVoterList.add(roleHierarchyVoter);

        AffirmativeBased accessDecisionManager = new AffirmativeBased(accessDecisionVoterList);

        FilterSecurityInterceptor filterSecurityInterceptor = new FilterSecurityInterceptor();
        filterSecurityInterceptor.setSecurityMetadataSource(filterInvocationSecurityMetadataSource);
        filterSecurityInterceptor.setAccessDecisionManager(accessDecisionManager);

        filterSecurityInterceptor.setAuthenticationManager(http.getSharedObject(AuthenticationManager.class));

        http.addFilterAt(filterSecurityInterceptor, FilterSecurityInterceptor.class);
        http.addFilterBefore(jwtTokenFilter, UsernamePasswordAuthenticationFilter.class);
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(12);
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.addAllowedOriginPattern("*");
        // configuration.setAllowedOrigins(List.of("http://192.168.20.12:3000","http://192.168.20.14:3000","http://192.168.20.19:3000"));
        configuration.setAllowedHeaders(List.of("*"));
        configuration.setAllowedMethods(List.of("*"));
        configuration.setExposedHeaders(List.of("*"));
        configuration.setAllowCredentials(true);
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }

    @Bean
    public RoleHierarchyImpl roleHierarchy() {
        RoleHierarchyImpl roleHierarchy = new RoleHierarchyImpl();
        roleHierarchy.setHierarchy(securedResourceService.getRoleHierarchyStringRepresentation());

        return roleHierarchy;
    }

    @Bean
    public DaoAuthenticationProvider daoAuthenticationProvider() {
        return new UserLoginProvider();
    }

    @Bean
    public WebSecurityCustomizer webSecurityCustomizer() {
        return (web) -> web.ignoring().requestMatchers(
                new AntPathRequestMatcher("/static/**"),
                new AntPathRequestMatcher("/*"),
                new AntPathRequestMatcher("/login/reissue"),
                new AntPathRequestMatcher("/common/getStringForQRBarCode"),
                new AntPathRequestMatcher("/common/config/readConfig"),
                new AntPathRequestMatcher("/common/health"),
                new AntPathRequestMatcher("/api/v1/satp/**"),
                new AntPathRequestMatcher("/api-docs/**"),
                new AntPathRequestMatcher("/configuration/**"),
                new AntPathRequestMatcher("/swagger*/**"),
                new AntPathRequestMatcher("/webjars/**"),
                new AntPathRequestMatcher("/swagger-ui/**"),
                new AntPathRequestMatcher("/common/if/wallet/gentoken"),
                new AntPathRequestMatcher("/docs"),
                new AntPathRequestMatcher("/api/login"),
                new AntPathRequestMatcher("/ewa/common/confirmUser"),
                new AntPathRequestMatcher("/ewa/common/v2/confirmUser"),
                new AntPathRequestMatcher("/ewa/common/selfAuth"),
                new AntPathRequestMatcher("/ewa/common/selfAuthNum"),
                new AntPathRequestMatcher("/ewa/common/v2/selfAuth"),
                new AntPathRequestMatcher("/ewa/common/v2/selfAuthNum"),
                new AntPathRequestMatcher("/ewa/common/createUser"),
                new AntPathRequestMatcher("/ewa/common/v2/createUser"),
                new AntPathRequestMatcher("/ewa/common/getWalletCreateLog"),                
                new AntPathRequestMatcher("/ewa/stplat/readList"),
                new AntPathRequestMatcher("/ewa/stplat/insertAgrt"),
                new AntPathRequestMatcher("/ewa/common/regPinNum"),
                new AntPathRequestMatcher("/ewa/common/pinNumEnc"),                
                new AntPathRequestMatcher("/ewa/common/acnutList"),
                new AntPathRequestMatcher("/ewa/common/acnut"),
                new AntPathRequestMatcher("/ewa/common/acnutChk"),                
                new AntPathRequestMatcher("/ewa/common/ars1"),
                new AntPathRequestMatcher("/ewa/common/ars2"),
                new AntPathRequestMatcher("/ewa/common/arsCallBack"),
                new AntPathRequestMatcher("/ewa/common/test"),
                new AntPathRequestMatcher("/ewa/common/test1"),
                new AntPathRequestMatcher("/ewa/common/eltWallHldYn"),
                new AntPathRequestMatcher("/ewa/common/certSerial"),
                new AntPathRequestMatcher("/ewa/common/newOneVerify"),
                new AntPathRequestMatcher("/ewa/wallet/api/signVerifyReq"),
                new AntPathRequestMatcher("/ewa/wallet/api/signVerifyRes"),
                new AntPathRequestMatcher("/ewa/wallet/api/signVerifyTest"),
                new AntPathRequestMatcher("/mtranskeyServlet*"),
                new AntPathRequestMatcher("/mtranskeyServlet"),
                new AntPathRequestMatcher("/ewa/common/temp/readList"),
                new AntPathRequestMatcher("/actuator/**"),
                new AntPathRequestMatcher("/actuator/ephemeral-command/**"),
                new AntPathRequestMatcher("/system/check"),
                new AntPathRequestMatcher("/custom/ephemeral-command/**"),
                new AntPathRequestMatcher("/ewa/acnut/depositTrans"),
                // DID, NEWWON 뱅킹 연계 - spring security 예외처리
                new AntPathRequestMatcher("/newwon/dpstTknEltWallInq/eltWallHldYn"),
                new AntPathRequestMatcher("/did/dpstTknEltWallInq/eltWallHldYn"),
                new AntPathRequestMatcher("/did/dpstTknEltWallInq/eltWallInf"),
                new AntPathRequestMatcher("/did/dpstTknEltWallInq/eltWallTrnPrts"),
                new AntPathRequestMatcher("/testApi/**"),
                new AntPathRequestMatcher("/ewa/gw/**"),
                new AntPathRequestMatcher("/pdm/wallet/**")
                );
    }
}

Look at the /pdm/wallet/**.

When I call this endpoint with token, no problem? Doesn't the security filter remove the token? Or just pass the token to the endpoint?
```
#### 답
```plain text
Let me analyze the security configuration to answer your questions about the /pdm/wallet/** endpoint behavior.
Looking at the code, I notice that /pdm/wallet/** is listed in the webSecurityCustomizer() method under web.ignoring().requestMatchers(). This is significant because:

When a path is added to web.ignoring(), it completely bypasses the Spring Security filter chain
This means that ALL security filters, including the JWT token filter (jwtTokenFilter), will be bypassed for this endpoint
If you send a request to /pdm/wallet/**:

The token will not be validated
The token will not be removed
The token will simply be passed through to the endpoint as is

So to directly answer your questions:

The security filter will not process or remove the token
The token will be passed unchanged to the endpoint
It's up to your endpoint implementation to handle any token validation if needed

If you want the JWT token validation to occur for /pdm/wallet/** endpoints, you should remove that path from the webSecurityCustomizer() method. This would make the endpoint go through the normal security filter chain, including your jwtTokenFilter.
```
### Kafka 구조 변경
#### v1: 업무 처리가 들어가기 이전 버전.
```java
@Slf4j
@Component
public class MessageListener {

    @Autowired
    private KafkaTemplate<String, TxMessage> kafkaTemplate;

    @Value(value = "${spring.kafka.topicTxRequest}")
    public String[] topicTxRequest;

    @Value(value = "${spring.kafka.topicTxResponse}")
    private String topicTxResponse;

    @Value(value = "${config.bank-code}")
    private String bankCode;

    @Value(value = "${spring.kafka.group}")
    public String group;
    @Value(value = "${spring.kafka.bc-group}")
    public String bcGroup;

    private @Autowired TransactionSagaMapper transactionSagaMapper;
    private @Autowired TransactionRecordMapper transactionRecordMapper;
    private @Autowired TransactionMapping transactionMapping;

    private @Autowired SetPushDataService setPushData;
    private @Autowired KafkaProducer kafkaProducer;
    private @Autowired ConfigProperties config;
    // For gateway
    private @Autowired BridgeServiceInterface bridgeService;

    public String[] dynamicTopics;

    @PostConstruct
    public void initializeTopics() {
        // 각 원소에 "_${config.bank-code}"를 추가
        dynamicTopics = Arrays.stream(topicTxRequest)
                .map(topic -> topic + "_" + bankCode)
                .toArray(String[]:new);

        log.info("Dynamic Topics Initialized: {}", Arrays.toString(dynamicTopics));
    }    

    private boolean vouchTranSactionData(TxMessage message) {

        switch (message.getCommand()) {
            case PM: //바우처 연계 : 결제 요청
                transactionMapping.setTransactionComplete( message.getCommand(),message.getTxDbId(),message.getPersonId(),"", message);
                return true;
            case TX, TR: //바우처 연계 : 거래번호 생성및 요청
                transactionMapping.setTransactionComplete( message.getCommand(),message.getTxDbId(),message.getPersonId(),"", message);
                return true;
            case PR, PF: // 바우처 연계 승인정보전달 Update 후 종료 , 승인 Update key 'TX_CD' , 결제승인번호는 '리퀘스트ID'
                transactionRecordMapper.updatePr(message);
                return true;
            case RR, RF: // 바우처 연계 환불정보전달 Update 후 종료 , 환불 Update key 'TX_CD' , 환불승인번호는 '리퀘스트ID'
                transactionRecordMapper.updateRr(message);
                return true;
            case CR: // 바우처 연계 캐쉬백정보전달 Update 후 종료 , 캐쉬백 Update key 'TX_CD' , 캐쉬백승인번호는 '리퀘스트ID'
                transactionRecordMapper.updateCr(message);
                return true;
            default:
                return false;
        }
    }

    public void updateTransactionComplete(TxMessage message) {
        String messageSttus = "";
        switch (message.getCommand()) {
            case M, I, B, R, M1, M2, D1, D2, I1, I2, R1, R2:
                messageSttus = "S".equals(message.getTrnscSttusCd()) ? "C" : "F";
                break;
            case D:
                messageSttus = "S".equals(message.getTrnscSttusCd()) ? "A" : "F";
                break;
            default:
                messageSttus = "S".equals(message.getTrnscSttusCd()) ? "C" : "F";
                return;
        }
        transactionMapping.setTransactionComplete(message.getCommand(), message.getTxDbId(), message.getPersonId(),
                messageSttus, message);
    }

    @RetryableTopic(attempts = "3", backoff = @Backoff(  delay = 1000, maxDelay = 5000, multiplier = 2), kafkaTemplate = "kafkaTemplate", dltStrategy = DltStrategy.FAIL_ON_ERROR, listenerContainerFactory = "retryContainerFactory")
    @KafkaListener(id = "txRequest", topics = "#{@messageListener.dynamicTopics}", containerFactory = "kafkaListenerContainerFactory", groupId = "${spring.kafka.group}" )
    public void listenTxRequest(TxMessage message, Acknowledgment acknowledgment) throws WalletSdkException, InterruptedException, ExecutionException {

        log.debug("txRequest message {} : {}", message.getRequestId(), message.toString());

        //바우처 연계
        try {
            if(vouchTranSactionData(message)){
                acknowledgment.acknowledge();
                return;
               }
        }catch (Exception e){
            acknowledgment.acknowledge();
            log.error("vouchTranSactionData: {}",ExceptionUtils.getMessage(e),e);
            return;
        }

        // 지갑으로 기록할 거래 장부를 판단하고 기록
        kafkaProducer.insertTransactionData(1, message);

        if ("S".equals(message.getTrnscSttusCd()) || "F".equals(message.getTrnscSttusCd())) {
            if ((config.getBokCode().equals(message.getFromBankCode()) && config.getBokCode().equals(message.getToBankCode())) ||
                    ((bankCode.equals(message.getFromBankCode()) || "END".equals(message.getFromBankCode()))&& message.getNum() == 0)) {
                updateTransactionComplete(message);
            }

            // Push 메시지 전달
            setPushData.setPushData(message);

            // 바우처 연계 : 결제 거래 성공후 승인정보전달
            if(ObjectUtils.equals(CommandType.T1 , message.getCommand()) && StringUtils.equals(bankCode , message.getFromBankCode())){
                if (StringUtils.equals(TrnscType.PAYMENT.getValue(), message.getTxType())){
                    message.setCommand(CommandType.PR);
                    message.setMessage("3 group:"+group+"  bcGroup:"+bcGroup);
                    message.setApprovalCd(message.getRequestId());
                    kafkaProducer.sendMessage(String.join(",", topicTxRequest), message);

                }else if(StringUtils.equals(TrnscType.ONLINE_PAYMENT.getValue(), message.getTxType())){
                    message.setCommand(CommandType.PF);
                    message.setMessage("4 group:"+group+"  bcGroup:"+bcGroup);
                    message.setApprovalCd(message.getRequestId());
                    kafkaProducer.sendMessage(String.join(",", topicTxRequest), message);
                }
            }



            //[IF-GWS-O-004] 예금토큰 Off Ramp
            // if (StringUtils.equals(TrnscType.CONVERS.getValue(), message.getTxType()) && "S".equals(message.getTrnscSttusCd())){
            //     bridgeService.sendOnOffRampData(message);
            // }


            //[IF-GWS-O-005] 예금토큰 On Ramp 실패 통지
            // "F"이외 "W","H" 인경우 대사처리
            // if (StringUtils.equals(TrnscType.DEPOSIT.getValue(), message.getTxType()) && "F".equals(message.getTrnscSttusCd())){
            //     bridgeService.failureNotification(message);
            // }

            //[IF-GWS-O-008] 예금토큰 처리이력 전송
            // if ( (CommandType.T1 == message.getCommand()) && "S".equals(message.getTrnscSttusCd())){
            //     bridgeService.tokenProcessingHistory(message);
            // }
                        

            //[IF-GWS-O-010] CBDC On/Off Ramp 내역 전송
            //중앙은행에서 CBDC 발행 결과 전달받은 후 실행

            // if(( CommandType.I == message.getCommand() || CommandType.R == message.getCommand() ) && (CoinType.CBDC == message.getCoin())){
            //    bridgeService.offrampHistory(message, CommandType.I == message.getCommand() ? "1" : "2");
            // }

        }

        //SAGA테이블 적재
        if (!"W".equals(message.getTrnscSttusCd())) {
            TxMessage returnMessage = TxMessage.builder()
                    .command(message.getCommand())
                    .txDbId(message.getTxDbId())
                    .txSagaId(message.getTxSagaId())
                    .toBankCode(message.getFromBankCode())
                    .fromBankCode(message.getToBankCode())
                    .coinBankCode(message.getCoinBankCode())
                    .txType(message.getTxType())
                    .personId(message.getPersonId())
                    .amount(message.getAmount())
                    .timestamp(new Date())
                    .acnutno(message.getAcnutno())
                    .fromAcnutno(message.getFromAcnutno())
                    .walletDpstr(message.getWalletDpstr())
                    .fromWalletDpstr(message.getFromWalletDpstr())
                    .aliasNm(message.getAliasNm())
                    .trnscSttusCd(message.getTrnscSttusCd())
                    .txHash(message.getTxHash()).retry(0).tretInstt(bankCode)
                    .build();

            if (config.getBokCode().equals(message.getFromBankCode()) && config.getBokCode().equals(message.getToBankCode())) {
                if (StringUtils.isNotEmpty(message.getTretInstt()) && message.getTretInstt().length() == 3) {

                    returnMessage.setToBankCode(message.getTretInstt());
                    log.debug("Return Message : {}", returnMessage);
                    kafkaTemplate.send(topicTxResponse + "_" + returnMessage.getToBankCode(), returnMessage.getRequestId(), returnMessage);

                }

            } else if (!bankCode.equals(message.getFromBankCode())) {
                // save Transaction information to DB
                returnMessage.setToBankCode("END".equals(message.getFromBankCode()) ? message.getToBankCode()
                        : message.getTretInstt());
                log.debug("Return Message : {}", returnMessage);
                kafkaTemplate.send(topicTxResponse + "_" + returnMessage.getToBankCode(), returnMessage.getRequestId(), returnMessage);

            } else if (!bankCode.equals(message.getTretInstt()) &&
                    StringUtils.isNotEmpty(message.getTretInstt()) && message.getTretInstt().length() == 3) {
                returnMessage.setToBankCode(message.getTretInstt());
                kafkaTemplate.send(topicTxResponse  + "_" + returnMessage.getToBankCode(), returnMessage.getRequestId(), returnMessage);
            } else {
                // 트랜잭션 SAGA 테이블 동기화 상태 변경
                transactionSagaMapper.updateStatus(message.getTxSagaId(),
                        message.getTrnscSttusCd(), message.getTxHash(), message.getTretInstt(), null);
            }
        }

        acknowledgment.acknowledge();

    }

    @RetryableTopic(attempts = "3", backoff = @Backoff(delay = 1000, maxDelay = 5000, multiplier = 2), kafkaTemplate = "kafkaTemplate", dltStrategy = DltStrategy.FAIL_ON_ERROR, listenerContainerFactory = "retryContainerFactory")
    @KafkaListener(id = "txResponse", topics = "${spring.kafka.topicTxResponse}" + "_" + "${config.bank-code}", containerFactory = "kafkaListenerContainerFactory", groupId = "${spring.kafka.group}" )
    public void listenTxResponse(TxMessage message, Acknowledgment acknowledgment) {

        log.debug("txResponse message {} : {}", message.getRequestId(), message.toString());

        if (bankCode.equals(message.getToBankCode())) {

            // 트랜잭션 SAGA 테이블 동기화 상태 변경
            transactionSagaMapper.updateStatus(message.getTxSagaId(),
                    message.getTrnscSttusCd(), message.getTxHash(), message.getTretInstt(), null);

        }

        acknowledgment.acknowledge();

    }

    @DltHandler
    public void handleDltMessge(TxMessage message, @Header(KafkaHeaders.RECEIVED_TOPIC) String topic) {
        log.info("Event dlt topic topic={}, paylod={}", topic, message.toString());

    }


}
```
#### v2: v1에 업무 처리가 추가된 버전
```java
@Slf4j
@Component
public class MessageListener {

    @Autowired
    private KafkaTemplate<String, TxMessage> kafkaTemplate;

    @Value(value = "${spring.kafka.topicTxRequest}")
    public String[] topicTxRequest;

    @Value(value = "${spring.kafka.topicTxResponse}")
    private String topicTxResponse;

    @Value(value = "${config.bank-code}")
    private String bankCode;

    @Value(value = "${spring.kafka.group}")
    public String group;
    @Value(value = "${spring.kafka.bc-group}")
    public String bcGroup;

    private @Autowired TransactionSagaMapper transactionSagaMapper;
    private @Autowired TransactionRecordMapper transactionRecordMapper;
    private @Autowired TransactionMapping transactionMapping;

    private @Autowired SetPushDataService setPushData;
    private @Autowired KafkaProducer kafkaProducer;
    private @Autowired ConfigProperties config;
    private @Autowired TbEwaCstmrMastrMapper tbEwaCstmrMastrMapper;
    private @Autowired GenericMapperService genericMapperService;
    private @Autowired ApiCallHelper apiCallHelper;
    private @Autowired ConfigProperties configProperties;
    private @Autowired WalletMastrEntityMapper tdWalletMastrMapper;
    private @Autowired TbPdmAcnutMastrMapper tbPdmAcnutMastrMapper;
    private @Autowired TbPdmCstmrMastrMapper tbPdmCstmrMastrMapper;
    private @Autowired AliasBanksServiceImpl aliasBanksService;
    private @Autowired EwaDc1IsuMastrMapper ewaDc1IsuMastrMapper;
    private @Autowired EwaDc1RedempMastrEntityMapper ewaDc1RedempMastrEntityMapper;
    private @Autowired InterfaceSend interfaceSend;
    private @Autowired DepositTokenServiceImpl depositTokenServiceImpl;
    private @Autowired BlockChainHelper blockChain;
    private static final ObjectMapper objectMapper = new ObjectMapper();

    public String[] dynamicTopics;

    @PostConstruct
    public void initializeTopics() {
        // 각 원소에 "_${config.bank-code}"를 추가
        dynamicTopics = Arrays.stream(topicTxRequest)
                .map(topic -> topic + "_" + bankCode)
                .toArray(String[]:new);

        log.info("Dynamic Topics Initialized: {}", Arrays.toString(dynamicTopics));
    }    

    private boolean vouchTranSactionData(TxMessage message) {

        switch (message.getCommand()) {
            case PM: //바우처 연계 : 결제 요청
                transactionMapping.setTransactionComplete( message.getCommand(),message.getTxDbId(),message.getPersonId(),"", message);
                return true;
            case TX, TR: //바우처 연계 : 거래번호 생성및 요청
                transactionMapping.setTransactionComplete( message.getCommand(),message.getTxDbId(),message.getPersonId(),"", message);
                return true;
            case PR, PF: // 바우처 연계 승인정보전달 Update 후 종료 , 승인 Update key 'TX_CD' , 결제승인번호는 '리퀘스트ID'
                transactionRecordMapper.updatePr(message);
                return true;
            case RR, RF: // 바우처 연계 환불정보전달 Update 후 종료 , 환불 Update key 'TX_CD' , 환불승인번호는 '리퀘스트ID'
                transactionRecordMapper.updateRr(message);
                return true;
            case CR: // 바우처 연계 캐쉬백정보전달 Update 후 종료 , 캐쉬백 Update key 'TX_CD' , 캐쉬백승인번호는 '리퀘스트ID'
                transactionRecordMapper.updateCr(message);
                return true;
            default:
                return false;
        }
    }

    private Optional<CbsRampResponseDto> parseGatewayResponse(JsonNode response, String errorContext) {
        try {
            return Optional.of(objectMapper.treeToValue(response, CbsRampResponseDto.class));
        } catch (JsonProcessingException e) {
            log.error("계정계 " + errorContext + " 응답[{}] 파싱 에러: {}", response.toPrettyString(), e.getMessage());
            return Optional.empty();
        }
    }

    private boolean checkGWResponse(Optional<CbsRampResponseDto> responseOpt, Runnable errorHandler) {
        if (responseOpt.isPresent()) {
            CbsRampResponseDto response = responseOpt.get();
            String errcode = response.getErrcode();
            if (errcode != null) {
                
                if (errorHandler != null) {
                    errorHandler.run();
                }

                String errmsg = response.getErrusrmsg();
                List<CbsErrorDto> errlist = response.getErrorlist();
                if (errlist != null && !errlist.isEmpty()) {
                    errcode = errlist.get(0).getMsgCd();
                    errmsg = errlist.get(0).getMainMsgTxt();
                }
                log.error("계정계 호출 에러 {} {}", errcode, errmsg);
                return false;
            }
            log.debug("[jkoh] OffRamp step 7 계정계 offRamp 요청 완료");
            return true;
        }
        else {
            errorHandler.run();
            return false;
        }
    }

    public void subtractCustomerBalance(TxMessage message) {
        log.debug("[jkoh] OffRamp step 7-1 계좌 복구(감액 처리)");
        // 계좌 차감 처리 (계좌잔액= 계좌잔액 - 전환입금액, DC1 = DC1잔액 + 전환입금액)
        TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(message.getPersonId());
        BigDecimal trnscAmt = BigDecimal.valueOf(message.getAmount());
        tbCstmrMastr.setAcnutnoBlce(tbCstmrMastr.getAcnutnoBlce().subtract(trnscAmt));

        try {
            // Perform database update
            genericMapperService.updateModel(tbCstmrMastr, TbCstmrMastr.class, TbEwaAcnutMastrMapper.class, "updateBlce");
        } catch (DataAccessException e) {
            log.error("고객 {} 잔액 변경 중 에러가 발생했습니다. 에러 내용: {}", tbCstmrMastr.getCstmrNo(), e.getMessage());
        } catch (Exception e) {
            log.error("고객 {} 잔액 변경 중 에러가 발생했습니다. 에러 내용: {}", tbCstmrMastr.getCstmrNo(), e.getMessage());
        }
    }

    public void updateTransactionComplete(TxMessage message) {
        String messageSttus = "";
        switch (message.getCommand()) {
            case M, I, B, R, M1, M2, D1, D2, I1, I2, R1, R2:
                messageSttus = "S".equals(message.getTrnscSttusCd()) ? "C" : "F";
                break;
            case D:
                messageSttus = "S".equals(message.getTrnscSttusCd()) ? "A" : "F";
                break;
            default:
                messageSttus = "S".equals(message.getTrnscSttusCd()) ? "C" : "F";
                return;
        }
        transactionMapping.setTransactionComplete(message.getCommand(), message.getTxDbId(), message.getPersonId(),
                messageSttus, message);
    }

    private void handleOffRampRecovery(TxMessage message) {
        try {
            // Try to reissue the deposit token using the common logic
            depositTokenServiceImpl.issueDepositTokenOnly(message.getPersonId(), BigDecimal.valueOf(message.getAmount()));
            log.info("계정계 OffRamp 실패 후, TD 재발행(onRamp) 완료 {}", message.getTxDbId());
        } catch (Exception e) {
            log.error("계정계 OffRamp 실패 후, TD 재발행(onRamp) 실패 {}: {}", 
                message.getTxDbId(), e.getMessage());
            // Consider additional error handling or notification
        }
    }
    
    private void performOffRampRecovery(TxMessage message) {
        try {
            subtractCustomerBalance(message);
            handleOffRampRecovery(message);
        } catch (Exception e) {
            log.error("OffRamp 실패 후, 원복 거래 실패: {}", e.getMessage());
        }
    }

    private void quitUser(TbCstmrMastr tbCstmrMastr, TxMessage message, String trnLogKeyVal){
        // step2 분산원장 지갑폐기
        try {
        Checker checker = new Checker();
        checker.setLevel(AccessLevel.personal);
        checker.setHdKeyAccToken(tbCstmrMastr.getHdKeyaccToken());
        checker.setWalletAddress(tbCstmrMastr.getWalletAdres());
        checker.setHdKeyId(tbCstmrMastr.getHdKeyid());
        
        String stopReqId = blockChain.setEoaWalletStatus(checker, WalletStatus.STOP);
        String discardReqId = blockChain.setEoaWalletStatus(checker, WalletStatus.DISCARD);
        Assert.hasLength(stopReqId, "지갑 정보 수정중 오류가 발생 하였습니다.");
        Assert.hasLength(discardReqId, "지갑 정보 수정중 오류가 발생 하였습니다.");
    
        //step4 성공시 지갑폐기정보 저장(지갑삭제, 계좌지갑ID 삭제)
        if(!tbCstmrMastr.getWalletId().isEmpty()){
            Assert.isTrue(1 == tdWalletMastrMapper.updateDeleteAt(tbCstmrMastr.getWalletId()), "지갑삭제 실패.");
        }
        Assert.isTrue(1 == tbPdmAcnutMastrMapper.updateWalletId(TbAcnutMastr.builder().cstmrNo(tbCstmrMastr.getCstmrNo()).walletId("").build()), "지갑삭제 실패.");

        //실증추가 고객 삭제
        Assert.isTrue(1 == tbPdmCstmrMastrMapper.deleteCstmr(tbCstmrMastr.getCstmrNo()),"고객 삭제 실패.");
        //실증추가 계좌 삭제
        Assert.isTrue(1 == tbPdmAcnutMastrMapper.deleteAcnut(tbCstmrMastr.getCstmrNo()),"계좌 삭제 실패.");

        // //step5 간편주소 삭제
        AliasManageModel aliasManageModel = AliasManageModel.builder().trgetInstt(config.getBankCode()).userId(tbCstmrMastr.getCstmrNo()).aliasNm(tbCstmrMastr.getAliasNm()).build();
        aliasBanksService.delete(aliasManageModel);
        } catch (Exception e) {

            BigDecimal trnscAmt = BigDecimal.valueOf(message.getAmount());
            //탈회 계정계 
            InterfaceMap param = new InterfaceMap();
            param.put("dpsAcno", tbCstmrMastr.getAcnutno());
            param.put("trnAm", trnscAmt.toString());
            param.put("canYn", "Y");
            param.put("glblId", trnLogKeyVal);
            interfaceSend.api_E_006_withdraw(param);
        }

    }
    
    @RetryableTopic(attempts = "3", backoff = @Backoff(  delay = 1000, maxDelay = 5000, multiplier = 2), kafkaTemplate = "kafkaTemplate", dltStrategy = DltStrategy.FAIL_ON_ERROR, listenerContainerFactory = "retryContainerFactory")
    @KafkaListener(id = "txRequest", topics = "#{@messageListener.dynamicTopics}", containerFactory = "kafkaListenerContainerFactory", groupId = "${spring.kafka.group}" )
    public void listenTxRequest(TxMessage message, Acknowledgment acknowledgment) throws WalletSdkException, InterruptedException, ExecutionException {

    	// log.info("txRequest message {} : {}", message.getRequestId(), message.toString());
        log.debug("[jkoh] txRequest message {} : {}", message.getRequestId(), message.toString());
        String trnscSttusCd = message.getTrnscSttusCd();
        String trnscType = message.getTxType();

        //바우처 연계
        try {
            if(vouchTranSactionData(message)){
                acknowledgment.acknowledge();
                return;
            }
        }catch (Exception e){
            acknowledgment.acknowledge();
            log.error("바우처 연계정보 DB 수정 에러 vouchTranSactionData: {}", ExceptionUtils.getMessage(e));
            return;
        }

        // 지갑으로 기록할 거래 장부를 판단하고 기록
        kafkaProducer.insertTransactionData(1, message);

        if ("S".equals(trnscSttusCd) || "F".equals(trnscSttusCd)) {
            if ((config.getBokCode().equals(message.getFromBankCode()) && config.getBokCode().equals(message.getToBankCode())) ||
                    ((bankCode.equals(message.getFromBankCode()) || "END".equals(message.getFromBankCode()))&& message.getNum() == 0)) {
                log.debug("[jkoh] call updateTransactionComplete");
                updateTransactionComplete(message);
            }

            try {
                setPushData.setPushData(message);
                log.debug("[jkoh] call setPushData");
            } catch (Exception e) {
                log.error("setPushData error in MessageListener.listenTxRequest: {}", e.getMessage());
            }


            // 바우처 연계 : 결제 거래 성공후 승인정보전달
            if( CommandType.T1 == message.getCommand() && StringUtils.equals(bankCode , message.getFromBankCode())){
                if (StringUtils.equals(TrnscType.PAYMENT.getValue(), message.getTxType())){
                    message.setCommand(CommandType.PR);
                    message.setMessage("3 group:"+group+"  bcGroup:"+bcGroup);
                    message.setApprovalCd(message.getRequestId());
                    kafkaProducer.sendMessage(String.join(",", topicTxRequest), message);

                }else if(StringUtils.equals(TrnscType.ONLINE_PAYMENT.getValue(), message.getTxType())){
                    message.setCommand(CommandType.PF);
                    message.setMessage("4 group:"+group+"  bcGroup:"+bcGroup);
                    message.setApprovalCd(message.getRequestId());
                    kafkaProducer.sendMessage(String.join(",", topicTxRequest), message);
                }
            }

            /*
##### [ GateWay ] [IF-GWS-O-010] CBDC On/Off Ramp 내역 전송
##### 중앙은행에서 CBDC 발행 결과 전달받은 후 실행
##### 
##### pdm > G/W CBDC On-Ramp 내역 전송
##### */
			if ("S".equals(trnscSttusCd)
					&& (CommandType.I == message.getCommand() || CommandType.R == message.getCommand())
					&& (CoinType.CBDC == message.getCoin())) {
				InterfaceMap param = new InterfaceMap();
				param.put("trnDscd", CommandType.I == message.getCommand() ? "01" : "02");
				param.put("trnAm", message.getAmount());
				try {
					interfaceSend.api_E_001(param);
				} catch (Exception e) {
					log.error("api_E_001 call param: {}, error: {}", param, e.getMessage());
				}
			}

            // onRamp 처리
            if (Objects.equals(trnscType, TrnscType.DEPOSIT.getValue())) {
                // 블록체인 거래 성공 -> 로그
                if (trnscSttusCd.equals("S")) {
                    try {
                        TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(message.getPersonId());
                        if (tbCstmrMastr != null) {
                            log.info("계좌({}) 전환 입금(onRamp) 거래 완료", tbCstmrMastr.getAcnutno());
                        } else {
                            log.error("성공한 onRamp 거래지만 DB에서 이 고객 정보({})를 찾을 수 없습니다. 시스템을 점검하십시오.\nMessage: {}", message.getPersonId(), message);
                            acknowledgment.acknowledge();
                            return;
                        }
                    } catch (DataAccessException e) {
                        log.error("고객 정보 조회 데이터베이스 에러: {}", ExceptionUtils.getMessage(e));
                    } catch (Exception e) {
                        log.error("고객 정보 조회 에러 : {}", ExceptionUtils.getMessage(e));
                    }
                    log.debug("[jkoh] OnRamp step 7 onRamp 거래 최종 완료");
                }
                // 블록체인 거래 실패 -> 계좌 차감, 계정계 취소
                else if (trnscSttusCd.equals("F")) {
                    // OnRamp 실패 처리
                    // Step 1. NCP DB 계좌 증액 처리
                    // 계좌 증액 처리 (계좌잔액= 계좌잔액 + 전환입금액, DC1 = DC1잔액 - 전환입금액)
                    log.debug("[jkoh] OnRamp step 7 onRamp 실패");
                    try {
                        try {
                            TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(message.getPersonId());
                            if (tbCstmrMastr == null) {
                                log.error("실패한 onRamp 거래. DB에서 이 고객 정보({})를 찾을 수 없습니다. 시스템을 점검하십시오.\nMessage: {}", message.getPersonId(), message);
                                acknowledgment.acknowledge();
                                return;
                            }
                            BigDecimal trnscAmt = BigDecimal.valueOf(message.getAmount());
                            tbCstmrMastr.setAcnutnoBlce(tbCstmrMastr.getAcnutnoBlce().add(trnscAmt));
                            try {
                                genericMapperService.updateModel(tbCstmrMastr, TbCstmrMastr.class, TbEwaAcnutMastrMapper.class, "updateBlce");
                            } catch (Exception e) {
                                log.error("계좌({}) 증액 처리 에러: {}", tbCstmrMastr.getAcnutno(), e.getMessage());
                            }
                            log.debug("[jkoh] OnRamp step 7-1 계좌 복구(증액 처리)");
                        } catch (DataAccessException e) {
                            log.error("고객 정보 조회 데이터베이스 에러: {}", ExceptionUtils.getMessage(e));
                        } catch (Exception e) {
                            log.error("고객 정보 조회 에러 : {}", ExceptionUtils.getMessage(e));
                        }
                    } catch (DataAccessException e) {
                        // global ID 조회하지 못하면 이후 onRamp 취소 거래를 보낼 수 없다. 그래서 여기서 종료
                        log.error("GlobalID 조회 데이터베이스 에러: {}", ExceptionUtils.getMessage(e));
                        acknowledgment.acknowledge();
                        return;
                    } catch (Exception e) {
                        log.error("GlobalID 조회 에러 : {}", ExceptionUtils.getMessage(e));
                        acknowledgment.acknowledge();
                        return;
                    }

                    // Step 2. 계정계 onRamp 거래 취소 통지
                    // Step 1이 실패해도 계정계 계좌 onRamp 실패 통지는 해야 한다.
                    // 블록체인 거래 실패로 전자지갑으로 돈이 들어가지 않았으므로.
                    String wGuid = null;
                    wGuid = ewaDc1IsuMastrMapper.selectGuid(message.getTxDbId());
                    if (wGuid != null) {
                        HashMap<String, Object> param = new HashMap<>();
                        param.put("internalTxId", "internalTxId");
                        param.put("oriId", wGuid);
                        param.put("customerId", message.getAcnutno());
                        log.debug("[jkoh] onRamp Fail send to CBS: {}", param);
                        JsonNode response = null;
                        try {
                        	String url = apiCallHelper.getGwUrl(configProperties.getGateway().getOnRampFail().getUrl());
                            response = apiCallHelper.callURL(
                            		url,
                            		null,
                            		(new ObjectMapper()).valueToTree(param),
                            		HttpMethod.POST);
                            try {
                                CbsRampResponseDto onRampFailResponse = new ObjectMapper().treeToValue(response, CbsRampResponseDto.class);
                                String errcode = onRampFailResponse.getErrcode();
                                if (errcode != null) {
                                    String errmsg = onRampFailResponse.getErrusrmsg();
                                    List<CbsErrorDto> errlist = onRampFailResponse.getErrorlist();
                                    if (errlist != null && !errlist.isEmpty()) {
                                        errcode = errlist.get(0).getMsgCd();
                                        errmsg = errlist.get(0).getMainMsgTxt();
                                    }
                                    log.error("GlobalID({}) 계정계 호출 에러 {} {}", wGuid, errcode, errmsg);
                                }
                            } catch (JsonProcessingException e) {
                                log.error("GlobalID({}) Json response({}) 파싱 에러: ", wGuid, response.toPrettyString(), e.getMessage());
                            }
                        } catch (ResourceAccessException e) {
                            log.error("onRampFail API timeout or connection error: {}", e.getMessage());
                        } catch (HttpClientErrorException e) {
                            log.error("onRampFail API client error (4xx): Status {}, Response {}", e.getStatusCode(), e.getResponseBodyAsString());
                        } catch (HttpServerErrorException e) {
                            log.error("onRampFail API server error (5xx): Status {}, Response {}", e.getStatusCode(), e.getResponseBodyAsString());
                        } catch (Exception e) {
                            log.error("Unexpected error calling onRampFail API: {}", e.getMessage(), e);
                        }
                        log.debug("[jkoh] OnRamp step 7-2 계정계 거래 취소 요청 완료");
                    }
                    else {
                        log.error("{}값에 대응되는 키값이 DB에 없어서 계정계에 취소 거래를 보낼 수 없습니다.", message.getTxDbId());
                    }
                }
            }
            // offRamp 처리
            else if (Objects.equals(trnscType, TrnscType.CONVERS.getValue())) {
                // 블록체인 거래 성공 -> 계정계 offRamp 전송 및 에러 처리
                if (trnscSttusCd.equals("S")) {
                    Optional<CbsRampResponseDto> offRampResponse = null;
                    TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(message.getPersonId());
                    if (tbCstmrMastr == null) {
                        log.error("성공한 offRamp 거래지만 DB에서 이 고객 정보({})를 찾을 수 없습니다. 시스템을 점검하십시오.\nMessage: {}", message.getPersonId(), message);
                        acknowledgment.acknowledge();
                    }
                    BigDecimal trnscAmt = BigDecimal.valueOf(message.getAmount());

                    // step 7 계정계 입금 요청 Gateway 호출
                    GwRampDto paramOffRamp = depositTokenServiceImpl.createRampParams("internalTxId"
                                                            , tbCstmrMastr
                                                            , trnscAmt
                                                            , BigInteger.valueOf(message.getFromTrnscAfterBlce()).add(trnscAmt.toBigInteger()));
                    JsonNode respOffRamp = null;
                    try {
                    	String url = apiCallHelper.getGwUrl(configProperties.getGateway().getOffRamp().getUrl());
                        respOffRamp = apiCallHelper.callURL(
                        		url,
                        		null,
                        		objectMapper.valueToTree(paramOffRamp),
                        		HttpMethod.POST);
                        offRampResponse = parseGatewayResponse(respOffRamp, "offRamp");
                        if (checkGWResponse(offRampResponse, () -> performOffRampRecovery(message))) {
                            CbsRampResponseDto responseDto = offRampResponse.get();
                            Dc1RedempMastr dc1RedempMastrUpdate = Dc1RedempMastr.builder()
                                                            .dc1RedempId(message.getTxDbId())
                                                            .cbsTrnAcno(responseDto.getDpsInpAcno())
                                                            .cbsTrnDt(responseDto.getTrnDt())
                                                            .mcaGuid(responseDto.getTrnLogKeyVal())
                                                            .cbsTrnSrno(responseDto.getTrnSrno())
                                                            .build();

                            try {
                                genericMapperService.updateModel(dc1RedempMastrUpdate, Dc1RedempMastr.class, EwaDc1RedempMastrMapper.class, "update");
                            } catch (Exception e) {
                                log.error("계좌({}) 거래키({}) 거래일련번호({})에 대한 예금토큰 환수 내역 갱신(계정계 응답 데이터) 에러: {}", tbCstmrMastr.getAcnutno(), responseDto.getTrnLogKeyVal(), responseDto.getTrnSrno(), e.getMessage());
                                log.error("계좌({}) 예금토큰 환수 내역 저장 에러: {}", tbCstmrMastr.getAcnutno(), e.getMessage());
                            }
                        }
                    } catch (ResourceAccessException e) {
                        performOffRampRecovery(message);
                        log.error("OffRamp API timeout or connection error: {}", e.getMessage());
                    } catch (HttpClientErrorException e) {
                        performOffRampRecovery(message);
                        log.error("OffRamp API client error (4xx): Status {}, Response {}", e.getStatusCode(), e.getResponseBodyAsString());
                    } catch (HttpServerErrorException e) {
                        performOffRampRecovery(message);
                        log.error("OffRamp API server error (5xx): Status {}, Response {}", e.getStatusCode(), e.getResponseBodyAsString());
                    } catch (Exception e) {
                        performOffRampRecovery(message);
                        log.error("Unexpected error calling OffRamp API: {}", e.getMessage(), e);
                    }
                }
                // 블록체인 거래 실패 -> 계좌 차감 
                else if (trnscSttusCd.equals("F")) {
                    subtractCustomerBalance(message);
                }
            }
            // 탈회 처리
             else if (Objects.equals(trnscType, TrnscType.QUIT.getValue())) {

                // 블록체인 거래 성공 -> 계정계 offRamp 전송 및 에러 처리
                if (trnscSttusCd.equals("S")) {
                    Optional<CbsRampResponseDto> offRampResponse = null;
                    TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(message.getPersonId());
                    BigDecimal trnscAmt = BigDecimal.valueOf(message.getAmount());
                    String cusDsCd = Objects.toString(tdWalletMastrMapper.selectCusDsCd(tbCstmrMastr.getCstmrNo()),"00");

                    try {
                        // 압류/파산/개인회생 , 금액이 0원이 아닌경우 off ramp만 처리
                        if(cusDsCd.equals("02") || cusDsCd.equals("03") || cusDsCd.equals("04") ){
                             // step 7 계정계 입금 요청 Gateway 호출
                            GwRampDto paramOffRamp = depositTokenServiceImpl.createRampParams("internalTxId"
                            , tbCstmrMastr
                            , trnscAmt
                            , BigInteger.valueOf(message.getFromTrnscAfterBlce()).add(trnscAmt.toBigInteger()));
                            JsonNode respOffRamp = null;

                            String url = apiCallHelper.getGwUrl(configProperties.getGateway().getOffRamp().getUrl());
                            respOffRamp = apiCallHelper.callURL(
                            		url,
                            		null,
                            		objectMapper.valueToTree(paramOffRamp),
                            		HttpMethod.POST);
                            offRampResponse = parseGatewayResponse(respOffRamp, "offRamp");
                            checkGWResponse(offRampResponse, () -> performOffRampRecovery(message));
                        
                        }else{
                            //탈회 계정계 
                            InterfaceMap param = new InterfaceMap();
                            param.put("dpsAcno", tbCstmrMastr.getAcnutno());
                            param.put("trnAm", trnscAmt.toString());
                            param.put("canYn", "N");
                            InterfaceMap result =null;
                            result = interfaceSend.api_E_006_withdraw(param);
                            offRampResponse = parseGatewayResponse(new ObjectMapper().valueToTree(result), "offRamp Q");
                            checkGWResponse(offRampResponse, () -> performOffRampRecovery(message));
                        }

                        CbsRampResponseDto responseDto = offRampResponse.get();

                        // 계정계 성공시 or (압류,파산,개인회생 금액 0원일 경우)
                        if(responseDto.getErrcode() == null ) {
                            Dc1RedempMastr dc1RedempMastrUpdate = Dc1RedempMastr.builder()
                                                            .dc1RedempId(message.getTxDbId())
                                                            .cbsTrnAcno(responseDto.getDpsInpAcno())
                                                            .cbsTrnDt(responseDto.getTrnDt())
                                                            .mcaGuid(responseDto.getTrnLogKeyVal())
                                                            .cbsTrnSrno(responseDto.getTrnSrno())
                                                            .build();
                            
                            try {
                                genericMapperService.updateModel(dc1RedempMastrUpdate, Dc1RedempMastr.class, EwaDc1RedempMastrMapper.class, "update");
                                String trnLogKeyVal = responseDto.getTrnLogKeyVal();
                                //사망/압류자 처리 여부 추가
                                if(message.getOrderNo().equals("ded")){
                                    tdWalletMastrMapper.checkPrcUser(tbCstmrMastr.getCstmrNo());
                                    if(cusDsCd.equals("01")){
                                        quitUser(tbCstmrMastr, message, trnLogKeyVal );
                                    }
                                }else{
                                    quitUser(tbCstmrMastr, message, trnLogKeyVal);
                                }
        
                            } catch (Exception e) {
                                log.error("계좌({}) 거래키({}) 거래일련번호({})에 대한 예금토큰 환수 내역 갱신(계정계 응답 데이터) 에러: {}", tbCstmrMastr.getAcnutno(), responseDto.getTrnLogKeyVal(), responseDto.getTrnSrno(), e.getMessage());
                                log.error("계좌({}) 예금토큰 환수 내역 저장 에러: {}", tbCstmrMastr.getAcnutno(), e.getMessage());
                            }
                        }
                    } catch (ResourceAccessException e) {
                        performOffRampRecovery(message);
                        log.error("OffRamp Q API timeout or connection error: {}", e.getMessage());
                    } catch (HttpClientErrorException e) {
                        performOffRampRecovery(message);
                        log.error("OffRamp Q API client error (4xx): Status {}, Response {}", e.getStatusCode(), e.getResponseBodyAsString());
                    } catch (HttpServerErrorException e) {
                        performOffRampRecovery(message);
                        log.error("OffRamp Q API server error (5xx): Status {}, Response {}", e.getStatusCode(), e.getResponseBodyAsString());
                    } catch (Exception e) {
                        performOffRampRecovery(message);
                        log.error("Unexpected error calling OffRamp Q API: {}", e.getMessage(), e);
                    }

                }
                // 블록체인 거래 실패 -> 계좌 차감 
                else if (trnscSttusCd.equals("F")) {
                    subtractCustomerBalance(message);
                }
            }
        }
        else if (trnscSttusCd.equals("R")) {
            log.debug("[jkoh] trnscSttusCd is R. Decide what to do.");
            // TODO jkoh 블록체인 호출할 때 실패하면 trnscSttusCd를 'R'로 설정하는데 실제 R이 오는지 확인
            // 여기서 특별히 할 일은? 
        }

        //SAGA테이블 적재
        if (!"W".equals(trnscSttusCd)) {
            TxMessage returnMessage = TxMessage.builder()
                    .command(message.getCommand())
                    .txDbId(message.getTxDbId())
                    .txSagaId(message.getTxSagaId())
                    .toBankCode(message.getFromBankCode())
                    .fromBankCode(message.getToBankCode())
                    .coinBankCode(message.getCoinBankCode())
                    .txType(message.getTxType())
                    .personId(message.getPersonId())
                    .amount(message.getAmount())
                    .timestamp(new Date())
                    .acnutno(message.getAcnutno())
                    .fromAcnutno(message.getFromAcnutno())
                    .walletDpstr(message.getWalletDpstr())
                    .fromWalletDpstr(message.getFromWalletDpstr())
                    .aliasNm(message.getAliasNm())
                    .trnscSttusCd(message.getTrnscSttusCd())
                    .txHash(message.getTxHash()).retry(0).tretInstt(bankCode)
                    .build();

            if (config.getBokCode().equals(message.getFromBankCode()) && config.getBokCode().equals(message.getToBankCode())) {
                if (StringUtils.isNotEmpty(message.getTretInstt()) && message.getTretInstt().length() == 3) {

                    returnMessage.setToBankCode(message.getTretInstt());
                    log.debug("[jkoh] TretInstt not empty Return Message : {}", returnMessage);
                    kafkaTemplate.send(topicTxResponse + "_" + returnMessage.getToBankCode(), returnMessage.getRequestId(), returnMessage);

                }

            } else if (!bankCode.equals(message.getFromBankCode())) {
                // save Transaction information to DB
                returnMessage.setToBankCode("END".equals(message.getFromBankCode()) ? message.getToBankCode()
                        : message.getTretInstt());
                log.debug("[jkoh] Return Message to other bank: {}", returnMessage);
                kafkaTemplate.send(topicTxResponse + "_" + returnMessage.getToBankCode(), returnMessage.getRequestId(), returnMessage);

            } else if (!bankCode.equals(message.getTretInstt()) &&
                    StringUtils.isNotEmpty(message.getTretInstt()) && message.getTretInstt().length() == 3) {
                returnMessage.setToBankCode(message.getTretInstt());
                log.debug("[jkoh] Last Return Message : {}", returnMessage);
                kafkaTemplate.send(topicTxResponse  + "_" + returnMessage.getToBankCode(), returnMessage.getRequestId(), returnMessage);
            } else {
                // 트랜잭션 SAGA 테이블 동기화 상태 변경
                log.debug("[jkoh] Just update saga table?");
                transactionSagaMapper.updateStatus(message.getTxSagaId(),
                        message.getTrnscSttusCd(), message.getTxHash(), message.getTretInstt(), null);
            }
        }

        acknowledgment.acknowledge();

    }

    @RetryableTopic(attempts = "3", backoff = @Backoff(delay = 1000, maxDelay = 5000, multiplier = 2), kafkaTemplate = "kafkaTemplate", dltStrategy = DltStrategy.FAIL_ON_ERROR, listenerContainerFactory = "retryContainerFactory")
    @KafkaListener(id = "txResponse", topics = "${spring.kafka.topicTxResponse}" + "_" + "${config.bank-code}", containerFactory = "kafkaListenerContainerFactory", groupId = "${spring.kafka.group}" )
    public void listenTxResponse(TxMessage message, Acknowledgment acknowledgment) {

        log.debug("[jkoh] txResponse message {} : {}", message.getRequestId(), message.toString());

        if (bankCode.equals(message.getToBankCode())) {

            // 트랜잭션 SAGA 테이블 동기화 상태 변경
            try {
                transactionSagaMapper.updateStatus(message.getTxSagaId(),
                        message.getTrnscSttusCd(), message.getTxHash(), message.getTretInstt(), null);
            } catch (Exception e) {
                log.error("transactionSagaMapper.updateStatus error: {}", e.getMessage());
            }

        }

        acknowledgment.acknowledge();

    }

    @DltHandler
    public void handleDltMessge(TxMessage message, @Header(KafkaHeaders.RECEIVED_TOPIC) String topic) {
        log.info("Event dlt topic topic={}, paylod={}", topic, message.toString());

    }
}

```
#### v3: 구조가 완전히 바뀐 버전
```java
package kr.or.cbdc.infrastructure.queue;

import kr.or.bok.wallet.sdk.errorhandling.WalletSdkException;
import kr.or.cbdc.application.common.bridge.service.BridgeServiceInterface;
import kr.or.cbdc.config.props.ConfigProperties;
import kr.or.cbdc.domain.main.mapper.transaction.OutboxMapper;
import kr.or.cbdc.domain.main.mapper.transaction.TransactionRecordMapper;
import kr.or.cbdc.domain.main.mapper.transaction.TransactionSagaMapper;
import kr.or.cbdc.domain.main.service.push.SetPushDataService;

import kr.or.cbdc.interfaces.blockchain.CoinType;
import kr.or.cbdc.interfaces.blockchain.CommandType;
import kr.or.cbdc.interfaces.blockchain.TransactionMapping;
import kr.or.cbdc.interfaces.blockchain.TrnscType;
import lombok.extern.slf4j.Slf4j;

import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.exception.ExceptionUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.kafka.annotation.DltHandler;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.annotation.RetryableTopic;

import org.springframework.kafka.core.KafkaOperations;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.retrytopic.DltStrategy;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.kafka.support.KafkaHeaders;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.retry.annotation.Backoff;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.event.TransactionPhase;
import org.springframework.transaction.event.TransactionalEventListener;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.Arrays;
import java.util.Date;
import java.util.concurrent.ExecutionException;

import jakarta.annotation.PostConstruct;

@Slf4j
@Component
public class MessageListener {

    @Autowired
    private KafkaTemplate<String, TxMessage> kafkaTemplate;

    @Value(value = "${spring.kafka.topicTxRequest}")
    public String[] topicTxRequest;

    @Value(value = "${spring.kafka.topicTxResponse}")
    private String topicTxResponse;

    @Value(value = "${config.bank-code}")
    private String bankCode;

    @Value(value = "${spring.kafka.group}")
    public String group;
    @Value(value = "${spring.kafka.bc-group}")
    public String bcGroup;

    private @Autowired ApplicationEventPublisher eventPublisher;
    private @Autowired TransactionSagaMapper transactionSagaMapper;
    private @Autowired TransactionRecordMapper transactionRecordMapper;
    private @Autowired TransactionMapping transactionMapping;

    private @Autowired SetPushDataService setPushData;
    private @Autowired KafkaProducer kafkaProducer;
    private @Autowired ConfigProperties config;
    // For gateway
    private @Autowired BridgeServiceInterface bridgeService;
    private @Autowired ObjectMapper objectMapper;
    private @Autowired OutboxMapper outboxMapper;

    public static String[] dynamicTopics;

    @PostConstruct
    public void initializeTopics() {
        // 각 원소에 "_${config.bank-code}"를 추가
        dynamicTopics = Arrays.stream(topicTxRequest)
                .map(topic -> topic + "_" + bankCode)
                .toArray(String[]:new);

        log.info("Dynamic Topics Initialized: {}", Arrays.toString(dynamicTopics));
    }

    public static String[] computeTopics(String nonfinalTopics, String bankCode) {
        return Arrays.stream(nonfinalTopics.split(","))
                     .map(topic -> topic.trim() + "_" + bankCode)
                     .toArray(String[]::new);
    }

    private boolean vouchTranSactionData(TxMessage message) {

        switch (message.getCommand()) {
            case PM: // 바우처 연계 : 결제 요청
                transactionMapping.setTransactionComplete(message.getCommand(), message.getTxDbId(),
                        message.getPersonId(), "", message);
                return true;
            case TX, TR: // 바우처 연계 : 거래번호 생성및 요청
                transactionMapping.setTransactionComplete(message.getCommand(), message.getTxDbId(),
                        message.getPersonId(), "", message);
                return true;
            case PR, PF: // 바우처 연계 승인정보전달 Update 후 종료 , 승인 Update key 'TX_CD' , 결제승인번호는 '리퀘스트ID'
                transactionRecordMapper.updatePr(message);
                return true;
            case RR, RF: // 바우처 연계 환불정보전달 Update 후 종료 , 환불 Update key 'TX_CD' , 환불승인번호는 '리퀘스트ID'
                transactionRecordMapper.updateRr(message);
                return true;
            case CR: // 바우처 연계 캐쉬백정보전달 Update 후 종료 , 캐쉬백 Update key 'TX_CD' , 캐쉬백승인번호는 '리퀘스트ID'
                transactionRecordMapper.updateCr(message);
                return true;
            default:
                return false;
        }
    }

    public void updateTransactionComplete(TxMessage message) {
        String messageSttus = "";
        switch (message.getCommand()) {
            case M, I, B, R, M1, M2, D1, D2, I1, I2, R1, R2:
                messageSttus = "S".equals(message.getTrnscSttusCd()) ? "C" : "F";
                break;
            case D:
                messageSttus = "S".equals(message.getTrnscSttusCd()) ? "A" : "F";
                break;
            default:
                messageSttus = "S".equals(message.getTrnscSttusCd()) ? "C" : "F";
                return;
        }
        transactionMapping.setTransactionComplete(message.getCommand(), message.getTxDbId(), message.getPersonId(),
                messageSttus, message);
    }

    @Transactional
    @RetryableTopic(attempts = "3", backoff = @Backoff(delay = 1000, maxDelay = 5000, multiplier = 2), kafkaTemplate = "nonTransactionalKafkaTemplate", dltStrategy = DltStrategy.FAIL_ON_ERROR, listenerContainerFactory = "retryContainerFactory")
    @KafkaListener(id = "txRequest", topics = "#{T(kr.or.cbdc.infrastructure.queue.MessageListener).computeTopics('${spring.kafka.topicTxRequest}', '${config.bank-code}')}", containerFactory = "kafkaListenerContainerFactory", groupId = "${spring.kafka.group}")
    public void listenTxRequest(TxMessage message, Acknowledgment acknowledgment)
            throws WalletSdkException, InterruptedException, ExecutionException {

        log.trace("txRequest message {} : {}", message.getRequestId(), message.toString());

        // 바우처 연계
        try {
            if (vouchTranSactionData(message)) {
                acknowledgment.acknowledge();
                return;
            }
        } catch (Exception e) {
            acknowledgment.acknowledge();
            log.error("vouchTranSactionData: {}", ExceptionUtils.getMessage(e), e);
            return;
        }

        // 지갑으로 기록할 거래 장부를 판단하고 기록
        kafkaProducer.insertTransactionData(1, message);

        if ("S".equals(message.getTrnscSttusCd()) || "F".equals(message.getTrnscSttusCd())) {
            if ((config.getBokCode().equals(message.getFromBankCode())
                    && config.getBokCode().equals(message.getToBankCode())) ||
                    ((bankCode.equals(message.getFromBankCode()) || "END".equals(message.getFromBankCode()))
                            && message.getNum() == 0)) {
                updateTransactionComplete(message);
            }

            // Push 메시지 전달
            setPushData.setPushData(message);

        }

        // 트랜잭션 SAGA 테이블 동기화 상태 변경
        if (bankCode.equals(message.getFromBankCode()) &&
                (bankCode.equals(message.getToBankCode()) ||
                        (StringUtils.isEmpty(message.getTretInstt()) || message.getTretInstt().length() != 3))) {

            transactionSagaMapper.updateStatus(message.getTxSagaId(),
                    message.getTrnscSttusCd(), message.getTxHash(), message.getTretInstt(),
                    null);
        }

        eventPublisher.publishEvent(message);

        acknowledgment.acknowledge();

    }

    private void updateResult(StringBuilder result,int index, String newValue) {
        if (index >= 0 && index < result.length()) {
            result.setCharAt(index, newValue.charAt(0));
        }
    }

    @TransactionalEventListener(phase = TransactionPhase.BEFORE_COMMIT)
    public void outBoxBankLegacyEvent(TxMessage message) throws WalletSdkException, JsonProcessingException {
        // save message to outbox
        String jsonBody = objectMapper.writeValueAsString(message);
        // OUTBOX_ID는 18자리로 UUID 사용
        // MyBatis를 통한 DB 저장
        outboxMapper.insert(message.getTxSagaId(), jsonBody);

    }

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void sendBankLegacyEvent(TxMessage message)
            throws WalletSdkException, InterruptedException, ExecutionException {
        

        kafkaTemplate.executeInTransaction(kafkaOperations -> {
            StringBuilder result = new StringBuilder("FFF");
            try {
                updateResult(result, 0,sendBridgeService(message));
                sendSagaStateSyncMessage(message, kafkaOperations);
                sendVoucherMessage(message, kafkaOperations);
                updateResult(result, 1,"S");
                if ("S".equals(message.getTrnscSttusCd()) || "F".equals(message.getTrnscSttusCd())) {
                    
                    // [IF-GWS-O-008] 예금토큰 처리이력 전송
                    // 1) 전환입금 txType == TrnscType.DEPOSIT
                    // 2) 결제 command == T1
                    if ((StringUtils.equals(TrnscType.DEPOSIT.getValue(), message.getTxType())
                            || CommandType.T1 == message.getCommand()) && "S".equals(message.getTrnscSttusCd())) {
                        // bridgeService.tokenProcessingHistory(message);
                        // updateResult(result, 2,"S");  //  성공시

                    }

                    // [IF-GWS-O-010] CBDC On/Off Ramp 내역 전송
                    // 중앙은행에서 CBDC 발행 결과 전달받은 후 실행

                    if ((CommandType.I == message.getCommand() || CommandType.R == message.getCommand())
                            && (CoinType.CBDC == message.getCoin())) {
                        // bridgeService.offrampHistory(message, CommandType.I == message.getCommand() ? "1" : "2");
                        // updateResult(result, 2,"S");  //  성공시

                    }

                }

                outboxMapper.update(message.getTxSagaId(), result.toString());
                return true;
            } catch (Exception ex) {
                outboxMapper.update(message.getTxSagaId(), result.toString());

                // Kafka 트랜잭션 내에서 발생한 모든 예외는 여기서 감싸져서 전파되면 rollback 처리됨
                throw new RuntimeException("Error in Kafka transaction, rolling back", ex);
            }
        });

    }

    private String sendBridgeService(TxMessage message) {

        if ("S".equals(message.getTrnscSttusCd()) || "F".equals(message.getTrnscSttusCd())) {

            // [IF-GWS-O-004] 예금토큰 Off Ramp
            if (StringUtils.equals(TrnscType.CONVERS.getValue(), message.getTxType())
                    && "S".equals(message.getTrnscSttusCd())) {
                // bridgeService.sendOnOffRampData(message);
            }

            // [IF-GWS-O-005] 예금토큰 On Ramp 실패 통지
            // "F"이외 "W","H" 인경우 대사처리
            if (StringUtils.equals(TrnscType.DEPOSIT.getValue(), message.getTxType())
                    && "F".equals(message.getTrnscSttusCd())) {
                // bridgeService.failureNotification(message);
            }
 
        }        
        return "S"; // "S" : 성공 , "P" : 패스  "F" : 실패시
    }

    private void sendSagaStateSyncMessage(TxMessage message, KafkaOperations<String, TxMessage> kafkaOperations) {

        if (!"W".equals(message.getTrnscSttusCd())) {
            TxMessage returnMessage = TxMessage.builder()
                    .command(message.getCommand())
                    .txDbId(message.getTxDbId())
                    .txSagaId(message.getTxSagaId())
                    .toBankCode(message.getFromBankCode())
                    .fromBankCode(message.getToBankCode())
                    .coinBankCode(message.getCoinBankCode())
                    .txType(message.getTxType())
                    .personId(message.getPersonId())
                    .amount(message.getAmount())
                    .timestamp(new Date())
                    .acnutno(message.getAcnutno())
                    .fromAcnutno(message.getFromAcnutno())
                    .walletDpstr(message.getWalletDpstr())
                    .fromWalletDpstr(message.getFromWalletDpstr())
                    .aliasNm(message.getAliasNm())
                    .trnscSttusCd(message.getTrnscSttusCd())
                    .requestId(message.getRequestId())
                    .txHash(message.getTxHash()).retry(0).tretInstt(bankCode)
                    .build();

            if (config.getBokCode().equals(message.getFromBankCode())
                    && config.getBokCode().equals(message.getToBankCode())) {
                if (StringUtils.isNotEmpty(message.getTretInstt()) && message.getTretInstt().length() == 3) {

                    returnMessage.setToBankCode(message.getTretInstt());
                    log.debug("Return Message : {}", returnMessage);
                    kafkaOperations.send(topicTxResponse + "_" + returnMessage.getToBankCode(),
                            returnMessage.getRequestId(), returnMessage);

                }

            } else if (!bankCode.equals(message.getFromBankCode())) {
                // save Transaction information to DB
                returnMessage.setToBankCode("END".equals(message.getFromBankCode()) ? message.getToBankCode()
                        : message.getTretInstt());
                log.debug("Return Message : {}", returnMessage);
                kafkaOperations.send(topicTxResponse + "_" + returnMessage.getToBankCode(),
                        returnMessage.getRequestId(), returnMessage);

            } else if (!bankCode.equals(message.getTretInstt()) &&
                    StringUtils.isNotEmpty(message.getTretInstt()) && message.getTretInstt().length() == 3) {
                returnMessage.setToBankCode(message.getTretInstt());
                kafkaOperations.send(topicTxResponse + "_" + returnMessage.getToBankCode(),
                        returnMessage.getRequestId(), returnMessage);
            }
        }

    }

    private void sendVoucherMessage(TxMessage message, KafkaOperations<String, TxMessage> kafkaOperations)
            throws InterruptedException, ExecutionException, WalletSdkException {
        // 바우처 연계 : 결제 거래 성공후 승인정보전달
        if ("S".equals(message.getTrnscSttusCd()) || "F".equals(message.getTrnscSttusCd())) {
            if (StringUtils.equals(TrnscType.PAYMENT.getValue(), message.getTxType())) {
                message.setCommand(CommandType.PR);
                message.setMessage("3 group:" + group + "  bcGroup:" + bcGroup);
                message.setApprovalCd(message.getRequestId());
                kafkaProducer.sendMessage(String.join(",", topicTxRequest), message, kafkaOperations);
            } else if (StringUtils.equals(TrnscType.ONLINE_PAYMENT.getValue(), message.getTxType())) {
                message.setCommand(CommandType.PF);
                message.setMessage("4 group:" + group + "  bcGroup:" + bcGroup);
                message.setApprovalCd(message.getRequestId());
                kafkaProducer.sendMessage(String.join(",", topicTxRequest), message, kafkaOperations);
            }
        }

    }

    @RetryableTopic(attempts = "3", backoff = @Backoff(delay = 1000, maxDelay = 5000, multiplier = 2), kafkaTemplate = "kafkaTemplate", dltStrategy = DltStrategy.FAIL_ON_ERROR, listenerContainerFactory = "retryContainerFactory")
    @KafkaListener(id = "txResponse", topics = "${spring.kafka.topicTxResponse}" + "_"
            + "${config.bank-code}", containerFactory = "kafkaListenerContainerFactory", groupId = "${spring.kafka.group}")
    public void listenTxResponse(TxMessage message, Acknowledgment acknowledgment) {

        log.debug("txResponse message {} : {}", message.getRequestId(), message.toString());

        if (bankCode.equals(message.getToBankCode())) {

            // 트랜잭션 SAGA 테이블 동기화 상태 변경
            transactionSagaMapper.updateStatus(message.getTxSagaId(),
                    message.getTrnscSttusCd(), message.getTxHash(), message.getTretInstt(), null);

        }

        acknowledgment.acknowledge();

    }

    @DltHandler
    @Transactional
    public void handleDltMessge(TxMessage message, @Header(KafkaHeaders.RECEIVED_TOPIC) String dltTopic)
            throws WalletSdkException, InterruptedException, ExecutionException {
        log.info("Event dlt topic topic={}, paylod={}", dltTopic, message.toString());
        String originalTopic = dltTopic.replace("-dlt", "");

        if (Arrays.asList(dynamicTopics).contains(originalTopic)) {
            sendBankLegacyEvent(message);
        }

    }

}
```
#### v2에 있는 업무 처리를 v3에 적용한 것은 소스 디렉토리에
#### 순서도
![[100. media/image/gIo9Liz4Mj.png]]
### Kafka 활용과 Saga pattern
#### 질문: kafka 활용 개론
##### KafkaProducer.lava - A custom class responsible for
##### Sending messages to Kafka topics
##### Managing transaction sagas (coordinating distributed transactions)
##### Generating unique request IDs
##### Storing transaction states
```java
package kr.or.cbdc.infrastructure.queue;

import kr.or.bok.wallet.sdk.errorhandling.WalletSdkException;
import kr.or.cbdc.config.props.ConfigProperties;
import kr.or.cbdc.domain.main.mapper.transaction.TransactionMirrorRecordMapper;
import kr.or.cbdc.domain.main.mapper.transaction.TransactionRecordMapper;
import kr.or.cbdc.domain.main.mapper.transaction.TransactionSagaMapper;
import kr.or.cbdc.domain.main.model.transaction.TransactionRecord;
import kr.or.cbdc.domain.main.model.transaction.TransactionSaga;
import kr.or.cbdc.domain.main.service.push.SetPushDataService;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.ErrorAssert;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.ErrorCode;
import kr.or.cbdc.infrastructure.framework.web.support.codedata.CodeDataUtil;
import kr.or.cbdc.interfaces.TxRequestId;
import kr.or.cbdc.interfaces.TxRequestManaged;
import kr.or.cbdc.interfaces.TxRequestManaged;
import kr.or.cbdc.interfaces.blockchain.AccessLevel;
import kr.or.cbdc.interfaces.blockchain.TransactionMapping;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import org.apache.commons.lang3.exception.ExceptionUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.dao.DataAccessException;
import org.springframework.kafka.core.KafkaOperations;
import org.springframework.kafka.core.KafkaOperations.OperationsCallback;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.support.SendResult;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

import java.util.Arrays;
import java.util.Date;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.ExecutionException;

@Slf4j
@Component
@RequiredArgsConstructor
public class KafkaProducer {

    private final KafkaTemplate<String, TxMessage> kafkaTemplate;
    private final TransactionSagaMapper transactionSagaMapper;
    private final ConfigProperties config;
    private final TransactionRecordMapper transactionRecordMapper;
    private final TransactionMirrorRecordMapper transactionMirrorRecordrMapper;
    private final TxRequestId txRequestId;

    @Value(value = "${spring.kafka.code}")
    private String prefixRequestId;

    @Value("${spring.profiles.active}")
    private String activeProfile;

    private final String GATE_WAY = "G";
    private final String BLOCK_CHAIN = "B";

    // 은행코드3자리 + 지갑타입 1자리 + 구분자 1자리 + UUID ( -제외 )

    // 구분자 1 자리
    // G : 은행과의 게이트웨이 Tx
    // B : 블록체인과의 Tx

    @TxRequestManaged
    public String generateRequestId(String prefix, AccessLevel walletType) {
        ErrorAssert.hasLength(walletType.name(), ErrorCode.WALL_TYPE_ERROR);
        txRequestId.setValue(prefix + walletType.name().substring(0, 1).toUpperCase() + BLOCK_CHAIN
                + UUID.randomUUID().toString().replace("-", ""));
        return txRequestId.getValue();
    }

    public String generateGateWayRequestId(String prefix) {
        return prefix + "X" + GATE_WAY + UUID.randomUUID().toString().replace("-", "");
    }

    @Transactional
    public void send(String topic, List<TxMessage> messages)
            throws InterruptedException, ExecutionException, WalletSdkException {

        for (TxMessage message : messages) {
            sendMessage(topic, message);
        }

    }

    public void send(String topic, List<TxMessage> messages, KafkaOperations<String, TxMessage> operations)
            throws InterruptedException, ExecutionException, WalletSdkException {

        for (TxMessage message : messages) {
            sendMessage(topic, message, operations);
        }

    }

    public String setSaga(List<TxMessage> messages) {

        return setSaga(messages, AccessLevel.central);

    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public String setSaga(List<TxMessage> messages, AccessLevel walletType) {

        int num = 1;
        boolean isFirst = false;
        String requestId = generateRequestId(prefixRequestId, walletType);
        for (TxMessage message : messages) {

            // 트랜잭션 SAGA 테이블 동기화 상태 변경
            TransactionSaga txSaga = TransactionSaga.builder().fromAdres(message.getFrom())
                    .toAdres(message.getTo())
                    .fromInstt(message.getFromBankCode())
                    .toInstt(message.getToBankCode())
                    .trnscAmt(message.getAmount())
                    .trnscHash(message.getTxHash())
                    .trnscDbId(message.getTxDbId())
                    .trnscSttus("W")
                    .aliasNm(message.getAliasNm())
                    .sagaGrupId(requestId)
                    .trnscTypeSe(message.getCommand().name())
                    .build().newId();

            transactionSagaMapper.insert(txSaga);
            message.setTxSagaId(txSaga.getTrnscId());
            message.setRequestId(requestId);
            if (!isFirst && config.getBankCode().equals(message.getFromBankCode())) {
                message.setNum(0);
                isFirst = true;
            } else {
                message.setNum(num);
                num++;
            }
            log.debug("=setSaga========> {}" + message.toString());

        }

        return requestId;

    }

    public void sendMessage(String topic, TxMessage message, KafkaOperations<String, TxMessage> operations)
            throws InterruptedException, ExecutionException, WalletSdkException {

        String selectedTopic = Arrays.stream(topic.split(","))
                .reduce((s1, s2) -> activeProfile.contains("ewa") ? (s1.length() > s2.length() ? s1 : s2)
                        : (s1.length() <= s2.length() ? s1 : s2))
                .orElse(""); // 배열이 비어 있을 경우 빈 문자열 반환

        // fromBankCode와 toBankCode가 동일한 경우 하나의 전송만 처리
        if (message.getFromBankCode().equals(message.getToBankCode())) {
            sendToTopicIfValid(selectedTopic, message, message.getFromBankCode(), operations);
        } else {
            sendToTopicIfValid(selectedTopic, message, message.getFromBankCode(), operations);
            sendToTopicIfValid(selectedTopic, message, message.getToBankCode(), operations);
        }
    }

    public void sendMessage(String topic, TxMessage message) throws InterruptedException, ExecutionException, WalletSdkException {
        String selectedTopic = Arrays.stream(topic.split(","))
                .reduce((s1, s2) -> activeProfile.contains("ewa") ? (s1.length() > s2.length() ? s1 : s2)
                        : (s1.length() <= s2.length() ? s1 : s2))
                .orElse(""); // 배열이 비어 있을 경우 빈 문자열 반환

        // fromBankCode와 toBankCode가 동일한 경우 하나의 전송만 처리
        if (message.getFromBankCode().equals(message.getToBankCode())) {
            sendToTopicIfValid(selectedTopic, message, message.getFromBankCode());
        } else {
            sendToTopicIfValid(selectedTopic, message, message.getFromBankCode());
            sendToTopicIfValid(selectedTopic, message, message.getToBankCode());
        }
    }

    private void sendToTopicIfValid(String selectedTopic, TxMessage message, String bankCode)
            throws InterruptedException, ExecutionException, WalletSdkException {

        // bankCode가 "END"가 아닌 경우에만 메시지 전송
        if (!"END".equals(bankCode)) {
            String topicWithBankCode = selectedTopic.trim() + "_" + bankCode;
            SendResult<String, TxMessage> result = kafkaTemplate
                    .send(topicWithBankCode, message.getRequestId(), message).get();

            ErrorAssert.isTrue(result != null && result.getProducerRecord() != null, ErrorCode.MESSAGE_SEND_ERROR);

        }
    }

    private void sendToTopicIfValid(String selectedTopic, TxMessage message, String bankCode,
            KafkaOperations<String, TxMessage> operations)
            throws InterruptedException, ExecutionException, WalletSdkException {

        // bankCode가 "END"가 아닌 경우에만 메시지 전송
        if (!"END".equals(bankCode)) {
            String topicWithBankCode = selectedTopic.trim() + "_" + bankCode;
            SendResult<String, TxMessage> result = operations
                    .send(topicWithBankCode, message.getRequestId(), message).get();

            ErrorAssert.isTrue(result != null && result.getProducerRecord() != null, ErrorCode.MESSAGE_SEND_ERROR);
        }
    }

    public void insertTransactionData(int status, TxMessage message) {

        if (status == 1) {

            TransactionRecord txInRecord = TransactionRecord.builder().trnscAmt(message.getAmount())
                    .trnscTypeCd(message.getTxType())
                    .trnscTypeSe(message.getCommand())
                    .trnscSttusCd(message.getTrnscSttusCd())
                    .coinType(message.getCoin())
                    .registerId(message.getPersonId())
                    .trnscDt(message.getTimestamp())
                    .walletAdres(message.getFrom())
                    .rcppaySttusCd("O")
                    .trnscAfterBlce(message.getFromTrnscAfterBlce())
                    .walletInsttCd(message.getFromBankCode())
                    .coinInsttCd(message.getCoinBankCode())
                    .walletInsttNo(CodeDataUtil.getDcName("[PRTCMPNY_GUBUN]", message.getFromBankCode()))
                    .acnutno(message.getFromAcnutno())
                    .trnscSeq(message.getTxSagaId())
                    .trnscSaga(message.getTxSagaId())
                    .aliasNm(message.getFromAliasNm())
                    .walletDpstr(message.getFromWalletDpstr())
                    .trnscHash(message.getTxHash())
                    .bchainReqstId(message.getRequestId())
                    .trnscDcsnDt(new Date())
                    .blckChain(message.getBlockNo()).build().newId();

            TransactionRecord txOutRecord = TransactionRecord.builder().trnscAmt(message.getAmount())
                    .trnscTypeCd(message.getTxType())
                    .trnscTypeSe(message.getCommand())
                    .trnscSttusCd(message.getTrnscSttusCd())
                    .coinType(message.getCoin())
                    .registerId(message.getPersonId())
                    .trnscDt(message.getTimestamp())
                    .walletAdres(message.getTo())
                    .rcppaySttusCd("I")
                    .trnscAfterBlce(message.getTrnscAfterBlce())
                    .walletInsttCd(message.getToBankCode())
                    .coinInsttCd(message.getCoinBankCode())
                    .walletInsttNo(CodeDataUtil.getDcName("[PRTCMPNY_GUBUN]", message.getToBankCode()))
                    .acnutno(message.getAcnutno())
                    .trnscSeq(message.getTxSagaId())
                    .trnscSaga(message.getTxSagaId())
                    .aliasNm(message.getAliasNm())
                    .walletDpstr(message.getWalletDpstr())
                    .trnscHash(message.getTxHash())
                    .bchainReqstId(message.getRequestId())
                    .trnscDcsnDt(new Date())
                    .blckChain(message.getBlockNo()).build().newId();

            try {
                transactionRecordMapper.insert(txInRecord);
            } catch (DataAccessException e) {
                log.error("데이터베이스 : {}", ExceptionUtils.getMessage(e));
            } catch (Exception e) {
                log.error("데이터베이스 : {}", ExceptionUtils.getMessage(e));
            }

            try {
                transactionMirrorRecordrMapper.insert(txInRecord);
            } catch (DataAccessException e) {
                log.error("미러데이터베이스 : {}", ExceptionUtils.getMessage(e));
            } catch (Exception e) {
                log.error("미러데이터베이스 : {}", ExceptionUtils.getMessage(e));
            }

            try {
                transactionRecordMapper.insert(txOutRecord);
            } catch (DataAccessException e) {
                log.error("미러데이터베이스 : {}", ExceptionUtils.getMessage(e));
            } catch (Exception e) {
                log.error("미러데이터베이스 : {}", ExceptionUtils.getMessage(e));
            }

            try {
                transactionMirrorRecordrMapper.insert(txOutRecord);
            } catch (DataAccessException e) {
                log.error("미러데이터베이스 : {}", ExceptionUtils.getMessage(e));
            } catch (Exception e) {
                log.error("미러데이터베이스 : {}", ExceptionUtils.getMessage(e));
            }

        }

    }

    public void updateSagaStatus(TxMessage message) {
        transactionSagaMapper.updateStatus(message.getTxSagaId(),
                message.getTrnscSttusCd(), message.getTxHash(), message.getTretInstt(), null);
    }

}
```
##### EwaAcnutManageServiceImpl.java
```java
package kr.or.cbdc.application.ewa.cstmr.service;

import kr.or.bok.wallet.sdk.errorhandling.WalletSdkException;
import kr.or.bok.wallet.sdk.model.common.Signer;
import kr.or.cbdc.application.common.alias.mapper.BlockListManageMapper;
import kr.or.cbdc.application.common.alias.model.AliasResponse;
import kr.or.cbdc.application.common.alias.model.AliasSearchInfo;
import kr.or.cbdc.application.common.alias.service.BaseBlockListServiceImpl;
import kr.or.cbdc.application.common.deposit.DepositTokenServiceImpl;
import kr.or.cbdc.application.ewa.alias.service.AliasEwaBanksServiceImpl;
import kr.or.cbdc.application.ewa.common.service.EwaGWServiceImpl;
import kr.or.cbdc.application.ewa.common.dto.CbsAcnoResponseDto;
import kr.or.cbdc.application.ewa.common.dto.GwAcnoDto;
import kr.or.cbdc.application.ewa.cstmr.model.AcnutManageModel;
import kr.or.cbdc.application.ewa.policy.service.EwaPolicyManageServiceImpl;
import kr.or.cbdc.application.ewa.wallet.service.EwaWalletManageServiceImpl;
import kr.or.cbdc.config.props.ConfigProperties;
import kr.or.cbdc.domain.main.mapper.ewa.cstmr.TbEwaAcnutMastrMapper;
import kr.or.cbdc.domain.main.mapper.ewa.cstmr.TbEwaCstmrMastrMapper;
import kr.or.cbdc.domain.main.mapper.ewa.dc1.EwaDc1RedempMastrMapper;
import kr.or.cbdc.domain.main.mapper.ewa.wallet.TbEwaWalletMastrMapper;
import kr.or.cbdc.domain.main.model.com.wallet.TbWalletMastr;
import kr.or.cbdc.domain.main.model.ewa.cstmr.TbCstmrMastr;
import kr.or.cbdc.domain.main.model.ewa.dc1.Dc1RedempMastr;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.BizException;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.ErrorAssert;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.ErrorCode;
import kr.or.cbdc.infrastructure.idgen.util.IdGenerationUtil;
import kr.or.cbdc.infrastructure.mybatis.GenericMapperService;
import kr.or.cbdc.infrastructure.profile.EwaProfileCondition;
import kr.or.cbdc.infrastructure.queue.KafkaProducer;
import kr.or.cbdc.infrastructure.queue.TxMessage;
import kr.or.cbdc.infrastructure.util.TokenUtils;
import kr.or.cbdc.interfaces.blockchain.BlockChainHelper;
import kr.or.cbdc.interfaces.blockchain.CoinType;
import kr.or.cbdc.interfaces.blockchain.CommandType;
import kr.or.cbdc.interfaces.blockchain.SupportCallback;
import kr.or.cbdc.interfaces.blockchain.TrnscType;
import kr.or.cbdc.interfaces.blockchain.WalletType;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Conditional;
import org.springframework.stereotype.Service;
import com.hazelcast.core.HazelcastInstance;
import com.hazelcast.cp.lock.FencedLock;
import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Random;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import static kr.or.cbdc.application.common.deposit.DepositTokenServiceImpl.BalanceOperationType;;

/**
 * 계좌 관리 Service
 */
@Slf4j
@Service
@Conditional(EwaProfileCondition.class)
public class EwaAcnutManageServiceImpl extends SupportCallback {

    private @Autowired TbEwaCstmrMastrMapper tbEwaCstmrMastrMapper;
    private @Autowired TbEwaAcnutMastrMapper tbEwaAcnutMastrMapper;
    private @Autowired TbEwaWalletMastrMapper tbEwaWalletMastrMapper;
    private @Autowired EwaPolicyManageServiceImpl ewaPolicyManageService;
    private @Autowired EwaWalletManageServiceImpl ewaWalletManageService;
    private @Autowired AliasEwaBanksServiceImpl aliasEwaBanksService;
    private @Autowired BlockListManageMapper blockListManageMapper;
    private @Autowired BlockChainHelper _blockChain;
    private @Autowired KafkaProducer kafkaProducer;
    private @Autowired GenericMapperService genericMapperService;
    private @Autowired ConfigProperties config;
    private @Autowired BaseBlockListServiceImpl blockListService;
    private @Autowired HazelcastInstance hazelcastInstance;
    private @Autowired EwaGWServiceImpl ewaGWService;
    private @Autowired DepositTokenServiceImpl depositTokenServiceImpl;

    private static final Random rand = new Random();
    private static final ObjectMapper objectMapper = new ObjectMapper();

    private void validateInput(AcnutManageModel model) {
        ErrorAssert.notNull(model, ErrorCode.MISSING_REQUIRED_FIELD);
        ErrorAssert.notNull(model.getTbAcnutMastr(), ErrorCode.MISSING_REQUIRED_FIELD);
        ErrorAssert.notNull(model.getTbAcnutMastr().getTrnscAmt(), ErrorCode.MISSING_REQUIRED_FIELD);
    }
    
    /**
     * 계정계로 잔액 조회를 요청해서 검증
     * @param accountNo Account number to check
     * @param amount Amount to validate
     * @throws BizException if validation fails
     */
    private void validateAccountWithdrawal(String accountNo, BigDecimal amount) {
        GwAcnoDto acnoParam = GwAcnoDto.builder()
                .inqDscd("01")  // 보유계좌잔액조회
                .dpsAcno(accountNo)
                .build();
        
        JsonNode acnoResponse = ewaGWService.acno(acnoParam);
        if (acnoResponse == null) {
            throw new BizException(ErrorCode.BRIDGE_CALL_ERROR, "계정계 잔액 조회 결과가 없습니다. 게이트웨이를 확인하십시오.");
        }

        try {
            CbsAcnoResponseDto acnoResponseDto = objectMapper.treeToValue(acnoResponse, CbsAcnoResponseDto.class);
            
            if (acnoResponseDto.getErrorlist() != null && !acnoResponseDto.getErrorlist().isEmpty()) {
                log.error("계정계 잔액조회 에러: {}", acnoResponseDto.getErrorlist().get(0).getMainMsgTxt());
                throw new BizException(ErrorCode.INVALID_BALANCE_REQUIRED);
            }

            BigDecimal availableAmount = BigDecimal.valueOf(acnoResponseDto.getPayAvlAm());
            if (availableAmount.compareTo(amount) < 0) {
                log.error("계정계 출금가능금액 부족. 계좌: {}, 출금가능금액: {}, 요청금액: {}", 
                        accountNo, availableAmount, amount.intValue());
                throw new BizException(ErrorCode.INSUFFICIENT_ACCOUNT_BALANCE);
            }
        } catch (JsonProcessingException e) {
            log.error("계정계 잔액조회 응답 파싱 에러: {}", e.getMessage());
            throw new BizException(ErrorCode.PARSING_ERROR);
        }
    }

    /**
     * 전환 입금 (예금토큰 발행)
     *
     * @param model
     * @return
     * @throws WalletSdkException
     */
    public String convDeposit(AcnutManageModel model) throws WalletSdkException {
        if (lock(TokenUtils.getToken())) {
            try {
        		// step0 입력값 검증
        		validateInput(model);
                String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));

        		TbCstmrMastr tbCstmrMastr = depositTokenServiceImpl.validateCustomer(cstmrNo);

        		BigDecimal trnscAmt = depositTokenServiceImpl.validateAmount(model.getTbAcnutMastr().getTrnscAmt());
        		log.debug("[jkoh] convDeposit start cstmrNo: {} trnsAmt {}", cstmrNo, trnscAmt);
        		log.debug("[jkoh] tbCstmrMastr: {}", tbCstmrMastr);

        		ErrorAssert.isNull(blockListManageMapper.selectBlclstWallet(bankCd, cstmrNo), ErrorCode.BLACKLIST_TARGET);
                blockListService.findBlockStatus(bankCd);
        		
                BigInteger toBalance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);

        		// IF-GWS-O-006 참가기관 이용자 Core Banking(계정계) 연계 계좌의 잔액 조회
                validateAccountWithdrawal(tbCstmrMastr.getAcnutno(), trnscAmt);

                // step 2-1 통화정책 한도검증 (보유)
                ewaPolicyManageService.policyLimit(null, null, toBalance.add(trnscAmt.toBigInteger()),
                        trnscAmt.toBigInteger(), cstmrNo);

                return depositTokenServiceImpl.issueDepositToken(cstmrNo, trnscAmt);

            } finally {
                unlock(TokenUtils.getToken());
            }
        } else {
            throw new BizException(ErrorCode.DISTRIBUTED_LOCK_ERROR);
        }
    }

    /**
     * 예금 전환(예금토큰 환수)
     *
     * @param model
     * @return
     * @throws WalletSdkException
     */
    public String depositConv(AcnutManageModel model) throws WalletSdkException {
        if (lock(TokenUtils.getToken())) {
            try {
        		// step0 입력값 검증
        		validateInput(model);

                String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));
        		TbCstmrMastr tbCstmrMastr = depositTokenServiceImpl.validateCustomer(cstmrNo);
        		BigDecimal acnutnoBlce = tbCstmrMastr.getAcnutnoBlce();
        		
        		BigDecimal trnscAmt = depositTokenServiceImpl.validateAmount(model.getTbAcnutMastr().getTrnscAmt());

        		// blockListService.chkBlockStatus(cstmrNo, bankCd); 20250106_Source merge할 때 이 부분 막고 20250106_Source의 코드로 바꿈.
                blockListService.findBlockStatus(bankCd);

                // step1 지갑 검증
        		TbWalletMastr tbWalletMastr = depositTokenServiceImpl.validateWallet(WalletType.R1, tbCstmrMastr, ErrorCode.INVALID_TD_REDEMPTION_WALET);

                // step 2 예금전환액 검증
                BigInteger balance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);
                ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(balance) > 0), ErrorCode.INSUFFICIENT_BALANCE);
        		log.debug("[jkoh] OffRamp step 2 지갑, 잔액 검증 완료");
        		
        		// step3 계좌증액
        		depositTokenServiceImpl.updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
        		log.debug("[jkoh] OffRamp step 3 계좌 증액 완료");

                // step4 DC1 환수 이력 생성
                Dc1RedempMastr dc1RedempMastr = Dc1RedempMastr.builder().dc1RedempSttus("W")
                        .trgetInstt(bankCd)
                        .dc1RedempAmount(trnscAmt.longValue())
                        .applcntId(cstmrNo)
                        .build().newId();
        		try {
                    genericMapperService.insertModel(dc1RedempMastr, Dc1RedempMastr.class, EwaDc1RedempMastrMapper.class,
                        "insert");
        		} catch (Exception e) {
        			log.error("계좌({}에 대한 예금토큰 환수 내역 신규저장 에러: {}", tbCstmrMastr.getAcnutno(), e.getMessage());
        			depositTokenServiceImpl.updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.SUBTRACT);
        			throw new BizException(ErrorCode.DATA_ACCESS_ERROR, e.getMessage(), e);
        		}
        		log.debug("[jkoh] OffRamp step 4 TD 환수 이력 저장 완료");

                // kafka message 생성
                TxMessage txMessage = TxMessage.builder().command(CommandType.R1)
                        .txDbId(dc1RedempMastr.getDc1RedempId())
                        .from(tbCstmrMastr.getWalletAdres())
                        .to(tbWalletMastr.getWalletAdres())
                        .fromBankCode(bankCd)
                        .toBankCode(bankCd)
                        .amount(trnscAmt.longValue())
                        .timestamp(new Date())
                        .trnscAfterBlce(balance.subtract(trnscAmt.toBigInteger()).longValue())
                        .fromTrnscAfterBlce(balance.longValue())
                        .fromAcnutno(tbCstmrMastr.getAcnutno())
                        .fromWalletDpstr(tbCstmrMastr.getKoreanNm())
                        .walletDpstr(tbWalletMastr.getWalletNm())
                        .personId(cstmrNo)
                        .coin(CoinType.DC1)
                        .txType(TrnscType.CONVERS.getValue())
                        .retry(0).build();
                List<TxMessage> txMessages = new ArrayList<>();
                txMessages.add(txMessage);
        		
        		String requestId = null;
        		try {
        			requestId = kafkaProducer.setSaga(txMessages);
        			log.debug("[jkoh] depositConv requestId from setSage: {}", requestId);
        		} catch (Exception e) {
        			depositTokenServiceImpl.updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.SUBTRACT);
        			log.error("offRamp 트랜잭션 관리용 Saga requestId for txMessage {} 생성 에러: {}", txMessage, e);
        			throw e;
        		}

                // step 5 카프카 등록및 오류처리
                try {
                    kafkaProc(List.of(txMessage), requestId, "W");
        		} catch (BizException e) {
        			depositTokenServiceImpl.updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.SUBTRACT);
        			log.error("offRamp Kafka 메시지[SagaID({})] 송신 에러: {}", requestId, e.getMessage());
        			throw e;
        		} 
        		log.debug("[jkoh] OffRamp step 5 kafka 전송 완료");
        		
        		try {

                    // step 6 이용자지갑 > 환수지갑 : 분산원장 Call , 참가기관 단일서명
        			String result = _blockChain.sendTransaction(requestId, tbCstmrMastr.getOwner(), tbWalletMastr.getWalletAdres(),
        					trnscAmt.toBigInteger(), this.bankCd, CoinType.DC1, getCallBack(txMessages,CoinType.DC1.name()));
                    ErrorAssert.hasLength(result, ErrorCode.KAFKA_PRODUCE_ERROR);
        		} catch (WalletSdkException e) {
        			log.error("SagaId({}) 예금토큰 환수({} -> {}) 블록체인 호출 에러 {}", requestId, tbCstmrMastr.getWalletAdres(), tbWalletMastr.getWalletAdres(), e.getMessage());
                    kafkaProc(List.of(txMessage), requestId, "R");
        			// 계좌 차감 처리 (계좌잔액= 계좌잔액 - 전환입금액, DC1 = DC1잔액 + 전환입금액)
        			depositTokenServiceImpl.updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.SUBTRACT);
        			throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
        		}
        		log.debug("[jkoh] OffRamp step 6 블록체인 요청 완료.");
        		
        		return requestId;
            } finally {
                unlock(TokenUtils.getToken());
            }
        } else {
            throw new BizException(ErrorCode.DISTRIBUTED_LOCK_ERROR);
        }
    }

    /**
     * 예금 토큰 송금 (DC1 당,타행 이체)
     *
     * @param model
     * @return
     * @throws WalletSdkException
     */
    public String depositTrans(AcnutManageModel model) throws WalletSdkException {

        String result = "";
        String requestId = "";
        String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));

        ErrorAssert.notNull(tbEwaCstmrMastrMapper.select(cstmrNo),ErrorCode.USER_ID_NOT_FOUND);
        ErrorAssert.isTrue(!StringUtils.equals(tbEwaCstmrMastrMapper.select(cstmrNo).getCstmrSttusCd() ,"1"), ErrorCode.INVALID_CUSTOMER_STATE);
        String aliasNm = model.getTbAcnutMastr().getAliasNm();
        String walletInsttCd = model.getTbAcnutMastr().getWalletInsttCd();
        BigDecimal trnscAmt = model.getTbAcnutMastr().getTrnscAmt();
        boolean extYn = StringUtils.equals(walletInsttCd, bankCd);

        // step0 입력값 검증
        ErrorAssert.hasLength(cstmrNo, ErrorCode.CUSTOMER_ID_REQUIRED);
        ErrorAssert.hasLength(aliasNm, ErrorCode.INVALID_ALIAS);
        ErrorAssert.hasLength(trnscAmt.toString(), ErrorCode.EMPTY_TRANSACTION_AMOUNT);
        ErrorAssert.isNull(blockListManageMapper.selectBlclstWallet(bankCd, cstmrNo), ErrorCode.BLACKLIST_TARGET);
        blockListService.findBlockStatus(bankCd);

        // step1 수취인조회및 검증(수취인 지갑여부)
        AliasSearchInfo aliasSearchInfo = AliasSearchInfo.builder().aliasNm(aliasNm).trgetInstt(walletInsttCd).build();

        AliasResponse response = extYn ? aliasEwaBanksService.readFromLocal(aliasSearchInfo)
                : aliasEwaBanksService.read(aliasSearchInfo);

        // step2 이용자 지갑 검증
        TbWalletMastr tbWalletMastrA = this.tbEwaWalletMastrMapper.selectWalletByWalletSe("A");
        Signer signerA = Signer.builder().walletAddress(tbWalletMastrA.getWalletAdres())
                .hdKeyAccToken(tbWalletMastrA.getHdKeyaccToken())
                .hdKeyId(tbWalletMastrA.getHdKeyid()).build();
        TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(cstmrNo);
        ErrorAssert.hasLength(tbCstmrMastr.getWalletAdres(), ErrorCode.WALLET_MISSING);
        ErrorAssert.hasLength(response.getWalletAdres(), ErrorCode.WALLET_INFO_NOT_FOUND);
        ErrorAssert.isTrue(!StringUtils.equals(tbCstmrMastr.getWalletAdres(), response.getWalletAdres()), ErrorCode.WRONG_TRANSFER_REQUIRED);
        ErrorAssert.hasLength(tbCstmrMastr.getWalletAdres(), ErrorCode.WALLET_MISSING);
        ErrorAssert.hasLength(response.getWalletAdres(), ErrorCode.WALLET_INFO_NOT_FOUND);
        ErrorAssert.isTrue(!StringUtils.equals(tbCstmrMastr.getWalletAdres(), response.getWalletAdres()), ErrorCode.WRONG_TRANSFER_REQUIRED);


        // step3 DC1 차감(송금자) > DC1 증액(수취인)
        BigInteger fromBalance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);
        BigInteger toBalance = _blockChain.getBalance(response.getWalletAdres(), bankCd, CoinType.DC1);
        ErrorAssert.isTrue(fromBalance.compareTo(BigInteger.ZERO) > 0, ErrorCode.INSUFFICIENT_BALANCE);
        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.TRANS_AMOUNT_EXCEEDS_BALANCE);
        ErrorAssert.isTrue(fromBalance.compareTo(BigInteger.ZERO) > 0, ErrorCode.INSUFFICIENT_BALANCE);
        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.TRANS_AMOUNT_EXCEEDS_BALANCE);


        // step 3-1 통화정책 한도검증 (1회 , 1일)
        ewaPolicyManageService.policyLimit(trnscAmt, ewaWalletManageService.selectAmtPerDay(cstmrNo), null);
        ewaPolicyManageService.policyTransferLimit(ewaWalletManageService.selectAmtCntPerDay(cstmrNo));

        /*
         * kafka message 생성
         * (당,티헹)
         * kafka message 0 이용자 >> 이용자 (거래내역용)
         * (티헹)
         * kafka message 1 이용자 >> TD환수
         * kafka message 2 출금은행 당좌 >> 입금은행 당좌
         * kafka message 3 출금은행 TD 발행 >> 이용자
         */
        List<TxMessage> txMessages = new ArrayList<>();
        TxMessage txMessage = TxMessage.builder().command(CommandType.T1)
                .txDbId(IdGenerationUtil.createUid("TB_DC_TRANS_MASTR"))
                .from(tbCstmrMastr.getWalletAdres())
                .to(response.getWalletAdres())
                .fromBankCode(bankCd)
                .toBankCode(walletInsttCd)
                .amount(trnscAmt.longValue())
                .timestamp(new Date())
                .fromTrnscAfterBlce(fromBalance.subtract(trnscAmt.toBigInteger()).longValue())
                .personId(cstmrNo)
                .coin(CoinType.DC1)
                .retry(0).build();
        txMessages.add(txMessage);

        // kafka message 0 이용자 >> 이용자 (거래내역용)
        txMessages.get(0).setFromAcnutno(tbCstmrMastr.getAcnutno());
        txMessages.get(0).setAcnutno(response.getAcnutno());
        txMessages.get(0).setAliasNm(tbCstmrMastr.getAliasNm());
        txMessages.get(0).setFromAliasNm(aliasNm);
        txMessages.get(0).setWalletDpstr(response.getPersonNm());
        txMessages.get(0).setFromWalletDpstr(tbCstmrMastr.getKoreanNm());
        txMessages.get(0).setTxType(TrnscType.TRANSFER.getValue());

        // step 5 당행 송금
        if (extYn) {
            requestId = kafkaProducer.setSaga(txMessages);

            // step 5 카프카 등록및 오류처리
            try {
                kafkaProc(txMessages, requestId, "W");

                txMessage.setTrnscAfterBlce(toBalance.add(trnscAmt.toBigInteger()).longValue());
                result = _blockChain.sendLimitTransaction(requestId, tbCstmrMastr.getOwner(), response.getWalletAdres(),
                        trnscAmt.toBigInteger(), bankCd, CoinType.DC1, getCallBack(txMessages, CoinType.DC1.name()));

            } catch (Exception e) {
                kafkaProc(txMessages, requestId, "R");
                throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
            }

        } else {// 타행 송금

            txMessages.add(txMessage.clone());
            txMessages.add(txMessage.clone());
            txMessages.add(txMessage.clone());

            // kafka message 1 이용자 >> TD환수
            String tdRedempWalletAddr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.R1.name()).getWalletAdres();
            txMessages.get(1).setCommand(CommandType.R1);
            txMessages.get(1).setTo(tdRedempWalletAddr);
            txMessages.get(1).setToBankCode(bankCd);

            // kafka message 2 출금은행 당좌 >> 입금은행 당좌
            String cWalletAddr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.C.name()).getWalletAdres();
            BigInteger cBlce = _blockChain.getPrivateBalance(signerA, cWalletAddr, bankCd, CoinType.CBDC);
            ErrorAssert.isTrue(cBlce.compareTo(BigInteger.valueOf(trnscAmt.longValue()))>=0, ErrorCode.INSUFFICIENT_BALANCE);

            String toCWalletAddr = ewaWalletManageService.selectExtWalletAddr(WalletType.C.name(), walletInsttCd);
            txMessages.get(2).setCommand(CommandType.T);
            txMessages.get(2).setFrom(cWalletAddr);
            txMessages.get(2).setTo(toCWalletAddr);
            txMessages.get(2).setFromBankCode(config.getBokCode());
            txMessages.get(2).setToBankCode(config.getBokCode());
            txMessages.get(2).setFromTrnscAfterBlce(0);
            txMessages.get(2).setCoin(CoinType.CBDC);
            txMessages.get(2).setTretInstt(bankCd);
            txMessages.get(2).setTxType(TrnscType.CBDCTRANS.getValue());

            // kafka message 3 출금은행 TD 발행 >> 이용자
            String toIWalletAddr = ewaWalletManageService.selectExtWalletAddr(WalletType.I1.name(), walletInsttCd);
            txMessages.get(3).setCommand(CommandType.I1);
            txMessages.get(3).setFrom(toIWalletAddr);
            txMessages.get(3).setFromBankCode(walletInsttCd);
            txMessages.get(3).setTretInstt(bankCd);
            txMessages.get(3).setFromTrnscAfterBlce(0);

            requestId = kafkaProducer.setSaga(txMessages);

            // step 5 카프카 등록및 오류처리
            try {
                kafkaProc(txMessages, requestId, "W");

                result = _blockChain.sendExtLimitTransaction(requestId, tbCstmrMastr.getOwner(), bankCd,
                        walletInsttCd,
                        response.getWalletAdres(), trnscAmt.toBigInteger(),
                        getCallBack(txMessages, CoinType.DC1.name()));

            } catch (Exception e) {
                kafkaProc(txMessages, requestId, "R");
                throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
            }
        }

        ErrorAssert.hasLength(result, ErrorCode.BLOCKCHAIN_TRANSFER_ERROR);
        ErrorAssert.hasLength(result, ErrorCode.BLOCKCHAIN_TRANSFER_ERROR);

        return requestId;
    }

    /**
     * 예금 토큰 결제 (DC1 예금 토큰 결제)
     *
     * @param model
     * @return
     * @throws WalletSdkException
     */
    public String payment(AcnutManageModel model) throws WalletSdkException {

        String result = "";
        String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));
        ErrorAssert.notNull(tbEwaCstmrMastrMapper.select(cstmrNo), ErrorCode.CUSTOMER_NOT_FOUND,cstmrNo);
        ErrorAssert.isTrue(!StringUtils.equals(tbEwaCstmrMastrMapper.select(cstmrNo).getCstmrSttusCd() ,"1"), ErrorCode.INVALID_CUSTOMER_STATE);
        String aliasNm = model.getTbAcnutMastr().getAliasNm();
        String walletInsttCd = model.getTbAcnutMastr().getWalletInsttCd();
        BigDecimal trnscAmt = model.getTbAcnutMastr().getTrnscAmt();
        boolean extYn = StringUtils.equals(walletInsttCd, bankCd);

        // step0 입력값 검증
        ErrorAssert.hasLength(cstmrNo, ErrorCode.CUSTOMER_ID_REQUIRED);
        ErrorAssert.hasLength(aliasNm, ErrorCode.INVALID_ALIAS);
        ErrorAssert.hasLength(trnscAmt.toString(), ErrorCode.INVALID_AMOUNT);
        ErrorAssert.isNull(blockListManageMapper.selectBlclstWallet(bankCd, cstmrNo), ErrorCode.BLACKLIST_TARGET);
        blockListService.findBlockStatus(bankCd);

        // step1 수취인조회및 검증(수취인 지갑여부)
        AliasSearchInfo aliasSearchInfo = AliasSearchInfo.builder().aliasNm(aliasNm).trgetInstt(walletInsttCd).build();

        AliasResponse response = extYn ? aliasEwaBanksService.readFromLocal(aliasSearchInfo)
                : aliasEwaBanksService.read(aliasSearchInfo);

        // step2 이용자 지갑 검증
        TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(cstmrNo);
        ErrorAssert.hasLength(tbCstmrMastr.getWalletAdres(), ErrorCode.WALLET_MISSING);
        ErrorAssert.hasLength(response.getWalletAdres(), ErrorCode.INVALID_WALLET_INFO_ERROR);
        ErrorAssert.isTrue(!StringUtils.equals(tbCstmrMastr.getWalletAdres(), response.getWalletAdres()),ErrorCode.WRONG_PAYMENT_REQUIRED);


        // step3 DC1 차감(송금자) > DC1 증액(결제처)
        BigInteger fromBalance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);
        BigInteger toBalance = _blockChain.getBalance(response.getWalletAdres(), bankCd, CoinType.DC1);
        ErrorAssert.isTrue(fromBalance.compareTo(BigInteger.ZERO) > 0, ErrorCode.INSUFFICIENT_BALANCE);
        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.PAYMENT_AMOUNT_EXCEEDS_BALANCE);
        ErrorAssert.isTrue(fromBalance.compareTo(BigInteger.ZERO) > 0, ErrorCode.INSUFFICIENT_BALANCE);
        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.PAYMENT_AMOUNT_EXCEEDS_BALANCE);



        /*
         * kafka message 생성
         * (당,티헹)
         * kafka message 0 이용자 >> 이용자 (거래내역용)
         * (티헹)
         * kafka message 1 이용자 >> TD환수
         * kafka message 2 출금은행 당좌 >> 입금은행 당좌
         * kafka message 3 출금은행 TD 발행 >> 이용자
         */
        List<TxMessage> txMessages = new ArrayList<>();
        TxMessage txMessage = TxMessage.builder().command(CommandType.T1)
                .txDbId(IdGenerationUtil.createUid("TB_DC_TRANS_MASTR"))
                .from(tbCstmrMastr.getWalletAdres())
                .to(response.getWalletAdres())
                .fromBankCode(bankCd)
                .toBankCode(walletInsttCd)
                .amount(trnscAmt.longValue())
                .timestamp(new Date())
                .fromTrnscAfterBlce(fromBalance.subtract(trnscAmt.toBigInteger()).longValue())
                .personId(cstmrNo)
                .coin(CoinType.DC1)
                .retry(0).build();
        txMessages.add(txMessage);

        // kafka message 0 이용자 >> 이용자 (거래내역용)
        txMessages.get(0).setFromAcnutno(tbCstmrMastr.getAcnutno());
        txMessages.get(0).setAcnutno(response.getAcnutno());
        txMessages.get(0).setAliasNm(tbCstmrMastr.getAliasNm());
        txMessages.get(0).setFromAliasNm(aliasNm);
        txMessages.get(0).setWalletDpstr(response.getPersonNm());
        txMessages.get(0).setFromWalletDpstr(tbCstmrMastr.getKoreanNm());
        txMessages.get(0).setTxType(TrnscType.PAYMENT.getValue());

        String requestId = "";

        // step 5 당행 결제
        if (extYn) {
            requestId = kafkaProducer.setSaga(txMessages);

            // step 5 카프카 등록및 오류처리
            try {
                kafkaProc(txMessages, requestId, "W");

                txMessage.setTrnscAfterBlce(toBalance.add(trnscAmt.toBigInteger()).longValue());
                result = _blockChain.sendTransaction(requestId, tbCstmrMastr.getOwner(), response.getWalletAdres(),
                        trnscAmt.toBigInteger(), bankCd, CoinType.DC1, getCallBack(txMessages, CoinType.DC1.name()));
            } catch (Exception e) {
                kafkaProc(List.of(txMessage), requestId, "R");
                throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
            }

        } else {// 타행 결제

            txMessages.add(txMessage.clone());
            txMessages.add(txMessage.clone());
            txMessages.add(txMessage.clone());

            // kafka message 1 이용자 >> TD환수
            String tdRedempWalletAddr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.R1.name()).getWalletAdres();
            txMessages.get(1).setCommand(CommandType.R1);
            txMessages.get(1).setTo(tdRedempWalletAddr);
            txMessages.get(1).setToBankCode(bankCd);

            // kafka message 2 출금은행 당좌 >> 입금은행 당좌
            String cWalletAddr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.C.name()).getWalletAdres();
            String toCWalletAddr = ewaWalletManageService.selectExtWalletAddr(WalletType.C.name(), walletInsttCd);
            txMessages.get(2).setCommand(CommandType.T);
            txMessages.get(2).setFrom(cWalletAddr);
            txMessages.get(2).setTo(toCWalletAddr);
            txMessages.get(2).setFromBankCode(config.getBokCode());
            txMessages.get(2).setToBankCode(config.getBokCode());
            txMessages.get(2).setTretInstt(bankCd);
            txMessages.get(2).setFromTrnscAfterBlce(0);
            txMessages.get(2).setTxType(TrnscType.CBDCTRANS.getValue());
            txMessages.get(2).setCoin(CoinType.CBDC);

            // kafka message 3 출금은행 TD 발행 >> 이용자
            String toIWalletAddr = ewaWalletManageService.selectExtWalletAddr(WalletType.I1.name(), walletInsttCd);
            txMessages.get(3).setCommand(CommandType.I1);
            txMessages.get(3).setFrom(toIWalletAddr);
            txMessages.get(3).setFromBankCode(walletInsttCd);
            txMessages.get(3).setTretInstt(bankCd);
            txMessages.get(3).setFromTrnscAfterBlce(0);

            requestId = kafkaProducer.setSaga(txMessages);

            // step 5 카프카 등록및 오류처리
            try {
                kafkaProc(txMessages, requestId, "W");

                result = _blockChain.sendExtTransaction(requestId, tbCstmrMastr.getOwner(), bankCd, walletInsttCd,
                        response.getWalletAdres(), trnscAmt.toBigInteger(),
                        getCallBack(txMessages, CoinType.DC1.name()));

            } catch (Exception e) {
                kafkaProc(txMessages, requestId, "R");
                throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
            }
        }

        ErrorAssert.hasLength(result, ErrorCode.KAFKA_PRODUCE_ERROR);

        return requestId;
    }

    private void kafkaProc(List<TxMessage> txMessages, String requestId, String trnscSttusCd) {

        txMessages.forEach(tx -> {
            tx.setTrnscSttusCd(trnscSttusCd);
            tx.setRequestId(requestId);
        });

        try {
            kafkaProducer.send(topicTxRequest, txMessages);
        } catch (InterruptedException | ExecutionException e) {
            throw new BizException(ErrorCode.SERVER_ERROR  ,  requestId ,  e);
        } catch (Exception e) {
            throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);

        }
        ErrorAssert.hasLength(requestId, ErrorCode.KAFKA_PRODUCE_ERROR);
    }

    /**
     * 계좌인증정보입력(검증) 워드3+난수3 자리생성
     *
     * @param model
     * @return
     */
    public String accountValid(AcnutManageModel model) {

        String[] words = { "송아리", "도사리", "미리내", "가루비", "도둑눈", "산돌림", "나비잠", "흰여울", "그루잠", "희나리" };

        StringBuilder result = new StringBuilder();
        result.append(words[rand.nextInt(words.length)]);

        ErrorAssert.isTrue(tbEwaAcnutMastrMapper.accountValid(model.getTbAcnutMastr()) != null,
                ErrorCode.WALLET_INFO_NOT_FOUND);

        // [Mockup][IF-GWS-O-007
        // ewaBridgeServiceImpl.validityCheck();

        return result.append(rand.nextInt(900) + 100).toString();
    }

    /**
     * 계좌 상세 조회
     *
     * @param cstmrNo
     * @return
     */
    public AcnutManageModel read(String cstmrNo) {

        AcnutManageModel model = new AcnutManageModel();
        model.setTbAcnutMastr(tbEwaAcnutMastrMapper.select(cstmrNo));
        return model;
    }

    public boolean lock(String userId) {
    	log.error("hazelcastInstance lock ::: {}", userId);
        FencedLock lock = hazelcastInstance.getCPSubsystem().getLock("lock:" + userId);
        return lock.tryLock(10, TimeUnit.SECONDS);
    }

    public void unlock(String userId) {
    	log.error("hazelcastInstance unlock :::: {}", userId);
        FencedLock lock = hazelcastInstance.getCPSubsystem().getLock("lock:" + userId);
        lock.unlock();
    }
}
```
##### SupportCallback.java
```java
package kr.or.cbdc.interfaces.blockchain;

import kr.or.bok.wallet.sdk.errorhandling.WalletSdkException;
import kr.or.cbdc.application.common.coin.mapper.DigitalCoinMapper;
import kr.or.cbdc.application.common.coin.model.DigitalCoinModel;
import kr.or.cbdc.config.props.ConfigProperties;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.BizException;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.ErrorAssert;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.ErrorCode;
import kr.or.cbdc.infrastructure.queue.KafkaProducer;
import kr.or.cbdc.infrastructure.queue.TxMessage;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.ObjectUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.atomic.AtomicReference;

@Slf4j
public class SupportCallback {

    @Value(value = "${config.bank-code}")
    protected String bankCd;

    @Value(value = "${spring.kafka.topicTxRequest}")
    protected String topicTxRequest;

    protected @Autowired DigitalCoinMapper digitalCoinMapper;
    protected @Autowired KafkaProducer kafkaProducer;
    protected @Autowired ConfigProperties config;

    protected CallBack<Pending, Confirmed, Failed> getCallBack(List<TxMessage> txMessages, String coin) {

        return new CallBack<Pending, Confirmed, Failed>() {
            @Override
            public void onSuccessHash(Pending result) {
                log.debug("onSuccessHash : {}", result.toString());
                ErrorAssert.hasLength(result.getTransactionHash(), ErrorCode.TRANSACTION_HASH_MISSING);

                // 거래 해시 저장
                txMessages.stream().forEach(tx -> {
                    tx.setTxHash(result.getTransactionHash());
                    tx.setRequestId(result.getRequestId());
                    tx.setTrnscSttusCd("H");
                });
                try {
                    kafkaProducer.send(topicTxRequest, txMessages);
                } catch (InterruptedException | ExecutionException | WalletSdkException e) {
                    Thread.currentThread().interrupt();
                    log.error("onSuccess Exception : {} ", e.getMessage());
                }

            }

            @Override
            public void onSuccessFinal(Confirmed result) throws WalletSdkException {
                log.debug("onSuccessFinal : {}", result.toString());

                // 거래 성공 저장
                txMessages.stream().forEach(tx -> {
                    tx.setRequestId(result.getRequestId());
                    tx.setTrnscSttusCd("S");
                    tx.setBlockNo(result.getBlockNumber());
                });

                // 성공 카프카
                try {
                    kafkaProducer.send(topicTxRequest, txMessages);
                } catch (InterruptedException | ExecutionException e) {
                    Thread.currentThread().interrupt();
                    log.error("onSuccess Exception : {} ", e.getMessage());
                }
            }

            @Override
            @Transactional(noRollbackFor = { BizException.class })
            public void onFailure(Failed e) {

                DigitalCoinModel dcModel = digitalCoinMapper.selectOne(coin,
                        (coin.equals(CoinType.CBDC.name()) || coin.equals(CoinType.VC.name())) ? null : bankCd);

                String errorMessage = e.handleErrorMessage(dcModel.getContractAdres());
                log.error("onFailure : {} ", errorMessage);

                // 실패 카프카
                txMessages.stream().forEach(tx -> {
                    tx.setRequestId(e.getRequestId());
                    tx.setTrnscSttusCd("F");
                });

                try {
                    kafkaProducer.send(topicTxRequest, txMessages);
                } catch (InterruptedException | ExecutionException | WalletSdkException e2) {
                    Thread.currentThread().interrupt();
                    log.error("onFailure Exception : {} ", e2.getMessage());
                }

            }
        };
    }

    protected CallBack<Pending, Confirmed, Failed> syncCallBack(String coin, CompletableFuture<Confirmed> resultFuture) {

        AtomicReference<Pending> pendingResultRef = new AtomicReference<>();

        return new CallBack<Pending, Confirmed, Failed>() {
            @Override
            public void onSuccessHash(Pending result) {
                log.debug("onSuccessHash : {}", result);
                if (ObjectUtils.isEmpty(result) ||ObjectUtils.isEmpty(result.getTransactionHash())  ) {
                    resultFuture.completeExceptionally(new IllegalStateException("트랜잭션 HASH 값이 없습니다."));
                } else {
                    pendingResultRef.set(result);
                }

            }

            @Override
            public void onSuccessFinal(Confirmed result) throws WalletSdkException {
                log.debug("onSuccessFinal : {}", result.toString());
                if (ObjectUtils.isEmpty(pendingResultRef) || ObjectUtils.isEmpty(pendingResultRef.get()) ) {
                    log.error("onSuccessFinal : {} : {}", result.toString(), "Pending시 해시값을 읽지 못했습니다.");
                    resultFuture.completeExceptionally(new IllegalStateException("Pending시 해시값을 읽지 못했습니다."));
                } else {
                    Pending pendingResult = pendingResultRef.get();
                    result.setTransactionHash(pendingResult.getTransactionHash());
                    resultFuture.complete(result);
                }

            }

            @Override
            @Transactional(noRollbackFor = { BizException.class })
            public void onFailure(Failed e) {

                try {
                    DigitalCoinModel dcModel = digitalCoinMapper.selectOne(coin,
                            coin.equals(CoinType.CBDC.name()) ? null : bankCd);

                    String errorMessage = e.handleErrorMessage(dcModel.getContractAdres());
                    log.error("onFailure : {} ", errorMessage);

                    resultFuture.completeExceptionally(new IllegalStateException(errorMessage));
                } catch ( BizException ex) {
                    resultFuture.completeExceptionally(new IllegalStateException(ex.getMessage()));

                }

            }
        };
    }
}
```
##### MessageListener.java - Processes messages by
##### Consuming messages from Kafka topics using `@KafkaListener` annotations
##### Handling transaction events
##### Processing updates and sending responses
##### Managing retries for failed messages
```java
package kr.or.cbdc.infrastructure.queue;

import kr.or.bok.wallet.sdk.errorhandling.WalletSdkException;
import kr.or.cbdc.application.bank.alias.service.AliasBanksServiceImpl;
import kr.or.cbdc.application.common.alias.model.AliasManageModel;
import kr.or.cbdc.application.common.bridge.service.BridgeServiceInterface;
import kr.or.cbdc.config.props.ConfigProperties;
import kr.or.cbdc.domain.main.mapper.transaction.OutboxMapper;
import kr.or.cbdc.domain.main.mapper.transaction.TransactionRecordMapper;
import kr.or.cbdc.domain.main.mapper.transaction.TransactionSagaMapper;
import kr.or.cbdc.domain.main.model.bank.cstmr.TbAcnutMastr;
import kr.or.cbdc.domain.main.model.ewa.dc1.Dc1RedempMastr;
import kr.or.cbdc.domain.main.model.ewa.cstmr.TbCstmrMastr;
import kr.or.cbdc.domain.main.service.push.SetPushDataService;
import kr.or.cbdc.interfaces.blockchain.CoinType;
import kr.or.cbdc.interfaces.blockchain.CommandType;
import kr.or.cbdc.interfaces.blockchain.TransactionMapping;
import kr.or.cbdc.interfaces.blockchain.TrnscType;
import kr.or.cbdc.interfaces.blockchain.WalletStatus;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.exception.ExceptionUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.dao.DataAccessException;
import org.springframework.http.HttpMethod;
import org.springframework.kafka.annotation.DltHandler;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.annotation.RetryableTopic;
import org.springframework.kafka.core.KafkaOperations;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.retrytopic.DltStrategy;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.kafka.support.KafkaHeaders;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.retry.annotation.Backoff;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.event.TransactionPhase;
import org.springframework.transaction.event.TransactionalEventListener;
import org.springframework.util.Assert;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.HttpServerErrorException;
import org.springframework.web.client.ResourceAccessException;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import kr.or.cbdc.interfaces.blockchain.Checker;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.Arrays;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.ExecutionException;

import jakarta.annotation.PostConstruct;
import kr.or.cbdc.domain.main.mapper.ewa.cstmr.TbEwaAcnutMastrMapper;
import kr.or.cbdc.domain.main.mapper.ewa.cstmr.TbEwaCstmrMastrMapper;
import kr.or.cbdc.domain.main.mapper.ewa.dc1.EwaDc1IsuMastrMapper;
import kr.or.cbdc.infrastructure.mybatis.GenericMapperService;
import kr.or.cbdc.interfaces.ApiCallHelper;
import kr.or.cbdc.interfaces.InterfaceMap;
import kr.or.cbdc.interfaces.InterfaceSend;
import kr.or.cbdc.domain.main.mapper.bank.cstmr.TbPdmAcnutMastrMapper;
import kr.or.cbdc.domain.main.mapper.bank.cstmr.TbPdmCstmrMastrMapper;
import kr.or.cbdc.domain.main.mapper.com.wallet.WalletMastrEntityMapper;
import kr.or.cbdc.application.common.deposit.DepositTokenServiceImpl;
import kr.or.cbdc.application.ewa.common.dto.CbsErrorDto;
import kr.or.cbdc.application.ewa.common.dto.CbsRampResponseDto;
import kr.or.cbdc.application.ewa.common.dto.GwRampDto;
import kr.or.cbdc.application.ewa.common.dto.GwUmsAppPushDto;
import kr.or.cbdc.interfaces.blockchain.AccessLevel;
import kr.or.cbdc.interfaces.blockchain.BlockChainHelper;
import kr.or.cbdc.domain.main.mapper.ewa.dc1.EwaDc1RedempMastrMapper;

@Slf4j
@Component
public class MessageListener {

    @Autowired
    private KafkaTemplate<String, TxMessage> kafkaTemplate;

    @Value(value = "${spring.kafka.topicTxRequest}")
    public String[] topicTxRequest;

    @Value(value = "${spring.kafka.topicTxResponse}")
    private String topicTxResponse;

    @Value(value = "${config.bank-code}")
    private String bankCode;

    @Value(value = "${spring.kafka.group}")
    public String group;
    @Value(value = "${spring.kafka.bc-group}")
    public String bcGroup;

    private @Autowired ApplicationEventPublisher eventPublisher;
    private @Autowired TransactionSagaMapper transactionSagaMapper;
    private @Autowired TransactionRecordMapper transactionRecordMapper;
    private @Autowired TransactionMapping transactionMapping;
    private @Autowired SetPushDataService setPushData;
    private @Autowired KafkaProducer kafkaProducer;
    private @Autowired ConfigProperties config;
    private @Autowired ObjectMapper objectMapper;
    private @Autowired OutboxMapper outboxMapper;
    private @Autowired TbEwaCstmrMastrMapper tbEwaCstmrMastrMapper;
    private @Autowired GenericMapperService genericMapperService;
    private @Autowired ApiCallHelper apiCallHelper;
    private @Autowired ConfigProperties configProperties;
    private @Autowired WalletMastrEntityMapper tdWalletMastrMapper;
    private @Autowired TbPdmAcnutMastrMapper tbPdmAcnutMastrMapper;
    private @Autowired TbPdmCstmrMastrMapper tbPdmCstmrMastrMapper;
    private @Autowired AliasBanksServiceImpl aliasBanksService;
    private @Autowired EwaDc1IsuMastrMapper ewaDc1IsuMastrMapper;
    private @Autowired InterfaceSend interfaceSend;
    private @Autowired DepositTokenServiceImpl depositTokenServiceImpl;
    private @Autowired BlockChainHelper blockChain;

    public static String[] dynamicTopics;

    @PostConstruct
    public void initializeTopics() {
        // 각 원소에 "_${config.bank-code}"를 추가
        dynamicTopics = Arrays.stream(topicTxRequest)
                .map(topic -> topic + "_" + bankCode)
                .toArray(String[]:new);

        log.info("Dynamic Topics Initialized: {}", Arrays.toString(dynamicTopics));
    }

    public static String[] computeTopics(String nonfinalTopics, String bankCode) {
        return Arrays.stream(nonfinalTopics.split(","))
                     .map(topic -> topic.trim() + "_" + bankCode)
                     .toArray(String[]::new);
    }

    private boolean vouchTranSactionData(TxMessage message) {

        switch (message.getCommand()) {
            case PM: //바우처 연계 : 결제 요청
                transactionMapping.setTransactionComplete( message.getCommand(),message.getTxDbId(),message.getPersonId(),"", message);
                return true;
            case TX, TR: //바우처 연계 : 거래번호 생성및 요청
                transactionMapping.setTransactionComplete( message.getCommand(),message.getTxDbId(),message.getPersonId(),"", message);
                return true;
            case PR, PF: // 바우처 연계 승인정보전달 Update 후 종료 , 승인 Update key 'TX_CD' , 결제승인번호는 '리퀘스트ID'
                transactionRecordMapper.updatePr(message);
                return true;
            case RR, RF: // 바우처 연계 환불정보전달 Update 후 종료 , 환불 Update key 'TX_CD' , 환불승인번호는 '리퀘스트ID'
                transactionRecordMapper.updateRr(message);
                return true;
            case CR: // 바우처 연계 캐쉬백정보전달 Update 후 종료 , 캐쉬백 Update key 'TX_CD' , 캐쉬백승인번호는 '리퀘스트ID'
                transactionRecordMapper.updateCr(message);
                return true;
            default:
                return false;
        }
    }

    private Optional<CbsRampResponseDto> parseGatewayResponse(JsonNode response, String errorContext) {
        try {
            return Optional.of(objectMapper.treeToValue(response, CbsRampResponseDto.class));
        } catch (JsonProcessingException e) {
            log.error("계정계 " + errorContext + " 응답[{}] 파싱 에러: {}", response.toPrettyString(), e.getMessage());
            return Optional.empty();
        }
    }

    private boolean checkGWResponse(Optional<CbsRampResponseDto> responseOpt, Runnable errorHandler) {
        if (responseOpt.isPresent()) {
            CbsRampResponseDto response = responseOpt.get();
            String errcode = response.getErrcode();
            if (errcode != null) {
                
                if (errorHandler != null) {
                    errorHandler.run();
                }

                String errmsg = response.getErrusrmsg();
                List<CbsErrorDto> errlist = response.getErrorlist();
                if (errlist != null && !errlist.isEmpty()) {
                    errcode = errlist.get(0).getMsgCd();
                    errmsg = errlist.get(0).getMainMsgTxt();
                }
                log.error("계정계 호출 에러 {} {}", errcode, errmsg);
                return false;
            }
            log.debug("[jkoh] OffRamp step 7 계정계 offRamp 요청 완료");
            return true;
        }
        else {
            errorHandler.run();
            return false;
        }
    }

    public void subtractCustomerBalance(TxMessage message) {
        log.debug("[jkoh] OffRamp step 7-1 계좌 복구(감액 처리)");
        // 계좌 차감 처리 (계좌잔액= 계좌잔액 - 전환입금액, DC1 = DC1잔액 + 전환입금액)
        TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(message.getPersonId());
        BigDecimal trnscAmt = BigDecimal.valueOf(message.getAmount());
        tbCstmrMastr.setAcnutnoBlce(tbCstmrMastr.getAcnutnoBlce().subtract(trnscAmt));

        try {
            // Perform database update
            genericMapperService.updateModel(tbCstmrMastr, TbCstmrMastr.class, TbEwaAcnutMastrMapper.class, "updateBlce");
        } catch (DataAccessException e) {
            log.error("고객 {} 잔액 변경 중 에러가 발생했습니다. 에러 내용: {}", tbCstmrMastr.getCstmrNo(), e.getMessage());
        } catch (Exception e) {
            log.error("고객 {} 잔액 변경 중 에러가 발생했습니다. 에러 내용: {}", tbCstmrMastr.getCstmrNo(), e.getMessage());
        }
    }

    public void updateTransactionComplete(TxMessage message) {
        String messageSttus = "";
        switch (message.getCommand()) {
            case M, I, B, R, M1, M2, D1, D2, I1, I2, R1, R2:
                messageSttus = "S".equals(message.getTrnscSttusCd()) ? "C" : "F";
                break;
            case D:
                messageSttus = "S".equals(message.getTrnscSttusCd()) ? "A" : "F";
                break;
            default:
                messageSttus = "S".equals(message.getTrnscSttusCd()) ? "C" : "F";
                return;
        }
        transactionMapping.setTransactionComplete(message.getCommand(), message.getTxDbId(), message.getPersonId(),
                messageSttus, message);
    }

    private void handleOffRampRecovery(TxMessage message) {
        try {
            // Try to reissue the deposit token using the common logic
            depositTokenServiceImpl.issueDepositTokenOnly(message.getPersonId(), BigDecimal.valueOf(message.getAmount()));
            log.info("계정계 OffRamp 실패 후, TD 재발행(onRamp) 완료 {}", message.getTxDbId());
        } catch (Exception e) {
            log.error("계정계 OffRamp 실패 후, TD 재발행(onRamp) 실패 {}: {}", 
                message.getTxDbId(), e.getMessage());
            // Consider additional error handling or notification
        }
    }
    
    private void performOffRampRecovery(TxMessage message) {
        try {
            subtractCustomerBalance(message);
            handleOffRampRecovery(message);
        } catch (Exception e) {
            log.error("OffRamp 실패 후, 원복 거래 실패: {}", e.getMessage());
        }
    }

    private void quitUser(TbCstmrMastr tbCstmrMastr, TxMessage message, String trnLogKeyVal){
        // step2 분산원장 지갑폐기
        try {
        Checker checker = new Checker();
        checker.setLevel(AccessLevel.personal);
        checker.setHdKeyAccToken(tbCstmrMastr.getHdKeyaccToken());
        checker.setWalletAddress(tbCstmrMastr.getWalletAdres());
        checker.setHdKeyId(tbCstmrMastr.getHdKeyid());
        
        String stopReqId = blockChain.setEoaWalletStatus(checker, WalletStatus.STOP);
        String discardReqId = blockChain.setEoaWalletStatus(checker, WalletStatus.DISCARD);
        Assert.hasLength(stopReqId, "지갑 정보 수정중 오류가 발생 하였습니다.");
        Assert.hasLength(discardReqId, "지갑 정보 수정중 오류가 발생 하였습니다.");
    
        //step4 성공시 지갑폐기정보 저장(지갑삭제, 계좌지갑ID 삭제)
        if(!tbCstmrMastr.getWalletId().isEmpty()){
            Assert.isTrue(1 == tdWalletMastrMapper.updateDeleteAt(tbCstmrMastr.getWalletId()), "지갑삭제 실패.");
        }
        Assert.isTrue(1 == tbPdmAcnutMastrMapper.updateWalletId(TbAcnutMastr.builder().cstmrNo(tbCstmrMastr.getCstmrNo()).walletId("").build()), "지갑삭제 실패.");

        //실증추가 고객 삭제
        Assert.isTrue(1 == tbPdmCstmrMastrMapper.deleteCstmr(tbCstmrMastr.getCstmrNo()),"고객 삭제 실패.");
        //실증추가 계좌 삭제
        Assert.isTrue(1 == tbPdmAcnutMastrMapper.deleteAcnut(tbCstmrMastr.getCstmrNo()),"계좌 삭제 실패.");

        // //step5 간편주소 삭제
        AliasManageModel aliasManageModel = AliasManageModel.builder().trgetInstt(config.getBankCode()).userId(tbCstmrMastr.getCstmrNo()).aliasNm(tbCstmrMastr.getAliasNm()).build();
        aliasBanksService.delete(aliasManageModel);

            try {
                GwUmsAppPushDto push = GwUmsAppPushDto.builder()
                        .umsTmplCd("RPWSTTPE0132435")
                        .csno(tbCstmrMastr.getCstmrNo())
                        .cusNm(tbCstmrMastr.getKoreanNm())
                        .build();
                apiCallHelper.callUMSGateway(push);
            } catch (Exception e) {
                log.error("PdmWalletManageServiceImpl deleteWallet callUMSGateway error:" + e.getMessage());
            }
        } catch (Exception e) {

            BigDecimal trnscAmt = BigDecimal.valueOf(message.getAmount());
            //탈회 계정계 
            InterfaceMap param = new InterfaceMap();
            param.put("dpsAcno", tbCstmrMastr.getAcnutno());
            param.put("trnAm", trnscAmt.toString());
            param.put("canYn", "Y");
            param.put("glblId", trnLogKeyVal);
            interfaceSend.api_E_006_withdraw(param);
        }

    }

    @Transactional
    @RetryableTopic(attempts = "3", backoff = @Backoff(delay = 1000, maxDelay = 5000, multiplier = 2), kafkaTemplate = "nonTransactionalKafkaTemplate", dltStrategy = DltStrategy.FAIL_ON_ERROR, listenerContainerFactory = "retryContainerFactory")
    @KafkaListener(id = "txRequest", topics = "#{T(kr.or.cbdc.infrastructure.queue.MessageListener).computeTopics('${spring.kafka.topicTxRequest}', '${config.bank-code}')}", containerFactory = "kafkaListenerContainerFactory", groupId = "${spring.kafka.group}")
    public void listenTxRequest(TxMessage message, Acknowledgment acknowledgment) throws WalletSdkException, InterruptedException, ExecutionException {

    	// log.info("txRequest message {} : {}", message.getRequestId(), message.toString());
        log.debug("[jkoh] txRequest message {} : {}", message.getRequestId(), message.toString());
        String trnscSttusCd = message.getTrnscSttusCd();

        //바우처 연계
        try {
            if(vouchTranSactionData(message)){
                acknowledgment.acknowledge();
                return;
            }
        }catch (Exception e){
            acknowledgment.acknowledge();
            log.error("바우처 연계정보 DB 수정 에러 vouchTranSactionData: {}", ExceptionUtils.getMessage(e));
            return;
        }

        // 지갑으로 기록할 거래 장부를 판단하고 기록
        kafkaProducer.insertTransactionData(1, message);

        if ("S".equals(trnscSttusCd) || "F".equals(trnscSttusCd)) {
            if ((config.getBokCode().equals(message.getFromBankCode()) && config.getBokCode().equals(message.getToBankCode())) ||
                    ((bankCode.equals(message.getFromBankCode()) || "END".equals(message.getFromBankCode()))&& message.getNum() == 0)) {
                log.debug("[jkoh] call updateTransactionComplete");
                updateTransactionComplete(message);
            }

            // 푸시발송 로직 위치 변경
//            try {
//                 setPushData.setPushData(message);
//                log.debug("[jkoh] call setPushData");
//            } catch (Exception e) {
//                log.error("setPushData error in MessageListener.listenTxRequest: {}", e.getMessage());
//            }
        }

        // 트랜잭션 SAGA 테이블 동기화 상태 변경
        if (bankCode.equals(message.getFromBankCode()) &&
                (bankCode.equals(message.getToBankCode()) ||
                        (StringUtils.isEmpty(message.getTretInstt()) || message.getTretInstt().length() != 3))) {

            transactionSagaMapper.updateStatus(message.getTxSagaId(),
                    message.getTrnscSttusCd(), message.getTxHash(), message.getTretInstt(),
                    null);
        }

        // Publish event for the async business logic processing
        eventPublisher.publishEvent(message);

        acknowledgment.acknowledge();
    }

    private void updateResult(StringBuilder result, int index, String newValue) {
        if (index >= 0 && index < result.length()) {
            result.setCharAt(index, newValue.charAt(0));
        }
    }

    @TransactionalEventListener(phase = TransactionPhase.BEFORE_COMMIT)
    public void outBoxBankLegacyEvent(TxMessage message) throws WalletSdkException, JsonProcessingException {
        // save message to outbox
        String jsonBody = objectMapper.writeValueAsString(message);
        // OUTBOX_ID는 18자리로 UUID 사용
        // MyBatis를 통한 DB 저장
        outboxMapper.insert(message.getTxSagaId(), jsonBody);
    }

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void sendBankLegacyEvent(TxMessage message)
            throws WalletSdkException, InterruptedException, ExecutionException {
        
        kafkaTemplate.executeInTransaction(kafkaOperations -> {
            StringBuilder result = new StringBuilder("FFF");
            try {
            	// Process all business logic within the Kafka transaction
            	updateResult(result, 0,sendBridgeService(message));
                sendSagaStateSyncMessage(message, kafkaOperations);
                sendVoucherMessage(message, kafkaOperations);
                updateResult(result, 1,"S");
                if ("S".equals(message.getTrnscSttusCd()) || "F".equals(message.getTrnscSttusCd())) {
                    
                    // [IF-GWS-O-010] CBDC On/Off Ramp 내역 전송
                    // 중앙은행에서 CBDC 발행 결과 전달받은 후 실행

					if ((CommandType.I == message.getCommand() || CommandType.R == message.getCommand())
							&& (CoinType.CBDC == message.getCoin())) {
						InterfaceMap param = new InterfaceMap();
						param.put("trnDscd", CommandType.I == message.getCommand() ? "01" : "02");
						param.put("trnAm", message.getAmount());
						interfaceSend.api_E_001(param);
						updateResult(result, 2, "S"); // 성공시
					}
                    
                    // Push 메시지 전달
                    setPushData.setPushData(message);
                }

                outboxMapper.update(message.getTxSagaId(), result.toString());
                return true;
            } catch (Exception ex) {
                outboxMapper.update(message.getTxSagaId(), result.toString());

                // Kafka 트랜잭션 내에서 발생한 모든 예외는 여기서 감싸져서 전파되면 rollback 처리됨
                throw new RuntimeException("Error in Kafka transaction, rolling back", ex);
            }
        });
    }

    // Centralized method to handle all banking system integration logic
    private String sendBridgeService(TxMessage message) {
        String trnscSttusCd = message.getTrnscSttusCd();
        String trnscType = message.getTxType();
        
        String resultCode = "S";
        
        try {
            // onRamp 처리
            if (Objects.equals(trnscType, TrnscType.DEPOSIT.getValue())) {
                processOnRampTransaction(message, trnscSttusCd);
                resultCode = "S";
            }
            // offRamp 처리
            else if (Objects.equals(trnscType, TrnscType.CONVERS.getValue())) {
                processOffRampTransaction(message, trnscSttusCd);
                resultCode = "S";
            }
            // 탈회 처리
            else if (Objects.equals(trnscType, TrnscType.QUIT.getValue())) {
                processQuitTransaction(message, trnscSttusCd);
                resultCode = "S";
            }
            
            return resultCode;
        } catch (Exception e) {
            log.error("Error in sendBridgeService: {}", e.getMessage(), e);
            return "F";
        }
    }
    
    // onRamp 처리(계좌 -> 전자지갑)
    private void processOnRampTransaction(TxMessage message, String trnscSttusCd) {
        // 블록체인 거래 성공 -> 로그
        if (trnscSttusCd.equals("S")) {
            try {
                TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(message.getPersonId());
                if (tbCstmrMastr != null) {
                    log.info("계좌({}) 전환 입금(onRamp) 거래 완료", tbCstmrMastr.getAcnutno());
                } else {
                    log.error("성공한 onRamp 거래지만 DB에서 이 고객 정보({})를 찾을 수 없습니다. 시스템을 점검하십시오.\nMessage: {}", message.getPersonId(), message);
                    return;
                }
            } catch (DataAccessException e) {
                log.error("고객 정보 조회 데이터베이스 에러: {}", ExceptionUtils.getMessage(e));
            } catch (Exception e) {
                log.error("고객 정보 조회 에러 : {}", ExceptionUtils.getMessage(e));
            }
            log.debug("[jkoh] OnRamp step 7 onRamp 거래 최종 완료");
        }
        // 블록체인 거래 실패 -> 계좌 차감, 계정계 취소
        else if (trnscSttusCd.equals("F")) {
            // OnRamp 실패 처리
            // Step 1. NCP DB 계좌 증액 처리
            // 계좌 증액 처리 (계좌잔액= 계좌잔액 + 전환입금액, DC1 = DC1잔액 - 전환입금액)
            log.debug("[jkoh] OnRamp step 7 onRamp 실패");
            try {
                TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(message.getPersonId());
                if (tbCstmrMastr == null) {
                    log.error("실패한 onRamp 거래. DB에서 이 고객 정보({})를 찾을 수 없습니다. 시스템을 점검하십시오.\nMessage: {}", message.getPersonId(), message);
                    return;
                }
                BigDecimal trnscAmt = BigDecimal.valueOf(message.getAmount());
                tbCstmrMastr.setAcnutnoBlce(tbCstmrMastr.getAcnutnoBlce().add(trnscAmt));
                try {
                    genericMapperService.updateModel(tbCstmrMastr, TbCstmrMastr.class, TbEwaAcnutMastrMapper.class, "updateBlce");
                } catch (Exception e) {
                    log.error("계좌({}) 증액 처리 에러: {}", tbCstmrMastr.getAcnutno(), e.getMessage());
                }
                log.debug("[jkoh] OnRamp step 7-1 계좌 복구(증액 처리)");
            } catch (DataAccessException e) {
                log.error("고객 정보 조회 데이터베이스 에러: {}", ExceptionUtils.getMessage(e));
            } catch (Exception e) {
                log.error("고객 정보 조회 에러 : {}", ExceptionUtils.getMessage(e));
            }

            // Step 2. 계정계 onRamp 거래 취소 통지
            // Step 1이 실패해도 계정계 계좌 onRamp 실패 통지는 해야 한다.
            // 블록체인 거래 실패로 전자지갑으로 돈이 들어가지 않았으므로.
            String wGuid = null;
            try {
                wGuid = ewaDc1IsuMastrMapper.selectGuid(message.getTxDbId());
            } catch (DataAccessException e) {
                // global ID 조회하지 못하면 이후 onRamp 취소 거래를 보낼 수 없다. 그래서 여기서 종료
                log.error("GlobalID 조회 데이터베이스 에러: {}", ExceptionUtils.getMessage(e));
                return;
            } catch (Exception e) {
                log.error("GlobalID 조회 에러 : {}", ExceptionUtils.getMessage(e));
                return;
            }

            if (wGuid != null) {
                HashMap<String, Object> param = new HashMap<>();
                param.put("internalTxId", "internalTxId");
                param.put("oriId", wGuid);
                param.put("customerId", message.getAcnutno());
                log.debug("[jkoh] onRamp Fail send to CBS: {}", param);
                JsonNode response = null;
                try {
                    String url = apiCallHelper.getGwUrl(configProperties.getGateway().getOnRampFail().getUrl());
                    response = apiCallHelper.callURL(
                            url,
                            null,
                            objectMapper.valueToTree(param),
                            HttpMethod.POST);
                    try {
                        CbsRampResponseDto onRampFailResponse = objectMapper.treeToValue(response, CbsRampResponseDto.class);
                        String errcode = onRampFailResponse.getErrcode();
                        if (errcode != null) {
                            String errmsg = onRampFailResponse.getErrusrmsg();
                            List<CbsErrorDto> errlist = onRampFailResponse.getErrorlist();
                            if (errlist != null && !errlist.isEmpty()) {
                                errcode = errlist.get(0).getMsgCd();
                                errmsg = errlist.get(0).getMainMsgTxt();
                            }
                            log.error("GlobalID({}) 계정계 호출 에러 {} {}", wGuid, errcode, errmsg);
                        }
                    } catch (JsonProcessingException e) {
                        log.error("GlobalID({}) Json response({}) 파싱 에러: ", wGuid, response.toPrettyString(), e.getMessage());
                    }
                } catch (ResourceAccessException e) {
                    log.error("onRampFail API timeout or connection error: {}", e.getMessage());
                } catch (HttpClientErrorException e) {
                    log.error("onRampFail API client error (4xx): Status {}, Response {}", e.getStatusCode(), e.getResponseBodyAsString());
                } catch (HttpServerErrorException e) {
                    log.error("onRampFail API server error (5xx): Status {}, Response {}", e.getStatusCode(), e.getResponseBodyAsString());
                } catch (Exception e) {
                    log.error("Unexpected error calling onRampFail API: {}", e.getMessage(), e);
                }
                log.debug("[jkoh] OnRamp step 7-2 계정계 거래 취소 요청 완료");
            }
            else {
                log.error("{}값에 대응되는 키값이 DB에 없어서 계정계에 취소 거래를 보낼 수 없습니다.", message.getTxDbId());
                return;
            }
        }
    }

    // offRamp 처리
    private void processOffRampTransaction(TxMessage message, String trnscSttusCd) {
        // 블록체인 거래 성공 -> 계정계 offRamp 전송 및 에러 처리
        if (trnscSttusCd.equals("S")) {
            Optional<CbsRampResponseDto> offRampResponse = null;
            TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(message.getPersonId());
            if (tbCstmrMastr == null) {
                log.error("성공한 offRamp 거래지만 DB에서 이 고객 정보({})를 찾을 수 없습니다. 시스템을 점검하십시오.\nMessage: {}", message.getPersonId(), message);
                return;
            }
            BigDecimal trnscAmt = BigDecimal.valueOf(message.getAmount());

            // step 7 계정계 입금 요청 Gateway 호출
            GwRampDto paramOffRamp = depositTokenServiceImpl.createRampParams("internalTxId"
                                                , tbCstmrMastr
                                                , trnscAmt
                                                , BigInteger.valueOf(message.getFromTrnscAfterBlce()).add(trnscAmt.toBigInteger()));
            JsonNode respOffRamp = null;
            try {
                String url = apiCallHelper.getGwUrl(configProperties.getGateway().getOffRamp().getUrl());
                respOffRamp = apiCallHelper.callURL(
                        url,
                        null,
                        objectMapper.valueToTree(paramOffRamp),
                        HttpMethod.POST);
                offRampResponse = parseGatewayResponse(respOffRamp, "offRamp");
                if (checkGWResponse(offRampResponse, () -> performOffRampRecovery(message))) {
                    CbsRampResponseDto responseDto = offRampResponse.get();
                    Dc1RedempMastr dc1RedempMastrUpdate = Dc1RedempMastr.builder()
                                                    .dc1RedempId(message.getTxDbId())
                                                    .cbsTrnAcno(responseDto.getDpsInpAcno())
                                                    .cbsTrnDt(responseDto.getTrnDt())
                                                    .mcaGuid(responseDto.getTrnLogKeyVal())
                                                    .cbsTrnSrno(responseDto.getTrnSrno())
                                                    .build();

                    try {
                        genericMapperService.updateModel(dc1RedempMastrUpdate, Dc1RedempMastr.class, EwaDc1RedempMastrMapper.class, "update");
                    } catch (Exception e) {
                        log.error("계좌({}) 거래키({}) 거래일련번호({})에 대한 예금토큰 환수 내역 갱신(계정계 응답 데이터) 에러: {}", tbCstmrMastr.getAcnutno(), responseDto.getTrnLogKeyVal(), responseDto.getTrnSrno(), e.getMessage());
                        log.error("계좌({}) 예금토큰 환수 내역 저장 에러: {}", tbCstmrMastr.getAcnutno(), e.getMessage());
                    }
                }
            } catch (ResourceAccessException e) {
                performOffRampRecovery(message);
                log.error("OffRamp API timeout or connection error: {}", e.getMessage());
            } catch (HttpClientErrorException e) {
                performOffRampRecovery(message);
                log.error("OffRamp API client error (4xx): Status {}, Response {}", e.getStatusCode(), e.getResponseBodyAsString());
            } catch (HttpServerErrorException e) {
                performOffRampRecovery(message);
                log.error("OffRamp API server error (5xx): Status {}, Response {}", e.getStatusCode(), e.getResponseBodyAsString());
            } catch (Exception e) {
                performOffRampRecovery(message);
                log.error("Unexpected error calling OffRamp API: {}", e.getMessage(), e);
            }
        }
        // 블록체인 거래 실패 -> 계좌 차감 
        else if (trnscSttusCd.equals("F")) {
            subtractCustomerBalance(message);
        }
    }
    
    // 탈회 처리
    private void processQuitTransaction(TxMessage message, String trnscSttusCd) {
        // 블록체인 거래 성공 -> 계정계 offRamp 전송 및 에러 처리
        if (trnscSttusCd.equals("S")) {
            Optional<CbsRampResponseDto> offRampResponse = null;
            TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(message.getPersonId());
            BigDecimal trnscAmt = BigDecimal.valueOf(message.getAmount());
            String cusDsCd = Objects.toString(tdWalletMastrMapper.selectCusDsCd(tbCstmrMastr.getCstmrNo()),"00");

            try {
                // 압류/파산/개인회생 , 금액이 0원이 아닌경우 off ramp만 처리
                if(cusDsCd.equals("02") || cusDsCd.equals("03") || cusDsCd.equals("04") ){
                     // step 7 계정계 입금 요청 Gateway 호출
                    GwRampDto paramOffRamp = depositTokenServiceImpl.createRampParams("internalTxId"
                    , tbCstmrMastr
                    , trnscAmt
                    , BigInteger.valueOf(message.getFromTrnscAfterBlce()).add(trnscAmt.toBigInteger()));
                    JsonNode respOffRamp = null;

                    String url = apiCallHelper.getGwUrl(configProperties.getGateway().getOffRamp().getUrl());
                    respOffRamp = apiCallHelper.callURL(
                            url,
                            null,
                            objectMapper.valueToTree(paramOffRamp),
                            HttpMethod.POST);
                    offRampResponse = parseGatewayResponse(respOffRamp, "offRamp");
                    checkGWResponse(offRampResponse, () -> performOffRampRecovery(message));
                
                } else {
                    //탈회 계정계 
                    InterfaceMap param = new InterfaceMap();
                    param.put("dpsAcno", tbCstmrMastr.getAcnutno());
                    param.put("trnAm", trnscAmt.toString());
                    param.put("canYn", "N");
                    InterfaceMap result = null;
                    result = interfaceSend.api_E_006_withdraw(param);
                    offRampResponse = parseGatewayResponse(objectMapper.valueToTree(result), "offRamp Q");
                    checkGWResponse(offRampResponse, () -> performOffRampRecovery(message));
                }

                CbsRampResponseDto responseDto = offRampResponse.get();

                // 계정계 성공시 or (압류,파산,개인회생 금액 0원일 경우)
                if(responseDto.getErrcode() == null ) {
                    Dc1RedempMastr dc1RedempMastrUpdate = Dc1RedempMastr.builder()
                                                    .dc1RedempId(message.getTxDbId())
                                                    .cbsTrnAcno(responseDto.getDpsInpAcno())
                                                    .cbsTrnDt(responseDto.getTrnDt())
                                                    .mcaGuid(responseDto.getTrnLogKeyVal())
                                                    .cbsTrnSrno(responseDto.getTrnSrno())
                                                    .build();
                    
                    try {
                        genericMapperService.updateModel(dc1RedempMastrUpdate, Dc1RedempMastr.class, EwaDc1RedempMastrMapper.class, "update");
                        String trnLogKeyVal = responseDto.getTrnLogKeyVal();
                        //사망/압류자 처리 여부 추가
                        if(message.getOrderNo().equals("ded")){
                            tdWalletMastrMapper.checkPrcUser(tbCstmrMastr.getCstmrNo());
                            if(cusDsCd.equals("01")){
                                quitUser(tbCstmrMastr, message, trnLogKeyVal);
                            }
                        } else {
                            quitUser(tbCstmrMastr, message, trnLogKeyVal);
                        }

                    } catch (Exception e) {
                        log.error("계좌({}) 거래키({}) 거래일련번호({})에 대한 예금토큰 환수 내역 갱신(계정계 응답 데이터) 에러: {}", tbCstmrMastr.getAcnutno(), responseDto.getTrnLogKeyVal(), responseDto.getTrnSrno(), e.getMessage());
                        log.error("계좌({}) 예금토큰 환수 내역 저장 에러: {}", tbCstmrMastr.getAcnutno(), e.getMessage());
                    }
                }
            } catch (ResourceAccessException e) {
                performOffRampRecovery(message);
                log.error("OffRamp Q API timeout or connection error: {}", e.getMessage());
            } catch (HttpClientErrorException e) {
                performOffRampRecovery(message);
                log.error("OffRamp Q API client error (4xx): Status {}, Response {}", e.getStatusCode(), e.getResponseBodyAsString());
            } catch (HttpServerErrorException e) {
                performOffRampRecovery(message);
                log.error("OffRamp Q API server error (5xx): Status {}, Response {}", e.getStatusCode(), e.getResponseBodyAsString());
            } catch (Exception e) {
                performOffRampRecovery(message);
                log.error("Unexpected error calling OffRamp Q API: {}", e.getMessage(), e);
            }
        }
        // 블록체인 거래 실패 -> 계좌 차감 
        else if (trnscSttusCd.equals("F")) {
            subtractCustomerBalance(message);
        }
    }

    private void sendSagaStateSyncMessage(TxMessage message, KafkaOperations<String, TxMessage> kafkaOperations) {

        if (!"W".equals(message.getTrnscSttusCd())) {
            TxMessage returnMessage = TxMessage.builder()
                    .command(message.getCommand())
                    .txDbId(message.getTxDbId())
                    .txSagaId(message.getTxSagaId())
                    .toBankCode(message.getFromBankCode())
                    .fromBankCode(message.getToBankCode())
                    .coinBankCode(message.getCoinBankCode())
                    .txType(message.getTxType())
                    .personId(message.getPersonId())
                    .amount(message.getAmount())
                    .timestamp(new Date())
                    .acnutno(message.getAcnutno())
                    .fromAcnutno(message.getFromAcnutno())
                    .walletDpstr(message.getWalletDpstr())
                    .fromWalletDpstr(message.getFromWalletDpstr())
                    .aliasNm(message.getAliasNm())
                    .trnscSttusCd(message.getTrnscSttusCd())
                    .requestId(message.getRequestId())
                    .txHash(message.getTxHash()).retry(0).tretInstt(bankCode)
                    .build();

            if (config.getBokCode().equals(message.getFromBankCode())
                    && config.getBokCode().equals(message.getToBankCode())) {
                if (StringUtils.isNotEmpty(message.getTretInstt()) && message.getTretInstt().length() == 3) {
                    returnMessage.setToBankCode(message.getTretInstt());
                    log.debug("[jkoh] TretInstt not empty Return Message : {}", returnMessage);
                    kafkaOperations.send(topicTxResponse + "_" + returnMessage.getToBankCode(),
                            returnMessage.getRequestId(), returnMessage);
                }
            } else if (!bankCode.equals(message.getFromBankCode())) {
                // save Transaction information to DB
                returnMessage.setToBankCode("END".equals(message.getFromBankCode()) ? message.getToBankCode()
                        : message.getTretInstt());
                log.debug("[jkoh] Return Message to other bank: {}", returnMessage);
                kafkaOperations.send(topicTxResponse + "_" + returnMessage.getToBankCode(),
                        returnMessage.getRequestId(), returnMessage);
            } else if (!bankCode.equals(message.getTretInstt()) &&
                    StringUtils.isNotEmpty(message.getTretInstt()) && message.getTretInstt().length() == 3) {
                returnMessage.setToBankCode(message.getTretInstt());
                log.debug("[jkoh] Last Return Message : {}", returnMessage);
                kafkaOperations.send(topicTxResponse + "_" + returnMessage.getToBankCode(),
                        returnMessage.getRequestId(), returnMessage);
            }
        }
    }

    private void sendVoucherMessage(TxMessage message, KafkaOperations<String, TxMessage> kafkaOperations)
            throws InterruptedException, ExecutionException, WalletSdkException {
        // 바우처 연계 : 결제 거래 성공후 승인정보전달
        if ("S".equals(message.getTrnscSttusCd()) || "F".equals(message.getTrnscSttusCd())) {
            if (CommandType.T1 == message.getCommand() && StringUtils.equals(bankCode, message.getFromBankCode())) {
                if (StringUtils.equals(TrnscType.PAYMENT.getValue(), message.getTxType())) {
                    message.setCommand(CommandType.PR);
                    message.setMessage("3 group:" + group + "  bcGroup:" + bcGroup);
                    message.setApprovalCd(message.getRequestId());
                    kafkaProducer.sendMessage(String.join(",", topicTxRequest), message, kafkaOperations);
                } else if (StringUtils.equals(TrnscType.ONLINE_PAYMENT.getValue(), message.getTxType())) {
                    message.setCommand(CommandType.PF);
                    message.setMessage("4 group:" + group + "  bcGroup:" + bcGroup);
                    message.setApprovalCd(message.getRequestId());
                    kafkaProducer.sendMessage(String.join(",", topicTxRequest), message, kafkaOperations);
                }
            }
        }
    }

    @RetryableTopic(attempts = "3", backoff = @Backoff(delay = 1000, maxDelay = 5000, multiplier = 2), kafkaTemplate = "kafkaTemplate", dltStrategy = DltStrategy.FAIL_ON_ERROR, listenerContainerFactory = "retryContainerFactory")
    @KafkaListener(id = "txResponse", topics = "${spring.kafka.topicTxResponse}" + "_"
            + "${config.bank-code}", containerFactory = "kafkaListenerContainerFactory", groupId = "${spring.kafka.group}")
    public void listenTxResponse(TxMessage message, Acknowledgment acknowledgment) {

        log.debug("[jkoh] txResponse message {} : {}", message.getRequestId(), message.toString());

        if (bankCode.equals(message.getToBankCode())) {

            // 트랜잭션 SAGA 테이블 동기화 상태 변경
            try {
                transactionSagaMapper.updateStatus(message.getTxSagaId(),
                        message.getTrnscSttusCd(), message.getTxHash(), message.getTretInstt(), null);
            } catch (Exception e) {
                log.error("transactionSagaMapper.updateStatus error: {}", e.getMessage());
            }

        }

        acknowledgment.acknowledge();

    }

    @DltHandler
    @Transactional
    public void handleDltMessge(TxMessage message, @Header(KafkaHeaders.RECEIVED_TOPIC) String dltTopic)
            throws WalletSdkException, InterruptedException, ExecutionException {
        log.info("Event dlt topic topic={}, paylod={}", dltTopic, message.toString());
        String originalTopic = dltTopic.replace("-dlt", "");

        if (Arrays.asList(dynamicTopics).contains(originalTopic)) {
            sendBankLegacyEvent(message);
        }
    }
}
```
#### 답
##### Kafka
##### How messages flow
##### The system uses Kafka to manage transactions in the CBDC system, such as:
##### Converting bank deposits to digital currency (onRamp)
##### Converting digital currency back to bank deposits (offRamp)
##### Making payments with digital currency
##### Transferring currency between users
##### For example, in a typical flow:
##### A service initiates a transaction (e.g., in `EwaAcnutManageServiceImpl`)
##### It creates transaction messages and sends them to Kafka via the `KafkaProducer`
##### The `MessageListener` consumes these messages and processes them
##### Status updates are published back to Kafka
##### For cross-bank operations, messages are routed to different bank-specific topics
##### ## Notable Kafka Implementation Details
##### **Dynamic Topics**: Topics are constructed dynamically with bank codes as suffixes (`topicTxRequest_BANKCODE`)
##### **Transaction Saga Pattern**: Used to track and manage distributed transaction states
##### **Retry Mechanism**: Uses `@RetryableTopic` for automatic retries of failed messages
##### **Dead Letter Topics**: Failed messages are sent to DLT topics after retry attempts
##### **Transactional Processing**: Uses Spring's transaction support with Kafka operations
##### Saga pattern with kafka
##### How Saga Pattern is Implemented
##### Transaction Saga Records
##### The system creates a transaction saga record for each step in a distributed transaction:
```java
TransactionSaga txSaga = TransactionSaga.builder()
    .fromAdres(message.getFrom())
    .toAdres(message.getTo())
    .fromInstt(message.getFromBankCode())
    .toInstt(message.getToBankCode())
    .trnscAmt(message.getAmount())
    .trnscHash(message.getTxHash())
    .trnscDbId(message.getTxDbId())
    .trnscSttus("W")  // Initially in "Waiting" state
    .aliasNm(message.getAliasNm())
    .sagaGrupId(requestId)  // Groups related transactions
    .trnscTypeSe(message.getCommand().name())
    .build().newId();
    ```
##### Saga Coordination with Kafka
##### In the `KafkaProducer.setSaga()` method, a unique saga group ID is generated, and all related messages are assigned this ID:
```java
public String setSaga(List<TxMessage> messages, AccessLevel walletType) {
    String requestId = generateRequestId(prefixRequestId, walletType);
    for (TxMessage message : messages) {
        // Create and store saga record
        transactionSagaMapper.insert(txSaga);
        message.setTxSagaId(txSaga.getTrnscId());
        message.setRequestId(requestId);
        // Set message sequence number
        message.setNum(num);
    }
    return requestId;
}
```
##### State Tracking and Progression
##### The `MessageListener` processes messages and updates the saga state:
```java
transactionSagaMapper.updateStatus(message.getTxSagaId(),
        message.getTrnscSttusCd(), message.getTxHash(), message.getTretInstt(), null);
```
##### Compensating Transactions? 설명이 좀 잘못된 것 같다.
### Serializable and Clonable
#### 질문: Should I implement Serializable and Cloneable for Kafka messaging?
##### TxMessage.java
```java
package kr.or.cbdc.infrastructure.queue;
import java.io.Serializable;
import java.math.BigDecimal;
import java.util.Date;
import kr.or.cbdc.infrastructure.framework.core.support.collection.BaseMap;
import kr.or.cbdc.interfaces.blockchain.CoinType;
import kr.or.cbdc.interfaces.blockchain.CommandType;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TxMessage implements Serializable , Cloneable {
    private String txSagaId;            // tx saga id
    private CommandType command;        // tx 구분
    private String  txDbId;             // DB 거래 ID ( 제조, 환수 등 ...)
    private String  toBankCode;         // 메시지 처리 Bank
    private String  fromBankCode;       // 메시지 회수 Bank
    private String  coinBankCode;       // TD발행 Bank
    private String  personId;           // 명령은 수행한 사용자
    private CoinType coin;              // 코인 타입
    private String txType;              // 거래 타입
    private String  txHash;             // 블록체인 Tx hash 값
    private String  from;               // 송신자 지갑주소
    private String  to;                 // 수신자 지갑주소
    private String  aliasNm;            // 수신인 간편주소
    private String  fromAliasNm;        // 송금인 간편주소
    private String  walletDpstr;        // 수신인 명
    private String  fromWalletDpstr;    // 송금인 명
    private String  acnutno;            // 수신 계좌번호
    private String  fromAcnutno;        // 송금 계좌번호
    private long    amount;             // 금액
    private long    trnscAfterBlce;     // 잔액
    private long    fromTrnscAfterBlce; // 잔액
    private int     retry;              // 재 전송 횟수
    private Date    timestamp;          // 거래일시
    private String  result;             // 결과메세지
    private String  tretInstt;          // 처리 참가기관 | 한국은행 전달용
    private String  trnscSttusCd;       // 처리 상태코드
    private String  requestId;          // 블록체인 요구ID
    private int     num;                // 순서
    private String  blockNo;            // 블록 번호 24.11.13 추가 : 대사작업으로 인하여
    private String txCode;              //결제승인 트랜잭션코드
    private String orderNo;             //주문번호
    private String uniqueNo;            //유니크Id
    private String customerBankCode;    //이용자 뱅크코드
    private String placeId;             //사용처 ID
    private String placeSecret;         //사용처
    private String placeNm;         //사용처
    private String ownerId;             //주문Id
    private String placeBankCode;       //사용처뱅크코드
    private String vouchId;             //바우처Id
    private long vouchAmount;           //바우처금액
    private String approvalCd;          //결제승인번호코드
    private String walletAdres;         //지갑주소
    private BaseMap voucherPlaceMap;    //사용처 장소정보
    private String message;             //메세지 정보
    private String errorMessage;             //메세지 정보
    @Override
    public TxMessage clone() {
        try {
            TxMessage clone = (TxMessage) super.clone();
            return clone;
        } catch (CloneNotSupportedException e) {
            throw new AssertionError();
        }
    }
}
```
#### 답
##### **Serializable**: Yes, implementing Serializable is appropriate for Kafka messages. Kafka's default serializers/deserializers often rely on Java serialization when working with complex objects. While Kafka has its own serialization mechanisms, having your message class implement Serializable provides flexibility.
##### **Cloneable**: This is less necessary for Kafka specifically. The Cloneable interface is more about object copying within your application rather than message transmission. Your implementation of `clone()` might be useful for your application logic (creating copies of messages before modification), but it's not directly required for Kafka messaging.
##### Interfaces
##### ### Serializable
##### **Purpose**: Marks a class as being capable of converting its instances to a byte stream (serialization) and reconstructing objects from byte streams (deserialization).
##### **How it works**: It's a marker interface with no methods, but it signals to the JVM that instances can be serialized.
##### **Usage in your context**: Allows your TxMessage objects to be converted to bytes for transmission via Kafka and reconstructed on the receiving end.
##### ### Cloneable
##### **Purpose**: Indicates that a class supports the `clone()` method for creating copies of an object.
##### **How it works**: Like Serializable, it's a marker interface, but simply implementing it doesn't provide cloning functionality - you must override `Object.clone()` as you've done.
##### **Your implementation**: Your `clone()` method performs a shallow copy (which may be sufficient if all fields are immutable or primitive).
### blockchain callback
#### EwaAcnutManageServiceImpl.java
```java
package kr.or.cbdc.application.ewa.cstmr.service;

import kr.or.bok.wallet.sdk.errorhandling.WalletSdkException;
import kr.or.bok.wallet.sdk.model.common.Signer;
import kr.or.cbdc.application.common.alias.mapper.BlockListManageMapper;
import kr.or.cbdc.application.common.alias.model.AliasResponse;
import kr.or.cbdc.application.common.alias.model.AliasSearchInfo;
import kr.or.cbdc.application.common.alias.service.BaseBlockListServiceImpl;
import kr.or.cbdc.application.common.deposit.DepositTokenServiceImpl;
import kr.or.cbdc.application.ewa.alias.service.AliasEwaBanksServiceImpl;
import kr.or.cbdc.application.ewa.common.service.EwaGWServiceImpl;
import kr.or.cbdc.application.ewa.common.dto.CbsAcnoResponseDto;
import kr.or.cbdc.application.ewa.common.dto.GwAcnoDto;
import kr.or.cbdc.application.ewa.cstmr.model.AcnutManageModel;
import kr.or.cbdc.application.ewa.policy.service.EwaPolicyManageServiceImpl;
import kr.or.cbdc.application.ewa.wallet.service.EwaWalletManageServiceImpl;
import kr.or.cbdc.config.props.ConfigProperties;
import kr.or.cbdc.domain.main.mapper.ewa.cstmr.TbEwaAcnutMastrMapper;
import kr.or.cbdc.domain.main.mapper.ewa.cstmr.TbEwaCstmrMastrMapper;
import kr.or.cbdc.domain.main.mapper.ewa.dc1.EwaDc1RedempMastrMapper;
import kr.or.cbdc.domain.main.mapper.ewa.wallet.TbEwaWalletMastrMapper;
import kr.or.cbdc.domain.main.model.com.wallet.TbWalletMastr;
import kr.or.cbdc.domain.main.model.ewa.cstmr.TbCstmrMastr;
import kr.or.cbdc.domain.main.model.ewa.dc1.Dc1RedempMastr;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.BizException;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.ErrorAssert;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.ErrorCode;
import kr.or.cbdc.infrastructure.idgen.util.IdGenerationUtil;
import kr.or.cbdc.infrastructure.mybatis.GenericMapperService;
import kr.or.cbdc.infrastructure.profile.EwaProfileCondition;
import kr.or.cbdc.infrastructure.queue.KafkaProducer;
import kr.or.cbdc.infrastructure.queue.TxMessage;
import kr.or.cbdc.infrastructure.util.TokenUtils;
import kr.or.cbdc.interfaces.blockchain.BlockChainHelper;
import kr.or.cbdc.interfaces.blockchain.CoinType;
import kr.or.cbdc.interfaces.blockchain.CommandType;
import kr.or.cbdc.interfaces.blockchain.SupportCallback;
import kr.or.cbdc.interfaces.blockchain.TrnscType;
import kr.or.cbdc.interfaces.blockchain.WalletType;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Conditional;
import org.springframework.stereotype.Service;
import com.hazelcast.core.HazelcastInstance;
import com.hazelcast.cp.lock.FencedLock;
import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Random;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import static kr.or.cbdc.application.common.deposit.DepositTokenServiceImpl.BalanceOperationType;;

/**
 * 계좌 관리 Service
 */
@Slf4j
@Service
@Conditional(EwaProfileCondition.class)
public class EwaAcnutManageServiceImpl extends SupportCallback {

    private @Autowired TbEwaCstmrMastrMapper tbEwaCstmrMastrMapper;
    private @Autowired TbEwaAcnutMastrMapper tbEwaAcnutMastrMapper;
    private @Autowired TbEwaWalletMastrMapper tbEwaWalletMastrMapper;
    private @Autowired EwaPolicyManageServiceImpl ewaPolicyManageService;
    private @Autowired EwaWalletManageServiceImpl ewaWalletManageService;
    private @Autowired AliasEwaBanksServiceImpl aliasEwaBanksService;
    private @Autowired BlockListManageMapper blockListManageMapper;
    private @Autowired BlockChainHelper _blockChain;
    private @Autowired KafkaProducer kafkaProducer;
    private @Autowired GenericMapperService genericMapperService;
    private @Autowired ConfigProperties config;
    private @Autowired BaseBlockListServiceImpl blockListService;
    private @Autowired HazelcastInstance hazelcastInstance;
    private @Autowired EwaGWServiceImpl ewaGWService;
    private @Autowired DepositTokenServiceImpl depositTokenServiceImpl;

    private static final Random rand = new Random();
    private static final ObjectMapper objectMapper = new ObjectMapper();

    private void validateInput(AcnutManageModel model) {
        ErrorAssert.notNull(model, ErrorCode.MISSING_REQUIRED_FIELD);
        ErrorAssert.notNull(model.getTbAcnutMastr(), ErrorCode.MISSING_REQUIRED_FIELD);
        ErrorAssert.notNull(model.getTbAcnutMastr().getTrnscAmt(), ErrorCode.MISSING_REQUIRED_FIELD);
    }
    
    /**
     * 계정계로 잔액 조회를 요청해서 검증
     * @param accountNo Account number to check
     * @param amount Amount to validate
     * @throws BizException if validation fails
     */
    private void validateAccountWithdrawal(String accountNo, BigDecimal amount) {
        GwAcnoDto acnoParam = GwAcnoDto.builder()
                .inqDscd("01")  // 보유계좌잔액조회
                .dpsAcno(accountNo)
                .build();
        
        JsonNode acnoResponse = ewaGWService.acno(acnoParam);
        if (acnoResponse == null) {
            throw new BizException(ErrorCode.BRIDGE_CALL_ERROR, "계정계 잔액 조회 결과가 없습니다. 게이트웨이를 확인하십시오.");
        }

        try {
            CbsAcnoResponseDto acnoResponseDto = objectMapper.treeToValue(acnoResponse, CbsAcnoResponseDto.class);
            
            if (acnoResponseDto.getErrorlist() != null && !acnoResponseDto.getErrorlist().isEmpty()) {
                log.error("계정계 잔액조회 에러: {}", acnoResponseDto.getErrorlist().get(0).getMainMsgTxt());
                throw new BizException(ErrorCode.INVALID_BALANCE_REQUIRED);
            }

            BigDecimal availableAmount = BigDecimal.valueOf(acnoResponseDto.getPayAvlAm());
            if (availableAmount.compareTo(amount) < 0) {
                log.error("계정계 출금가능금액 부족. 계좌: {}, 출금가능금액: {}, 요청금액: {}", 
                        accountNo, availableAmount, amount.intValue());
                throw new BizException(ErrorCode.INSUFFICIENT_ACCOUNT_BALANCE);
            }
        } catch (JsonProcessingException e) {
            log.error("계정계 잔액조회 응답 파싱 에러: {}", e.getMessage());
            throw new BizException(ErrorCode.PARSING_ERROR);
        }
    }

    /**
     * 전환 입금 (예금토큰 발행)
     *
     * @param model
     * @return
     * @throws WalletSdkException
     */
    public String convDeposit(AcnutManageModel model) throws WalletSdkException {
        if (lock(TokenUtils.getToken())) {
            try {
        		// step0 입력값 검증
        		validateInput(model);
                String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));

        		TbCstmrMastr tbCstmrMastr = depositTokenServiceImpl.validateCustomer(cstmrNo);

        		BigDecimal trnscAmt = depositTokenServiceImpl.validateAmount(model.getTbAcnutMastr().getTrnscAmt());
        		log.debug("[jkoh] convDeposit start cstmrNo: {} trnsAmt {}", cstmrNo, trnscAmt);
        		log.debug("[jkoh] tbCstmrMastr: {}", tbCstmrMastr);

        		ErrorAssert.isNull(blockListManageMapper.selectBlclstWallet(bankCd, cstmrNo), ErrorCode.BLACKLIST_TARGET);
                blockListService.findBlockStatus(bankCd);
        		
                BigInteger toBalance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);

        		// IF-GWS-O-006 참가기관 이용자 Core Banking(계정계) 연계 계좌의 잔액 조회
                validateAccountWithdrawal(tbCstmrMastr.getAcnutno(), trnscAmt);

                // step 2-1 통화정책 한도검증 (보유)
                ewaPolicyManageService.policyLimit(null, null, toBalance.add(trnscAmt.toBigInteger()),
                        trnscAmt.toBigInteger(), cstmrNo);

                return depositTokenServiceImpl.issueDepositToken(cstmrNo, trnscAmt);

            } finally {
                unlock(TokenUtils.getToken());
            }
        } else {
            throw new BizException(ErrorCode.DISTRIBUTED_LOCK_ERROR);
        }
    }

    /**
     * 예금 전환(예금토큰 환수)
     *
     * @param model
     * @return
     * @throws WalletSdkException
     */
    public String depositConv(AcnutManageModel model) throws WalletSdkException {
        if (lock(TokenUtils.getToken())) {
            try {
        		// step0 입력값 검증
        		validateInput(model);

                String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));
        		TbCstmrMastr tbCstmrMastr = depositTokenServiceImpl.validateCustomer(cstmrNo);
        		BigDecimal acnutnoBlce = tbCstmrMastr.getAcnutnoBlce();
        		
        		BigDecimal trnscAmt = depositTokenServiceImpl.validateAmount(model.getTbAcnutMastr().getTrnscAmt());

        		// blockListService.chkBlockStatus(cstmrNo, bankCd); 20250106_Source merge할 때 이 부분 막고 20250106_Source의 코드로 바꿈.
                blockListService.findBlockStatus(bankCd);

                // step1 지갑 검증
        		TbWalletMastr tbWalletMastr = depositTokenServiceImpl.validateWallet(WalletType.R1, tbCstmrMastr, ErrorCode.INVALID_TD_REDEMPTION_WALET);

                // step 2 예금전환액 검증
                BigInteger balance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);
                ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(balance) > 0), ErrorCode.INSUFFICIENT_BALANCE);
        		log.debug("[jkoh] OffRamp step 2 지갑, 잔액 검증 완료");
        		
        		// step3 계좌증액
        		depositTokenServiceImpl.updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
        		log.debug("[jkoh] OffRamp step 3 계좌 증액 완료");

                // step4 DC1 환수 이력 생성
                Dc1RedempMastr dc1RedempMastr = Dc1RedempMastr.builder().dc1RedempSttus("W")
                        .trgetInstt(bankCd)
                        .dc1RedempAmount(trnscAmt.longValue())
                        .applcntId(cstmrNo)
                        .build().newId();
        		try {
                    genericMapperService.insertModel(dc1RedempMastr, Dc1RedempMastr.class, EwaDc1RedempMastrMapper.class,
                        "insert");
        		} catch (Exception e) {
        			log.error("계좌({}에 대한 예금토큰 환수 내역 신규저장 에러: {}", tbCstmrMastr.getAcnutno(), e.getMessage());
        			depositTokenServiceImpl.updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.SUBTRACT);
        			throw new BizException(ErrorCode.DATA_ACCESS_ERROR, e.getMessage(), e);
        		}
        		log.debug("[jkoh] OffRamp step 4 TD 환수 이력 저장 완료");

                // kafka message 생성
                TxMessage txMessage = TxMessage.builder().command(CommandType.R1)
                        .txDbId(dc1RedempMastr.getDc1RedempId())
                        .from(tbCstmrMastr.getWalletAdres())
                        .to(tbWalletMastr.getWalletAdres())
                        .fromBankCode(bankCd)
                        .toBankCode(bankCd)
                        .amount(trnscAmt.longValue())
                        .timestamp(new Date())
                        .trnscAfterBlce(balance.subtract(trnscAmt.toBigInteger()).longValue())
                        .fromTrnscAfterBlce(balance.longValue())
                        .fromAcnutno(tbCstmrMastr.getAcnutno())
                        .fromWalletDpstr(tbCstmrMastr.getKoreanNm())
                        .walletDpstr(tbWalletMastr.getWalletNm())
                        .personId(cstmrNo)
                        .coin(CoinType.DC1)
                        .txType(TrnscType.CONVERS.getValue())
                        .retry(0).build();
                List<TxMessage> txMessages = new ArrayList<>();
                txMessages.add(txMessage);
        		
        		String requestId = null;
        		try {
        			requestId = kafkaProducer.setSaga(txMessages);
        			log.debug("[jkoh] depositConv requestId from setSage: {}", requestId);
        		} catch (Exception e) {
        			depositTokenServiceImpl.updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.SUBTRACT);
        			log.error("offRamp 트랜잭션 관리용 Saga requestId for txMessage {} 생성 에러: {}", txMessage, e);
        			throw e;
        		}

                // step 5 카프카 등록및 오류처리
                try {
                    kafkaProc(List.of(txMessage), requestId, "W");
        		} catch (BizException e) {
        			depositTokenServiceImpl.updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.SUBTRACT);
        			log.error("offRamp Kafka 메시지[SagaID({})] 송신 에러: {}", requestId, e.getMessage());
        			throw e;
        		} 
        		log.debug("[jkoh] OffRamp step 5 kafka 전송 완료");
        		
        		try {

                    // step 6 이용자지갑 > 환수지갑 : 분산원장 Call , 참가기관 단일서명
        			String result = _blockChain.sendTransaction(requestId, tbCstmrMastr.getOwner(), tbWalletMastr.getWalletAdres(),
        					trnscAmt.toBigInteger(), this.bankCd, CoinType.DC1, getCallBack(txMessages,CoinType.DC1.name()));
                    ErrorAssert.hasLength(result, ErrorCode.KAFKA_PRODUCE_ERROR);
        		} catch (WalletSdkException e) {
        			log.error("SagaId({}) 예금토큰 환수({} -> {}) 블록체인 호출 에러 {}", requestId, tbCstmrMastr.getWalletAdres(), tbWalletMastr.getWalletAdres(), e.getMessage());
                    kafkaProc(List.of(txMessage), requestId, "R");
        			// 계좌 차감 처리 (계좌잔액= 계좌잔액 - 전환입금액, DC1 = DC1잔액 + 전환입금액)
        			depositTokenServiceImpl.updateCustomerBalance(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.SUBTRACT);
        			throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
        		}
        		log.debug("[jkoh] OffRamp step 6 블록체인 요청 완료.");
        		
        		return requestId;
            } finally {
                unlock(TokenUtils.getToken());
            }
        } else {
            throw new BizException(ErrorCode.DISTRIBUTED_LOCK_ERROR);
        }
    }

    /**
     * 예금 토큰 송금 (DC1 당,타행 이체)
     *
     * @param model
     * @return
     * @throws WalletSdkException
     */
    public String depositTrans(AcnutManageModel model) throws WalletSdkException {

        String result = "";
        String requestId = "";
        String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));

        ErrorAssert.notNull(tbEwaCstmrMastrMapper.select(cstmrNo),ErrorCode.USER_ID_NOT_FOUND);
        ErrorAssert.isTrue(!StringUtils.equals(tbEwaCstmrMastrMapper.select(cstmrNo).getCstmrSttusCd() ,"1"), ErrorCode.INVALID_CUSTOMER_STATE);
        String aliasNm = model.getTbAcnutMastr().getAliasNm();
        String walletInsttCd = model.getTbAcnutMastr().getWalletInsttCd();
        BigDecimal trnscAmt = model.getTbAcnutMastr().getTrnscAmt();
        boolean extYn = StringUtils.equals(walletInsttCd, bankCd);

        // step0 입력값 검증
        ErrorAssert.hasLength(cstmrNo, ErrorCode.CUSTOMER_ID_REQUIRED);
        ErrorAssert.hasLength(aliasNm, ErrorCode.INVALID_ALIAS);
        ErrorAssert.hasLength(trnscAmt.toString(), ErrorCode.EMPTY_TRANSACTION_AMOUNT);
        ErrorAssert.isNull(blockListManageMapper.selectBlclstWallet(bankCd, cstmrNo), ErrorCode.BLACKLIST_TARGET);
        blockListService.findBlockStatus(bankCd);

        // step1 수취인조회및 검증(수취인 지갑여부)
        AliasSearchInfo aliasSearchInfo = AliasSearchInfo.builder().aliasNm(aliasNm).trgetInstt(walletInsttCd).build();

        AliasResponse response = extYn ? aliasEwaBanksService.readFromLocal(aliasSearchInfo)
                : aliasEwaBanksService.read(aliasSearchInfo);

        // step2 이용자 지갑 검증
        TbWalletMastr tbWalletMastrA = this.tbEwaWalletMastrMapper.selectWalletByWalletSe("A");
        Signer signerA = Signer.builder().walletAddress(tbWalletMastrA.getWalletAdres())
                .hdKeyAccToken(tbWalletMastrA.getHdKeyaccToken())
                .hdKeyId(tbWalletMastrA.getHdKeyid()).build();
        TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(cstmrNo);
        ErrorAssert.hasLength(tbCstmrMastr.getWalletAdres(), ErrorCode.WALLET_MISSING);
        ErrorAssert.hasLength(response.getWalletAdres(), ErrorCode.WALLET_INFO_NOT_FOUND);
        ErrorAssert.isTrue(!StringUtils.equals(tbCstmrMastr.getWalletAdres(), response.getWalletAdres()), ErrorCode.WRONG_TRANSFER_REQUIRED);
        ErrorAssert.hasLength(tbCstmrMastr.getWalletAdres(), ErrorCode.WALLET_MISSING);
        ErrorAssert.hasLength(response.getWalletAdres(), ErrorCode.WALLET_INFO_NOT_FOUND);
        ErrorAssert.isTrue(!StringUtils.equals(tbCstmrMastr.getWalletAdres(), response.getWalletAdres()), ErrorCode.WRONG_TRANSFER_REQUIRED);


        // step3 DC1 차감(송금자) > DC1 증액(수취인)
        BigInteger fromBalance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);
        BigInteger toBalance = _blockChain.getBalance(response.getWalletAdres(), bankCd, CoinType.DC1);
        ErrorAssert.isTrue(fromBalance.compareTo(BigInteger.ZERO) > 0, ErrorCode.INSUFFICIENT_BALANCE);
        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.TRANS_AMOUNT_EXCEEDS_BALANCE);
        ErrorAssert.isTrue(fromBalance.compareTo(BigInteger.ZERO) > 0, ErrorCode.INSUFFICIENT_BALANCE);
        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.TRANS_AMOUNT_EXCEEDS_BALANCE);


        // step 3-1 통화정책 한도검증 (1회 , 1일)
        ewaPolicyManageService.policyLimit(trnscAmt, ewaWalletManageService.selectAmtPerDay(cstmrNo), null);
        ewaPolicyManageService.policyTransferLimit(ewaWalletManageService.selectAmtCntPerDay(cstmrNo));

        /*
         * kafka message 생성
         * (당,티헹)
         * kafka message 0 이용자 >> 이용자 (거래내역용)
         * (티헹)
         * kafka message 1 이용자 >> TD환수
         * kafka message 2 출금은행 당좌 >> 입금은행 당좌
         * kafka message 3 출금은행 TD 발행 >> 이용자
         */
        List<TxMessage> txMessages = new ArrayList<>();
        TxMessage txMessage = TxMessage.builder().command(CommandType.T1)
                .txDbId(IdGenerationUtil.createUid("TB_DC_TRANS_MASTR"))
                .from(tbCstmrMastr.getWalletAdres())
                .to(response.getWalletAdres())
                .fromBankCode(bankCd)
                .toBankCode(walletInsttCd)
                .amount(trnscAmt.longValue())
                .timestamp(new Date())
                .fromTrnscAfterBlce(fromBalance.subtract(trnscAmt.toBigInteger()).longValue())
                .personId(cstmrNo)
                .coin(CoinType.DC1)
                .retry(0).build();
        txMessages.add(txMessage);

        // kafka message 0 이용자 >> 이용자 (거래내역용)
        txMessages.get(0).setFromAcnutno(tbCstmrMastr.getAcnutno());
        txMessages.get(0).setAcnutno(response.getAcnutno());
        txMessages.get(0).setAliasNm(tbCstmrMastr.getAliasNm());
        txMessages.get(0).setFromAliasNm(aliasNm);
        txMessages.get(0).setWalletDpstr(response.getPersonNm());
        txMessages.get(0).setFromWalletDpstr(tbCstmrMastr.getKoreanNm());
        txMessages.get(0).setTxType(TrnscType.TRANSFER.getValue());

        // step 5 당행 송금
        if (extYn) {
            requestId = kafkaProducer.setSaga(txMessages);

            // step 5 카프카 등록및 오류처리
            try {
                kafkaProc(txMessages, requestId, "W");

                txMessage.setTrnscAfterBlce(toBalance.add(trnscAmt.toBigInteger()).longValue());
                result = _blockChain.sendLimitTransaction(requestId, tbCstmrMastr.getOwner(), response.getWalletAdres(),
                        trnscAmt.toBigInteger(), bankCd, CoinType.DC1, getCallBack(txMessages, CoinType.DC1.name()));

            } catch (Exception e) {
                kafkaProc(txMessages, requestId, "R");
                throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
            }

        } else {// 타행 송금

            txMessages.add(txMessage.clone());
            txMessages.add(txMessage.clone());
            txMessages.add(txMessage.clone());

            // kafka message 1 이용자 >> TD환수
            String tdRedempWalletAddr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.R1.name()).getWalletAdres();
            txMessages.get(1).setCommand(CommandType.R1);
            txMessages.get(1).setTo(tdRedempWalletAddr);
            txMessages.get(1).setToBankCode(bankCd);

            // kafka message 2 출금은행 당좌 >> 입금은행 당좌
            String cWalletAddr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.C.name()).getWalletAdres();
            BigInteger cBlce = _blockChain.getPrivateBalance(signerA, cWalletAddr, bankCd, CoinType.CBDC);
            ErrorAssert.isTrue(cBlce.compareTo(BigInteger.valueOf(trnscAmt.longValue()))>=0, ErrorCode.INSUFFICIENT_BALANCE);

            String toCWalletAddr = ewaWalletManageService.selectExtWalletAddr(WalletType.C.name(), walletInsttCd);
            txMessages.get(2).setCommand(CommandType.T);
            txMessages.get(2).setFrom(cWalletAddr);
            txMessages.get(2).setTo(toCWalletAddr);
            txMessages.get(2).setFromBankCode(config.getBokCode());
            txMessages.get(2).setToBankCode(config.getBokCode());
            txMessages.get(2).setFromTrnscAfterBlce(0);
            txMessages.get(2).setCoin(CoinType.CBDC);
            txMessages.get(2).setTretInstt(bankCd);
            txMessages.get(2).setTxType(TrnscType.CBDCTRANS.getValue());

            // kafka message 3 출금은행 TD 발행 >> 이용자
            String toIWalletAddr = ewaWalletManageService.selectExtWalletAddr(WalletType.I1.name(), walletInsttCd);
            txMessages.get(3).setCommand(CommandType.I1);
            txMessages.get(3).setFrom(toIWalletAddr);
            txMessages.get(3).setFromBankCode(walletInsttCd);
            txMessages.get(3).setTretInstt(bankCd);
            txMessages.get(3).setFromTrnscAfterBlce(0);

            requestId = kafkaProducer.setSaga(txMessages);

            // step 5 카프카 등록및 오류처리
            try {
                kafkaProc(txMessages, requestId, "W");

                result = _blockChain.sendExtLimitTransaction(requestId, tbCstmrMastr.getOwner(), bankCd,
                        walletInsttCd,
                        response.getWalletAdres(), trnscAmt.toBigInteger(),
                        getCallBack(txMessages, CoinType.DC1.name()));

            } catch (Exception e) {
                kafkaProc(txMessages, requestId, "R");
                throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
            }
        }

        ErrorAssert.hasLength(result, ErrorCode.BLOCKCHAIN_TRANSFER_ERROR);
        ErrorAssert.hasLength(result, ErrorCode.BLOCKCHAIN_TRANSFER_ERROR);

        return requestId;
    }

    /**
     * 예금 토큰 결제 (DC1 예금 토큰 결제)
     *
     * @param model
     * @return
     * @throws WalletSdkException
     */
    public String payment(AcnutManageModel model) throws WalletSdkException {

        String result = "";
        String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));
        ErrorAssert.notNull(tbEwaCstmrMastrMapper.select(cstmrNo), ErrorCode.CUSTOMER_NOT_FOUND,cstmrNo);
        ErrorAssert.isTrue(!StringUtils.equals(tbEwaCstmrMastrMapper.select(cstmrNo).getCstmrSttusCd() ,"1"), ErrorCode.INVALID_CUSTOMER_STATE);
        String aliasNm = model.getTbAcnutMastr().getAliasNm();
        String walletInsttCd = model.getTbAcnutMastr().getWalletInsttCd();
        BigDecimal trnscAmt = model.getTbAcnutMastr().getTrnscAmt();
        boolean extYn = StringUtils.equals(walletInsttCd, bankCd);

        // step0 입력값 검증
        ErrorAssert.hasLength(cstmrNo, ErrorCode.CUSTOMER_ID_REQUIRED);
        ErrorAssert.hasLength(aliasNm, ErrorCode.INVALID_ALIAS);
        ErrorAssert.hasLength(trnscAmt.toString(), ErrorCode.INVALID_AMOUNT);
        ErrorAssert.isNull(blockListManageMapper.selectBlclstWallet(bankCd, cstmrNo), ErrorCode.BLACKLIST_TARGET);
        blockListService.findBlockStatus(bankCd);

        // step1 수취인조회및 검증(수취인 지갑여부)
        AliasSearchInfo aliasSearchInfo = AliasSearchInfo.builder().aliasNm(aliasNm).trgetInstt(walletInsttCd).build();

        AliasResponse response = extYn ? aliasEwaBanksService.readFromLocal(aliasSearchInfo)
                : aliasEwaBanksService.read(aliasSearchInfo);

        // step2 이용자 지갑 검증
        TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(cstmrNo);
        ErrorAssert.hasLength(tbCstmrMastr.getWalletAdres(), ErrorCode.WALLET_MISSING);
        ErrorAssert.hasLength(response.getWalletAdres(), ErrorCode.INVALID_WALLET_INFO_ERROR);
        ErrorAssert.isTrue(!StringUtils.equals(tbCstmrMastr.getWalletAdres(), response.getWalletAdres()),ErrorCode.WRONG_PAYMENT_REQUIRED);


        // step3 DC1 차감(송금자) > DC1 증액(결제처)
        BigInteger fromBalance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);
        BigInteger toBalance = _blockChain.getBalance(response.getWalletAdres(), bankCd, CoinType.DC1);
        ErrorAssert.isTrue(fromBalance.compareTo(BigInteger.ZERO) > 0, ErrorCode.INSUFFICIENT_BALANCE);
        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.PAYMENT_AMOUNT_EXCEEDS_BALANCE);
        ErrorAssert.isTrue(fromBalance.compareTo(BigInteger.ZERO) > 0, ErrorCode.INSUFFICIENT_BALANCE);
        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.PAYMENT_AMOUNT_EXCEEDS_BALANCE);



        /*
         * kafka message 생성
         * (당,티헹)
         * kafka message 0 이용자 >> 이용자 (거래내역용)
         * (티헹)
         * kafka message 1 이용자 >> TD환수
         * kafka message 2 출금은행 당좌 >> 입금은행 당좌
         * kafka message 3 출금은행 TD 발행 >> 이용자
         */
        List<TxMessage> txMessages = new ArrayList<>();
        TxMessage txMessage = TxMessage.builder().command(CommandType.T1)
                .txDbId(IdGenerationUtil.createUid("TB_DC_TRANS_MASTR"))
                .from(tbCstmrMastr.getWalletAdres())
                .to(response.getWalletAdres())
                .fromBankCode(bankCd)
                .toBankCode(walletInsttCd)
                .amount(trnscAmt.longValue())
                .timestamp(new Date())
                .fromTrnscAfterBlce(fromBalance.subtract(trnscAmt.toBigInteger()).longValue())
                .personId(cstmrNo)
                .coin(CoinType.DC1)
                .retry(0).build();
        txMessages.add(txMessage);

        // kafka message 0 이용자 >> 이용자 (거래내역용)
        txMessages.get(0).setFromAcnutno(tbCstmrMastr.getAcnutno());
        txMessages.get(0).setAcnutno(response.getAcnutno());
        txMessages.get(0).setAliasNm(tbCstmrMastr.getAliasNm());
        txMessages.get(0).setFromAliasNm(aliasNm);
        txMessages.get(0).setWalletDpstr(response.getPersonNm());
        txMessages.get(0).setFromWalletDpstr(tbCstmrMastr.getKoreanNm());
        txMessages.get(0).setTxType(TrnscType.PAYMENT.getValue());

        String requestId = "";

        // step 5 당행 결제
        if (extYn) {
            requestId = kafkaProducer.setSaga(txMessages);

            // step 5 카프카 등록및 오류처리
            try {
                kafkaProc(txMessages, requestId, "W");

                txMessage.setTrnscAfterBlce(toBalance.add(trnscAmt.toBigInteger()).longValue());
                result = _blockChain.sendTransaction(requestId, tbCstmrMastr.getOwner(), response.getWalletAdres(),
                        trnscAmt.toBigInteger(), bankCd, CoinType.DC1, getCallBack(txMessages, CoinType.DC1.name()));
            } catch (Exception e) {
                kafkaProc(List.of(txMessage), requestId, "R");
                throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
            }

        } else {// 타행 결제

            txMessages.add(txMessage.clone());
            txMessages.add(txMessage.clone());
            txMessages.add(txMessage.clone());

            // kafka message 1 이용자 >> TD환수
            String tdRedempWalletAddr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.R1.name()).getWalletAdres();
            txMessages.get(1).setCommand(CommandType.R1);
            txMessages.get(1).setTo(tdRedempWalletAddr);
            txMessages.get(1).setToBankCode(bankCd);

            // kafka message 2 출금은행 당좌 >> 입금은행 당좌
            String cWalletAddr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.C.name()).getWalletAdres();
            String toCWalletAddr = ewaWalletManageService.selectExtWalletAddr(WalletType.C.name(), walletInsttCd);
            txMessages.get(2).setCommand(CommandType.T);
            txMessages.get(2).setFrom(cWalletAddr);
            txMessages.get(2).setTo(toCWalletAddr);
            txMessages.get(2).setFromBankCode(config.getBokCode());
            txMessages.get(2).setToBankCode(config.getBokCode());
            txMessages.get(2).setTretInstt(bankCd);
            txMessages.get(2).setFromTrnscAfterBlce(0);
            txMessages.get(2).setTxType(TrnscType.CBDCTRANS.getValue());
            txMessages.get(2).setCoin(CoinType.CBDC);

            // kafka message 3 출금은행 TD 발행 >> 이용자
            String toIWalletAddr = ewaWalletManageService.selectExtWalletAddr(WalletType.I1.name(), walletInsttCd);
            txMessages.get(3).setCommand(CommandType.I1);
            txMessages.get(3).setFrom(toIWalletAddr);
            txMessages.get(3).setFromBankCode(walletInsttCd);
            txMessages.get(3).setTretInstt(bankCd);
            txMessages.get(3).setFromTrnscAfterBlce(0);

            requestId = kafkaProducer.setSaga(txMessages);

            // step 5 카프카 등록및 오류처리
            try {
                kafkaProc(txMessages, requestId, "W");

                result = _blockChain.sendExtTransaction(requestId, tbCstmrMastr.getOwner(), bankCd, walletInsttCd,
                        response.getWalletAdres(), trnscAmt.toBigInteger(),
                        getCallBack(txMessages, CoinType.DC1.name()));

            } catch (Exception e) {
                kafkaProc(txMessages, requestId, "R");
                throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
            }
        }

        ErrorAssert.hasLength(result, ErrorCode.KAFKA_PRODUCE_ERROR);

        return requestId;
    }

    private void kafkaProc(List<TxMessage> txMessages, String requestId, String trnscSttusCd) {

        txMessages.forEach(tx -> {
            tx.setTrnscSttusCd(trnscSttusCd);
            tx.setRequestId(requestId);
        });

        try {
            kafkaProducer.send(topicTxRequest, txMessages);
        } catch (InterruptedException | ExecutionException e) {
            throw new BizException(ErrorCode.SERVER_ERROR  ,  requestId ,  e);
        } catch (Exception e) {
            throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);

        }
        ErrorAssert.hasLength(requestId, ErrorCode.KAFKA_PRODUCE_ERROR);
    }

    /**
     * 계좌인증정보입력(검증) 워드3+난수3 자리생성
     *
     * @param model
     * @return
     */
    public String accountValid(AcnutManageModel model) {

        String[] words = { "송아리", "도사리", "미리내", "가루비", "도둑눈", "산돌림", "나비잠", "흰여울", "그루잠", "희나리" };

        StringBuilder result = new StringBuilder();
        result.append(words[rand.nextInt(words.length)]);

        ErrorAssert.isTrue(tbEwaAcnutMastrMapper.accountValid(model.getTbAcnutMastr()) != null,
                ErrorCode.WALLET_INFO_NOT_FOUND);

        // [Mockup][IF-GWS-O-007
        // ewaBridgeServiceImpl.validityCheck();

        return result.append(rand.nextInt(900) + 100).toString();
    }

    /**
     * 계좌 상세 조회
     *
     * @param cstmrNo
     * @return
     */
    public AcnutManageModel read(String cstmrNo) {

        AcnutManageModel model = new AcnutManageModel();
        model.setTbAcnutMastr(tbEwaAcnutMastrMapper.select(cstmrNo));
        return model;
    }

    public boolean lock(String userId) {
    	log.error("hazelcastInstance lock ::: {}", userId);
        FencedLock lock = hazelcastInstance.getCPSubsystem().getLock("lock:" + userId);
        return lock.tryLock(10, TimeUnit.SECONDS);
    }

    public void unlock(String userId) {
    	log.error("hazelcastInstance unlock :::: {}", userId);
        FencedLock lock = hazelcastInstance.getCPSubsystem().getLock("lock:" + userId);
        lock.unlock();
    }
}
```
#### SupportCallback.java
```java
package kr.or.cbdc.interfaces.blockchain;

import kr.or.bok.wallet.sdk.errorhandling.WalletSdkException;
import kr.or.cbdc.application.common.coin.mapper.DigitalCoinMapper;
import kr.or.cbdc.application.common.coin.model.DigitalCoinModel;
import kr.or.cbdc.config.props.ConfigProperties;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.BizException;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.ErrorAssert;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.ErrorCode;
import kr.or.cbdc.infrastructure.queue.KafkaProducer;
import kr.or.cbdc.infrastructure.queue.TxMessage;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.ObjectUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.atomic.AtomicReference;

@Slf4j
public class SupportCallback {

    @Value(value = "${config.bank-code}")
    protected String bankCd;

    @Value(value = "${spring.kafka.topicTxRequest}")
    protected String topicTxRequest;

    protected @Autowired DigitalCoinMapper digitalCoinMapper;
    protected @Autowired KafkaProducer kafkaProducer;
    protected @Autowired ConfigProperties config;

    protected CallBack<Pending, Confirmed, Failed> getCallBack(List<TxMessage> txMessages, String coin) {

        return new CallBack<Pending, Confirmed, Failed>() {
            @Override
            public void onSuccessHash(Pending result) {
                log.debug("onSuccessHash : {}", result.toString());
                ErrorAssert.hasLength(result.getTransactionHash(), ErrorCode.TRANSACTION_HASH_MISSING);

                // 거래 해시 저장
                txMessages.stream().forEach(tx -> {
                    tx.setTxHash(result.getTransactionHash());
                    tx.setRequestId(result.getRequestId());
                    tx.setTrnscSttusCd("H");
                });
                try {
                    kafkaProducer.send(topicTxRequest, txMessages);
                } catch (InterruptedException | ExecutionException | WalletSdkException e) {
                    Thread.currentThread().interrupt();
                    log.error("onSuccess Exception : {} ", e.getMessage());
                }

            }

            @Override
            public void onSuccessFinal(Confirmed result) throws WalletSdkException {
                log.debug("onSuccessFinal : {}", result.toString());

                // 거래 성공 저장
                txMessages.stream().forEach(tx -> {
                    tx.setRequestId(result.getRequestId());
                    tx.setTrnscSttusCd("S");
                    tx.setBlockNo(result.getBlockNumber());
                });

                // 성공 카프카
                try {
                    kafkaProducer.send(topicTxRequest, txMessages);
                } catch (InterruptedException | ExecutionException e) {
                    Thread.currentThread().interrupt();
                    log.error("onSuccess Exception : {} ", e.getMessage());
                }
            }

            @Override
            @Transactional(noRollbackFor = { BizException.class })
            public void onFailure(Failed e) {

                DigitalCoinModel dcModel = digitalCoinMapper.selectOne(coin,
                        (coin.equals(CoinType.CBDC.name()) || coin.equals(CoinType.VC.name())) ? null : bankCd);

                String errorMessage = e.handleErrorMessage(dcModel.getContractAdres());
                log.error("onFailure : {} ", errorMessage);

                // 실패 카프카
                txMessages.stream().forEach(tx -> {
                    tx.setRequestId(e.getRequestId());
                    tx.setTrnscSttusCd("F");
                });

                try {
                    kafkaProducer.send(topicTxRequest, txMessages);
                } catch (InterruptedException | ExecutionException | WalletSdkException e2) {
                    Thread.currentThread().interrupt();
                    log.error("onFailure Exception : {} ", e2.getMessage());
                }

            }
        };
    }

    protected CallBack<Pending, Confirmed, Failed> syncCallBack(String coin, CompletableFuture<Confirmed> resultFuture) {

        AtomicReference<Pending> pendingResultRef = new AtomicReference<>();

        return new CallBack<Pending, Confirmed, Failed>() {
            @Override
            public void onSuccessHash(Pending result) {
                log.debug("onSuccessHash : {}", result);
                if (ObjectUtils.isEmpty(result) ||ObjectUtils.isEmpty(result.getTransactionHash())  ) {
                    resultFuture.completeExceptionally(new IllegalStateException("트랜잭션 HASH 값이 없습니다."));
                } else {
                    pendingResultRef.set(result);
                }

            }

            @Override
            public void onSuccessFinal(Confirmed result) throws WalletSdkException {
                log.debug("onSuccessFinal : {}", result.toString());
                if (ObjectUtils.isEmpty(pendingResultRef) || ObjectUtils.isEmpty(pendingResultRef.get()) ) {
                    log.error("onSuccessFinal : {} : {}", result.toString(), "Pending시 해시값을 읽지 못했습니다.");
                    resultFuture.completeExceptionally(new IllegalStateException("Pending시 해시값을 읽지 못했습니다."));
                } else {
                    Pending pendingResult = pendingResultRef.get();
                    result.setTransactionHash(pendingResult.getTransactionHash());
                    resultFuture.complete(result);
                }

            }

            @Override
            @Transactional(noRollbackFor = { BizException.class })
            public void onFailure(Failed e) {

                try {
                    DigitalCoinModel dcModel = digitalCoinMapper.selectOne(coin,
                            coin.equals(CoinType.CBDC.name()) ? null : bankCd);

                    String errorMessage = e.handleErrorMessage(dcModel.getContractAdres());
                    log.error("onFailure : {} ", errorMessage);

                    resultFuture.completeExceptionally(new IllegalStateException(errorMessage));
                } catch ( BizException ex) {
                    resultFuture.completeExceptionally(new IllegalStateException(ex.getMessage()));

                }

            }
        };
    }
}
-------------
package kr.or.cbdc.interfaces.blockchain;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
public class CheckCallBack {

    private final Map<String, CallBack<Pending, Confirmed, Failed>> callbackMap = new ConcurrentHashMap<>();

    @PostConstruct
    private void init() {
        log.debug("init callbackMap[{}][{}][{}]",System.identityHashCode(this), System.identityHashCode(callbackMap), callbackMap.toString());

    }

    public void put(String key, CallBack<Pending, Confirmed, Failed> callback) {
        callbackMap.put(key, callback);
        log.debug("put callbackMap[{}][{}]",System.identityHashCode(callbackMap), callbackMap.toString());
    }

    public CallBack<Pending, Confirmed, Failed> get(String key) {
        log.debug("get callbackMap[{}][{}]",System.identityHashCode(callbackMap), callbackMap.toString() );
        return callbackMap.get(key);
    }

    public void remove(String key) {
        log.debug("remove callbackMap[{}][{}]",System.identityHashCode(callbackMap), callbackMap.toString() );
        callbackMap.remove(key);
    }

}
```
#### BlockchainListener.java
```java
package kr.or.cbdc.infrastructure.queue;

import org.apache.commons.lang3.ObjectUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.annotation.DltHandler;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.annotation.RetryableTopic;
import org.springframework.kafka.retrytopic.DltStrategy;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.kafka.support.KafkaHeaders;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.retry.annotation.Backoff;
import org.springframework.stereotype.Component;
import com.fasterxml.jackson.core.type.TypeReference;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import io.jsonwebtoken.lang.Assert;
import kr.or.bok.wallet.sdk.constants.KafkaResponseStatus;
import kr.or.bok.wallet.sdk.constants.KafkaResponseType;
import kr.or.bok.wallet.sdk.model.response.kafka.WalletCoreKafkaResponse;
import kr.or.bok.wallet.sdk.model.response.kafka.results.DeployCaWalletTxConfirmedResults;
import kr.or.bok.wallet.sdk.model.response.kafka.results.DeployContractTxConfirmedResults;
import kr.or.bok.wallet.sdk.model.response.kafka.results.TxConfirmedAndReceiptFailedResults;
import kr.or.bok.wallet.sdk.model.response.kafka.results.TxConfirmedResults;
import kr.or.bok.wallet.sdk.model.response.kafka.results.TxFailedResults;
import kr.or.bok.wallet.sdk.model.response.kafka.results.TxPendingResults;

import kr.or.cbdc.interfaces.blockchain.CheckCallBack;
import kr.or.cbdc.interfaces.blockchain.Confirmed;
import kr.or.cbdc.interfaces.blockchain.Failed;
import kr.or.cbdc.interfaces.blockchain.Pending;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Component
public class BlockChainListener {

    private final ObjectMapper mapper;
    private final CheckCallBack checkCallBack;    

    @Autowired
    public BlockChainListener(ObjectMapper mapper, CheckCallBack checkCallBack) {
        this.mapper = mapper;
        this.checkCallBack = checkCallBack;
    }

    @RetryableTopic(attempts = "3", backoff = @Backoff(delay = 1000, maxDelay = 5000, multiplier = 2), kafkaTemplate = "kafkaBcTemplate", dltStrategy = DltStrategy.FAIL_ON_ERROR, listenerContainerFactory = "retryBlockChainContainerFactory")
    @KafkaListener(id = "txBlockChainListen", topics = "${spring.kafka.topicTxBlockChain}", containerFactory = "kafkaListenerBlockChainContainerFactory", groupId = "${spring.kafka.bc-group}${CBDC_APP_ID:01}")
    public void listenBlockChain(String message, Acknowledgment acknowledgment) throws Exception {

        Assert.hasLength(message,"Invalid message received");
        WalletCoreKafkaResponse<JsonNode> commonResponse = mapper.readValue(
            message,
            new TypeReference<WalletCoreKafkaResponse<JsonNode>>() {}
        );
        log.debug("[jkoh] listenBlockChain's commonResponse: {}", commonResponse);

        if (ObjectUtils.isNotEmpty(checkCallBack.get(commonResponse.getRequestId()))) {

            switch (commonResponse.getStatus()) {
                case KafkaResponseStatus.PENDING:
                   TxPendingResults pendingStatusResponse = mapper.treeToValue(commonResponse.getResults(),TxPendingResults.class);
                    switch (commonResponse.getResponseType()) {
                        case KafkaResponseType.CA_CONTRACT_UPGRADE_WALLET:
                        case KafkaResponseType.CA_WALLET_CREATE_NEW_WALLET:
                        case KafkaResponseType.CA_WALLET_DEPLOY_NEW_VERSION_IMPL_CONTRACT:
                        case KafkaResponseType.CA_WALLET_EXECUTE_TRANSACTION:
                        case KafkaResponseType.CA_WALLET_UPDATE_OWNER:
                        case KafkaResponseType.CA_WALLET_UPDATE_STATUS:
                        case KafkaResponseType.DEPLOY_CONTRACT:
                        case KafkaResponseType.EOA_WALLET_SEND_TRANSACTION:
                        case KafkaResponseType.MPC_WALLET_SEND_SIGNED_TRANSACTION:
                            log.info("kafka message pendingStatusResponse: ");
                            Pending pending = Pending.builder()
                                    .rawTransaction(pendingStatusResponse.getRawTransaction())
                                    .transactionHash(pendingStatusResponse.getTransactionHash())
                                    .requestId(commonResponse.getRequestId())
                                    .build();
                            if (!ObjectUtils.isEmpty(checkCallBack.get(commonResponse.getRequestId()))) {
                                checkCallBack.get(commonResponse.getRequestId()).onSuccessHash(pending);
                            }
                            break;
                        default:
                            log.error("정의되지 않은 카프카 응답형식 에러 \"response type\": " + commonResponse.getResponseType());

                    }
                    break;
                case KafkaResponseStatus.CONFIRMED:
                    log.debug("[jkoh] commonResponse's status is CONFIRMED");
                    switch (commonResponse.getResponseType()) {
                        case KafkaResponseType.CA_WALLET_CREATE_NEW_WALLET:
                            DeployCaWalletTxConfirmedResults confirmedStatusResponseWithCaWalletAddress = mapper.treeToValue(commonResponse.getResults(), 
                                           DeployCaWalletTxConfirmedResults.class);
                            log.info("kafka message confirmedStatusResponseWithCaWalletAddress: {} ",
                            commonResponse.getRequestId());
                            Confirmed confirmed = Confirmed.builder()
                                    .blockNumber(String.valueOf(
                                            confirmedStatusResponseWithCaWalletAddress.getBlockNumber()))
                                    .caAddress(confirmedStatusResponseWithCaWalletAddress.getCaWalletAddress())
                                    .requestId(commonResponse.getRequestId())
                                    .build();
                            if (!ObjectUtils.isEmpty(
                                    checkCallBack.get(commonResponse.getRequestId()))) {

                                checkCallBack.get(commonResponse.getRequestId())
                                        .onSuccessFinal(confirmed);
                                checkCallBack.remove(commonResponse.getRequestId());
                            }
                            break;
                        case KafkaResponseType.DEPLOY_CONTRACT:
                        case KafkaResponseType.CA_WALLET_DEPLOY_NEW_VERSION_IMPL_CONTRACT:
                            DeployContractTxConfirmedResults confirmedStatusResponseWithContractAddress = mapper
                                    .treeToValue(commonResponse.getResults(),DeployContractTxConfirmedResults.class);
                            log.info("kafka message confirmedStatusResponseWithContractAddress: ");
                            confirmed = Confirmed.builder()
                                    .blockNumber(String.valueOf(
                                            confirmedStatusResponseWithContractAddress.getBlockNumber()))
                                    .caAddress(confirmedStatusResponseWithContractAddress.getContractAddress())
                                    .requestId(commonResponse.getRequestId())
                                    .build();
                            if (!ObjectUtils.isEmpty(
                                    checkCallBack.get(commonResponse.getRequestId()))) {

                                checkCallBack.get(commonResponse.getRequestId())
                                        .onSuccessFinal(confirmed);
                                checkCallBack.remove(commonResponse.getRequestId());
                            }

                            break;
                        case KafkaResponseType.CA_CONTRACT_UPGRADE_WALLET:
                        case KafkaResponseType.CA_WALLET_EXECUTE_TRANSACTION:
                        case KafkaResponseType.CA_WALLET_UPDATE_OWNER:
                        case KafkaResponseType.CA_WALLET_UPDATE_STATUS:
                        case KafkaResponseType.EOA_WALLET_SEND_TRANSACTION:
                        case KafkaResponseType.MPC_WALLET_SEND_SIGNED_TRANSACTION:
                            log.debug("[jkoh] CONFIRMED commonResponse responseType: {}", commonResponse.getResponseType());
                            TxConfirmedResults confirmedStatusResponse = mapper.treeToValue(
                                commonResponse.getResults(),TxConfirmedResults.class);
                            log.info("kafka message confirmedStatusResponseWithContractAddress: {}:[]",
                            commonResponse.getRequestId(),
                                    checkCallBack.get(commonResponse.getRequestId()));
                            confirmed = Confirmed.builder()
                                    .blockNumber(String.valueOf(confirmedStatusResponse.getBlockNumber()))
                                    .requestId(commonResponse.getRequestId())
                                    .build();
                            if (!ObjectUtils.isEmpty(checkCallBack.get(commonResponse.getRequestId()))) {
                                checkCallBack.get(commonResponse.getRequestId()).onSuccessFinal(confirmed);
                                checkCallBack.remove(commonResponse.getRequestId());
                            }

                            break;
                        default:
                            log.error("정의되지 않은 카프카 응답형식 에러 \"response type\": " + commonResponse.getResponseType());
                    }
                    break;
                case KafkaResponseStatus.FAILED:
                    log.debug("[jkoh] commonResponse fail responseType: {}", commonResponse.getResponseType());
                    TxFailedResults failedStatusResponse = mapper.treeToValue(commonResponse.getResults(),
                            TxFailedResults.class);
                    switch (commonResponse.getResponseType()) {
                        case KafkaResponseType.CA_CONTRACT_UPGRADE_WALLET:
                        case KafkaResponseType.CA_WALLET_CREATE_NEW_WALLET:
                        case KafkaResponseType.CA_WALLET_DEPLOY_NEW_VERSION_IMPL_CONTRACT:
                        case KafkaResponseType.CA_WALLET_EXECUTE_TRANSACTION:
                        case KafkaResponseType.CA_WALLET_UPDATE_OWNER:
                        case KafkaResponseType.CA_WALLET_UPDATE_STATUS:
                        case KafkaResponseType.DEPLOY_CONTRACT:
                        case KafkaResponseType.EOA_WALLET_SEND_TRANSACTION:
                        case KafkaResponseType.MPC_WALLET_SEND_SIGNED_TRANSACTION:
                            String errorMessage = failedStatusResponse.getErrorMessage();
                            log.error("블록체인 에러 [RequestId]:{}, [errorMsg]: {}", commonResponse.getRequestId(), errorMessage);
                            /*
                             * 스마트 컨트랙트 에러 메세지 해석
                             * - KafkaResponseStatus.FAILED 카프카 메세지 타입의 경우 errorMessage 에 컨트랙트 에러 정보를 닮을 수
                             * 있다.
                             * - 그런 경우 에러 메세지는 "0x"으로 시작한다.
                             * - 컨슈머 로직에서 Request ID 에 대항하는 ***컨트랙트 주소***를 알아야 에러 메세지를 해석할 수 있다.
                             * - 해당 컨트랙트 주소에 대한 abi 정보 또한 contract_address_abi 테이블에 존재해야한다.
                             */
                            // String contradctAddress = "0xcd7b18a8adc97d783511c63bf5c505f059348b57";
                            // if (errorMessage.startsWith("0x") && errorMessage.length() >= 10) {
                            // DecodedContractError decodedContractError = AbiParser
                            // .decodeContractErrorMessage(contradctAddress, errorMessage);
                            // log.info("decoded contract error message:");
                            // }

                            Failed failed = Failed.builder().errorMessage(errorMessage)
                                    .returnCode(failedStatusResponse.getReturnCode())
                                    .blockNumber(commonResponse.getRequestId())
                                    .requestId(commonResponse.getRequestId())
                                    .build();
                            if (!ObjectUtils.isEmpty(checkCallBack.get(commonResponse.getRequestId()))) {
                                checkCallBack.get(commonResponse.getRequestId()).onFailure(failed);
                                checkCallBack.remove(commonResponse.getRequestId());
                            }

                            break;
                        default:
                            log.error("정의되지 않은 카프카 응답형식 에러 \"response type\": " + commonResponse.getResponseType());
                    }
                    break;
                case KafkaResponseStatus.CONFIRMED_AND_RECEIPT_FAILED:
                    TxConfirmedAndReceiptFailedResults confirmedAndReceiptFailedStatusResponse = mapper
                            .treeToValue(commonResponse.getResults(),
                                    TxConfirmedAndReceiptFailedResults.class);
                    switch (commonResponse.getResponseType()) {
                        case KafkaResponseType.CA_CONTRACT_UPGRADE_WALLET:
                        case KafkaResponseType.CA_WALLET_CREATE_NEW_WALLET:
                        case KafkaResponseType.CA_WALLET_DEPLOY_NEW_VERSION_IMPL_CONTRACT:
                        case KafkaResponseType.CA_WALLET_EXECUTE_TRANSACTION:
                        case KafkaResponseType.CA_WALLET_UPDATE_OWNER:
                        case KafkaResponseType.CA_WALLET_UPDATE_STATUS:
                        case KafkaResponseType.DEPLOY_CONTRACT:
                        case KafkaResponseType.EOA_WALLET_SEND_TRANSACTION:
                        case KafkaResponseType.MPC_WALLET_SEND_SIGNED_TRANSACTION:
                            log.info("kafka message confirmedAndReceiptFailedStatusResponse: ");
                            Failed failed = Failed.builder()
                                    .blockNumber(String
                                            .valueOf(confirmedAndReceiptFailedStatusResponse.getBlockNumber()))
                                    .errorMessage("CONFIRMED_AND_RECEIPT_FAILED")
                                    .requestId(commonResponse.getRequestId())
                                    .build();

                            if (!ObjectUtils
                                    .isEmpty(checkCallBack
                                            .get(commonResponse.getRequestId()))) {

                                checkCallBack.get(commonResponse.getRequestId())
                                        .onFailure(failed);
                                checkCallBack.remove(commonResponse.getRequestId());
                            }

                            break;
                        default:
                            log.error("정의되지 않은 카프카 응답형식에러 \"response type\": " + commonResponse.getResponseType());
                    }
                    break;
                default:
                    log.error("정의되지 않은 카프카 응답상태 에러 \"status\": " + commonResponse.getStatus());
            }

        }

        acknowledgment.acknowledge();

    }

    @DltHandler
    public void handleBlockChainDltMessge(String message, @Header(KafkaHeaders.RECEIVED_TOPIC) String topic) {
        log.info("Event dlt topic topic={}, paylod={}", topic, message.toString());

    }

}
```
#### BlockchainFilter.java
```java
package kr.or.cbdc.infrastructure.queue;

import kr.or.cbdc.infrastructure.framework.core.foundation.exception.ErrorCode;
import kr.or.cbdc.infrastructure.util.JsonUtil;
import kr.or.cbdc.interfaces.blockchain.CheckCallBack;

import org.apache.commons.lang3.ObjectUtils;
import org.apache.commons.lang3.exception.ExceptionUtils;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.listener.adapter.RecordFilterStrategy;

import com.fasterxml.jackson.core.JsonProcessingException;

import jakarta.servlet.http.HttpServletResponse;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.BizException;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class BlockChainFilter implements RecordFilterStrategy<String, String> {

    @Value(value = "${spring.kafka.code}")
    private String prefixRequestId;    

    private @Autowired CheckCallBack checkCallBack;

    @Override
    public boolean filter(ConsumerRecord<String, String> consumerRecord) {
        // prefix가 다른 메시지는 리스너 메소드로 전달하지 않음 (필터링됨)
        try {
            String requestId = JsonUtil.get(consumerRecord.value(),"requestId");
            log.debug( "[kafka-requestId][{}]",requestId);
            return !requestId.startsWith(prefixRequestId) || ObjectUtils.isEmpty(checkCallBack.get(requestId));
        } catch ( JsonProcessingException | NullPointerException e) {
            // TODO Auto-generated catch block
            log.error("[requestId]:{}, {} ",ExceptionUtils.getMessage(e));
            throw new BizException(ErrorCode.SERVER_ERROR  , String.valueOf(HttpServletResponse.SC_BAD_REQUEST), "[requestId]:" + consumerRecord.value() + "  내용을 해석할 수 없습니다.");
        }
    }
}

```
#### Sequence Diagram
![[100. media/image/IGmipcjfJv.png]]
#### 상속관계가 "is-a" 관계가 아니고 이상. 대신 composite 방식으로 해도 아무런 문제 없음.
### lead to the **UnexpectedRollbackException** at the end.
#### 문제가 된 소스
```java
@Transactional(readOnly = false)
public VcPlaceOwnerModel read(String ownerId) {

        VcPlaceOwnerModel model = new VcPlaceOwnerModel();
        Assert.hasLength(ownerId,"사업주 User ID를 입력하여야 합니다");

        TbVcPlaceMastr master = this.vcPlaceOwnerManageMapper.selectByOwnerId(ownerId);
        Assert.isTrue(master != null,"사업주 정보가 존재하지 않습니다");

        // 업종코드 목록 조회
        master.setIndutyCdList(
            this.vcPlaceOwnerManageMapper.selectVcIndutyRlList(master.getPrtCmpnyId())
        );

        // IF-GWS-O-006  잔액조회
		BigDecimal acnutnoBlce = BigDecimal.ZERO;
		try {
			acnutnoBlce = this.vcAcnutGatewayService.acnutBalance(master.getUnityCstmrNo(), master.getAcnutno(),
					master.getAcnutnoBlce());         <-- 여기 acnutBalance 내부에서 예외 발생하여 아래 catch 문에서 잡힘.
		} catch (Exception e) {
			log.error("cannot get acnutnoBlce for the request {}, {}, {} : {}", master.getUnityCstmrNo(),
					master.getAcnutno(), master.getAcnutnoBlce(), e.getMessage());
		}
		master.setAcnutnoBlce(acnutnoBlce);

        // 지갑 잔액 조회
        String walletAddress = master.getWalletAdres();
        BigInteger walletBlce = BigInteger.valueOf(0);
        if (walletAddress != null && !walletAddress.isBlank()) {
            DigitalCoinModel dcModel = this.digitalCoinMapper.selectOne(CoinType.DC1.name(), null);
            TdRequestVo tdRequestVo = TdRequestVo.builder()
                .contractAddress(dcModel.getContractAdres())        /* TD 스마트계약주소 */
                .fromAddress(walletAddress)                         /* 사업자 지갑주소 */
                .build();
            try {
                walletBlce = this.vcSmartContractPbmService.execTdBalnceOf(tdRequestVo);
            } catch (WalletSdkException | InterruptedException e) {
                log.error("cannot get TD Balance for the request {} : {}", tdRequestVo, e.getMessage());
            }
        }
        master.setWalletBlce(String.valueOf(walletBlce));

        model.setTbVcPlaceOwnerMaster(master);
        model.setVcOwnedPlaceList(this.vcPlaceManageMapper.selectByOwnerId(ownerId));
        model.setVcPlaceVoucherList(this.vcPlaceVoucherMapper.selectByCstmrNo(ownerId));

        return model;
    }
```
#### 추출한 log
##### 첫 에러: **cannot get acnutBalance for the request**
##### 종료 commit 시도할 때 에러: **Transaction rolled back because it has been marked as rollback-only**
```plain text
2025-03-07 15:28:48.180 DEBUG [1529269:catalina-http-8090-exec-2] k.o.c.i.f.m.p.dao.interceptor.EncodingInterceptor  [020LEL8CB903BFE200-10.208.16.11] 암복 0208EIF5ACCC1EEA90
2025-03-07 15:28:48.180 DEBUG [1529269:catalina-http-8090-exec-2] k.o.c.a.v.v.m.V.selectVcIndutyRlList               [020LEL8CB903BFE200-10.208.16.11] ==> Parameters: 0208EIF5ACCC1EEA90(String)
2025-03-07 15:28:48.182 DEBUG [1529269:catalina-http-8090-exec-2] k.o.c.a.v.v.m.V.selectVcIndutyRlList               [020LEL8CB903BFE200-10.208.16.11] <==      Total: 1
2025-03-07 15:28:48.208 DEBUG [1529269:catalina-http-8090-exec-2] k.o.c.a.v.cstmr.service.VcAcnutGatewayServiceImpl  [020LEL8CB903BFE200-10.208.16.11] [jkoh] validateAndGetAccount start. account: 1005101874831
2025-03-07 15:28:48.209 INFO  [1529269:catalina-http-8090-exec-2] k.o.c.a.v.cstmr.service.VcAcnutGatewayServiceImpl  [020LEL8CB903BFE200-10.208.16.11] [jkoh] url: http://10.208.16.10:8090/ewa/gw/acno
2025-03-07 15:28:48.224 INFO  [1529269:catalina-http-8090-exec-2] kr.or.cbdc.interfaces.ApiCallHelper                [020LEL8CB903BFE200-10.208.16.11] connect URL=>http://10.208.16.10:8090/ewa/gw/acno
2025-03-07 15:28:48.912 DEBUG [1529269:catalina-http-8090-exec-2] k.o.c.a.v.cstmr.service.VcAcnutGatewayServiceImpl  [020LEL8CB903BFE200-10.208.16.11] [jkoh] payAvlAm value: 6482
2025-03-07 15:28:48.912 DEBUG [1529269:catalina-http-8090-exec-2] k.o.c.a.v.cstmr.service.VcAcnutGatewayServiceImpl  [020LEL8CB903BFE200-10.208.16.11] [jkoh] result is not ok
2025-03-07 15:28:48.912 ERROR [1529269:catalina-http-8090-exec-2] k.o.c.a.v.cstmr.service.VcAcnutGatewayServiceImpl  [020LEL8CB903BFE200-10.208.16.11] [1005101874831] Account validation failed during balance check
2025-03-07 15:28:48.913 ERROR [1529269:catalina-http-8090-exec-2] k.o.c.a.v.v.service.VcPlaceOwnerManageServiceImpl  [020LEL8CB903BFE200-10.208.16.11] cannot get acnutnoBlce for the request 659467541, 1005101874831, 6482 : 잔액조회를 실>패하였습니다. 관리자에게 문의해주세요.
2025-03-07 15:28:48.914 DEBUG [1529269:catalina-http-8090-exec-2] k.o.c.i.f.m.p.dao.helper.SqlMapHelperUtil          [020LEL8CB903BFE200-10.208.16.11] DatabaseMetaData.getDatabaseProductName() ==> MySQL
2025-03-07 15:28:48.916 DEBUG [1529269:catalina-http-8090-exec-2] k.o.c.i.f.m.p.dao.helper.SqlMapHelperUtil          [020LEL8CB903BFE200-10.208.16.11] DatabaseMetaData.getUserName() ==> dcapp@10.208.16.11
2025-03-07 15:28:48.917 INFO  [1529269:catalina-http-8090-exec-2] k.o.c.i.f.m.p.dao.interceptor.BaseSqlInterceptor   [020LEL8CB903BFE200-10.208.16.11] === SQL Mapper ==> kr.or.cbdc.application.common.coin.mapper.DigitalCoinMapper.selectOne
2025-03-07 15:28:48.917 DEBUG [1529269:catalina-http-8090-exec-2] k.o.c.a.c.coin.mapper.DigitalCoinMapper.selectOne  [020LEL8CB903BFE200-10.208.16.11] ==>  Preparing: /* kr.or.cbdc.application.common.coin.mapper.DigitalCoinMapper.selectOne */ SELECT TTL.COIN_ID , TTL.COIN_CD , TTL.COIN_NM , TTL.INSTT_CD , TTL.VER_NO , TTL.CONTRACT_NM , TTL.CONTRACT_ADRES , TTL.PROXY_CONTRACT_ADRES , TTL.OWN1_ADRES , TTL.OWN2_ADRES , TTL.CRTR_ID , TTL.CREATE_DT , TTL.WDTB_DT , TTL.CONTRACT_ABI , TTL.PROXY_CONTRACT_ABI , TTL.PROXY_CONTRACT_NM FROM TB_COIN_MASTR TTL WHERE 1=1 AND TTL.COIN_CD = ? AND TTL.COIN_STTUS = 'C' AND TTL.DELETE_AT = '0'
2025-03-07 15:28:48.917 DEBUG [1529269:catalina-http-8090-exec-2] k.o.c.i.f.m.p.dao.interceptor.EncodingInterceptor  [020LEL8CB903BFE200-10.208.16.11] 암복 kr.or.cbdc.infrastructure.framework.mybatis.persistence.dao.helper.SqlMapHelperForMySQL@754e119e
2025-03-07 15:28:48.917 DEBUG [1529269:catalina-http-8090-exec-2] k.o.c.i.f.m.p.dao.interceptor.EncodingInterceptor  [020LEL8CB903BFE200-10.208.16.11] 암복 null
2025-03-07 15:28:48.917 DEBUG [1529269:catalina-http-8090-exec-2] k.o.c.i.f.m.p.dao.interceptor.EncodingInterceptor  [020LEL8CB903BFE200-10.208.16.11] 암복 kr.or.cbdc.infrastructure.framework.web.persistence.dao.variables.WebSqlVariables@67c51f97
2025-03-07 15:28:48.917 DEBUG [1529269:catalina-http-8090-exec-2] k.o.c.i.f.m.p.dao.interceptor.EncodingInterceptor  [020LEL8CB903BFE200-10.208.16.11] 암복 DC1
2025-03-07 15:28:48.918 DEBUG [1529269:catalina-http-8090-exec-2] k.o.c.a.c.coin.mapper.DigitalCoinMapper.selectOne  [020LEL8CB903BFE200-10.208.16.11] ==> Parameters: DC1(String)
2025-03-07 15:28:48.920 DEBUG [1529269:catalina-http-8090-exec-2] k.o.c.a.c.coin.mapper.DigitalCoinMapper.selectOne  [020LEL8CB903BFE200-10.208.16.11] <==      Total: 1
2025-03-07 15:28:48.924 DEBUG [1529269:catalina-http-8090-exec-2] kr.or.cbdc.config.datasources.DataSourceAspect     [020LEL8CB903BFE200-10.208.16.11] =======>[main]
2025-03-07 15:28:48.925 DEBUG [1529269:catalina-http-8090-exec-2] k.o.c.i.f.m.p.dao.helper.SqlMapHelperUtil          [020LEL8CB903BFE200-10.208.16.11] DatabaseMetaData.getDatabaseProductName() ==> MySQL
2025-03-07 15:28:48.941 DEBUG [1529269:catalina-http-8090-exec-2] k.o.c.i.f.m.p.dao.helper.SqlMapHelperUtil          [020LEL8CB903BFE200-10.208.16.11] DatabaseMetaData.getUserName() ==> dcapp@10.208.16.11
2025-03-07 15:28:48.941 INFO  [1529269:catalina-http-8090-exec-2] k.o.c.i.f.m.p.dao.interceptor.BaseSqlInterceptor   [020LEL8CB903BFE200-10.208.16.11] === SQL Mapper ==> kr.or.cbdc.domain.main.mapper.voucher.wallet.TbVcWalletMastrMapper.selectByAddr

But it didn't throw exception. So it kept going.

2025-03-07 15:28:49.128 DEBUG [1529269:catalina-http-8090-exec-2] k.o.c.i.f.m.p.dao.helper.SqlMapHelperUtil          [020LEL8CB903BFE200-10.208.16.11] DatabaseMetaData.getUserName() ==> dcapp@10.208.16.11
2025-03-07 15:28:49.128 INFO  [1529269:catalina-http-8090-exec-2] k.o.c.i.f.m.p.dao.interceptor.BaseSqlInterceptor   [020LEL8CB903BFE200-10.208.16.11] === SQL Mapper ==> kr.or.cbdc.application.voucher.vcplace.mapper.VcPlaceVoucherMapper.selectByCstmrNo
2025-03-07 15:28:49.128 DEBUG [1529269:catalina-http-8090-exec-2] k.o.c.a.v.v.m.VcPlaceVoucherMapper.selectByCstmrNo [020LEL8CB903BFE200-10.208.16.11] ==>  Preparing: /* kr.or.cbdc.application.voucher.vcplace.mapper.VcPlaceVoucherMapper.selectByCstmrNo */ SELECT DISTINCT TVM.VOUCH_ID , TVM.VOUCH_NM , TVI.INSTT_NM , TVM.INSTT_ID AS PRT_CMPNY_ID , DATE_FORMAT(TVM.VOUCH_RCRIT_START_DT, '%Y-%m-%d') AS VOUCH_RCRIT_START_DT , DATE_FORMAT(TVM.VOUCH_RCRIT_END_DT, '%Y-%m-%d') AS VOUCH_RCRIT_END_DT , CASE VOUCH_TY_CD WHEN '2' THEN CONCAT(FORMAT(TVM.PYMNT_AMT, 0), '원/', TVM.PYMNT_RATE, '%/1회한도:' , FORMAT(TVM.ONE_LMT_AMT, 0) , '원' ) ELSE CONCAT(FORMAT(TVM.PYMNT_AMT, 0), '%/1회한도:' , FORMAT(TVM.ONE_LMT_AMT, 0) , '원' ) END AS VOUCH_USE_COND , (SELECT COUNT(*) FROM TB_VOUCH_PLACE VP JOIN TB_VOUCH_PLACE_RL RL ON (RL.PLACE_ID = VP.PLACE_ID AND RL.VOUCH_ID = TVM.VOUCH_ID) WHERE VP.OWNER_ID = UP_PLACE.CSTMR_NO AND VP.PLACE_TYPE_CD = 'P' ) NUMBER_OF_PLACE FROM TB_VOUCH_MASTR TVM JOIN TB_VOUCH_PLACE_RL TVPR ON TVM.VOUCH_ID = TVPR.VOUCH_ID JOIN TB_VOUCH_PLACE TVP ON TVPR.PLACE_ID = TVP.PLACE_ID -- 사용처 JOIN TB_VOUCH_INSTT TVI ON TVI.INSTT_ID = TVM.INSTT_ID JOIN TB_VOUCH_PLACE UP_PLACE ON UP_PLACE.CSTMR_NO = TVP.OWNER_ID WHERE 1=1 AND TVP.PLACE_TYPE_CD = 'P' AND (UP_PLACE.CSTMR_NO = ? OR UP_PLACE.PLACE_ID = ? )
2025-03-07 15:28:49.128 DEBUG [1529269:catalina-http-8090-exec-2] k.o.c.i.f.m.p.dao.interceptor.EncodingInterceptor  [020LEL8CB903BFE200-10.208.16.11] 암복 kr.or.cbdc.infrastructure.framework.mybatis.persistence.dao.helper.SqlMapHelperForMySQL@47b5d0e7
2025-03-07 15:28:49.129 DEBUG [1529269:catalina-http-8090-exec-2:] k.o.c.i.f.m.p.dao.interceptor.EncodingInterceptor  [020LEL8CB903BFE200-10.208.16.11] 암복 kr.or.cbdc.infrastructure.framework.web.persistence.dao.variables.WebSqlVariables@67c51f97
2025-03-07 15:28:49.129 DEBUG [1529269:catalina-http-8090-exec-2] k.o.c.i.f.m.p.dao.interceptor.EncodingInterceptor  [020LEL8CB903BFE200-10.208.16.11] 암복 testpay
2025-03-07 15:28:49.129 DEBUG [1529269:catalina-http-8090-exec-2] k.o.c.a.v.v.m.VcPlaceVoucherMapper.selectByCstmrNo [020LEL8CB903BFE200-10.208.16.11] ==> Parameters: testpay(String), testpay(String)
2025-03-07 15:28:49.139 DEBUG [1529269:catalina-http-8090-exec-2] k.o.c.a.v.v.m.VcPlaceVoucherMapper.selectByCstmrNo [020LEL8CB903BFE200-10.208.16.11] <== selectByCstmrNo     Total: 0
2025-03-07 15:28:49.191 ERROR [1529269:catalina-http-8090-exec-2] k.o.c.i.error.controller.ErrorHandleController     [020LEL8CB903BFE200-10.208.16.11] Trans Transaction rolled back because it has been marked as rollback-only
action rolled back because it has been marked as rollback-only
org.springframework.transaction.UnexpectedRollbackException: Transaction rolled back because it has been marked as rollback-only
        at org.springframework.transaction.support.AbstractPlatformTransactionManager.processRollback(AbstractPlatformTransactionManager.java:870)
        at org.springframework.transaction.support.AbstractPlatformTransactionManager.commit(AbstractPlatformTransactionManager.java:707)
        at org.springframework.transaction.interceptor.TransactionAspectSupport.commitTransactionAfterReturning(TransactionAspectSupport.java:660)
        at org.springframework.transaction.interceptor.TransactionAspectSupport.invokeWithinTransaction(TransactionAspectSupport.java:410)
        at org.springframework.transaction.interceptor.TransactionInterceptor.invoke(TransactionInterceptor.java:119)
        at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:184)
        at org.springframework.aop.framework.CglibAopProxy$CglibMethodInvocation.proceed(CglibAopProxy.java:751)
        at org.springframework.aop.interceptor.ExposeInvocationInterceptor.invoke(ExposeInvocationInterceptor.java:97)
        at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:184)
        at org.springframework.aop.framework.CglibAopProxy$CglibMethodInvocation.proceed(CglibAopProxy.java:751)
        at org.springframework.aop.framework.CglibAopProxy$DynamicAdvisedInterceptor.intercept(CglibAopProxy.java:703)
        at kr.or.cbdc.application.voucher.vcplace.service.VcPlaceOwnerManageServiceImpl$$SpringCGLIB$$0.read(<generated>)
        at kr.or.cbdc.application.voucher.vcplace.controller.VcPlaceOwnerManageRestController.read(VcPlaceOwnerManageRestController.java:70)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:77)
        at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
        at java.base/java.lang.reflect.Method.invoke(Method.java:568)
        at org.springframework.aop.support.AopUtils.invokeJoinpointUsingReflection(AopUtils.java:343)
        at org.springframework.aop.framework.CglibAopProxy$DynamicAdvisedInterceptor.intercept(CglibAopProxy.java:699)
        at kr.or.cbdc.application.voucher.vcplace.controller.VcPlaceOwnerManageRestController$$SpringCGLIB$$0.read(<generated>)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:77)
        at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
        at java.base/java.lang.reflect.Method.invoke(Method.java:568)
        at org.springframework.web.method.support.InvocableHandlerMethod.doInvoke(InvocableHandlerMethod.java:205)
        at org.springframework.web.method.support.InvocableHandlerMethod.invokeForRequest(InvocableHandlerMethod.java:150)
```
#### 답
##### Even though the exception is caught, it's causing the transaction to be marked as **rollback-only**, which leads to the **UnexpectedRollbackException** at the end.
##### Although you catch this exception, the transaction is already marked for rollback behind the scenes.
##### When Spring tries to commit the transaction at the end, it fails with `UnexpectedRollbackException` because the transaction was already marked as rollback-only.
#### 해결책. "Transactional" 주석 제거
### frontEnd에서 필수 입력 항목을 선택 입력으로 바꾸기(미완료)
#### create.tsx?
```typescript
import Row from 'shared/src/component/input/row';
import useBankModal from 'shared/src/component/modal/modalHook';
import codeUtil from 'shared/src/component/util/codeUtil';
import TextUtil from 'shared/src/component/util/textUtil';
import useActionHook from 'shared/src/features/vc/place/ownerManagement';
import bizEmpActionHook from 'shared/src/features/vc/place/bizEmpManagement';
import { IfTbSysAuthor, IfTbVcPlaceMaster, IfTbVouchInduty } from 'shared/src/services/types';
import { MutableRefObject, useCallback, useEffect, useState } from 'react';
import { Modal, Table } from 'react-bootstrap';
import Form from 'react-bootstrap/Form';
import VcIndutyList from '../../../common/induty';
import CreateFromFilePage from '../placeManagement/createFromFile';
import TextInput from 'shared/src/component/input/textInput';
import _, { isEmpty } from 'lodash';

interface CreateProps {
  listViewRef?: MutableRefObject<HTMLDivElement>;
  closeDetail: (reload: boolean) => void;
}

//  사업자관리 - 등록
export default function VcOwnerManagementCreate({ listViewRef, closeDetail }: CreateProps) {
  const { fnCreate, defCreate, fnCheckAccount } = useActionHook();
  const { fnLoginIdDupCheck } = bizEmpActionHook();
  const [create, setCreate] = useState<IfTbVcPlaceMaster>(defCreate());
  const [isSave, setIsSave] = useState<boolean>(false);
  const { openToast } = useBankModal();
  const [showPlaceFileUpload, setShowPlaceFileUpload] = useState<boolean>(false);

  const fnSave = () => {
    setIsSave(true);
    let data = _.cloneDeep(create);
    data.adres = `${data.legaldongCdNm || ''} ${data.adres || ''}`;

    if (data.stplatYn === 'N' || data.useAgreYn === 'N') {
      openToast({ color: 'red', content: '약관 비동의 시 사업자 등록이 불가합니다.' });
      return;
    }
    fnCreate(data).then((response) => {
      if (response) {
        // closeDetail(true);
        openToast({ color: 'app', content: '사용처를 등록해주세요.' });
        // if (!confirm('사용처를 등록하시겠습니까?')) return;
        setShowPlaceFileUpload(true);
      }
    });
  };

  //모달
  const [show, setShow] = useState(false);
  const handleClose = () => setShow(false);
  const handleOpen = () => setShow(true);
  const [indutyData, setIndutyData] = useState<Array<IfTbVouchInduty>>([]);

  //업종코드팝업에서 선택한 업종
  const handleValueChange = (newValue: Array<IfTbVouchInduty>) => {
    // setIndutyData((prv) => [...prv, ...newValue]);
    setIndutyData((prev) => {
      // 기존 데이터에서 고유성을 판단할 수 있는 필드를 기준으로 Set을 만듭니다.
      const existingKeys = new Set(prev.map((item) => `${item.indutyCd}|${item.indutyYear}`));

      // 새로운 값을 필터링하여 중복되지 않는 항목만 남깁니다.
      const uniqueNewValues = newValue.filter((item) => {
        const key = `${item.indutyCd}|${item.indutyYear}`;
        return !existingKeys.has(key);
      });
      return [...prev, ...uniqueNewValues];
    });
  };

  useEffect(() => {
    create.indutyCdList = indutyData;
  }, [indutyData]);

  const fnGetCodeNm = useCallback(
    (selected: string) => {
      let codenm = '';
      codeUtil.getCodeList('BIZ_TYPE_CD').map((item) => {
        if (item.cdValue === selected) {
          codenm = item.cdValueNm || '';
        }
      });
      return codenm;
    },
    [create?.bizTypeCd]
  );

  //아이디 중복확인
  const fnPersonLoginNmDupCheck = () => {
    fnLoginIdDupCheck(create?.cstmrNo!).then((dupCheck) => {
      setCreate((current) => ({ ...current, loginNmDupCheck: dupCheck ? -1 : 1 }));
    });
  };

  const fnAccountNo = () => {
    fnCheckAccount(create?.acnutno!, create?.unityCstmrNo!, create?.rprsntvNm!).then((result: [boolean, number]) => {
      const [valid, balance] = result;
      setCreate((current) => ({ 
        ...current, 
        acnutnoCheck: valid ? 1 : -1,
        acnutnoBlce: balance  // Update the balance in state
      }));
    });
  };

  const checkOnlyNumber = (input: string) => {
    const check = /[^0-9]/g;
    input = input.replace(check, '');
    return input;
  };

  return (
    <>
      <div className={'list-view on'} ref={listViewRef}>
        {!showPlaceFileUpload && (
          <>
            <h2 className="sub-title">
              사업자 상세정보
              <span className="essential-mark">*표시는 필수입력 사항입니다.</span>
            </h2>
            <Table bordered className="write-table">
              <caption>사업자 상세정보</caption>
              <colgroup>
                <col style={{ width: '10%' }} />
                <col style={{ width: '23.3%' }} />
                <col style={{ width: '10%' }} />
                <col style={{ width: '23.3%' }} />
                <col style={{ width: '10%' }} />
                <col style={{ width: '23.3%' }} />
              </colgroup>
              <tbody>
                <tr>
                  <Row
                    label={'사업자명'}
                    inputMode={'text'}
                    value={create?.placeNm}
                    textOptions={{
                      isError: isSave && !create.placeNm,
                      maxLength: 100,
                      onChange(value) {
                        setCreate((current) => ({ ...current, placeNm: value }));
                      }
                    }}
                  />
                  <Row
                    label={'대표자 이름'}
                    inputMode={'text'}
                    value={create?.rprsntvNm}
                    textOptions={{
                      isError: isSave && !create.rprsntvNm,
                      maxLength: 100,
                      onChange(value) {
                        setCreate((current) => ({ ...current, rprsntvNm: value }));
                      }
                    }}
                  />
                  <td colSpan={2}></td>
                </tr>
                <tr>
                  <Row
                    label={'사업자 구분'}
                    inputMode={'radio'}
                    value={create?.bizTypeCd}
                    radioOptions={{
                      options: codeUtil.getCodeList('BIZ_TYPE_CD'),
                      onChange(value) {
                        setCreate((current) => ({ ...current, bizTypeCd: value }));
                      }
                    }}
                  />
                  <Row
                    label={'사업자 등록번호'}
                    inputMode={'text'}
                    value={create?.bizrno}
                    textOptions={{
                      isError: isSave && !create.bizrno,
                      maxLength: 10,
                      onChange(value) {
                        setCreate((current) => ({ ...current, bizrno: checkOnlyNumber(value) }));
                      }
                    }}
                  />
                  <th className="req">업종코드</th>
                  <td>
                    {indutyData &&
                      indutyData.map((item, idx) => (
                        <span className="detail-blank">
                          {item.indutyCd}({item.indutyNm})
                        </span>
                      ))}
                    <button className="btn-type app" onClick={handleOpen}>
                      검색
                    </button>{' '}
                    <button
                      className="btn-type red"
                      onClick={() => {
                        setIndutyData([]);
                      }}
                    >
                      전체삭제
                    </button>
                  </td>
                </tr>
                <tr>
                  <Row
                    label={'사업자 코드'}
                    inputMode={'text'}
                    value={create?.placeCd}
                    textOptions={{
                      isError: isSave && !create.placeCd,
                      maxLength: 10,
                      onChange(value) {
                        setCreate((current) => ({ ...current, placeCd: value }));
                      }
                    }}
                  />
                  <Row
                    label={'대표번호'}
                    inputMode={'text'}
                    value={create?.rprsntvTelno}
                    textOptions={{
                      isError: isSave && !create.rprsntvTelno,
                      maxLength: 100,
                      onChange(value) {
                        setCreate((current) => ({ ...current, rprsntvTelno: value }));
                      }
                    }}
                  />
                  <th className="req">사업자 소재지</th>
                  <td>
                    <div className="flex gap5">
                      <label>
                        <Form.Select
                          style={{ width: '100%' }} //style추가
                          aria-label="Default select example"
                          value={create?.legaldongCd}
                          className={`'ipt-type' ${isSave && !create!.legaldongCd ? 'cus-error' : ''}`} // wp-100
                          onChange={(e) => {
                            setCreate((current) => ({
                              ...current,
                              legaldongCd: e.target.value,
                              legaldongCdNm: e.target.options[e.target.selectedIndex].text
                            }));
                            // setUserSttus(e.target.value);
                          }}
                        >
                          <option value="">선택</option>
                          {codeUtil.getChoiceItems('LEGALDONG_SIDO_CD').map((option) => {
                            if (option.cdValue && option.cdValueNm) {
                              return (
                                <option key={option.cdValueId} value={option.cdValue}>
                                  {option.cdValueNm}
                                </option>
                              );
                            }
                            return null;
                          })}
                        </Form.Select>
                      </label>
                      <label>
                        <TextInput
                          value={create?.adres}
                          //label={props.label}
                          placeholder={'상세주소를 입력하세요.'}
                          //className={props.textOptions.className}
                          //style={props.textOptions.style}
                          isError={isSave && !create!.adres}
                          maxLength={100}
                          onChange={(value) => setCreate({ ...create, adres: value })}
                          disabled={false}
                        />
                      </label>
                    </div>
                  </td>
                </tr>
                <tr>
                  <Row
                    label={'대표자 연락처'}
                    inputMode={'text'}
                    value={create?.rprsntvMbtlnum}
                    isReq={false}
                    textOptions={{
                      maxLength: 100,
                      onChange(value) {
                        setCreate((current) => ({ ...current, rprsntvMbtlnum: value }));
                      }
                    }}
                  />
                  <Row
                    label={'대표자 이메일'}
                    inputMode={'text'}
                    value={create?.rprsntvEmail}
                    isReq={true}
                    textOptions={{
                      isError: isSave && !create.rprsntvEmail,
                      maxLength: 100,
                      onChange(value) {
                        setCreate((current) => ({ ...current, rprsntvEmail: value }));
                      }
                    }}
                  />
                  <Row
                    label={'이용/약관 동의'}
                    colSpan={3}
                    inputMode={'radio'}
                    value={create?.useAgreYn}
                    radioOptions={{
                      options: codeUtil.getCodeList('AGRE_YN_CD'),
                      onChange(value) {
                        setCreate((current) => ({ ...current, useAgreYn: value, stplatYn: value }));
                      }
                    }}
                  />
                </tr>
                <tr>
                  <Row
                    label={'통합고객번호'}
                    inputMode={'text'}
                    value={create?.unityCstmrNo}
                    isReq={true}
                    textOptions={{
                      isError: isSave && !create.unityCstmrNo,
                      maxLength: 100,
                      onChange(value) {
                        setCreate((current) => ({ ...current, unityCstmrNo: value }));
                      }
                    }}
                  />
                  <td colSpan={4}></td>
                </tr>
              </tbody>
            </Table>

            <h2 className="sub-title">
              관리자 계정정보
              <span className="essential-mark">*표시는 필수입력 사항입니다.</span>
            </h2>
            <Table bordered className="write-table">
              <caption>관리자 계정정보</caption>
              <colgroup>
                <col style={{ width: '10%' }} />
                <col style={{ width: '23.3%' }} />
                <col style={{ width: '10%' }} />
                <col style={{ width: '23.3%' }} />
                <col style={{ width: '10%' }} />
                <col style={{ width: '23.3%' }} />
              </colgroup>
              <tbody>
                <tr>
                  <th className="req">User ID</th>
                  <td>
                    <div className="flex gap5">
                      <label>
                        <input
                          style={{ width: '100%' }} //style추가
                          type="text"
                          className={`ipt-type ${isSave && !create!.cstmrNo ? 'cus-error' : ''}`} // wp-70
                          placeholder="User ID 입력"
                          value={create?.cstmrNo}
                          onChange={(e) => setCreate((current) => ({ ...current, cstmrNo: e.target.value }))}
                        />
                      </label>
                      <button className="btn-type app" onClick={() => fnPersonLoginNmDupCheck()}>
                        중복확인
                      </button>
                    </div>
                  </td>
                  <Row
                    label={'관리자 이름'}
                    inputMode={'text'}
                    value={create?.koreanNm}
                    textOptions={{
                      isError: isSave && !create.koreanNm,
                      maxLength: 100,
                      onChange(value) {
                        setCreate((current) => ({ ...current, koreanNm: value }));
                      }
                    }}
                  />
                  <Row
                    label={'소속/부서'}
                    value={create?.deptNm}
                    inputMode={'text'}
                    textOptions={{
                      isError: isSave && !create.deptNm,
                      maxLength: 100,
                      onChange(value) {
                        setCreate((current) => ({ ...current, deptNm: value }));
                      }
                    }}
                  />
                </tr>
                <tr>
                  <th className="req">연락처</th>
                  <td>
                    <div className="flex gap5">
                      <label>
                        <Form.Select
                          style={{ width: '100%' }} //style추가
                          aria-label="Default select example"
                          className={`ipt-type ${isSave && !create!.telecomTypeCd ? 'cus-error' : ''}`} // wp-70
                          value={create?.telecomTypeCd}
                          onChange={(e) => setCreate((current) => ({ ...current, telecomTypeCd: e.target.value }))}
                        >
                          <option>통신사 선택</option>
                          {codeUtil.getChoiceItems('TELECOM_TYPE_CD').map((option) => {
                            if (option.cdValue && option.cdValueNm) {
                              return (
                                <option key={option.cdValueId} value={option.cdValue}>
                                  {option.cdValueNm}
                                </option>
                              );
                            }
                            return null;
                          })}
                        </Form.Select>
                      </label>
                      <label>
                        <input
                          style={{ width: '100%' }} //style추가
                          type="text"
                          className={`ipt-type wp-100 ${isSave && !create!.mbtlnum ? 'cus-error' : ''}`}
                          placeholder="연락처"
                          value={create?.mbtlnum}
                          maxLength={15}
                          onChange={(e) => setCreate((current) => ({ ...current, mbtlnum: checkOnlyNumber(e.target.value) }))}
                        />
                      </label>
                    </div>
                  </td>
                  <td colSpan={4}></td>
                </tr>
              </tbody>
            </Table>

            <h2 className="sub-title">
              지갑정보<span className="essential-mark">*표시는 필수입력 사항입니다.</span>
            </h2>
            <Table bordered className="write-table">
              <caption>지갑정보</caption>
              <colgroup>
                <col style={{ width: '10%' }} />
                <col style={{ width: '23.3%' }} />
                <col style={{ width: '10%' }} />
                <col style={{ width: '23.3%' }} />
                <col style={{ width: '10%' }} />
                <col style={{ width: '23.3%' }} />
              </colgroup>
              <tbody>
                <tr>
                  {/* <Row
                    label={'연동계좌'}
                    inputMode={'text'}
                    value={create?.acnutno}
                    textOptions={{
                      isError: isSave && !create.acnutno,
                      maxLength: 16,
                      onChange(value) {
                        setCreate((current) => ({ ...current, acnutno: checkOnlyNumber(value) }));
                      }
                    }}
                  /> */}

                  <th className="req">연동계좌</th>
                  <td>
                    <div className="flex gap5">
                      <label>
                        <input
                          style={{ width: '100%' }} //style추가
                          type="text"
                          className={`ipt-type ${isSave && !create!.acnutno ? 'cus-error' : ''}`} //wp-70
                          placeholder="연동계좌 입력"
                          maxLength={16}
                          value={create?.acnutno}
                          onChange={(e) => setCreate((current) => ({ ...current, acnutno: checkOnlyNumber(e.target.value) }))}
                        />
                      </label>
                      <button className="btn-type app" onClick={() => fnAccountNo()}>
                        계좌확인
                      </button>
                    </div>
                  </td>

                  <Row label={'계좌잔액'} value={`${TextUtil.parseValueComma(create.acnutnoBlce || 0)} 원`} />
                  <td colSpan={2}></td>
                </tr>
                <tr>
                  <Row label={'계좌인증'} value={''} colSpan={3} />
                  <Row label={'인증일시'} value={''} />
                </tr>
                <tr>
                  <Row label={'간편주소'} colSpan={3} value={''} inputMode={'addr'} />
                  <Row label={'지갑잔액'} value={''} valueType={'amount'} />
                </tr>
                <tr>
                  <Row label={'지갑주소'} colSpan={5} value={create.walletAdres} inputMode={'addr'} />
                </tr>
              </tbody>
            </Table>

            <div className="btn-layout right">
              <div>
                <button className="btn-type app" onClick={fnSave}>
                  저장
                </button>
              </div>
              <div>
                <button className="btn-type gry" onClick={() => closeDetail(false)}>
                  취소
                </button>
              </div>
            </div>
          </>
        )}
        {showPlaceFileUpload && (
          <>
            <h2 className="sub-title">사업자 기본정보</h2>
            <Table bordered className="write-table">
              <caption>사업자 기본정보 등록</caption>
              <colgroup>
                <col style={{ width: '10%' }} />
                <col style={{ width: '23.3%' }} />
                <col style={{ width: '10%' }} />
                <col style={{ width: '23.3%' }} />
                <col style={{ width: '10%' }} />
                <col style={{ width: '23.3%' }} />
              </colgroup>
              <tbody>
                <tr>
                  <Row label={'사업자명'} value={create?.placeNm} />
                  <Row label={'대표자 이름'} value={create?.rprsntvNm} />
                  <Row label={'사업자 User ID'} value={create?.cstmrNo} />
                </tr>
                <tr>
                  <Row label={'사업자 구분'} value={fnGetCodeNm(create?.bizTypeCd!)} />
                  <Row label={'사업자 등록번호'} value={create?.bizrno} />
                  <th>업종코드</th>
                  <td>
                    {indutyData &&
                      indutyData.map((item, idx) => (
                        <span className="detail-blank">
                          {item.indutyCd}({item.indutyNm})
                        </span>
                      ))}
                  </td>
                </tr>
              </tbody>
            </Table>
            <CreateFromFilePage closeDetail={() => closeDetail(true)} listViewRef={listViewRef} ownerPlaceNm={create.placeNm} />
          </>
        )}
      </div>

      <Modal show={show} onHide={handleClose} size="xl" aria-labelledby="contained-modal-title-vcenter" centered>
        <Modal.Header closeButton>
          <Modal.Title id="contained-modal-title-vcenter">업종선택</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <VcIndutyList onValueChange={handleValueChange} onSubHide={handleClose} indutyData={indutyData}></VcIndutyList>
        </Modal.Body>
        <Modal.Footer></Modal.Footer>
      </Modal>
    </>
  );
}
```
#### 사업자 코드, 업종 코드가 필수 입력값인데 이를 선택 입력으로 수정
### DB unique index 정의 및 error free insert
#### index 정의
```sql
CREATE UNIQUE_INDEX idx_unique_cstmr on TB_DEDPESZPE_LIST (ITCSNO, CUS_DSCD, CUS_STS_CHG_DTM)
```
##### 테이블 변경
```sql
ALTER TB_DEDPESZPE_LIST
ADD CONSTRAINT uk_dedpeszpe_list_combination
UNIQUE INDEX (ITCSNO, CUS_DSCD, CUS_STS_CHG_DTM)
```
#### 중복 키로 에러가 나도 다음 레코드로 넘어가기
```sql
<insert id=insertList parameterType="java.util.List">
  INSERT IGNORE INTO TB_DEDPESZPE_LIST
    (ITCSNO,
        CUS_DSCD,
        CUS_STS_CHG_DTM,
        REGIST_DT,
        PRC_YN)
  VALUES
    (#{item.itcsno,
     #{item.cusDscd,}
     #{item.cusStsChgDtm}},
     NOW(),
    '0')
<insert/>
```
### Distributed locking(FencedLock) with Hazelcast
#### EwaAcnutManageServiceImpl.java
```java
package kr.or.cbdc.application.ewa.cstmr.service;

import kr.or.bok.wallet.sdk.errorhandling.WalletSdkException;
import kr.or.bok.wallet.sdk.model.common.Signer;
import kr.or.cbdc.application.common.alias.mapper.BlockListManageMapper;
import kr.or.cbdc.application.common.alias.model.AliasResponse;
import kr.or.cbdc.application.common.alias.model.AliasSearchInfo;
import kr.or.cbdc.application.common.alias.service.BaseBlockListServiceImpl;
import kr.or.cbdc.application.common.deposit.DepositTokenPersistenceService;
import kr.or.cbdc.application.common.deposit.DepositTokenServiceImpl;
import kr.or.cbdc.application.ewa.alias.service.AliasEwaBanksServiceImpl;
import kr.or.cbdc.application.ewa.common.service.EwaGWServiceImpl;
import kr.or.cbdc.application.ewa.common.dto.CbsAcnoResponseDto;
import kr.or.cbdc.application.ewa.common.dto.GwAcnoDto;
import kr.or.cbdc.application.ewa.cstmr.model.AcnutManageModel;
import kr.or.cbdc.application.ewa.policy.service.EwaPolicyManageServiceImpl;
import kr.or.cbdc.application.ewa.wallet.service.EwaWalletManageServiceImpl;
import kr.or.cbdc.config.props.ConfigProperties;
import kr.or.cbdc.domain.main.mapper.ewa.cstmr.TbEwaAcnutMastrMapper;
import kr.or.cbdc.domain.main.mapper.ewa.cstmr.TbEwaCstmrMastrMapper;
import kr.or.cbdc.domain.main.mapper.ewa.dc1.EwaDc1RedempMastrMapper;
import kr.or.cbdc.domain.main.mapper.ewa.wallet.TbEwaWalletMastrMapper;
import kr.or.cbdc.domain.main.model.com.wallet.TbWalletMastr;
import kr.or.cbdc.domain.main.model.ewa.cstmr.TbCstmrMastr;
import kr.or.cbdc.domain.main.model.ewa.dc1.Dc1RedempMastr;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.BizException;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.ErrorAssert;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.ErrorCode;
import kr.or.cbdc.infrastructure.idgen.util.IdGenerationUtil;
import kr.or.cbdc.infrastructure.mybatis.GenericMapperService;
import kr.or.cbdc.infrastructure.profile.EwaProfileCondition;
import kr.or.cbdc.infrastructure.queue.KafkaProducer;
import kr.or.cbdc.infrastructure.queue.TxMessage;
import kr.or.cbdc.infrastructure.util.TokenUtils;
import kr.or.cbdc.interfaces.blockchain.BlockChainHelper;
import kr.or.cbdc.interfaces.blockchain.CoinType;
import kr.or.cbdc.interfaces.blockchain.CommandType;
import kr.or.cbdc.interfaces.blockchain.SupportCallback;
import kr.or.cbdc.interfaces.blockchain.TrnscType;
import kr.or.cbdc.interfaces.blockchain.WalletType;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Conditional;
import org.springframework.stereotype.Service;
import com.hazelcast.core.HazelcastInstance;
import com.hazelcast.cp.lock.FencedLock;
import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Random;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import static kr.or.cbdc.application.common.deposit.DepositTokenPersistenceService.BalanceOperationType;;

/**
##### 계좌 관리 Service
 */
@Slf4j
@Service
@Conditional(EwaProfileCondition.class)
public class EwaAcnutManageServiceImpl extends SupportCallback {

    private @Autowired TbEwaCstmrMastrMapper tbEwaCstmrMastrMapper;
    private @Autowired TbEwaAcnutMastrMapper tbEwaAcnutMastrMapper;
    private @Autowired TbEwaWalletMastrMapper tbEwaWalletMastrMapper;
    private @Autowired EwaPolicyManageServiceImpl ewaPolicyManageService;
    private @Autowired EwaWalletManageServiceImpl ewaWalletManageService;
    private @Autowired AliasEwaBanksServiceImpl aliasEwaBanksService;
    private @Autowired BlockListManageMapper blockListManageMapper;
    private @Autowired BlockChainHelper _blockChain;
    private @Autowired KafkaProducer kafkaProducer;
    private @Autowired GenericMapperService genericMapperService;
    private @Autowired ConfigProperties config;
    private @Autowired BaseBlockListServiceImpl blockListService;
    private @Autowired HazelcastInstance hazelcastInstance;
    private @Autowired EwaGWServiceImpl ewaGWService;
    private @Autowired DepositTokenServiceImpl depositTokenServiceImpl;
    private @Autowired DepositTokenPersistenceService dtps;

    private static final Random rand = new Random();
    private static final ObjectMapper objectMapper = new ObjectMapper();

    private void validateInput(AcnutManageModel model) {
        ErrorAssert.notNull(model, ErrorCode.MISSING_REQUIRED_FIELD);
        ErrorAssert.notNull(model.getTbAcnutMastr(), ErrorCode.MISSING_REQUIRED_FIELD);
        ErrorAssert.notNull(model.getTbAcnutMastr().getTrnscAmt(), ErrorCode.MISSING_REQUIRED_FIELD);
    }
    
    /**
##### 계정계로 잔액 조회를 요청해서 검증
##### @param accountNo Account number to check
##### @param amount Amount to validate
##### @throws BizException if validation fails
     */
    private void validateAccountWithdrawal(String accountNo, BigDecimal amount) {
        GwAcnoDto acnoParam = GwAcnoDto.builder()
                              .inqDscd("01")  // 보유계좌잔액조회
                              .dpsAcno(accountNo)
                              .build();
        
        JsonNode acnoResponse = ewaGWService.acno(acnoParam);
        if (acnoResponse == null) {
            throw new BizException(ErrorCode.BRIDGE_CALL_ERROR, "계정계 잔액 조회 결과가 없습니다. 게이트웨이를 확인하십시오.");
        }

        try {
            CbsAcnoResponseDto acnoResponseDto = objectMapper.treeToValue(acnoResponse, CbsAcnoResponseDto.class);
            
            if (acnoResponseDto.getErrorlist() != null && !acnoResponseDto.getErrorlist().isEmpty()) {
                log.error("계정계 잔액조회 에러: {}", acnoResponseDto.getErrorlist().get(0).getMainMsgTxt());
                throw new BizException(ErrorCode.INVALID_BALANCE_REQUIRED);
            }

            BigDecimal availableAmount = BigDecimal.valueOf(acnoResponseDto.getPayAvlAm());
            if (availableAmount.compareTo(amount) < 0) {
                log.error("계정계 출금가능금액 부족. 계좌: {}, 출금가능금액: {}, 요청금액: {}", 
                        accountNo, availableAmount, amount.intValue());
                throw new BizException(ErrorCode.INSUFFICIENT_ACCOUNT_BALANCE);
            }
        } catch (JsonProcessingException e) {
            log.error("계정계 잔액조회 응답 파싱 에러: {}", e.getMessage());
            throw new BizException(ErrorCode.PARSING_ERROR);
        }
    }

    /**
##### 전환 입금 (예금토큰 발행)
     *
##### @param model
##### @return requestId
##### @throws WalletSdkException
     */
    public String convDeposit(AcnutManageModel model) throws WalletSdkException {
        if (lock(TokenUtils.getToken())) {
            try {
        		// step0 입력값 검증
        		validateInput(model);
                String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));

        		TbCstmrMastr tbCstmrMastr = depositTokenServiceImpl.validateCustomer(cstmrNo);

        		BigDecimal trnscAmt = depositTokenServiceImpl.validateAmount(model.getTbAcnutMastr().getTrnscAmt());
        		log.debug("[jkoh] convDeposit start cstmrNo: {} trnsAmt {}", cstmrNo, trnscAmt);
        		log.debug("[jkoh] tbCstmrMastr: {}", tbCstmrMastr);

        		ErrorAssert.isNull(blockListManageMapper.selectBlclstWallet(bankCd, cstmrNo), ErrorCode.BLACKLIST_TARGET);
                blockListService.findBlockStatus(bankCd);
        		
                BigInteger toBalance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);

        		// IF-GWS-O-006 참가기관 이용자 Core Banking(계정계) 연계 계좌의 잔액 조회
                validateAccountWithdrawal(tbCstmrMastr.getAcnutno(), trnscAmt);

                // step 2-1 통화정책 한도검증 (보유)
                ewaPolicyManageService.policyLimit(null, null, toBalance.add(trnscAmt.toBigInteger()),
                        trnscAmt.toBigInteger(), cstmrNo);

                return depositTokenServiceImpl.issueDepositToken(cstmrNo, trnscAmt);

            } finally {
                unlock(TokenUtils.getToken());
            }
        } else {
            throw new BizException(ErrorCode.DISTRIBUTED_LOCK_ERROR);
        }
    }

    /**
##### 예금 전환(예금토큰 환수)
     *
##### @param model
##### @return requestId
##### @throws WalletSdkException
     */
    public String depositConv(AcnutManageModel model) throws WalletSdkException {
        if (lock(TokenUtils.getToken())) {
            try {
        		// step0 입력값 검증
        		validateInput(model);

                String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));
        		TbCstmrMastr tbCstmrMastr = depositTokenServiceImpl.validateCustomer(cstmrNo);
        		BigDecimal acnutnoBlce = tbCstmrMastr.getAcnutnoBlce();
        		
        		BigDecimal trnscAmt = depositTokenServiceImpl.validateAmount(model.getTbAcnutMastr().getTrnscAmt());

        		// blockListService.chkBlockStatus(cstmrNo, bankCd); 20250106_Source merge할 때 이 부분 막고 20250106_Source의 코드로 바꿈.
                blockListService.findBlockStatus(bankCd);

                // step1 지갑 검증
        		TbWalletMastr tbWalletMastr = depositTokenServiceImpl.validateWallet(WalletType.R1, tbCstmrMastr, ErrorCode.INVALID_TD_REDEMPTION_WALET);

                // step 2 예금전환액 검증
                BigInteger balance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);
                ErrorAssert.isTrue((balance.compareTo(trnscAmt.toBigInteger()) >= 0), ErrorCode.INSUFFICIENT_BALANCE);
        		log.debug("[jkoh] OffRamp step 2 지갑, 잔액 검증 완료");
        		
                BigDecimal updatedBalance = new BigDecimal(0);
        		// step3 계좌증액
        		updatedBalance = dtps.updateCustomerBalanceInNewTransaction(cstmrNo, acnutnoBlce, trnscAmt, BalanceOperationType.ADD);
        		log.debug("[jkoh] OffRamp step 3 계좌 증액 완료");

                String txDbId = dtps.createAndSaveRedempRecord(cstmrNo, tbCstmrMastr.getAcnutno(), trnscAmt, updatedBalance);

                // kafka message 생성
                TxMessage txMessage = TxMessage.builder().command(CommandType.R1)
                        .txDbId(txDbId)
                        .from(tbCstmrMastr.getWalletAdres())
                        .to(tbWalletMastr.getWalletAdres())
                        .fromBankCode(bankCd)
                        .toBankCode(bankCd)
                        .amount(trnscAmt.longValue())
                        .timestamp(new Date())
                        .trnscAfterBlce(balance.subtract(trnscAmt.toBigInteger()).longValue())
                        .fromTrnscAfterBlce(balance.longValue())
                        .fromAcnutno(tbCstmrMastr.getAcnutno())
                        .fromWalletDpstr(tbCstmrMastr.getKoreanNm())
                        .walletDpstr(tbWalletMastr.getWalletNm())
                        .personId(cstmrNo)
                        .coin(CoinType.DC1)
                        .txType(TrnscType.CONVERS.getValue())
                        .retry(0).build();
                List<TxMessage> txMessages = new ArrayList<>();
                txMessages.add(txMessage);
        		
        		String requestId = null;
        		try {
        			requestId = kafkaProducer.setSaga(txMessages);
        			log.debug("[jkoh] depositConv requestId from setSage: {}", requestId);
        		} catch (Exception e) {
        			dtps.updateCustomerBalanceInNewTransaction(cstmrNo, updatedBalance, trnscAmt, BalanceOperationType.SUBTRACT);
        			log.error("offRamp 트랜잭션 관리용 Saga requestId for txMessage {} 생성 에러: {}", txMessage, e);
        			throw e;
        		}

                // step 5 카프카 등록및 오류처리
                try {
                    kafkaProc(List.of(txMessage), requestId, "W");
        		} catch (BizException e) {
        			dtps.updateCustomerBalanceInNewTransaction(cstmrNo, updatedBalance, trnscAmt, BalanceOperationType.SUBTRACT);
        			log.error("offRamp Kafka 메시지[SagaID({})] 송신 에러: {}", requestId, e.getMessage());
        			throw e;
        		} 
        		log.debug("[jkoh] OffRamp step 5 kafka 전송 완료");
        		
        		try {

                    // step 6 이용자지갑 > 환수지갑 : 분산원장 Call , 참가기관 단일서명
        			String result = _blockChain.sendTransaction(requestId, tbCstmrMastr.getOwner(), tbWalletMastr.getWalletAdres(),
        					trnscAmt.toBigInteger(), this.bankCd, CoinType.DC1, getCallBack(txMessages,CoinType.DC1.name()));
                    ErrorAssert.hasLength(result, ErrorCode.KAFKA_PRODUCE_ERROR);
        		} catch (WalletSdkException e) {
        			log.error("SagaId({}) 예금토큰 환수({} -> {}) 블록체인 호출 에러 {}", requestId, tbCstmrMastr.getWalletAdres(), tbWalletMastr.getWalletAdres(), e.getMessage());
                    kafkaProc(List.of(txMessage), requestId, "R");
        			// 계좌 차감 처리 (계좌잔액= 계좌잔액 - 전환입금액, DC1 = DC1잔액 + 전환입금액)
        			dtps.updateCustomerBalanceInNewTransaction(cstmrNo, updatedBalance, trnscAmt, BalanceOperationType.SUBTRACT);
        			throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
        		}
        		log.debug("[jkoh] OffRamp step 6 블록체인 요청(requestId : {}) 완료.", requestId);
        		
        		return requestId;
            } finally {
                unlock(TokenUtils.getToken());
            }
        } else {
            throw new BizException(ErrorCode.DISTRIBUTED_LOCK_ERROR);
        }
    }

    /**
##### 예금 토큰 송금 (DC1 당,타행 이체)
     *
##### @param model
##### @return
##### @throws WalletSdkException
     */
    public String depositTrans(AcnutManageModel model) throws WalletSdkException {

        String result = "";
        String requestId = "";
        String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));

        ErrorAssert.notNull(tbEwaCstmrMastrMapper.select(cstmrNo),ErrorCode.USER_ID_NOT_FOUND);
        ErrorAssert.isTrue(!StringUtils.equals(tbEwaCstmrMastrMapper.select(cstmrNo).getCstmrSttusCd() ,"1"), ErrorCode.INVALID_CUSTOMER_STATE);
        String aliasNm = model.getTbAcnutMastr().getAliasNm();
        String walletInsttCd = model.getTbAcnutMastr().getWalletInsttCd();
        BigDecimal trnscAmt = model.getTbAcnutMastr().getTrnscAmt();
        boolean extYn = StringUtils.equals(walletInsttCd, bankCd);

        // step0 입력값 검증
        ErrorAssert.hasLength(cstmrNo, ErrorCode.CUSTOMER_ID_REQUIRED);
        ErrorAssert.hasLength(aliasNm, ErrorCode.INVALID_ALIAS);
        ErrorAssert.hasLength(trnscAmt.toString(), ErrorCode.EMPTY_TRANSACTION_AMOUNT);
        ErrorAssert.isNull(blockListManageMapper.selectBlclstWallet(bankCd, cstmrNo), ErrorCode.BLACKLIST_TARGET);
        blockListService.findBlockStatus(bankCd);

        // step1 수취인조회및 검증(수취인 지갑여부)
        AliasSearchInfo aliasSearchInfo = AliasSearchInfo.builder().aliasNm(aliasNm).trgetInstt(walletInsttCd).build();

        AliasResponse response = extYn ? aliasEwaBanksService.readFromLocal(aliasSearchInfo)
                : aliasEwaBanksService.read(aliasSearchInfo);

        // step2 이용자 지갑 검증
        TbWalletMastr tbWalletMastrA = this.tbEwaWalletMastrMapper.selectWalletByWalletSe("A");
        Signer signerA = Signer.builder().walletAddress(tbWalletMastrA.getWalletAdres())
                .hdKeyAccToken(tbWalletMastrA.getHdKeyaccToken())
                .hdKeyId(tbWalletMastrA.getHdKeyid()).build();
        TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(cstmrNo);
        ErrorAssert.hasLength(tbCstmrMastr.getWalletAdres(), ErrorCode.WALLET_MISSING);
        ErrorAssert.hasLength(response.getWalletAdres(), ErrorCode.WALLET_INFO_NOT_FOUND);
        ErrorAssert.isTrue(!StringUtils.equals(tbCstmrMastr.getWalletAdres(), response.getWalletAdres()), ErrorCode.WRONG_TRANSFER_REQUIRED);
        ErrorAssert.hasLength(tbCstmrMastr.getWalletAdres(), ErrorCode.WALLET_MISSING);
        ErrorAssert.hasLength(response.getWalletAdres(), ErrorCode.WALLET_INFO_NOT_FOUND);
        ErrorAssert.isTrue(!StringUtils.equals(tbCstmrMastr.getWalletAdres(), response.getWalletAdres()), ErrorCode.WRONG_TRANSFER_REQUIRED);


        // step3 DC1 차감(송금자) > DC1 증액(수취인)
        BigInteger fromBalance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);
        BigInteger toBalance = _blockChain.getBalance(response.getWalletAdres(), bankCd, CoinType.DC1);
        ErrorAssert.isTrue(fromBalance.compareTo(BigInteger.ZERO) > 0, ErrorCode.INSUFFICIENT_BALANCE);
        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.TRANS_AMOUNT_EXCEEDS_BALANCE);
        ErrorAssert.isTrue(fromBalance.compareTo(BigInteger.ZERO) > 0, ErrorCode.INSUFFICIENT_BALANCE);
        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.TRANS_AMOUNT_EXCEEDS_BALANCE);


        // step 3-1 통화정책 한도검증 (1회 , 1일)
        ewaPolicyManageService.policyLimit(trnscAmt, ewaWalletManageService.selectAmtPerDay(cstmrNo), null);
        ewaPolicyManageService.policyTransferLimit(ewaWalletManageService.selectAmtCntPerDay(cstmrNo));

        /*
##### kafka message 생성
##### (당,티헹)
##### kafka message 0 이용자 >> 이용자 (거래내역용)
##### (티헹)
##### kafka message 1 이용자 >> TD환수
##### kafka message 2 출금은행 당좌 >> 입금은행 당좌
##### kafka message 3 출금은행 TD 발행 >> 이용자
         */
        List<TxMessage> txMessages = new ArrayList<>();
        TxMessage txMessage = TxMessage.builder().command(CommandType.T1)
                .txDbId(IdGenerationUtil.createUid("TB_DC_TRANS_MASTR"))
                .from(tbCstmrMastr.getWalletAdres())
                .to(response.getWalletAdres())
                .fromBankCode(bankCd)
                .toBankCode(walletInsttCd)
                .amount(trnscAmt.longValue())
                .timestamp(new Date())
                .fromTrnscAfterBlce(fromBalance.subtract(trnscAmt.toBigInteger()).longValue())
                .personId(cstmrNo)
                .coin(CoinType.DC1)
                .retry(0).build();
        txMessages.add(txMessage);

        // kafka message 0 이용자 >> 이용자 (거래내역용)
        txMessages.get(0).setFromAcnutno(tbCstmrMastr.getAcnutno());
        txMessages.get(0).setAcnutno(response.getAcnutno());
        txMessages.get(0).setAliasNm(tbCstmrMastr.getAliasNm());
        txMessages.get(0).setFromAliasNm(aliasNm);
        txMessages.get(0).setWalletDpstr(response.getPersonNm());
        txMessages.get(0).setFromWalletDpstr(tbCstmrMastr.getKoreanNm());
        txMessages.get(0).setTxType(TrnscType.TRANSFER.getValue());

        // step 5 당행 송금
        if (extYn) {
            requestId = kafkaProducer.setSaga(txMessages);

            // step 5 카프카 등록및 오류처리
            try {
                kafkaProc(txMessages, requestId, "W");

                txMessage.setTrnscAfterBlce(toBalance.add(trnscAmt.toBigInteger()).longValue());
                result = _blockChain.sendLimitTransaction(requestId, tbCstmrMastr.getOwner(), response.getWalletAdres(),
                        trnscAmt.toBigInteger(), bankCd, CoinType.DC1, getCallBack(txMessages, CoinType.DC1.name()));

            } catch (Exception e) {
                kafkaProc(txMessages, requestId, "R");
                throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
            }

        } else {// 타행 송금

            txMessages.add(txMessage.clone());
            txMessages.add(txMessage.clone());
            txMessages.add(txMessage.clone());

            // kafka message 1 이용자 >> TD환수
            String tdRedempWalletAddr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.R1.name()).getWalletAdres();
            txMessages.get(1).setCommand(CommandType.R1);
            txMessages.get(1).setTo(tdRedempWalletAddr);
            txMessages.get(1).setToBankCode(bankCd);

            // kafka message 2 출금은행 당좌 >> 입금은행 당좌
            String cWalletAddr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.C.name()).getWalletAdres();
            BigInteger cBlce = _blockChain.getPrivateBalance(signerA, cWalletAddr, bankCd, CoinType.CBDC);
            ErrorAssert.isTrue(cBlce.compareTo(BigInteger.valueOf(trnscAmt.longValue()))>=0, ErrorCode.INSUFFICIENT_BALANCE);

            String toCWalletAddr = ewaWalletManageService.selectExtWalletAddr(WalletType.C.name(), walletInsttCd);
            txMessages.get(2).setCommand(CommandType.T);
            txMessages.get(2).setFrom(cWalletAddr);
            txMessages.get(2).setTo(toCWalletAddr);
            txMessages.get(2).setFromBankCode(config.getBokCode());
            txMessages.get(2).setToBankCode(config.getBokCode());
            txMessages.get(2).setFromTrnscAfterBlce(0);
            txMessages.get(2).setCoin(CoinType.CBDC);
            txMessages.get(2).setTretInstt(bankCd);
            txMessages.get(2).setTxType(TrnscType.CBDCTRANS.getValue());

            // kafka message 3 출금은행 TD 발행 >> 이용자
            String toIWalletAddr = ewaWalletManageService.selectExtWalletAddr(WalletType.I1.name(), walletInsttCd);
            txMessages.get(3).setCommand(CommandType.I1);
            txMessages.get(3).setFrom(toIWalletAddr);
            txMessages.get(3).setFromBankCode(walletInsttCd);
            txMessages.get(3).setTretInstt(bankCd);
            txMessages.get(3).setFromTrnscAfterBlce(0);

            requestId = kafkaProducer.setSaga(txMessages);

            // step 5 카프카 등록및 오류처리
            try {
                kafkaProc(txMessages, requestId, "W");

                result = _blockChain.sendExtLimitTransaction(requestId, tbCstmrMastr.getOwner(), bankCd,
                        walletInsttCd,
                        response.getWalletAdres(), trnscAmt.toBigInteger(),
                        getCallBack(txMessages, CoinType.DC1.name()));

            } catch (Exception e) {
                kafkaProc(txMessages, requestId, "R");
                throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
            }
        }

        ErrorAssert.hasLength(result, ErrorCode.BLOCKCHAIN_TRANSFER_ERROR);
        ErrorAssert.hasLength(result, ErrorCode.BLOCKCHAIN_TRANSFER_ERROR);

        return requestId;
    }

    /**
##### 예금 토큰 결제 (DC1 예금 토큰 결제)
     *
##### @param model
##### @return
##### @throws WalletSdkException
     */
    public String payment(AcnutManageModel model) throws WalletSdkException {

        String result = "";
        String cstmrNo = tbEwaCstmrMastrMapper.selectCstmrNo(TokenUtils.getCIFromToken(TokenUtils.USER_ID));
        ErrorAssert.notNull(tbEwaCstmrMastrMapper.select(cstmrNo), ErrorCode.CUSTOMER_NOT_FOUND,cstmrNo);
        ErrorAssert.isTrue(!StringUtils.equals(tbEwaCstmrMastrMapper.select(cstmrNo).getCstmrSttusCd() ,"1"), ErrorCode.INVALID_CUSTOMER_STATE);
        String aliasNm = model.getTbAcnutMastr().getAliasNm();
        String walletInsttCd = model.getTbAcnutMastr().getWalletInsttCd();
        BigDecimal trnscAmt = model.getTbAcnutMastr().getTrnscAmt();
        boolean extYn = StringUtils.equals(walletInsttCd, bankCd);

        // step0 입력값 검증
        ErrorAssert.hasLength(cstmrNo, ErrorCode.CUSTOMER_ID_REQUIRED);
        ErrorAssert.hasLength(aliasNm, ErrorCode.INVALID_ALIAS);
        ErrorAssert.hasLength(trnscAmt.toString(), ErrorCode.INVALID_AMOUNT);
        ErrorAssert.isNull(blockListManageMapper.selectBlclstWallet(bankCd, cstmrNo), ErrorCode.BLACKLIST_TARGET);
        blockListService.findBlockStatus(bankCd);

        // step1 수취인조회및 검증(수취인 지갑여부)
        AliasSearchInfo aliasSearchInfo = AliasSearchInfo.builder().aliasNm(aliasNm).trgetInstt(walletInsttCd).build();

        AliasResponse response = extYn ? aliasEwaBanksService.readFromLocal(aliasSearchInfo)
                : aliasEwaBanksService.read(aliasSearchInfo);

        // step2 이용자 지갑 검증
        TbCstmrMastr tbCstmrMastr = tbEwaCstmrMastrMapper.select(cstmrNo);
        ErrorAssert.hasLength(tbCstmrMastr.getWalletAdres(), ErrorCode.WALLET_MISSING);
        ErrorAssert.hasLength(response.getWalletAdres(), ErrorCode.INVALID_WALLET_INFO_ERROR);
        ErrorAssert.isTrue(!StringUtils.equals(tbCstmrMastr.getWalletAdres(), response.getWalletAdres()),ErrorCode.WRONG_PAYMENT_REQUIRED);


        // step3 DC1 차감(송금자) > DC1 증액(결제처)
        BigInteger fromBalance = _blockChain.getBalance(tbCstmrMastr.getWalletAdres(), bankCd, CoinType.DC1);
        BigInteger toBalance = _blockChain.getBalance(response.getWalletAdres(), bankCd, CoinType.DC1);
        ErrorAssert.isTrue(fromBalance.compareTo(BigInteger.ZERO) > 0, ErrorCode.INSUFFICIENT_BALANCE);
        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.PAYMENT_AMOUNT_EXCEEDS_BALANCE);
        ErrorAssert.isTrue(fromBalance.compareTo(BigInteger.ZERO) > 0, ErrorCode.INSUFFICIENT_BALANCE);
        ErrorAssert.isTrue(!(trnscAmt.toBigInteger().compareTo(fromBalance) > 0), ErrorCode.PAYMENT_AMOUNT_EXCEEDS_BALANCE);



        /*
##### kafka message 생성
##### (당,티헹)
##### kafka message 0 이용자 >> 이용자 (거래내역용)
##### (티헹)
##### kafka message 1 이용자 >> TD환수
##### kafka message 2 출금은행 당좌 >> 입금은행 당좌
##### kafka message 3 출금은행 TD 발행 >> 이용자
         */
        List<TxMessage> txMessages = new ArrayList<>();
        TxMessage txMessage = TxMessage.builder().command(CommandType.T1)
                .txDbId(IdGenerationUtil.createUid("TB_DC_TRANS_MASTR"))
                .from(tbCstmrMastr.getWalletAdres())
                .to(response.getWalletAdres())
                .fromBankCode(bankCd)
                .toBankCode(walletInsttCd)
                .amount(trnscAmt.longValue())
                .timestamp(new Date())
                .fromTrnscAfterBlce(fromBalance.subtract(trnscAmt.toBigInteger()).longValue())
                .personId(cstmrNo)
                .coin(CoinType.DC1)
                .retry(0).build();
        txMessages.add(txMessage);

        // kafka message 0 이용자 >> 이용자 (거래내역용)
        txMessages.get(0).setFromAcnutno(tbCstmrMastr.getAcnutno());
        txMessages.get(0).setAcnutno(response.getAcnutno());
        txMessages.get(0).setAliasNm(tbCstmrMastr.getAliasNm());
        txMessages.get(0).setFromAliasNm(aliasNm);
        txMessages.get(0).setWalletDpstr(response.getPersonNm());
        txMessages.get(0).setFromWalletDpstr(tbCstmrMastr.getKoreanNm());
        txMessages.get(0).setTxType(TrnscType.PAYMENT.getValue());

        String requestId = "";

        // step 5 당행 결제
        if (extYn) {
            requestId = kafkaProducer.setSaga(txMessages);

            // step 5 카프카 등록및 오류처리
            try {
                kafkaProc(txMessages, requestId, "W");

                txMessage.setTrnscAfterBlce(toBalance.add(trnscAmt.toBigInteger()).longValue());
                result = _blockChain.sendTransaction(requestId, tbCstmrMastr.getOwner(), response.getWalletAdres(),
                        trnscAmt.toBigInteger(), bankCd, CoinType.DC1, getCallBack(txMessages, CoinType.DC1.name()));
            } catch (Exception e) {
                kafkaProc(List.of(txMessage), requestId, "R");
                throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
            }

        } else {// 타행 결제

            txMessages.add(txMessage.clone());
            txMessages.add(txMessage.clone());
            txMessages.add(txMessage.clone());

            // kafka message 1 이용자 >> TD환수
            String tdRedempWalletAddr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.R1.name()).getWalletAdres();
            txMessages.get(1).setCommand(CommandType.R1);
            txMessages.get(1).setTo(tdRedempWalletAddr);
            txMessages.get(1).setToBankCode(bankCd);

            // kafka message 2 출금은행 당좌 >> 입금은행 당좌
            String cWalletAddr = tbEwaWalletMastrMapper.selectWalletSe(WalletType.C.name()).getWalletAdres();
            String toCWalletAddr = ewaWalletManageService.selectExtWalletAddr(WalletType.C.name(), walletInsttCd);
            txMessages.get(2).setCommand(CommandType.T);
            txMessages.get(2).setFrom(cWalletAddr);
            txMessages.get(2).setTo(toCWalletAddr);
            txMessages.get(2).setFromBankCode(config.getBokCode());
            txMessages.get(2).setToBankCode(config.getBokCode());
            txMessages.get(2).setTretInstt(bankCd);
            txMessages.get(2).setFromTrnscAfterBlce(0);
            txMessages.get(2).setTxType(TrnscType.CBDCTRANS.getValue());
            txMessages.get(2).setCoin(CoinType.CBDC);

            // kafka message 3 출금은행 TD 발행 >> 이용자
            String toIWalletAddr = ewaWalletManageService.selectExtWalletAddr(WalletType.I1.name(), walletInsttCd);
            txMessages.get(3).setCommand(CommandType.I1);
            txMessages.get(3).setFrom(toIWalletAddr);
            txMessages.get(3).setFromBankCode(walletInsttCd);
            txMessages.get(3).setTretInstt(bankCd);
            txMessages.get(3).setFromTrnscAfterBlce(0);

            requestId = kafkaProducer.setSaga(txMessages);

            // step 5 카프카 등록및 오류처리
            try {
                kafkaProc(txMessages, requestId, "W");

                result = _blockChain.sendExtTransaction(requestId, tbCstmrMastr.getOwner(), bankCd, walletInsttCd,
                        response.getWalletAdres(), trnscAmt.toBigInteger(),
                        getCallBack(txMessages, CoinType.DC1.name()));

            } catch (Exception e) {
                kafkaProc(txMessages, requestId, "R");
                throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);
            }
        }

        ErrorAssert.hasLength(result, ErrorCode.KAFKA_PRODUCE_ERROR);

        return requestId;
    }

    private void kafkaProc(List<TxMessage> txMessages, String requestId, String trnscSttusCd) {

        txMessages.forEach(tx -> {
            tx.setTrnscSttusCd(trnscSttusCd);
            tx.setRequestId(requestId);
        });

        try {
            kafkaProducer.send(topicTxRequest, txMessages);
        } catch (InterruptedException | ExecutionException e) {
            throw new BizException(ErrorCode.SERVER_ERROR  ,  requestId ,  e);
        } catch (Exception e) {
            throw new BizException(ErrorCode.SERVER_ERROR, requestId, e);

        }
        ErrorAssert.hasLength(requestId, ErrorCode.KAFKA_PRODUCE_ERROR);
    }

    /**
##### 계좌인증정보입력(검증) 워드3+난수3 자리생성
     *
##### @param model
##### @return
     */
    public String accountValid(AcnutManageModel model) {

        String[] words = { "송아리", "도사리", "미리내", "가루비", "도둑눈", "산돌림", "나비잠", "흰여울", "그루잠", "희나리" };

        StringBuilder result = new StringBuilder();
        result.append(words[rand.nextInt(words.length)]);

        ErrorAssert.isTrue(tbEwaAcnutMastrMapper.accountValid(model.getTbAcnutMastr()) != null,
                ErrorCode.WALLET_INFO_NOT_FOUND);

        // [Mockup][IF-GWS-O-007
        // ewaBridgeServiceImpl.validityCheck();

        return result.append(rand.nextInt(900) + 100).toString();
    }

    /**
##### 계좌 상세 조회
     *
##### @param cstmrNo
##### @return
     */
    public AcnutManageModel read(String cstmrNo) {

        AcnutManageModel model = new AcnutManageModel();
        model.setTbAcnutMastr(tbEwaAcnutMastrMapper.select(cstmrNo));
        return model;
    }

    public boolean lock(String userId) {
    	log.error("hazelcastInstance lock ::: {}", userId);
        FencedLock lock = hazelcastInstance.getCPSubsystem().getLock("lock:" + userId);
        return lock.tryLock(10, TimeUnit.SECONDS);
    }

    public void unlock(String userId) {
    	log.error("hazelcastInstance unlock :::: {}", userId);
        FencedLock lock = hazelcastInstance.getCPSubsystem().getLock("lock:" + userId);
        lock.unlock();
    }
}
```
#### 답: This pattern is common in financial systems where you need stronger guarantees than what regular database transactions provide, especially in distributed environments. It prevents scenarios like a user initiating two token redemptions simultaneously from different devices, potentially leading to incorrect balance calculations or double-spending.
### Default transation
#### config 설정으로 @Transaction이 없어도 특정 파일 내 메소드가 기본적으로 Transactional이 되도록 한 것(using AOP with transaction advisors)
##### TransactionConfigProperties.java
```java
package kr.or.cbdc.infrastructure.framework.core.persistence.transaction.props;

import org.springframework.transaction.TransactionDefinition;

public class TransactionConfigProperties {

    private IsolationLevelNames isolationLevel;
    public String[] readOnlyMethodNames;

    public IsolationLevelNames getIsolationLevel() {
        return this.isolationLevel;
    }

    public void setIsolationLevel(IsolationLevelNames isolationLevel) {
        this.isolationLevel = isolationLevel;
    }

    public String[] getReadOnlyMethodNames() {
        return this.readOnlyMethodNames;
    }

    public void setReadOnlyMethodNames(String[] readOnlyMethodNames) {
        this.readOnlyMethodNames = readOnlyMethodNames;
    }

    public enum IsolationLevelNames {

        ISOLATION_DEFAULT(TransactionDefinition.ISOLATION_DEFAULT), //
        ISOLATION_READ_UNCOMMITTED(TransactionDefinition.ISOLATION_READ_UNCOMMITTED), //
        ISOLATION_READ_COMMITTED(TransactionDefinition.ISOLATION_READ_COMMITTED), //
        ISOLATION_REPEATABLE_READ(TransactionDefinition.ISOLATION_REPEATABLE_READ), //
        ISOLATION_SERIALIZABLE(TransactionDefinition.ISOLATION_SERIALIZABLE), //
        ;

        private final int value;

        private IsolationLevelNames(int value) {
            this.value = value;
        }

        public int getValue() {
            return value;
        }

    }

}
```
##### TransactionInterceptorFactory.java
```java
package kr.or.cbdc.infrastructure.framework.core.persistence.transaction.config;

import java.util.ArrayList;
import java.util.List;

import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.interceptor.NameMatchTransactionAttributeSource;
import org.springframework.transaction.interceptor.RuleBasedTransactionAttribute;
import org.springframework.transaction.interceptor.TransactionAttributeSource;
import org.springframework.transaction.interceptor.TransactionInterceptor;

import kr.or.cbdc.infrastructure.framework.core.persistence.transaction.props.TransactionConfigProperties;
import kr.or.cbdc.infrastructure.framework.core.persistence.transaction.props.TransactionConfigProperties.IsolationLevelNames;

public class TransactionInterceptorFactory {

    private final TransactionConfigProperties transactionConfig;

    private String attributeName;
    private PlatformTransactionManager transactionManager;

    public TransactionInterceptorFactory(TransactionConfigProperties transactionConfig) {
        this.transactionConfig = transactionConfig;
    }

    public String getAttributeName() {
        return this.attributeName;
    }

    public void setAttributeName(String attributeName) {
        this.attributeName = attributeName;
    }

    public PlatformTransactionManager getTransactionManager() {
        return this.transactionManager;
    }

    public void setTransactionManager(PlatformTransactionManager transactionManager) {
        this.transactionManager = transactionManager;
    }

    public TransactionInterceptor getObject() {
        IsolationLevelNames isolationLevel = null;
        String[] readOnlyMethodNames = null;

        if (this.transactionConfig != null) {
            isolationLevel = this.transactionConfig.getIsolationLevel();
            readOnlyMethodNames = this.transactionConfig.getReadOnlyMethodNames();
        }

        List<NameMatchTransactionAttributeSource> transactionAttributeSourceList = new ArrayList<NameMatchTransactionAttributeSource>();

        NameMatchTransactionAttributeSource transactionAttributeSource;
        RuleBasedTransactionAttribute transactionAttribute;

        if (readOnlyMethodNames != null) {
            transactionAttribute = new RuleBasedTransactionAttribute();
            transactionAttribute.setName(this.attributeName + ".readOnly");
            if (isolationLevel != null) {
                transactionAttribute.setIsolationLevel(isolationLevel.getValue());
            }
            transactionAttribute.setReadOnly(true);
            transactionAttributeSource = new NameMatchTransactionAttributeSource();
            for (String methodName : readOnlyMethodNames) {
                transactionAttributeSource.addTransactionalMethod(methodName, transactionAttribute);
            }
            transactionAttributeSourceList.add(transactionAttributeSource);
        }

        {
            transactionAttribute = new RuleBasedTransactionAttribute();
            transactionAttribute.setName(this.attributeName);
            if (isolationLevel != null) {
                transactionAttribute.setIsolationLevel(isolationLevel.getValue());
            }
            transactionAttributeSource = new NameMatchTransactionAttributeSource();
            transactionAttributeSource.addTransactionalMethod("*", transactionAttribute);
            transactionAttributeSourceList.add(transactionAttributeSource);
        }

        TransactionAttributeSource[] transactionAttributeSources = new TransactionAttributeSource[transactionAttributeSourceList
                .size()];
        transactionAttributeSourceList.toArray(transactionAttributeSources);

        TransactionInterceptor txAdvice = new TransactionInterceptor();
        txAdvice.setTransactionManager(this.transactionManager);
        txAdvice.setTransactionAttributeSources(transactionAttributeSources);

        return txAdvice;
    }

}
```
##### DataSourceMainConfig.java
```java
package kr.or.cbdc.config.datasources;

import com.zaxxer.hikari.HikariDataSource;

import kr.or.cbdc.application.common.encryption.interfae.EncryptionService;
import kr.or.cbdc.application.common.encryption.service.DamoServiceImpl;
import kr.or.cbdc.config.props.ConfigProperties;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.BaseException;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.BizException;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.ErrorCode;
import kr.or.cbdc.infrastructure.framework.core.persistence.transaction.config.TransactionInterceptorFactory;
import kr.or.cbdc.infrastructure.framework.core.persistence.transaction.props.TransactionConfigProperties;
import kr.or.cbdc.infrastructure.framework.mybatis.persistence.dao.helper.SqlMapHelperForMySQL;
import kr.or.cbdc.infrastructure.framework.mybatis.persistence.dao.helper.SqlMapHelperUtil;
import kr.or.cbdc.infrastructure.framework.mybatis.persistence.dao.interceptor.BaseSqlInterceptor;
import kr.or.cbdc.infrastructure.framework.mybatis.persistence.dao.interceptor.DataResultHandleInterceptor;
import kr.or.cbdc.infrastructure.framework.mybatis.persistence.dao.interceptor.DataUpdatedCheckInterceptor;
import kr.or.cbdc.infrastructure.framework.mybatis.persistence.dao.interceptor.DecodingInterceptor;
import kr.or.cbdc.infrastructure.framework.mybatis.persistence.dao.interceptor.EncodingInterceptor;
import kr.or.cbdc.infrastructure.framework.mybatis.persistence.dao.interceptor.SelectQueryWrappingInterceptor;
import kr.or.cbdc.infrastructure.framework.mybatis.persistence.dao.scripting.SelectQueryWrappingLanguageDriver;
import kr.or.cbdc.infrastructure.framework.mybatis.persistence.dao.type.*;
import kr.or.cbdc.infrastructure.framework.mybatis.persistence.dao.variables.MyBatisDataSourceSpec;
import kr.or.cbdc.infrastructure.framework.mybatis.persistence.datasource.config.MapperLocationResources;
import kr.or.cbdc.infrastructure.framework.mybatis.persistence.datasource.props.DatabaseIdProperties;
import kr.or.cbdc.infrastructure.framework.mybatis.persistence.datasource.props.MyBatisConfigProperties;
import kr.or.cbdc.infrastructure.framework.web.persistence.dao.variables.WebSqlVariables;
import kr.or.cbdc.infrastructure.logging.interceptor.LoggingMyBatisInterceptor;
import kr.or.cbdc.infrastructure.user.AnonymousUser;
import kr.or.cbdc.infrastructure.user.SystemUser;
import org.apache.commons.lang3.ObjectUtils;
import org.apache.ibatis.mapping.VendorDatabaseIdProvider;
import org.apache.ibatis.plugin.Interceptor;
import org.apache.ibatis.session.LocalCacheScope;
import org.apache.ibatis.session.SqlSessionFactory;
import org.apache.ibatis.type.JdbcType;
import org.apache.ibatis.type.TypeHandlerRegistry;
import org.mybatis.spring.SqlSessionFactoryBean;
import org.mybatis.spring.SqlSessionTemplate;
import org.mybatis.spring.annotation.MapperScan;
import org.springframework.aop.Advisor;
import org.springframework.aop.aspectj.AspectJExpressionPointcut;
import org.springframework.aop.support.DefaultPointcutAdvisor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.quartz.QuartzDataSource;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.jdbc.datasource.DataSourceTransactionManager;
import org.springframework.jdbc.datasource.LazyConnectionDataSourceProxy;
import org.springframework.jdbc.datasource.lookup.JndiDataSourceLookup;
import org.springframework.stereotype.Component;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.interceptor.TransactionInterceptor;

import javax.sql.DataSource;
import java.lang.annotation.*;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

@Configuration
public class DataSourceMainConfig {

    public static final String MAIN = "main";
    public static final String MIRROR = "mirror";

    @Autowired
    private WebSqlVariables sqlVariables;

    @Autowired
    private EncryptionService encryptionService;

    @Autowired
    private ConfigProperties configProperties;

    @Bean
    @ConfigurationProperties(prefix = "config.datasources.main")
    public DatabaseProperties mainProperties() {
        return new DatabaseProperties();

    }

    @Bean
    @ConfigurationProperties(prefix = "config.datasources.mirror")
    public DatabaseProperties mirrorProperties() {
        return new DatabaseProperties();

    }

    @Bean
    @QuartzDataSource
    public DataSource mainDataSource() {
        DatabaseProperties data = mainProperties();
        return getDataSource(data);
    }


    public DataSource mirrorDataSource() {
        DatabaseProperties data = mirrorProperties();
        return getDataSource(data);

    }


    public DataSource getDataSource(DatabaseProperties data) {
        DataSource dataSource;
        if (ObjectUtils.isEmpty(data.getJndi()) ) {
            dataSource = new HikariDataSource(data.getHikari());
        } else {
            JndiDataSourceLookup jndiDataSourceLookup = new JndiDataSourceLookup();
            jndiDataSourceLookup.setResourceRef(data.getJndi().isResourceRef());
            dataSource = jndiDataSourceLookup.getDataSource(data.getJndi().getJndiName());
        }       

        return dataSource;
    }


    @Bean(name = "myBatisConfig.main")
    @ConfigurationProperties(prefix = "config.datasources.main.mybatis")
    public MyBatisConfigProperties myBatisConfig() {
        return new MyBatisConfigProperties();
    }

    @Bean(name = "transactionConfig.main")
    @ConfigurationProperties(prefix = "config.datasources.main.transaction")
    public TransactionConfigProperties transactionConfig() {
        return new TransactionConfigProperties();
    }

    @Bean
    public DataSource routingDataSource(){
        Map<Object,Object> datasources = new HashMap<>();
        datasources.put(MAIN, mainDataSource());
        datasources.put(MIRROR, mirrorDataSource());

        RoutingDataSourceMain routingDataSourceMain = new RoutingDataSourceMain();
        routingDataSourceMain.setTargetDataSources((datasources));
        routingDataSourceMain.setDefaultTargetDataSource(mainDataSource());
        routingDataSourceMain.afterPropertiesSet();

        return routingDataSourceMain;
    } 

    @Primary
    @Bean(name = "dataSource.main")
    public DataSource dataSource() {
        // return new DataSourceSpy(realDataSource());
        return new LazyConnectionDataSourceProxy(routingDataSource());
    }

    @Primary
    @Bean(name = "transactionManager.main")
    public PlatformTransactionManager transactionManager() {
        return new DataSourceTransactionManager(dataSource());
    }

    @Bean(name = "transactionAdvice.main")
    public TransactionInterceptor transactionAdvice() {
        TransactionInterceptorFactory transactionInterceptorFactory = new TransactionInterceptorFactory(
                transactionConfig());
        transactionInterceptorFactory.setAttributeName("transactionAdvice.main");
        transactionInterceptorFactory.setTransactionManager(transactionManager());

        return transactionInterceptorFactory.getObject();
    }

    @Bean(name = "transactionAdviceAdvisor.main")
    public Advisor transactionAdviceAdvisor() {
        AspectJExpressionPointcut pointcut = new AspectJExpressionPointcut();
        pointcut.setExpression(
                "execution(* *..service.*ServiceImpl.*(..)) || execution(* *..service.impl.*ServiceImpl.*(..))");

        DefaultPointcutAdvisor txAdviceAdvisor = new DefaultPointcutAdvisor();
        txAdviceAdvisor.setPointcut(pointcut);
        txAdviceAdvisor.setAdvice(transactionAdvice());

        return txAdviceAdvisor;
    }

    @Primary
    @Bean(name = "sqlSession.main")
    public SqlSessionTemplate sqlSession() {
        return new SqlSessionTemplate(sqlSessionFactory());
    }

    @Bean(name = "sqlSessionFactory.main")
    public SqlSessionFactory sqlSessionFactory() {
        SqlSessionFactoryBean sqlSessionFactoryBean = new SqlSessionFactoryBean();
        sqlSessionFactoryBean.setDataSource(dataSource());

        Properties databaseIdProperties = new DatabaseIdProperties();

        VendorDatabaseIdProvider databaseIdProvider = new VendorDatabaseIdProvider();
        databaseIdProvider.setProperties(databaseIdProperties);
        sqlSessionFactoryBean.setDatabaseIdProvider(databaseIdProvider);

        org.apache.ibatis.session.Configuration configuration = new org.apache.ibatis.session.Configuration();
        configuration.setCacheEnabled(true);
        configuration.setLocalCacheScope(LocalCacheScope.STATEMENT);
        configuration.setMapUnderscoreToCamelCase(true);
        configuration.setCallSettersOnNulls(true);
        configuration.setJdbcTypeForNull(JdbcType.VARCHAR);
        configuration.setDefaultScriptingLanguage(SelectQueryWrappingLanguageDriver.class);
        sqlSessionFactoryBean.setConfiguration(configuration);

        // WebSqlVariables sqlVariables = new WebSqlVariables();
        sqlVariables.setDataSourceSpec(new MyBatisDataSourceSpec(dataSource(), databaseIdProvider));
        sqlVariables.setAnonymousUser(new AnonymousUser());
        sqlVariables.setSystemUser(new SystemUser());

        BaseSqlInterceptor baseSqlInterceptor = new BaseSqlInterceptor();
        baseSqlInterceptor.setSqlVariables(sqlVariables);
        SelectQueryWrappingInterceptor selectQueryWrappingInterceptor = new SelectQueryWrappingInterceptor();
        DataResultHandleInterceptor dataResultHandleInterceptor = new DataResultHandleInterceptor();
        DataUpdatedCheckInterceptor dataUpdatedCheckInterceptor = new DataUpdatedCheckInterceptor();
        LoggingMyBatisInterceptor loggingMyBatisInterceptor = new LoggingMyBatisInterceptor();
        DecodingInterceptor decodingInterceptor = new DecodingInterceptor(configProperties, encryptionService);
        EncodingInterceptor encodingInterceptor = new EncodingInterceptor(configProperties, encryptionService);
        sqlSessionFactoryBean.setPlugins(new Interceptor[] { baseSqlInterceptor, selectQueryWrappingInterceptor,
                dataResultHandleInterceptor, encodingInterceptor, dataUpdatedCheckInterceptor, loggingMyBatisInterceptor, decodingInterceptor });

        TypeHandlerRegistry typeHandlerRegistry = configuration.getTypeHandlerRegistry();
        typeHandlerRegistry.register(EmptyToNullTypeHandler.class);
        typeHandlerRegistry.register(LocaleStringTypeHandler.class);
        typeHandlerRegistry.register(StringDateTypeHandler.class);
        typeHandlerRegistry.register(LONGVARCHARTypeHandler.class);
        typeHandlerRegistry.register(CLOBTypeHandler.class);

        MapperLocationResources mapperLocationResources = new MapperLocationResources(myBatisConfig());
        sqlSessionFactoryBean.setMapperLocations(mapperLocationResources.getResources());

        try {
            return sqlSessionFactoryBean.getObject();
        } catch (BizException e) {
            throw new BaseException(ErrorCode.SERVER_ERROR,e);
        } catch (Exception e) {
            throw new BaseException(ErrorCode.SERVER_ERROR,e);
        }
    }

    @MapperScan(annotationClass = MainSqlMapper.class, sqlSessionFactoryRef = "sqlSessionFactory.main", basePackages = {
            "kr.or.cbdc" })
    public static class MapperScanPackages {

        public MapperScanPackages() {
            SqlMapHelperUtil.addSqlMapHelper(new SqlMapHelperForMySQL());
        }

    }

    @Target(ElementType.TYPE)
    @Retention(RetentionPolicy.RUNTIME)
    @Documented
    @Component
    public @interface MainSqlMapper {

        String value() default "";

    }

}
```
##### application.yml
```plain text
config:
  validStdt: "9"
  validEddt: "14"
  iniFilePath: "damo/scpdb_agent.ini"
  scpKeyFilePath: "damo/WOORI_ARIA.scps"
  system-title: 한국은행 | 가상거액결제 시스템
  logs-directory: data/logs
  temp-directory: data/temp
  datasources:
    main:
      mybatis:
        mapper-locations:
        - classpath:/configuration/mapper/main-mysql/**/*.xml
      transaction:
        read-only-method-names:
        - view*
        - get*
```
#### 설정
##### In `DataSourceMainConfig`, there's a method called `transactionAdviceAdvisor()` that creates an AOP advisor with a pointcut expression:
```java
@Bean(name = "transactionAdviceAdvisor.main")
public Advisor transactionAdviceAdvisor() {
    AspectJExpressionPointcut pointcut = new AspectJExpressionPointcut();
    pointcut.setExpression(
            "execution(* *..service.*ServiceImpl.*(..)) || execution(* *..service.impl.*ServiceImpl.*(..))");

    DefaultPointcutAdvisor txAdviceAdvisor = new DefaultPointcutAdvisor();
    txAdviceAdvisor.setPointcut(pointcut);
    txAdviceAdvisor.setAdvice(transactionAdvice());

    return txAdviceAdvisor;
}
```
##### This pointcut expression applies transaction management to **all methods** in classes that:
##### End with `ServiceImpl`
##### Are in any package with `.service.` or `.service.impl.`
##### The transaction attributes (read-only, isolation level, etc.) are configured via `TransactionInterceptorFactory` which reads from application properties:
```java
@Bean(name = "transactionConfig.main")
@ConfigurationProperties(prefix = "config.datasources.main.transaction")
public TransactionConfigProperties transactionConfig() {
    return new TransactionConfigProperties();
}
```
##### From your application.yml, specific methods are designated as read-only:
```java
transaction:
  read-only-method-names:
  - view*
  - get*
```
##### All other methods that match the pointcut expression are configured with a default transaction attribute in `TransactionInterceptorFactory`:
```java
{
    transactionAttribute = new RuleBasedTransactionAttribute();
    transactionAttribute.setName(this.attributeName);
    if (isolationLevel != null) {
        transactionAttribute.setIsolationLevel(isolationLevel.getValue());
    }
    transactionAttributeSource = new NameMatchTransactionAttributeSource();
    transactionAttributeSource.addTransactionalMethod("*", transactionAttribute);
    transactionAttributeSourceList.add(transactionAttributeSource);
}
```
### API call interface
#### ApiCallHelper.java
```java
package kr.or.cbdc.interfaces;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import jakarta.servlet.http.HttpServletRequest;
import kr.or.cbdc.application.common.pushMsg.model.TbAppMssageMastr;
import kr.or.cbdc.application.ewa.common.dto.CbsRampResponseDto;
import kr.or.cbdc.application.ewa.common.dto.GwUmsAppPushDto;
import kr.or.cbdc.config.props.ConfigProperties;
import kr.or.cbdc.domain.main.mapper.sys.pushId.TbSysPushIdMapper;
import kr.or.cbdc.domain.main.model.sys.pushId.TbPushIdEntity;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.BizException;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.ErrorAssert;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.ErrorCode;
import kr.or.cbdc.infrastructure.util.SeqNoGenerator;
import kr.or.cbdc.infrastructure.util.TokenUtils;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import java.util.function.Supplier;

import org.apache.commons.lang3.ObjectUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.HttpServerErrorException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
import java.io.IOException;
import java.util.Map;
import java.util.concurrent.TimeoutException;
import java.net.ConnectException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Slf4j
@Component
@RequiredArgsConstructor
public class ApiCallHelper {
    private static final int baseNo = 2;
    private final RestTemplate httpRestTemplate;
    private final RestTemplate httpsRestTemplate;
    private final ObjectMapper objectMapper ;
    private final ConfigProperties configProperties;
    private @Autowired TbSysPushIdMapper tbSysPushIdMapper;

    /**
##### ewa Api Call
     */
    public JsonNode wooriWonCallURL(String url, String token, ObjectNode jsonNodes, HttpMethod type) {
        //String devToken = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX";
        //appkey :XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        HttpEntity<JsonNode> request;
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.valueOf("application/json;charset=UTF-8"));
        //headers.setAccept(java.util.Arrays.asList(new MediaType[] { MediaType.APPLICATION_JSON }));
        //headers.set("X-IBK-Client-Id",clientId);
        //headers.set("X-IBK-Client-Secret",clientSecret);
        if (token != null) {
            //headers.setBearerAuth(token);
            headers.set("Authorization",token);
        }
        if (jsonNodes == null) {
            request = new HttpEntity<>(headers);
        } else {
            request = new HttpEntity<>(jsonNodes, headers);
        }

        String protocal = extractAndValidateProtocol(url);
        ResponseEntity<JsonNode> resp = "https".equalsIgnoreCase(protocal)
        ? httpsRestTemplate.exchange(url, type, request, JsonNode.class)
        : httpRestTemplate.exchange(url, type, request, JsonNode.class);

        return resp.getBody();
    }
    
    /**
##### Api Call
     */
    public JsonNode callURL(String url, String token, ObjectNode jsonNodes) {
        return callURL(url, token, jsonNodes, HttpMethod.POST);
    }

    /**
##### Api Call
     */
    public JsonNode callURL(String url, String token, ObjectNode jsonNodes, HttpMethod type) {
        HttpEntity<JsonNode> request;
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.valueOf("application/json;charset=UTF-8"));

        if (token != null) {
            headers.setBearerAuth(token);
        }

        if (jsonNodes == null) {
            request = new HttpEntity<>(headers);
        } else {
            request = new HttpEntity<>(jsonNodes, headers);
        }

        String protocal = extractAndValidateProtocol(url);
        ResponseEntity<JsonNode> resp = "https".equalsIgnoreCase(protocal)
                ? httpsRestTemplate.exchange(url, type, request, JsonNode.class)
                : httpRestTemplate.exchange(url, type, request, JsonNode.class);

        return resp.getBody();

    }

    /**
##### Api Array Call
     */
    public JsonNode callArrayURL(String url, String token, ArrayNode jsonNodes) {

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.valueOf("application/json;charset=UTF-8"));

            if (token != null) {
                headers.setBearerAuth(token);
            }

            HttpEntity<JsonNode> request = new HttpEntity<>(jsonNodes, headers);

            String protocal = extractAndValidateProtocol(url);

            ResponseEntity<JsonNode> resp = "https".equalsIgnoreCase(protocal)
                    ? httpsRestTemplate.exchange(url, HttpMethod.POST, request, JsonNode.class)
                    : httpRestTemplate.exchange(url, HttpMethod.POST, request, JsonNode.class);

            return resp.getBody();

    }

    /**
##### Api Call (가상거액 시스템)
     */
    public ResponseEntity<?> callPayURL(String url, String userId, String userPwd, String payLoad) {

            HttpHeaders headers = new HttpHeaders();

            if (userId != null) {
                headers.setBasicAuth(userId, userPwd);
            }

            HttpEntity<String> request = new HttpEntity<String>(payLoad, headers);

            String protocal = extractAndValidateProtocol(url);

            ResponseEntity<String> resp ="https".equalsIgnoreCase(protocal)
                    ? httpsRestTemplate.exchange(url, HttpMethod.POST, request, String.class)
                    : httpRestTemplate.exchange(url, HttpMethod.POST, request, String.class);

            return resp;

    }

    /**
##### Api Call (파일 전송)
     */
    public JsonNode callTransFileURL(String url, String token, String contentType, MultiValueMap<String, Object> body)
            throws RestClientException, JsonProcessingException {

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.valueOf(contentType));

            if (token != null) {
                headers.setBearerAuth(token);
            }

            HttpEntity<MultiValueMap<String, Object>> request = new HttpEntity<>(body, headers);
            String protocal = extractAndValidateProtocol(url);

            String resp = "https".equalsIgnoreCase(protocal) ? httpsRestTemplate.postForObject(url, request, String.class)
                    : httpRestTemplate.postForObject(url, request, String.class);

            return objectMapper.readTree(resp);

    }

    /**
##### Api Call (KSM 서버)
     */
    public JsonNode callKeyServerUrl(String url, String token, HttpMethod type) {

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.valueOf("application/json;charset=UTF-8"));
            headers.set("X-API-KEY", token);

            String protocal = extractAndValidateProtocol(url);

            ResponseEntity<JsonNode> resp = "https".equalsIgnoreCase(protocal) ? httpsRestTemplate.exchange(url, type, new HttpEntity<>(headers),
                            JsonNode.class)
                            : httpRestTemplate.exchange(url, type, new HttpEntity<>(headers),
                                    JsonNode.class);

            return resp.getBody();

    }

    public String addQueryParams(String baseUrl, String... params) {
        StringBuilder builder = new StringBuilder(baseUrl);

        if (params.length > 0) {
            builder.append("?");
            for (int i = 0; i < params.length; i += 2) {
                if (i > 0) {
                    builder.append("&");
                }
                if (ObjectUtils.isNotEmpty((params[i + 1])))
                    builder.append(params[i]).append("=").append(params[i + 1]);
            }
        }
        return builder.toString();
    }

    public static String extractAndValidateProtocol(String url) {
        // URL에서 "://" 존재 여부 확인
        log.info("connect URL=>{}", url);
        ErrorAssert.isPositive(url.indexOf("://"), ErrorCode.INVALID_HTTP_PROTOCOL_REQUIRED);
    
        // 프로토콜 추출
        String protocol = url.substring(0, url.indexOf("://")).trim();
    
        // 프로토콜 유효성 확인
        ErrorAssert.hasLength(protocol, ErrorCode.INVALID_HTTP_PROTOCOL_REQUIRED);
    
        return protocol; // 유효한 프로토콜 반환
    }
    
    /**
##### G/W Proxy 호출
##### 
##### @param url
##### @param jsonNodes
##### @param type
##### @param appkey
##### @return
     */
    public JsonNode callURLWithHeaders(String url, ObjectNode jsonNodes, HttpMethod type, Map<String, String> reqHeaders) {
    	try {
    		HttpEntity<JsonNode> request;
    		HttpHeaders headers = new HttpHeaders();
    		headers.setContentType(MediaType.valueOf("application/json;charset=UTF-8"));
    		
			if (reqHeaders != null) {
				for (String key : reqHeaders.keySet()) {
					headers.set(key, reqHeaders.get(key));
				}
			}
    		
    		if (jsonNodes == null) {
    			request = new HttpEntity<>(headers);
    		} else {
    			request = new HttpEntity<>(jsonNodes, headers);
    		}
    		
    		String protocal = extractAndValidateProtocol(url);
    		ResponseEntity<JsonNode> resp = "https".equalsIgnoreCase(protocal)
    				? httpRestTemplate.exchange(url, type, request, JsonNode.class)
    						: httpRestTemplate.exchange(url, type, request, JsonNode.class);
    		return resp.getBody();
    	} catch (RestClientException e) {
    		// If error response contains JSON (business error), parse and return it
    		if (e.getMessage() != null && e.getMessage().contains("\"ERRCODE\"")) {
    			try {
    				String errorMessage = e.getMessage();
    				// Extract JSON part from error message
    				int jsonStart = errorMessage.indexOf('{');
    				int jsonEnd = errorMessage.lastIndexOf('}') + 1;
    				String jsonStr = errorMessage.substring(jsonStart, jsonEnd);
    				
    				ObjectMapper mapper = new ObjectMapper();
    				return mapper.readTree(jsonStr);
    			} catch (JsonProcessingException ex) {
    				throw e;
    			}
    		}
    		throw e; // For other REST client exceptions (network errors etc)
    	}
    }

    /**
##### Api Call with appkey and cookies in header
     */
    public JsonNode callURLWithCookie(String url, HttpServletRequest request, ObjectNode jsonNodes, HttpMethod type) {
        HttpEntity<JsonNode> httpEntity;
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.valueOf("application/json;charset=UTF-8"));

        // Copy Authorization header if present
        String authHeader = request.getHeader(HttpHeaders.AUTHORIZATION);
        if (authHeader != null && !authHeader.isEmpty()) {
            headers.set(HttpHeaders.AUTHORIZATION, authHeader);
        }
        
        // Copy all cookies from the request
        String cookieHeader = request.getHeader(HttpHeaders.COOKIE);
        if (cookieHeader != null && !cookieHeader.isEmpty()) {
            headers.set(HttpHeaders.COOKIE, cookieHeader);
        }

        if (jsonNodes == null) {
            httpEntity = new HttpEntity<>(headers);
        } else {
            httpEntity = new HttpEntity<>(jsonNodes, headers);
        }

        String protocol = extractAndValidateProtocol(url);
        ResponseEntity<JsonNode> resp = "https".equalsIgnoreCase(protocol)
                ? httpsRestTemplate.exchange(url, type, httpEntity, JsonNode.class)
                : httpRestTemplate.exchange(url, type, httpEntity, JsonNode.class);

        return resp.getBody();
    }

    public static String generateTimeStamp() {
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime rsv_dt = now.plusSeconds(3);
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("YYYYMMDDhhmmss");
        return rsv_dt.format(formatter);
    }
    
	/**
## 랜딩페이지 화면코드 추가
## 
## @param umsTmplCd
## @return
	 */
	private String getTmpCd(String umsTmplCd) {
		switch (umsTmplCd) {
		case "RPWSTTPE0132434": // 전자지갑개설
			return "RPUMSCMP0153106";
		case "RPWSTTPE0132435": // 전자지갑해지
			return "RPUMSCMP0153107";
		case "RPWSTTPE0132436": // 예금전환
			return "RPUMSCMP0153039";
		case "RPWSTTPE0132437": // 전환입금
			return "RPUMSCMP0153038";
		case "RPWSTTPE0132438": // 결제
			return "RPUMSCMP0153110";
		case "RPWSTTPE0132439": // 환불
			return "RPUMSCMP0153111";
		}
		return null;
	}
	
	private String generateDateSeqNo() {
		TbPushIdEntity tbPushIdEntity = new TbPushIdEntity();
    	tbSysPushIdMapper.insert(tbPushIdEntity);
    	return tbPushIdEntity.getPushId();
	}

    public JsonNode callUMSGateway(GwUmsAppPushDto request) {
        try {
        	StringBuffer trnoSb = new StringBuffer();
        	trnoSb.append("PU");
        	trnoSb.append("SEG");
        	trnoSb.append(generateDateSeqNo());
            
        	char delimeter = 18;
			StringBuffer pushAddInfSb = new StringBuffer();
    		pushAddInfSb.append(LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd")));
    		pushAddInfSb.append(delimeter);
    		pushAddInfSb.append(LocalDateTime.now().format(DateTimeFormatter.ofPattern("HHmmss")));
    		pushAddInfSb.append(delimeter);
    		pushAddInfSb.append(delimeter);
    		pushAddInfSb.append(delimeter);
    		pushAddInfSb.append("NWSTL00038_001M?TEMPLATE_CODE=");
    		pushAddInfSb.append(getTmpCd(request.getUmsTmplCd()));
    		
            GwUmsAppPushDto paramUms = GwUmsAppPushDto.builder()
                    .umsTrno(trnoSb.toString())
                    .umsTmplCd(request.getUmsTmplCd())
                    .deptSbrCd("084543")
                    .umsAppId("41029")
                    .pushAddInf(pushAddInfSb.toString())
                    .rsvDt(generateTimeStamp())
                    .csno(request.getCsno())
                    .dpsTelNo(request.getDpsTelNo())
                    .dmsgTelNo(request.getDmsgTelNo())
    				.sprTxt1(request.getSprTxt1())
    				.sprTxt2(request.getSprTxt2())
    				.cusNm(request.getCusNm())
    				.acno(request.getAcno())
    				.stlAm(request.getStlAm())
    				.bal(request.getBal())
    				.crtfNo(request.getCrtfNo())
    				.bizTp(request.getBizTp())
    				.mpng1(request.getMpng1())
    				.mpng2(request.getMpng2())
    				.mpng3(request.getMpng3())
    				.mpng4(request.getMpng4())
    				.mpng5(request.getMpng5())
    				.mpng6(request.getMpng6())
    				.mpng7(request.getMpng7())
    				.mpng8(request.getMpng8())
    				.mpng9(request.getMpng9())
    				.mpng10(request.getMpng10())
    				.mpngAllTitl(request.getMpngAllTitl())
    				.mpngAll(request.getMpngAll())
    				.mpngAppBd(request.getMpngAppBd())
                    .build();
    
			String url = configProperties.getGateway().getUms().getUrl();
			ObjectNode param = new ObjectMapper().valueToTree(paramUms);
			JsonNode respUms = callURL(url, null, param, HttpMethod.POST);
    
            return respUms;
    
        } catch (RestClientException e) {
            if (e.getMessage() != null && e.getMessage().contains("\"ERRCODE\"")) {
                try {
                    String errorMessage = e.getMessage();
                    int jsonStart = errorMessage.indexOf('{');
                    int jsonEnd = errorMessage.lastIndexOf('}') + 1;
                    String jsonStr = errorMessage.substring(jsonStart, jsonEnd);
                    
                    JsonNode errorNode = new ObjectMapper().readTree(jsonStr);
                    String errorCode = errorNode.get("dataBody").get("ERRCODE").asText();
                    String errorMsg = errorNode.get("dataBody").get("ERRUSRMSG").asText();
                    log.error("UMS Error - Code: {}, Message: {}", errorCode, errorMsg);
                    
                    return errorNode;
                } catch (JsonProcessingException ex) {
                    throw e;
                }
            }
            log.error("UMS Gateway call error {}", e.getMessage());
            // TODO UMS 발송과 별개로 메세지적재해야함
//            throw e; // For other REST client exceptions (network errors etc)
        }
        return null;
    }

}
```
#### InterfaceMap.java
```java
package kr.or.cbdc.interfaces;

import com.google.gson.Gson;
import com.google.gson.JsonObject;

import java.io.UnsupportedEncodingException;
import java.util.HashMap;

public class InterfaceMap  extends HashMap{

	public InterfaceMap(){
		super();
	}
	
	public InterfaceMap(String jsonStr) {
		this.putAll(new Gson().fromJson(jsonStr, this.getClass()));
	}
	
	public InterfaceMap(JsonObject jsonObject) {
		this.putAll(new Gson().fromJson(jsonObject, this.getClass()));
	}

	@Override
	public Object get(Object key) {
		return super.get(key) == null ? "" : super.get(key);
	}	

	@Override
	public Object put(Object key, Object value) {
		value = value == null ? "" : value;
		return super.put(key, value);
	}

	public String getString(Object key){
		return getString(key, "");
	}
	
	public String getString(Object key, String defaultString){
		Object value = this.get(key);
		if("".equals(value)){
			if(defaultString == null){
				defaultString = "";
			}
			return defaultString;
		}else{
			return value.toString();
		}
	}
	
	public int getInt(Object key){
		try {
			return Integer.parseInt(this.get(key).toString());
		} catch (Exception e) {
			return 0;
		}
	}
	
	public int getInt(Object key, int value){
		try {
			return Integer.parseInt(this.get(key).toString());
		} catch (Exception e) {
			return value;
		}
	}



}
```
#### InterfaceSend.java
```java
package kr.or.cbdc.interfaces;

import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpMethod;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

import kr.or.cbdc.application.ewa.common.dto.CbsHeader;
import kr.or.cbdc.application.ewa.common.dto.CbsReqWrapper;
import kr.or.cbdc.config.props.ConfigProperties;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.ErrorCode;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Component
@Service
public class InterfaceSend {

	private @Autowired ApiCallHelper apiCallHelper;
	private @Autowired ConfigProperties configProperties;

    @Value(value = "${config.nice.info}")
    private String niceInfo ="";
    
    /**
##### 원인증서 token 설정
     */
    @Value(value = "${config.wooriwon.token}")
    private String wooriwonToken = "";
    
	/**
## G/W 호출(ewa/pdm > G/W)
## 
## @param url
## @param inMap
## @return
	 */
	public InterfaceMap sendGw(String url, InterfaceMap inMap) {
		ObjectNode jsonNodes = (new ObjectMapper()).valueToTree(inMap);
		log.debug(jsonNodes.toString());
		InterfaceMap ret = new InterfaceMap();
		try {
			String fullUrl = configProperties.getGateway().getUrl() + url;

			log.info("INTERFACE G/W REQUEST URL: " + fullUrl);
			log.info("INTERFACE G/W REQUEST PARAM: " + jsonNodes.toString());

			JsonNode respPayLoad = apiCallHelper.callURL(fullUrl, null, jsonNodes, HttpMethod.POST);

			log.info("Interface G/W RESPONSE response:" + respPayLoad.toString());
			ret = new InterfaceMap(respPayLoad.toString());
			log.debug("return=" + ret.toString());
			ret.forEach((key, value) -> log.debug("=======>[{}]=[{}]", key, value));
		} catch (Exception e) {
			throw new RuntimeException(e);
		}
		return ret;
	}
	
	/**
## G/W Proxy 호출(G/W > G/W Proxy)
## 
## @param url
## @param dto
## @param headers
## @return
	 */
	@SuppressWarnings("rawtypes")
	public JsonNode sendGwProxy(String url, CbsReqWrapper dto) {
		return sendGwProxy(url, dto, null);
	}

	/**
## G/W Proxy 호출(G/W > G/W Proxy)
## 
## @param url
## @param dto
## @param headers
## @return
	 */
	@SuppressWarnings("rawtypes")
	public JsonNode sendGwProxy(String url, CbsReqWrapper dto, Map<String, String> headers) {
		JsonNode ret = null;
		try {
			String fullUrl = configProperties.getCoreBanking().getUrl() + url;
			String appKey = configProperties.getCoreBanking().getAppKey();

			CbsHeader cbsHeader = CbsHeader.builder().build();
			dto.setDataHeader(cbsHeader);
			ObjectNode jsonNodes = (new ObjectMapper()).valueToTree(dto);

			log.info("INTERFACE G/W Proxy REQUEST URL: " + fullUrl);
			log.info("INTERFACE G/W Proxy REQUEST APP-KEY: " + appKey);
			log.info("INTERFACE G/W Proxy REQUEST PARAM: " + jsonNodes.toString());
			
			// HTTP Headers
			Map<String, String> reqHeaders = new HashMap<>();
			if (headers != null) {
				reqHeaders = headers;
			}
			reqHeaders.put("appkey", appKey);

			JsonNode respPayLoad = apiCallHelper.callURLWithHeaders(fullUrl, jsonNodes, HttpMethod.POST, reqHeaders);

			log.info("INTERFACE G/W Proxy REQUEST response: " + respPayLoad.toString());

			ret = respPayLoad.get("dataBody");
			log.debug("return=" + ret.toString());
		} catch (Exception e) {
			throw new RuntimeException(e);
		}
		return ret;
	}

	/**
## CBDC 발행/환수, 증감변화 내역 전송
## 
## @param map
## @return
	 */
	public InterfaceMap api_E_001(InterfaceMap map) {
		return sendGw("/ewa/gw/cbdc", map);
	}

	/**
## 이용자/사업자 전자지갑 연계계좌 등록/변경
## 
## @param map
## @return
	 */
	public InterfaceMap api_E_002(InterfaceMap map) {
		return sendGw("/ewa/gw/acReg", map);
	}
	
	/**
## 보유 계좌 목록 조회(전계좌조회), 보유 계좌 유효성 조회, 보유 계좌 잔액조회, 계좌 비밀번호 입력검증
## 
## @param map
## @return
	 */
	public InterfaceMap api_E_003_New(InterfaceMap map) {
		return sendGw("/ewa/gw/acno", map);
	}
		
	/**
## 보유 계좌 목록 조회(전계좌조회)
## 
## @param map
## @return
	 */
	public InterfaceMap api_E_003(InterfaceMap map) {
		map.put("inqDscd", "02");
		return sendGw("/ewa/gw/acno", map);
	}

	/**
## 보유 계좌 유효성조회
## 
## @param map
## @return
	 */
	public InterfaceMap api_E_003_valid(InterfaceMap map) {
		map.put("inqDscd", "01");
		return sendGw("/ewa/gw/acno", map);
	}

	/**
## 잔액 조회
## 
## @param map
## @return
	 */
	public InterfaceMap api_E_003_balance(InterfaceMap map) {
		map.put("inqDscd", "01");
		return sendGw("/ewa/gw/acno", map);
	}

	/**
## 계좌 비밀번호 입력 검증
## 
## @param map
## @return
	 */
	public InterfaceMap api_E_003_acnoPw(InterfaceMap map) {
		map.put("inqDscd", "03");
		return sendGw("/ewa/gw/acno", map);
	}
	
	/**
## 예금토큰 onRamp
## 
## @param map
## @return
	 */
	public InterfaceMap api_E_006_onRamp(InterfaceMap map) {
		return sendGw("/ewa/gw/onRamp", map);
	}
	
	/**
## 예금토큰 offRamp
## 
## @param map
## @return
	 */
	public InterfaceMap api_E_006_offRamp(InterfaceMap map) {
		return sendGw("/ewa/gw/offRamp", map);
	}
	
	/**
## 지갑탈회
## 
## @param map
## @return
	 */
	public InterfaceMap api_E_006_withdraw(InterfaceMap map) {
		return sendGw("/ewa/gw/withdraw", map);
	}
	
	/**
## 예금토큰 api_E_006_onRampFail
## 
## @param map
## @return
	 */
	public InterfaceMap api_E_006_onRampFail(InterfaceMap map) {
		return sendGw("/ewa/gw/onRampFail", map);
	}
	
	/**
## 예금토큰 api_E_006_offRampFail
## 
## @param map
## @return
	 */
	public InterfaceMap api_E_006_offRampFail(InterfaceMap map) {
		return sendGw("/ewa/gw/offRampFail", map);
	}
	
	/**
## 최종대사결과 계정계측에 보정처리 요청
## 
## @param map
## @return
	 */
	public InterfaceMap api_E_007(InterfaceMap map) {
		return sendGw("/ewa/gw/reconCorr", map);
	}

	/**
## 전자지갑개설 완료정보 전송 (비대명실명확인센터와 통신)
## 
## @param map
## @return
	 */
	public InterfaceMap api_E_008(InterfaceMap map) {
		return sendGw("/ewa/gw/walletReg", map);
	}
	
	/**
## 앱 푸시
## 
## @param map
## @return
	 */
	public InterfaceMap api_E_009(InterfaceMap map) {
		return sendGw("/ewa/gw/ums", map);
	}
		
	public InterfaceMap sendWooriWon(String url, InterfaceMap inMap) {
		log.debug("sendWooriWon Start url= {}",url);
		log.debug("sendWooriWon inMap= {}",inMap.toString());
        ObjectNode jsonNodes = (new ObjectMapper()).valueToTree(inMap);
        log.debug(jsonNodes.toString());
        InterfaceMap ret = new InterfaceMap();
        try {
        	//String appKey = configProperties.getCoreBanking().getAppKey();                
        	String token = wooriwonToken;      	
			// HTTP Headers
			//Map<String, String> reqHeaders = new HashMap<>();
			//reqHeaders.put("Authorization", token);
			//reqHeaders.put("appkey", appKey);
			//JsonNode respPayLoad = apiCallHelper.callURLWithHeaders(url, jsonNodes, HttpMethod.POST, reqHeaders);
            JsonNode respPayLoad  = apiCallHelper.wooriWonCallURL(url,token,jsonNodes,HttpMethod.POST);
            ret = new InterfaceMap(respPayLoad.toString());
            //log.debug("sendWooriWon return="+ret.toString());
            ret.forEach((key, value) -> log.debug("=======>[{}]=[{}]",key, value));
        }catch (Exception e) {
            //throw new RuntimeException(e);
        	log.error("sendWooriWon error="+e.getMessage());
        	ret = getErrMessage(e);
        }
        return ret;
	}	
	
    public InterfaceMap getErrMessage(Exception ex)
    {
    	InterfaceMap ret = new InterfaceMap();        
        String tmpStr = ex.getMessage();
        int tmpIdx = tmpStr.indexOf("{");
        if(tmpIdx != -1) {
            tmpStr = tmpStr.substring(tmpIdx, tmpStr.length()-1);
            try {
                ret = new InterfaceMap(tmpStr);
            }catch (Exception ex2) {
            	log.error("getErrMessage error="+ex2.getMessage());
            }
        }
        return ret;
    }
    
	/**
## CI로 인증서 시리얼조회
## 
## @param map
## @return
	 */	
	public InterfaceMap api_certSerial(InterfaceMap map) {
		
		//개발 https://apidev.wooribank.com/wpotdev/
		//테스트 https://apitst.wooribank.com/wpot/
		//운영 : https://api.wooribank.com/wpot/
		String url = "";
    	if(niceInfo.equals("dev")) {
    		//개발
    		//url = "https://apidev.wooribank.com/wpotdev/" + "cert/certSerial";
    		url = configProperties.getCoreBanking().getUrl() + "/wpotdev/cert/certSerial";
    	}else if(niceInfo.equals("stg")) { 
//    		테스트
    		//url = "https://apitst.wooribank.com/wpot/" + "cert/certSerial";
    		url = configProperties.getCoreBanking().getUrl() + "/wpot/cert/certSerial";
    	}else if(niceInfo.equals("real")) {
    		//운영
    		url = configProperties.getCoreBanking().getUrl() + "/wpot/cert/certSerial";    		
    	}
    	log.debug("sendWooriWon api_certSerial map="+map.toString());
		return sendWooriWon(url, map);
	}	
	
	/**
## 전자서명 값 검증후 결과전송
## 
## @param map
## @return
	 */	
	public InterfaceMap api_newOneVerify(InterfaceMap map) {
		//개발 https://apidev.wooribank.com/wpotdev/
		//테스트 https://apitst.wooribank.com/wpot/
		//운영 : https://api.wooribank.com/wpot/	
		String url = "";
    	if(niceInfo.equals("dev")) {
    	//if(!niceInfo.equals("real")) {	
    		//개발
    		//url = "https://apidev.wooribank.com/wpotdev/" + "cert/newOneVerify";
    		url = configProperties.getCoreBanking().getUrl() + "/wpotdev/cert/newOneVerify";
    	}else if(niceInfo.equals("stg")) {    	
//    		테스트
    		//url = "https://apitst.wooribank.com/wpot/" + "cert/newOneVerify";
    		url = configProperties.getCoreBanking().getUrl() + "/wpot/cert/newOneVerify";
    	}else if(niceInfo.equals("real")) {
    		//운영
    		url = configProperties.getCoreBanking().getUrl() + "/wpot/cert/newOneVerify";    		
    	}		
    	log.debug("sendWooriWon api_newOneVerify map="+map.toString());
		return sendWooriWon(url, map);
	}	
	
}
```
#### 그 외 관련 code
```java
package kr.or.cbdc.config.props;

import java.io.IOException;
import java.util.List;
import java.util.Map;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

import kr.or.cbdc.domain.main.mapper.sys.schdul.SyncScheduleMapper;
import kr.or.cbdc.infrastructure.framework.core.support.scheduling.AnyJob;
import kr.or.cbdc.infrastructure.framework.core.support.scheduling.interceptor.AnyJobInterceptor;
import lombok.Data;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;

@Data
@Configuration
@ConfigurationProperties(prefix = "config")
public class ConfigProperties {

    private String systemTitle;
    private String bankCode;
    private String bokCode = "BOK";
    private String bokNm = "한국은행";
    private String bankNo;
    private String bankNm;
    private String iniFilePath;
    private String activeServer;
    private java.io.File logsDirectory;
    private java.io.File tempDirectory;
    private String defaultLocale;
    private Message message;
    private Log log;
    private File file;
    private Scheduler scheduler;
    private Login login;
    private DataCrypt dataCrypt;
    private Coopsystem coopsystem;
    private Report report;
    private BokCbdc bokCbdc;
    private Payment payment;
    private List<String> holidayList;
    @Valid private CoreBanking coreBanking;
    @Valid private Gateway gateway;
    private String serverId;
    @Valid private Sftp sftp;

    @Data
    public static class Message {

        private InvalidText invalidText;
        @Data
        public static class InvalidText {

            private String prefix;
            private String suffix;
        }
    }
    @Data
    public static class Log {

        private boolean enable;
        private Query query;
        private Error error;
        private Login login;
        private Menu menu;

        @Data
        public static class Query {

            private boolean enable;


        }
        @Data
        public static class Error {

            private boolean enable;
            private String serverCode;
        }
        @Data
        public static class Login {

            private boolean enable;
        }
        @Data
        public static class Menu {

            private boolean enable;

        }

    }
    @Data
    public static class File {

        private String contentTransferEncoding;
        private Boolean downloadFilenameUrlEncode;
        private Boolean downloadFilenameEncoding;
        private Repository repository;
        private String downloadDir;

        @Data
        public static class Repository {

            private boolean createIfNotExists;
            private Map<String, String> repositories;

            public boolean isCreateIfNotExists() {
                return this.createIfNotExists;
            }

            public void setCreateIfNotExists(boolean createIfNotExists) {
                this.createIfNotExists = createIfNotExists;
            }

        }

    }
    @Data
    public static class Scheduler {

        private Boolean enable;
        private Class<? extends AnyJobInterceptor> jobInterceptor;
        private Map<String, JobDetailConfig> jobDetails;
        private String[] clusteredProfiles;

        @Data
        public static class JobDetailConfig {

            private String name;
            private String targetSchema;
            private Class<? extends AnyJob> jobClass;
            private Class<SyncScheduleMapper> countClass;
            private Boolean holdingJobContinuouslyExecute;
            private List<String> cronExpressionList;
            private List<String> dateRangeList;
            private Integer startDelay;
            private Integer jobSplits;
            private String[] profiles;

        }
    }
    @Data
    public static class Login {

        private String defaultAuthorCode;
        private Admin admin;
        private Sso sso;
        private Fail fail;

        @Data
        public static class Admin {

            private boolean enable;
            private List<String> ipList;
            private String key;
            private String password;
        }

        @Data
        public static class Sso {

            private boolean enable;
            private String sApiKey;
            private String ssoToKenName;

        }
        @Data
        public static class Fail {

            private int availCount;
        }

    }

    @Data
    public static class DataCrypt {

        private String[] columnNames;
        private String[] onewayColumnNames;

    }

    @Data
    public static class Coopsystem {

        private String srmsUrl;
        private String dbUrl;
        private String mainUrl;

    }

    @Data
    public static class Report {

        private java.io.File jsonDirectory;
        private java.io.File jarDirectory;


        public void setJsonDirectory(java.io.File jsonDirectory) {
            try {
                this.jsonDirectory = jsonDirectory.getCanonicalFile();
            } catch (IOException e) {
                this.jsonDirectory = jsonDirectory;
            }
        }

        public void setJarDirectory(java.io.File jarDirectory) {
            try {
                this.jarDirectory = jarDirectory.getCanonicalFile();
            } catch (IOException e) {
                this.jarDirectory = jarDirectory;
            }
        }

    }

    @Data
    public static class BokCbdc {
        private String bokServerRpc;
        private String keyServerRpc;
        private String defaultPubKey;
        private String fromAdres;
        private String toAdres;

    }

    @Data
    public static class Payment {
        public String url;

    }


    @Data
    public static class CoreBanking {
        private String url;
        private String appKey;
        @Valid private Retry retry;
        @Valid private Timeout timeout;
        private Token token;
        @Valid private CbdcRamp cbdcRamp;
        @Valid private BalanceCore balanceCore;
        @Valid private TdRamp tdRamp;
        @Valid private DeactivateBulk deactivateBulk;
        @Valid private ReconCbdc reconCbdc;
        @Valid private ReconTd reconTd;
        @Valid private IssueCbdc issueCbdc;
        @Valid private BurnCbdc burnCbdc;
        @Valid private DeactivateAll deactivateAll;
        @Valid private AppPush appPush;
    }

    @Data
    public static class Gateway {
        private String url;
        @Valid private Retry retry;
        @Valid private Timeout timeout;
        @Valid private Balance balance;
        @Valid private OnRamp onRamp;
        @Valid private OnRampFail OnRampFail;
        @Valid private OffRamp offRamp;
        @Valid private OffRampFail offRampFail;
        @Valid private Cbdc cbdc;
        @Valid private Ums ums;
    }
    @Data
    public static class Retry {
        @Min(value = 1, message = "Retry count must be at least 1")
        @Max(value = 3, message = "Retry count cannot exceed 3")
        private int count;
        
        @Min(value = 100, message = "Retry delay must be at least 100ms")
        @Max(value = 1000, message = "Retry delay cannot exceed 1000ms")
        private int delay;
    }

    @Data
    public static class Timeout {
        @Min(value = 1000, message = "Connect timeout must be at least 1000ms")
        @Max(value = 60000, message = "Connect timeout cannot exceed 60000ms")
        private int connect;
        
        @Min(value = 1000, message = "Connect timeout must be at least 1000ms")
        @Max(value = 60000, message = "Connect timeout cannot exceed 60000ms")
        private int read;
    }

    @Data
    public static class Token {
        private String value;
    }

    @Data
    public static class BalanceCore {
        @NotBlank(message = "balanceCore openAPI(core-banking) url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }
    
    @Data
    public static class CbdcRamp {
        @NotBlank(message = "cbdcRamp openAPI(core-banking) url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class TdRamp {
        @NotBlank(message = "tdRamp openAPI(core-banking) url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class OffRampFailCore {
        @NotBlank(message = "onRampFail openAPI(core-banking) url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class DeactivateBulk {
        @NotBlank(message = "deactivateBulk openAPI url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class ReconCbdc {
        @NotBlank(message = "reconCbdc openAPI url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class ReconTd {
        @NotBlank(message = "reconTd openAPI url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class IssueCbdc {
        @NotBlank(message = "issueCbdc openAPI url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class BurnCbdc {
        @NotBlank(message = "burnCbdc openAPI url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class DeactivateAll {
        @NotBlank(message = "deactivateAll openAPI url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class AppPush {
        @NotBlank(message = "appPush openAPI url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class Balance {
        @NotBlank(message = "balance gateway url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class OnRamp {
        @NotBlank(message = "onRamp gateway url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class OnRampFail {
        @NotBlank(message = "OnRampFail gateway url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class OffRamp {
        @NotBlank(message = "offRamp gateway url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class OffRampFail {
        @NotBlank(message = "OffRampFail gateway url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }

    @Data
    public static class Cbdc {
        @NotBlank(message = "cbdc gateway url이 없습니다.")
        @Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
        private String url;
    }
    
    @Data
    public static class Ums {
    	@NotBlank(message = "cbdc gateway url이 없습니다.")
    	@Pattern(regexp = "^(http|https)://.*", message = "URL은 http:// 또는 https://로 시작해야 합니다.")
    	private String url;
    }

    @Data
    public static class Sftp {
        @NotBlank(message = "SFTP host is required")
        private String host;
        
        @Min(value = 1, message = "Port must be greater than 0")
        @Max(value = 65535, message = "Port must be less than 65536")
        private int port;
        
        @NotBlank(message = "SFTP username is required")
        private String username;
        
        @NotBlank(message = "SFTP password is required")
        private String password;

        @Valid
        private Remote remote;
    }
    
    @Data
    public static class Remote {
        @NotBlank(message = "sftp 디렉토리가 없습니다.")
        private String directory;
        @NotBlank(message = "기본 파일명이 없습니다.")
        private String fileBaseName;
    }
}
--
package kr.or.cbdc.application.ewa.common.dto;

import java.util.Date;

import com.fasterxml.jackson.annotation.JsonAlias;
import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonInclude;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;
import lombok.ToString;

@Data
@EqualsAndHashCode(callSuper = true)
@ToString(callSuper = true)
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class CbsRampResponseDto extends CbsErrorResponseDto {

	@JsonAlias({ "dpstTknDscd", "DPST_TKN_DSCD" })
	private String dpstTknDscd;

	@JsonAlias({ "dpsInpAcno", "DPS_INP_ACNO" })
	private String dpsInpAcno;

	@JsonAlias({ "trnDt", "TRN_DT" })
	@JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "yyyyMMdd")
	private Date trnDt;

	@JsonAlias({ "trnSrno", "TRN_SRNO" })
	private String trnSrno;

	@JsonAlias({ "trnLogKeyVal", "TRN_LOG_KEY_VAL" })
	private String trnLogKeyVal;

}

--
package kr.or.cbdc.application.ewa.common.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
##### IF-API-E-009 앱 푸시 요청 DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class GwUmsAppPushDto {

	private String umsTrno;

	private String umsTmplCd;

	private String deptSbrCd;

	private String umsAppId;

	private String pushAddInf;

	private String rsvDt;

	private String csno;

	private String dpsTelNo;

	private String dmsgTelNo;

	private String sprTxt1;

	private String sprTxt2;

	private String cusNm;

	private String acno;

	private String stlAm;

	private String bal;

	private String crtfNo;

	private String bizTp;

	private String mpng1;

	private String mpng2;

	private String mpng3;

	private String mpng4;

	private String mpng5;

	private String mpng6;

	private String mpng7;

	private String mpng8;

	private String mpng9;

	private String mpng10;

	private String mpngAllTitl;

	private String mpngAll;

	private String mpngAppBd;

}
--
package kr.or.cbdc.application.ewa.common.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CbsHeader {
    @JsonProperty("appkey")
    private String appkey;
}

--
package kr.or.cbdc.application.ewa.common.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class CbsReqWrapper <T> {
    @JsonProperty("dataHeader")
    private CbsHeader dataHeader;
    
    @JsonProperty("dataBody")
    private T dataBody;
}
--
package kr.or.cbdc.application.common.pushMsg.model;

import kr.or.cbdc.infrastructure.idgen.util.IdGenerationUtil;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.experimental.SuperBuilder;

import java.util.Date;

@Getter
@Setter
@SuperBuilder
@NoArgsConstructor
public class TbAppMssageMastr {

    protected String mssageManageId;

    protected String nttManageId;

    protected String cstmrNo;

    protected String pushToken;

    protected String mssageTycd;

    protected String sj;

    protected String mssageCn;

    protected String processUrl;

    protected String sndngMssageCn;

    protected String otherSndngMssageCn;

    protected String indictYn;

    protected Date registDt;

    protected String registerId;

    protected Date lastChangeDt;

    protected String lastChangerId;

    public TbAppMssageMastr newId() {
        this.setMssageManageId(IdGenerationUtil.createUid("TB_APP_MSSAGE_MASTR"));

        return this;
    }

}

--
package kr.or.cbdc.domain.main.mapper.sys.pushId;

import org.apache.ibatis.annotations.Param;

import kr.or.cbdc.config.datasources.DataSourceMainConfig.MainSqlMapper;
import kr.or.cbdc.domain.main.model.sys.pushId.TbPushIdEntity;

/**
##### 시스템 - UID Entity Mapper
 */
@MainSqlMapper
public interface TbSysPushIdMapper {

	/**
## 생성
## 
## @param tbPushIdEntity
## @return
	 */
	public int insert(@Param("tbPushIdEntity") TbPushIdEntity tbPushIdEntity);

}

--
package kr.or.cbdc.domain.main.model.sys.pushId;

import kr.or.cbdc.domain.main.model.MainEntity;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.experimental.SuperBuilder;

@Getter
@Setter
@SuperBuilder
@NoArgsConstructor
public class TbPushIdEntity extends MainEntity {

	/**
## 
	 */
	private static final long serialVersionUID = -3436108795111110850L;

	protected String pushId;

	protected String reqstDt;

	protected String registerId;

}

--
package kr.or.cbdc.infrastructure.framework.core.foundation.exception;


public class BizException extends BaseException {

    private static final long serialVersionUID = 577016911774547784L;
    private String requestId;

    
    /**
##### 기본 생성자.
     */
    public BizException(ErrorCode errorCode) {
        super(errorCode);
    }

    /**
##### 기본 생성자.
     */
    public BizException(ErrorCode errorCode, Throwable cause) {
        super(errorCode,cause);
    }
    
    /**
##### 기본 생성자.
     */
    public BizException(ErrorCode errorCode, String requestId) {
        super(errorCode);
        this.requestId = requestId;
    }
    
    /**
##### 상세 메시지를 추가하는 생성자.
     *
##### @param errorCode ErrorCode 객체
##### @param message 상세 메시지
     */
    public BizException(ErrorCode errorCode, String requestId, Object... args) {
        super(errorCode, args);
        this.requestId = requestId;
        
    }

    /**
##### 원본 예외를 포함하는 생성자.
     *
##### @param errorCode ErrorCode 객체
##### @param cause 원인 예외
     */
    public BizException(ErrorCode errorCode, String requestId, Throwable cause) {
        super(errorCode, cause);
        this.requestId = requestId;

    }

    /**
##### 상세 메시지와 원본 예외를 포함하는 생성자.
     *
##### @param errorCode ErrorCode 객체
##### @param message 상세 메시지
##### @param cause 원인 예외
     */
    public BizException(ErrorCode errorCode, String requestId, String message, Throwable cause) {
        super(errorCode, message, cause);
        this.requestId = requestId;

    }

    /**
##### 에러 메시지 반환. 원래 예외 메시지와 함께 반환됨.
     */
    public String getDetailMessage() {
        return super.getDetailMessages(requestId);
    }

}
--
package kr.or.cbdc.infrastructure.framework.core.foundation.exception;

import org.springframework.lang.Nullable;
import org.springframework.util.CollectionUtils;
import org.springframework.util.ObjectUtils;
import org.springframework.util.StringUtils;
import java.util.Collection;
import java.util.Objects;

public final class ErrorAssert {

    private ErrorAssert() {
        // 유틸리티 클래스는 인스턴스화할 수 없음
    }

    /**
##### 조건이 참이 아니면 BizException을 던짐
     *
##### @param expression 검증할 조건
##### @param errorCode  실패 시 던질 ErrorCode 객체
     */
    public static void isTrue(boolean expression, ErrorCode errorCode, Object... args) {
        if (!expression) {
            throw new InputParamException(errorCode, null,args);
        }
    }

    /**
##### 객체가 null이 아니어야 함. null이면 InputParamException 던짐
     *
##### @param object    검증할 객체
##### @param errorCode 실패 시 던질 ErrorCode 객체
     */
    public static void notNull(Object object, ErrorCode errorCode, Object... args) {
        if (object == null) {
            throw new InputParamException(errorCode,null, args);
        }
    }

    /**
## Assert that an object is {@code null}.
	 *
	 */
	public static void isNull(@Nullable Object object, ErrorCode errorCode, Object... args) {
		if (object != null) {
			throw new InputParamException(errorCode,null, args);
		}
	}


    public static void hasLength(@Nullable String text, ErrorCode errorCode, Object... args) {
		if (!StringUtils.hasLength(text)) {
			throw new InputParamException(errorCode,null, args);
		}
	}

    /**
##### 문자열이 비어있으면 InputParamException 던짐
     *
##### @param text      검증할 문자열
##### @param errorCode 실패 시 던질 ErrorCode 객체
     */
    public static void notEmpty(String text, ErrorCode errorCode, Object... args) {
        if (text == null || text.trim().isEmpty()) {
            throw new InputParamException(errorCode,null, args);
        }
    }

    public static void notEmpty(@Nullable Object[] array, ErrorCode errorCode, Object... args) {
		if (ObjectUtils.isEmpty(array)) {
			throw new InputParamException(errorCode,null,args);
		}
	}

    public static void notEmpty(@Nullable Collection<?> collection,ErrorCode errorCode, Object... args) {
		if (CollectionUtils.isEmpty(collection)) {
			throw new InputParamException(errorCode,null,args);
		}
	}

    /**
##### 두 객체가 동일한지 확인합니다. 다르면 `BizException`을 던집니다.
     *
##### @param expected 기대되는 값
##### @param actual 실제 값
##### @param errorCode 에러 코드
##### @param args 메시지 포맷에 필요한 인수 (필요 없는 경우 제공하지 않음)
     */
    public static void equals(Object expected, Object actual, ErrorCode errorCode, Object... args) {
        if (!Objects.equals(expected, actual)) {
            throw new BizException(errorCode,null, args);
        }
    }

    /**
##### 숫자가 0 이상이어야 함. 그렇지 않으면 BizException을 던짐
     *
##### @param number    검증할 숫자
##### @param errorCode 실패 시 던질 ErrorCode 객체
     */
    public static void isPositive(int number, ErrorCode errorCode) {
        if (number <= 0) {
            throw new BizException(errorCode);
        }
    }

}

--
package kr.or.cbdc.infrastructure.framework.core.foundation.exception;

import jakarta.servlet.http.HttpServletResponse;
import java.util.Arrays;

public enum ErrorCode {

    // 400 BAD_REQUEST
    INVALID_PERSON_ID(400000, HttpServletResponse.SC_BAD_REQUEST, "회원 ID를 입력하여야 합니다."),
    INVALID_CBDC_TIME(400001, HttpServletResponse.SC_BAD_REQUEST, "CBDC 발행 / 환수가 가능한 시간이 아닙니다"),
    INVALID_PASSWORD(400002, HttpServletResponse.SC_BAD_REQUEST, "비밀번호가 8~16자여야 합니다."),
    PASSWORD_MUST_INCLUDE_UPPERCASE(400003, HttpServletResponse.SC_BAD_REQUEST, "비밀번호가 대문자를 포함하여야 합니다."),
    PASSWORD_MUST_INCLUDE_LOWERCASE(400004, HttpServletResponse.SC_BAD_REQUEST, "비밀번호가 소문자를 포함하여야 합니다."),
    PASSWORD_MUST_INCLUDE_NUMBER(400005, HttpServletResponse.SC_BAD_REQUEST, "비밀번호가 숫자를 포함하여야 합니다."),
    PASSWORD_MUST_INCLUDE_SPECIAL_CHARACTER(400006, HttpServletResponse.SC_BAD_REQUEST, "비밀번호가 특수문자를 포함하여야 합니다."),
    USER_ID_REQUIRED(400007, HttpServletResponse.SC_BAD_REQUEST, "사용자 ID를 입력하여야 합니다."),
    PERSON_ID_REQUIRED(400008, HttpServletResponse.SC_BAD_REQUEST, "사람 ID를 입력하여야 합니다."),
    PASSWORD_REQUIRED(400009, HttpServletResponse.SC_BAD_REQUEST, "비밀번호를 입력하여야 합니다."),
    INVALID_MENU_ID(400010, HttpServletResponse.SC_BAD_REQUEST, "메뉴 ID가 누락되었습니다."),
    INVALID_DATE_FORMAT(400011, HttpServletResponse.SC_BAD_REQUEST, "유효하지 않은 날짜입니다."),
    INVALID_REQUEST(400012, HttpServletResponse.SC_BAD_REQUEST, "유효하지 않은 요청입니다."),
    INVALID_SIGNATURE(400013, HttpServletResponse.SC_BAD_REQUEST, "유효하지 않은 서명입니다."),
    ILLEGAL_ARGUMENT(400014, HttpServletResponse.SC_BAD_REQUEST, "잘못된 인자가 전달되었습니다."),
    MISSING_REQUIRED_FIELD(400015, HttpServletResponse.SC_BAD_REQUEST, "필수 값이 누락되었습니다."),
    MISSING_INPUT_VALUE(400016, HttpServletResponse.SC_BAD_REQUEST, "입력값이 누락되었습니다."),
    PASSWORD_LENGTH_INVALID(400017, HttpServletResponse.SC_BAD_REQUEST, "비밀번호가 8~16자여야 합니다."),
    PASSWORD_UPPERCASE_REQUIRED(400018, HttpServletResponse.SC_BAD_REQUEST, "비밀번호가 대문자를 포함하여야 합니다."),
    PASSWORD_LOWERCASE_REQUIRED(400019, HttpServletResponse.SC_BAD_REQUEST, "비밀번호가 소문자를 포함하여야 합니다."),
    PASSWORD_NUMBER_REQUIRED(400020, HttpServletResponse.SC_BAD_REQUEST, "비밀번호가 숫자를 포함하여야 합니다."),
    PASSWORD_SPECIAL_CHARACTER_REQUIRED(400021, HttpServletResponse.SC_BAD_REQUEST, "비밀번호가 특수문자를 포함하여야 합니다."),
    INVALID_PIN_NUMBER(400022, HttpServletResponse.SC_BAD_REQUEST, "핀번호를 입력하여야 합니다."),
    DONT_USE_PREV_PIN_NUMBER(400023, HttpServletResponse.SC_BAD_REQUEST, "이전 핀번호로는 변경이 불가합니다."),
    INVALID_SEQUENTIAL_NUMBER(400024, HttpServletResponse.SC_BAD_REQUEST, "생년월일, 휴대폰 번호 또는 동일하거나 연속된 숫자는 등록이 제한됩니다."),
    EMPTY_BLACKLIST(400025, HttpServletResponse.SC_BAD_REQUEST, "등록할 블랙리스트가 없습니다."),
    FAILED_REGIST_USER(400026, HttpServletResponse.SC_BAD_REQUEST, "사용자 등록 실패."),
    CUSTOMER_ID_REQUIRED(400027, HttpServletResponse.SC_BAD_REQUEST, "고객번호를 입력하여야 합니다."),
    CUSTOMER_INFO_IS_NULL(400028, HttpServletResponse.SC_BAD_REQUEST, "고객 정보가 존재하지 않습니다. 회원가입 진행"),
    INVALID_TRANSACTION_AMOUNT(400029, HttpServletResponse.SC_BAD_REQUEST, "전환 입금 금액을 입력하여야 합니다."),
    INVALID_ALIAS(400030, HttpServletResponse.SC_BAD_REQUEST, "간편주소를 입력하여야 합니다."),
    OTP_KEY_MISSING(400031, HttpServletResponse.SC_BAD_REQUEST, "OTP 키가 존재하지 않습니다."),
    AUTH_SEQ_MISSING(400032, HttpServletResponse.SC_BAD_REQUEST, "authSeq를 입력하여야 합니다."),
    CI_MISSING(400033, HttpServletResponse.SC_BAD_REQUEST, "CI를 입력하여야 합니다."),
    INVALID_CI_MATCH(400034, HttpServletResponse.SC_BAD_REQUEST, "CI가 일치하지 않습니다."),
    CBDC_SERVICE_ADMIN_ROLE_FAILURE(400035, HttpServletResponse.SC_BAD_REQUEST, "CBDC 토큰에 서비스 관리자 설정이 실패했습니다."),
    CBDC_SERVICE_ACCESS_ROLE_FAILURE(400036, HttpServletResponse.SC_BAD_REQUEST, "CBDC 토큰에 대한 참가기관 접근 설정이 실패했습니다."),
    CBDC_MANUFACTURE_SERVICE_ACCESS_ROLE_FAILURE(400037, HttpServletResponse.SC_BAD_REQUEST, "CBDC 토큰에 대한 제조지갑의 접근 설정이 실패했습니다."),
    CBDC_MANUFACTURE_SERVICE_MANUFACTURE_ROLE_FAILURE(400038, HttpServletResponse.SC_BAD_REQUEST, "CBDC 토큰에 대한 제조지갑의 접근 설정이 실패했습니다."),
    CBDC_ISSUE_SERVICE_ACCESS_ROLE_FAILURE(400039, HttpServletResponse.SC_BAD_REQUEST, "CBDC 토큰에 발행준비지갑의 ACCESS_ROLE 접근 설정이 실패했습니다."),
    CBDC_REDEMP_SERVICE_ACCESS_ROLE_FAILURE(400040, HttpServletResponse.SC_BAD_REQUEST, "CBDC 환수지갑에 ACCESS_ROLE 설정이 실패했습니다."),
    CBDC_DSUSE_SERVICE_ACCESS_ROLE_FAILURE(400041, HttpServletResponse.SC_BAD_REQUEST, "CBDC 폐기지갑에 ACCESS_ROLE설정이 실패했습니다."),
    CBDC_MORTGATE_SERVICE_ACCESS_ROLE_FAILURE(400042, HttpServletResponse.SC_BAD_REQUEST, "CBDC 담보지갑에 대한 접근 설정이 실패했습니다."),
    CBDC_BURNER_SERVICE_A_ROLE_FAILURE(400043, HttpServletResponse.SC_BAD_REQUEST, "CBDC 폐기지갑에 BURNER_ROLE설정이 실패했습니다."),
    TD_SERVICE_ADMIN_ROLE_FAILURE(400044, HttpServletResponse.SC_BAD_REQUEST, "예금 토큰 에 서비스 관리자 설정이 실패했습니다."),
    TD_MANUFACTURING_WALLET_CREATION_FAILURE(400045, HttpServletResponse.SC_BAD_REQUEST, "예금 토큰 제조 지갑이 생성되어야 합니다."),
    MANUFACTURING_WALLET_NOT_FOUND(400046, HttpServletResponse.SC_BAD_REQUEST, "제조 지갑이 없습니다. 제조지갑을 생성하여 주십시오"),
    TD_MANUFACTURING_WALLET_APPROVAL_FAILURE(400047, HttpServletResponse.SC_BAD_REQUEST, "예금 토큰 제조 지갑이 생성 요청이 승인되지 않았습니다."),
    TD_MINTER_ROLE_ASSIGNMENT_FAILURE(400048, HttpServletResponse.SC_BAD_REQUEST, "예금 토큰 제조지갑에 MINTER_ROLE 권한 설정이 실패했습니다. MSG : [%s]"),
    TD_MINTER_ROLE_ASSIGNMENT_TIME_FAILURE(400049, HttpServletResponse.SC_BAD_REQUEST, "예금 토큰 제조지갑에 MINTER_ROLE 권한 설정이 실패했습니다."),
    TD_DISPOSAL_WALLET_CREATION_FAILURE(400050, HttpServletResponse.SC_BAD_REQUEST, "예금 토큰 폐기 지갑이 생성되어야 합니다."),
    TD_DISPOSAL_WALLET_APPROVAL_FAILURE(400051, HttpServletResponse.SC_BAD_REQUEST, "예금 토큰 폐기 지갑 요청이 승인되지 않았습니다."),
    TD_BURNER_ROLE_ASSIGNMENT_FAILURE(400052, HttpServletResponse.SC_BAD_REQUEST, "예금 토큰 폐기지갑에 BURNER_ROLE 권한 설정이 실패했습니다. MSG : [%s]"),
    TD_BURNER_ROLE_ASSIGNMENT_TIME_FAILURE(400053, HttpServletResponse.SC_BAD_REQUEST, "예금 토큰 폐기지갑에 BURNER_ROLE 권한 설정이 실패했습니다."),
    TD_CONTRACT_DEPLOYMENT_FAILURE(400054, HttpServletResponse.SC_BAD_REQUEST, "예금 토큰 컨트랙트가 배포되어야 합니다."),
    TD_CONTRACT_APPROVAL_FAILURE(400055, HttpServletResponse.SC_BAD_REQUEST, "예금 토큰 컨트랙트가 배포요청은 되었으나 승인이 안됐습니다."),
    CONTRACT_APPROVAL_FAILURE(400056, HttpServletResponse.SC_BAD_REQUEST, "[%s] 컨트랙트가 배포요청은 되었으나 승인이 안됐습니다."),
    TD_TOKEN_SERVICE_ADMIN_FAILURE(400057, HttpServletResponse.SC_BAD_REQUEST, "예금 토큰에 서비스 관리자 설정이 실패했습니다."),
    MANUFACTURING_WALLET_ROLE_ASSIGNMENT_FAILURE(400058, HttpServletResponse.SC_BAD_REQUEST, "예금 토큰 제조지갑에 권한 설정이 실패했습니다."),
    TD1_MANUFACTURING_FAILURE(400059, HttpServletResponse.SC_BAD_REQUEST, "예금 토큰 제조를 실패 했습니다."),
    MISSING_REQUIRED_FIELD_ROW(400060, HttpServletResponse.SC_BAD_REQUEST, "%d번째 row : 필수값이 누락되었습니다. 다시 확인해주세요."),
    OWNER_WALLET_CREATE_FAILURE(400061, HttpServletResponse.SC_BAD_REQUEST, "서비스 관리자 지갑을 생성할 수 없습니다."),
    NEED_OWNER_WALLET(400062, HttpServletResponse.SC_BAD_REQUEST, "서비스 관리자 지갑이 존재 하여야 합니다."),
    ADMIN_WALLET_CREATE_FAILURE(400063, HttpServletResponse.SC_BAD_REQUEST, "배포 관리자 지갑을 생성할 수 없습니다."),
    TD_ISU_WALLET_CREATE_FAILURE(400064, HttpServletResponse.SC_BAD_REQUEST, "예금 토큰 발행준비 지갑을 생성할 수 없습니다."),
    TD_REFUND_WALLET_CREATE_FAILURE(400065, HttpServletResponse.SC_BAD_REQUEST, "예금 토큰 환수 지갑을 생성할 수 없습니다."),

    MINTER_ROLE_EXISTENCE_VERIFICATION_FAILURE(400066, HttpServletResponse.SC_BAD_REQUEST, "예금 토큰 제조지갑의 MINTER_ROLE 존재 확인에 실패했습니다."),
    DISPOSAL_WALLET_CREATION_FAILURE(400067, HttpServletResponse.SC_BAD_REQUEST, "예금 토큰 폐기 지갑 생성을 실패했습니다."),
    DISPOSAL_WALLET_BURNER_ROLE_ASSIGNMENT_FAILURE(400068, HttpServletResponse.SC_BAD_REQUEST, "예금 토큰 폐기지갑에 BURNER_ROLE 권한 설정이 실패했습니다."),
    TX_SIGNATURE_MISSING(400069, HttpServletResponse.SC_BAD_REQUEST, "트랜잭션 서명을 받지 못했습니다."),
    DC_BURN_FAILURE(400070, HttpServletResponse.SC_BAD_REQUEST, "DC 소각 생성에 실패했습니다."),
    INVALID_PROGRAM_DURATION(400071, HttpServletResponse.SC_BAD_REQUEST, "사용 기간이 10일을 초과하였습니다."),
    EMPTY_WALLET_ADDRESS(400072, HttpServletResponse.SC_BAD_REQUEST, "지갑주소를 입력하여야 합니다."),
    EMPTY_TRANSACTION_AMOUNT(400073, HttpServletResponse.SC_BAD_REQUEST, "이체 입금 금액을 입력하여야 합니다."),
    TRANSACTION_AMOUNT_TOO_LOW(400074, HttpServletResponse.SC_BAD_REQUEST, "0원이상을 입력하여야 합니다."),
    EMPTY_PREP_WALLET(400075, HttpServletResponse.SC_BAD_REQUEST, "예금 토큰 발행준비지갑이 없습니다. 발행준비지갑 생성부터 진행해주세요."),
    EMPTY_BURN_WALLET(400076, HttpServletResponse.SC_BAD_REQUEST, "예금 토큰 폐기지갑이 없습니다. 지갑 생성부터 진행해주세요."),
    
    BLOCKCHAIN_CALL_FAILURE(400077, HttpServletResponse.SC_BAD_REQUEST, "입금 오류. 블록체인 호출에 문제가 생겼습니다."),
    KAFKA_CALL_FAILURE(400078, HttpServletResponse.SC_BAD_REQUEST, "소각 오류. 카프카 호출에 문제가 생겼습니다."),
    DC_REVERSE_APPROVAL_ONLY(400079, HttpServletResponse.SC_BAD_REQUEST, "신청단계만 승인이 가능합니다."),
    REVERSE_AMOUNT_REQUIRED(400080, HttpServletResponse.SC_BAD_REQUEST, "전환 입금 금액을 입력하여야 합니다."),
    UNSIGNED_ERROR(400081, HttpServletResponse.SC_BAD_REQUEST, "Unsigned Transaction 생성을 실패하였습니다"),
    REC_UNSIGNED_ERROR(400082, HttpServletResponse.SC_BAD_REQUEST, "중앙은행에서 Signed Transaction 을 받지 못하였습니다"),
    REC_DB_ID_ERROR(400083, HttpServletResponse.SC_BAD_REQUEST, "중앙은행에서 DB ID를 받지 못하였습니다"),
    DEPOSIT_REVERSE_AMOUNT_REQUIRED(400084, HttpServletResponse.SC_BAD_REQUEST, "예금 전환 금액을 입력하여야 합니다."),
    REVERSE_AMOUNT_BIGGER_TD_AMOUNT_REQUIRED(400085, HttpServletResponse.SC_BAD_REQUEST, "예금전환 금액이 예금 토큰 잔액 보다 큽니다.\n다시 확인해주세요."),
    REVERSE_AMOUNT_ERROR(400086, HttpServletResponse.SC_BAD_REQUEST, "전환 입금 오류. 블록체인 호출에 문제가 생겼습니다. "),
    DEPOSIT_REVERSE_AMOUNT_ERROR(400087, HttpServletResponse.SC_BAD_REQUEST, "예금 전환 오류. 블록체인 호출에 문제가 생겼습니다. "),
    WALLET_MISSING(400088, HttpServletResponse.SC_BAD_REQUEST, "이용자 지갑이 존재하지 않습니다. 지갑 개설 후 진행해주세요."),
    ALREADY_WALLET_REGIST(400089, HttpServletResponse.SC_BAD_REQUEST, "지갑이 존재합니다."),
    WALLET_CREATION_FAILURE(400090, HttpServletResponse.SC_BAD_REQUEST, "지갑생성에 오류가 발생하였습니다."),
    SIGNATURE_REQUIRED(400091, HttpServletResponse.SC_BAD_REQUEST, "signature를 입력하여야 합니다."),
    ENCDATA_REQUIRED(400092, HttpServletResponse.SC_BAD_REQUEST, "encData를 입력하여야 합니다."),
    WRONG_REQUIRED(400093, HttpServletResponse.SC_BAD_REQUEST, "잘못된 요청입니다"),
    PROVIDE_ENCRYPTION_WALLET_INFO (400094, HttpServletResponse.SC_BAD_REQUEST, "암호화 할 지갑 정보를 전달하여 주십시오"),
    BOK_DATA_REQUEST_FAILED (400095, HttpServletResponse.SC_BAD_REQUEST, "한국은행으로 데이터 요청에 실패하였습니다."),
    BOARD_ID_NOT_FOUND(400096, HttpServletResponse.SC_BAD_REQUEST, "게시판 ID가 없습니다."),
    POLICY_ID_NOT_FOUND(400097, HttpServletResponse.SC_BAD_REQUEST, "정책 ID가 없습니다."),
    COMMUNITY_MANAGER_ID_NOT_FOUND(400098, HttpServletResponse.SC_BAD_REQUEST, "커뮤니티 관리 ID가 없습니다."),
    NOT_CA_WALLET(400099, HttpServletResponse.SC_BAD_REQUEST, "CA지갑이 아닙니다."),
    NOT_EOA_WALLET(400100, HttpServletResponse.SC_BAD_REQUEST, "EOA지갑이 아닙니다."),
    ALREADY_JOINED_USER(400101, HttpServletResponse.SC_BAD_REQUEST, "이미 가입된 사용자입니다."),
    INVALID_SYSTEM_ID(400102, HttpServletResponse.SC_BAD_REQUEST, "시스템 구분자가 누락되었습니다"),
    INVALID_PRT_REQUIRED(400103, HttpServletResponse.SC_BAD_REQUEST, "유효하지 않은 참가기관의 요청입니다"),
    INVALID_PRT_CD_REQUIRED(400104, HttpServletResponse.SC_BAD_REQUEST, "참가기관의 은행코드가 존재하지 않습니다."),
    INVALID_REFUND_REQUIRED(400105, HttpServletResponse.SC_BAD_REQUEST, "환수 요청 액을 기술하여야 합니다."),
    INVALID_REDEMP_REQUIRED(400106, HttpServletResponse.SC_BAD_REQUEST, "결제 요청을 먼저 하여야 합니다."),
    INVALID_AUTHOR_REQUIRED(400107, HttpServletResponse.SC_BAD_REQUEST, "권한에 따른 승인 순서가 적합하지 않습니다."),
    INVALID_BAN_DATE_REQUIRED(400108, HttpServletResponse.SC_BAD_REQUEST, "블랙리스트 적용 시작 날짜는 미래 날짜여야 합니다."),
    INVALID_PART_ID(400109, HttpServletResponse.SC_BAD_REQUEST, "참여기관 ID 가 기술되어야 합니다."),
    INVALID_PART_NAME(400110, HttpServletResponse.SC_BAD_REQUEST, "참여기관 이름을 입력하세요."),
    INVALID_CBDC_TD_WALLET(400111, HttpServletResponse.SC_BAD_REQUEST, "참여기관 CBDC 당좌지갑이 존재하여야 합니다."),
    INVALID_CBDC_TE_WALLET(400112, HttpServletResponse.SC_BAD_REQUEST, "참여기관 CBDC 담보지갑이 존재하여야 합니다."),
    INVALID_CBDC_REDEMP_WALLET(400113, HttpServletResponse.SC_BAD_REQUEST, "참여기관 CBDC 환수지갑이 존재하여야 합니다."),
    INVALID_TD_CONTRACT(400114, HttpServletResponse.SC_BAD_REQUEST, "참여기관 예금 토큰이 배포되여야 합니다."),
    INVALID_TE_CONTRACT(400115, HttpServletResponse.SC_BAD_REQUEST, "참여기관 이머니토큰이 배포되여야 합니다."),
    INVALID_TD_ISSUANCE_WALLET(400116, HttpServletResponse.SC_BAD_REQUEST, "참여기관 예금 토큰 발행지갑이 존재하여야 합니다."),
    CREATE_TD_ISSUANCE_FAIL(400117, HttpServletResponse.SC_BAD_REQUEST, "블록체인을 통한 예금 토큰 생성에 실패하였습니다"),
    INVALID_TD_REDEMPTION_WALET(400118, HttpServletResponse.SC_BAD_REQUEST, "참여기관 예금 토큰 환수지갑이 존재하여야 합니다."),

    NOT_FOUND_TD_REDEMPTION_WALET(400119, HttpServletResponse.SC_BAD_REQUEST, "예금 토큰 환수지갑이 없습니다.\n환수지갑 생성부터 진행해주세요."),
    INVALID_REDEMPTION_AMOUNT(400120, HttpServletResponse.SC_BAD_REQUEST, "환수 지갑 이상의 액수를 폐기 처리 할 수 없습니다"),
    INVALID_TD_DISCARDED_WALLET(400121, HttpServletResponse.SC_BAD_REQUEST, "참여기관 예금 토큰 폐기지갑이 존재하여야 합니다."),
    INVALID_TE_ISSUANCE_WALLET(400122, HttpServletResponse.SC_BAD_REQUEST, "참여기관 이머니토큰 발행지갑이 존재하여야 합니다."),
    INVALID_TE_REDEMPTION_WALLET(400123, HttpServletResponse.SC_BAD_REQUEST, "참여기관 이머니토큰 환수지갑이 존재하여야 합니다."),
    INVALID_TE_DISCARDED_WALLET(400124, HttpServletResponse.SC_BAD_REQUEST, "참여기관 이머니토큰 폐기지갑이 존재하여야 합니다."),
    INVALID_CBDC_DSUSE_REQUIRED(400125, HttpServletResponse.SC_BAD_REQUEST, "[%s]에 해당되는 CBDC 폐기 요청을 찾을 수 없습니다."),
    INVALID_CBDC_DSUSE_APPROVAL(400126, HttpServletResponse.SC_BAD_REQUEST, "[%s]에 해당되는 CBDC 폐기 요청은 승인 받지 않았습니다."),
    INVALID_HTTP_PROTOCOL_REQUIRED(400127, HttpServletResponse.SC_BAD_REQUEST, "HTTP 프로토클임을 명시하여야 합니다."),
    INVALID_CBDC_MNFCTUR_REQUIRED(400128, HttpServletResponse.SC_BAD_REQUEST, "[%s]에 해당되는 CBDC 제조 요청을 찾을 수 없습니다."),
    INVALID_CBDC_MNFCTUR_APPROVAL(400129, HttpServletResponse.SC_BAD_REQUEST, "[%s]에 해당되는 CBDC 제조 요청은 승인 받지 않았습니다."),
    MISSING_PART_TOKEN(400130, HttpServletResponse.SC_BAD_REQUEST, "토큰을 입력하여야 합니다"),
    MISSING_AUTHOR_CODE(400131, HttpServletResponse.SC_BAD_REQUEST, "참가기관에 대한 사용권한 코드가 존재 하지 않습니다."),
    INVALID_AMOUNT(400132, HttpServletResponse.SC_BAD_REQUEST, "금액을 입력하여 주십시오"),
    INVALID_COMMAND(400133, HttpServletResponse.SC_BAD_REQUEST, "구분 값을 입력하여 주십시오"),
    INVALID_TOBANKCODE(400134, HttpServletResponse.SC_BAD_REQUEST, "수신은행 코드 값을 입력하여 주십시오"),
    INVALID_FROMBANKCODE(400135, HttpServletResponse.SC_BAD_REQUEST, "송신 은행 코드 값을 입력하여 주십시오"),
    INVALID_PERSONID(400136, HttpServletResponse.SC_BAD_REQUEST, "송신자의 고객번호를 입력하여 주십시오"),
    INVALID_ACNUTNO(400137, HttpServletResponse.SC_BAD_REQUEST, "수신자의 계좌번호를 입력하여 주십시오"),
    INVALID_WALLETDPSTR(400138, HttpServletResponse.SC_BAD_REQUEST, "송신자명을 입력하여 주십시오"),
    INVALID_FROMWALLETDPSTR(400139, HttpServletResponse.SC_BAD_REQUEST, "수신자명을 입력하여 주십시오"),
    INVALID_SCHEDULE_ID(400140, HttpServletResponse.SC_BAD_REQUEST, "대사 작업 ID를 입력하여야 합니다."),
    INVALID_SCHEDULE_TASK(400141, HttpServletResponse.SC_BAD_REQUEST, " 해당되는 작업을 찾을 수 없습니다."),
    INVALID_SCHEDULE_NM(400142, HttpServletResponse.SC_BAD_REQUEST, "JOB 그룹 이름이 존재하여야 합니다."),
    INVALID_SCHEDULE_GROUP(400143, HttpServletResponse.SC_BAD_REQUEST, "JOB 그룹이 존재하여야 합니다."),
    PART_ID_NOT_FOUND(400144, HttpServletResponse.SC_BAD_REQUEST, "참가기관의 계정을 입력하여야 합니다."),
    LOGIN_FAILED(400145, HttpServletResponse.SC_BAD_REQUEST, "로그인에 실패했습니다. "),
    INVALID_IP_ADRRESS(400146, HttpServletResponse.SC_BAD_REQUEST, "%s 유효하지 않은 IP 입니다. "),
    IDENTITY_TYPE_IS_NULL(400147, HttpServletResponse.SC_BAD_REQUEST, "신븐증인증유형을 입력하여야 합니다."),
    INVALID_VOUCH_TYCD(400148, HttpServletResponse.SC_BAD_REQUEST, "바우처 유형이 존재하지 않습니다."),
    INVALID_VOUCH_LIST(400149, HttpServletResponse.SC_BAD_REQUEST, "바우처가 존해하지 않습니다."),
    VOUCH_ID_NOT_INPUT(400150, HttpServletResponse.SC_BAD_REQUEST, "확인하실 바우처의 아이디를 넣어주십시오"),
    NAME_NOT_INPUT(400151, HttpServletResponse.SC_BAD_REQUEST, "이름을 입력하여야 합니다."),
    BIRTH_NOT_INPUT(400152, HttpServletResponse.SC_BAD_REQUEST, "생년월일 입력하여야 합니다."),
    TEL_COMPANY_NOT_INPUT(400153, HttpServletResponse.SC_BAD_REQUEST, "통신사를 입력하여야 합니다."),
    MBL_NUM_NOT_INPUT(400154, HttpServletResponse.SC_BAD_REQUEST, "휴대폰번호를 입력하여야 합니다."),
    DIVICE_NOT_INPUT(400155, HttpServletResponse.SC_BAD_REQUEST, "디바이스정보를 입력하여야 합니다."),
    AUTH_SEQ_NOT_INPUT(400156, HttpServletResponse.SC_BAD_REQUEST, "authSeq 입력하여야 합니다."),
    AUTH_NO_NOT_INPUT(400157, HttpServletResponse.SC_BAD_REQUEST, "authNo 입력하여야 합니다."),
    AUTH_SEQ_ERROR(400158, HttpServletResponse.SC_BAD_REQUEST, "authSeq 오류"),
    CI_NOT_MATCHING(400159, HttpServletResponse.SC_BAD_REQUEST, "CI가 일치 하지 않습니다. 입력 CI:"),
    TERM_APPROVAL_NOT_INPUT(400160, HttpServletResponse.SC_BAD_REQUEST, "약관동의여부를 입력하여야 합니다."),
    UNEXCEPTABLE_ERROR (400161, HttpServletResponse.SC_BAD_REQUEST, "예기치 못한 오류가 발생하였습니다."),
    PUSH_SEND_ERROR (400162, HttpServletResponse.SC_BAD_REQUEST, "푸시 메시지 전송 중 오류가 발생하였습니다."),
    DC1_SEND_ERROR (400163, HttpServletResponse.SC_BAD_REQUEST, "예금 토큰 환수지갑에서 폐기지갑으로 전송 실패했습니다."),
    MESSAGE_SEND_ERROR (400164, HttpServletResponse.SC_BAD_REQUEST, "메시지 전송 중 오류가 발생하였습니다."),
    SMART_CONTRACT_VERSION_ERROR (400165, HttpServletResponse.SC_BAD_REQUEST, "현재 등록된 버전과 같거나 낮은 버전은 등록 할 수 없습니다."),
    
    SMART_CONTRACT_UPGRADE_ERROR (400166, HttpServletResponse.SC_BAD_REQUEST, "사용중인 건만 업그레이드 가능합니다."),
    SMART_CONTRACT_CODE_ERROR (400167, HttpServletResponse.SC_BAD_REQUEST, "기존 계약 건과 코드가 일치하지 않습니다."),
    SMART_CONTRACT_DELETE_ERROR (400168, HttpServletResponse.SC_BAD_REQUEST, "신청중인 건만 삭제 가능합니다."),
    SMART_CONTRACT_STTUS_UPDATE_ERROR (400169, HttpServletResponse.SC_BAD_REQUEST, "배포 완료된 건만 상태 변경이 가능합니다."),
    SMART_CONTRACT_STTUS_REJECT_ERROR (400170, HttpServletResponse.SC_BAD_REQUEST, "신청중인 건만 반려 가능합니다."),
    SMART_CONTRACT_DEPLOY_ERROR (400171, HttpServletResponse.SC_BAD_REQUEST, "신청중인 건만 배포 가능합니다."),
    WALL_STTUS_MODIFY_ERROR(400172, HttpServletResponse.SC_BAD_REQUEST, "처리 가능한 상태가 아닙니다."),
    WALL_STTUS_CONFIRM_ERROR(400173, HttpServletResponse.SC_BAD_REQUEST, "해당 참여기관에 이미 승인 처리된 지갑이 있습니다."),
    WALL_STTUS_CREAT_ERROR(400174, HttpServletResponse.SC_BAD_REQUEST, "지갑 생성 요청에 실패하였습니다."),
    WALLET_AUTH_CREAT_ERROR(400175, HttpServletResponse.SC_BAD_REQUEST, "지갑에 [%s] 권한 설정이 실패했습니다."),
    WALL_TYPE_ERROR(400176, HttpServletResponse.SC_BAD_REQUEST, "잘못된 지갑 타입입니다."),
    WALL_STTUS_ERROR(400177, HttpServletResponse.SC_BAD_REQUEST, "지갑 상태가 올바르지 않습니다."),
    FILE_VALID_CUSTMR_ERROR(400178, HttpServletResponse.SC_BAD_REQUEST, "%d번째 row : 등록되지 않은 고객 정보입니다. 고객 아이디를 다시 확인해주세요."),
    FILE_VALID_REQUIRE_ERROR(400179, HttpServletResponse.SC_BAD_REQUEST, "%d번째 row : 필수값이 누락되었습니다. 다시 확인해주세요."),
    FILE_VALID_DATE_ERROR(400180, HttpServletResponse.SC_BAD_REQUEST, "%d번째 row : 유효하지 않은 날짜입니다. 다시 확인해주세요."),
    FILE_VALID_ALIAS_ERROR(400181, HttpServletResponse.SC_BAD_REQUEST, "%d번째 row : 등록되지 않은 간편주소 정보입니다. 은행코드와 간편주소를 다시 확인해주세요."),
    RESET_FILE_REQUEST_FAILED(400182, HttpServletResponse.SC_BAD_REQUEST, "%s : 초기화 실패했습니다."),
    RESET_FILE_NOT_FOUND(400183, HttpServletResponse.SC_BAD_REQUEST, "%s : 초기화 파일이 존재하지 않습니다."),
    BLOCK_LIST_DUPLICATE_ERROR(400184, HttpServletResponse.SC_BAD_REQUEST, "이미 적용중인 블랙리스트 내역이 존재합니다."),
    INVALID_FILENAME(400185, HttpServletResponse.SC_BAD_REQUEST, "유효하지 않은 파일명입니다."),
    CHECK_FILE_LIST(400186, HttpServletResponse.SC_BAD_REQUEST, "파일 리스트를 확인해주세요."),
    ABI_BIN_FILENAME_MISMATCH(400187, HttpServletResponse.SC_BAD_REQUEST, "abi, bin 파일명이 일치하지 않습니다."),
    TXCODE_MISMATCH(400188, HttpServletResponse.SC_BAD_REQUEST, "일치하는 txCode가 없습니다. TxCode: %s"),
    INVALID_PLACE_INFO_ERROR(400189, HttpServletResponse.SC_BAD_REQUEST, "사용처명 정보가 없습니다."),
    INVALID_WALLET_INFO_ERROR(400189, HttpServletResponse.SC_BAD_REQUEST, "결제처 정보가 올바르지 않습니다."),
    WRONG_PAYMENT_REQUIRED(400190, HttpServletResponse.SC_BAD_REQUEST, "본인에게 결제 할 수 없습니다."),
    BLOCK_LIST_ERROR(400191, HttpServletResponse.SC_BAD_REQUEST, "거래제한 적용대상 입니다."),
    INVAID_CSTMR_INFO_ERROR(400192, HttpServletResponse.SC_BAD_REQUEST, "고객 정보가 존재하지 않습니다. 회원가입 진행"),
    LIMIT_TRANSFER_AMOUNT_ERROR(400193, HttpServletResponse.SC_BAD_REQUEST, "1회 이체 한도 금액을 초과하였습니다..\n다시 확인해주세요."),
    LIMIT_AMOUNT_ERROR(400194, HttpServletResponse.SC_BAD_REQUEST, "보유 한도 금액을 초과하였습니다..\n다시 확인해주세요."),
    LIMIT_PAYMENT_AMOUNT_ERROR(400195, HttpServletResponse.SC_BAD_REQUEST, "기간 내 사용 한도 금액을 초과하였습니다..\n다시 확인해주세요."),
    WRONG_TRANSFER_REQUIRED(400196, HttpServletResponse.SC_BAD_REQUEST, "본인에게 송금 할 수 없습니다."),
    VOUCHER_PAYMENT_ROLE_SET_ERROR(400197, HttpServletResponse.SC_BAD_REQUEST, "바우처복합결제에 권한설정이 실패했습니다."),
    COIN_TYPE_ERROR(400198, HttpServletResponse.SC_BAD_REQUEST, "잘못된 코인 타입입니다."),
    LIMIT_REDEMP_BALANCE_ERROR(400199, HttpServletResponse.SC_BAD_REQUEST, "환수 금액이 당좌 잔액을 초과 합니다. 다시 확인해주세요."),
    REDEMP_BALANCE_ERROR(400200, HttpServletResponse.SC_BAD_REQUEST, "환수 금액은 0 보다 작을 수 없습니다. 다시 확인해주세요."),
    TD_PAYMENT_ROLE_SET_ERROR(400201, HttpServletResponse.SC_BAD_REQUEST, "TD에 대한 외부복합결제 설정이 실패했습니다. MSG : [%s] "),
    TD_PAYMENT_ROLE_SET_TIME_ERROR(400202, HttpServletResponse.SC_BAD_REQUEST, "TD에 대한 외부복합결제 설정이 실패했습니다."),
    TD_PAYMENT_INNER_ROLE_SET_ERROR(400203, HttpServletResponse.SC_BAD_REQUEST, "TD에 내부복합결제 설정이 실패했습니다. MSG : [%s] "),
    TD_PAYMENT_INNER_ROLE_SET_TIME_ERROR(400204, HttpServletResponse.SC_BAD_REQUEST, "TD에 내부복합결제 설정이 실패했습니다."),
    TD_VOUCHER_PAYMENT_ROLE_SET_ERROR(400205, HttpServletResponse.SC_BAD_REQUEST, "TD에 바우처복합결제 설정이 실패했습니다. MSG : [%s] "),
    TD_VOUCHER_PAYMENT_ROLE_SET_TIME_ERROR(400206, HttpServletResponse.SC_BAD_REQUEST, "TD에 바우처복합결제 설정이 실패했습니다."),
    LIMIT_DAILY_TRANSFER_ERROR(400207, HttpServletResponse.SC_BAD_REQUEST, "일일 거래 횟수를 초과했습니다."),
    INVALID_POLICY_ERROR(400208, HttpServletResponse.SC_BAD_REQUEST, "적용 중인 정책이 없습니다."),
    INVALID_POLICY_CREATE_ERROR(400209, HttpServletResponse.SC_BAD_REQUEST, "[정책 생성 실패]: %s "),
    
    CBDC_DAILY_SYNC_CONFIRM_ERROR(400210, HttpServletResponse.SC_BAD_REQUEST, "CBDC 일일대사의 확인 처리가 실패하였습니다"),    
    INVALID_PIN_MATCH(400211, HttpServletResponse.SC_BAD_REQUEST, "핀번호가 일치하지 않습니다."),
    INVALID_PASSWORD_MATCH(400212, HttpServletResponse.SC_BAD_REQUEST, "비밀번호가 일치하지 않습니다."),
    ERROR_PASSWORD_CANNOT_BE_PREVIOUS(400213, HttpServletResponse.SC_BAD_REQUEST, "이전 비밀번호로는 변경 불가합니다."),
    INVALID_TRAILER_NUMBER(400214, HttpServletResponse.SC_BAD_REQUEST, "실제 처리 숫자와 트레일러부 총 건수가 일치하지 않습니다. 총 건수: %d, 실제 처리수: %d"),
    SFTP_CONNECT_ERROR(400215, HttpServletResponse.SC_BAD_REQUEST, "sftp 서버 접속에 실패했습니다."),
    WRONG_FORMAT(400216, HttpServletResponse.SC_BAD_REQUEST, "파일 형식이 틀렸습니다."),
    NO_DATA(400217, HttpServletResponse.SC_BAD_REQUEST, "사망자/압류자 정보가 없습니다."),

    // 401 UNAUTHORIZED
    UNAUTHORIZED_ACCESS(401001, HttpServletResponse.SC_UNAUTHORIZED, "권한이 없습니다."),
    UNAUTHORIZED_TOKEN(401002, HttpServletResponse.SC_UNAUTHORIZED, "토큰이 없습니다."),
    UNAUTHORIZED_OTP_ACCESS(401003, HttpServletResponse.SC_UNAUTHORIZED, "OTP KEY를 발급받지 않았거나 OTP 인증번호가 다릅니다."),
    UNAUTHORIZED_REQUESTiD(401004, HttpServletResponse.SC_UNAUTHORIZED, "발급받지 않은 Request ID로 호출했습니다.", "다시 접속하여야 합니다."),

    // 403 FORBIDDEN
    ACCESS_DENIED(403001, HttpServletResponse.SC_FORBIDDEN, "접근이 거부되었습니다."),
    IP_INITIALIZATION_FAILED(403002, HttpServletResponse.SC_FORBIDDEN, "IP 정보가 없습니다."),
    IP_ADDRESS_UNAVAILABLE(403003, HttpServletResponse.SC_FORBIDDEN, "%s, 허용하지 않는 IP 입니다."),
    RESOURCE_ACCESS_DENIED(403004, HttpServletResponse.SC_FORBIDDEN, "리소스에 접근 권한이 없습니다."),
    EXPIRED_TOKEN_ACCESS_DENIED(403005,HttpServletResponse.SC_FORBIDDEN, "만료된 토큰입니다." ),
    RESTRICT_ACCESS_DENIED(403006, HttpServletResponse.SC_FORBIDDEN, " 제한된 참여기관입니다."),
    UNREGISTERED_ACCESS_TOKEN(403007, HttpServletResponse.SC_FORBIDDEN, "한국은행에 등록되지않는 토큰입니다."),
    REPEAT_RESTRICT_ACCESS_DENIED(403008, HttpServletResponse.SC_FORBIDDEN, "[반복] 제한된 참여기관입니다."),
    UNFORMER_QUERY(403009, HttpServletResponse.SC_FORBIDDEN, "일반적이지 않은 쿼리에 대한 실행 시도가 있습니다"),

    // 404 NOT_FOUND
    USER_ID_NOT_FOUND(404000, HttpServletResponse.SC_NOT_FOUND, "사용자 ID를 찾을 수 없습니다."),
    USER_NOT_FOUND(404001, HttpServletResponse.SC_NOT_FOUND, "사용자가 존재하지 않습니다."),
    FILE_NOT_FOUND(404002, HttpServletResponse.SC_NOT_FOUND, "파일을 찾을 수 없습니다."),
    ALIAS_NOT_FOUND(404003, HttpServletResponse.SC_NOT_FOUND, "%s 간편주소를 찾을 수 없습니다"),
    WALLET_NOT_FOUND(404004, HttpServletResponse.SC_NOT_FOUND, "%s 지갑이 존재하지 않습니다."),
    WALLET_NOT_CREATE(404005, HttpServletResponse.SC_NOT_FOUND, "%s 지갑을 생성할 수 없습니다."),
    UNREGISTERED_SIMPLE_ADDRESS(404006, HttpServletResponse.SC_NOT_FOUND, "등록되지 않은 간편주소 정보입니다. 은행코드와 간편주소를 다시 확인해주세요."),
    RESOURCE_NOT_FOUND(404007, HttpServletResponse.SC_NOT_FOUND, "리소스를 찾을 수 없습니다."),
    CUSTOMER_NOT_FOUND(404008, HttpServletResponse.SC_NOT_FOUND, "%s 고객 정보를 찾을 수 없습니다."),
    BOND_TOKEN_CONTRACT_MISSING(404009, HttpServletResponse.SC_NOT_FOUND, "채권 토큰 컨트랙트가 배포되어야 합니다."),
    CBDC_WALLET_MISSING(404010, HttpServletResponse.SC_NOT_FOUND, "CBDC 관리 지갑 존재하지 않습니다."),
    KAFKA_PRODUCE_ERROR(404011, HttpServletResponse.SC_NOT_FOUND, "블록체인(카프카) 호출에 문제가 있습니다."),
    DC2_TE_CONTRACT_MISSING(404012, HttpServletResponse.SC_NOT_FOUND, "DC2(TE) 컨트랙트가 배포되지 않았습니다."),
    CBDC_CONTRACT_MISSING(404013, HttpServletResponse.SC_NOT_FOUND, "CBDC 토큰 컨트랙트가 배포되어야 합니다."),
    CONTRACT_NOT_FOUND(404014, HttpServletResponse.SC_NOT_FOUND, "%s 컨트랙트가 배포되지 않았습니다."),
    CONTRACT_ADDRESS_NOT_FOUND(404015, HttpServletResponse.SC_NOT_FOUND, "%s 대한 컨트랙트 주소가 없습니다."),
    CONTRACT_ABI_NOT_FOUND(404016, HttpServletResponse.SC_NOT_FOUND, "%s 대한 컨트랙트 ABI가 없습니다."),
    COMMAND_NOT_FOUND(404017, HttpServletResponse.SC_NOT_FOUND, "%s 지원하는 command가 아닙니다."),
    CONTRACT_UPLOAD_FAILED(404018, HttpServletResponse.SC_NOT_FOUND, "%s 컨트랙트 등록이 실패했습니다."),
    MANAGE_ACCOUNT_UPLOAD_FAILED(404019, HttpServletResponse.SC_NOT_FOUND, "복합결제관리에 참가은행 : %s  등록실패했습니다."),
    RETRY_SCHEDULE_NOT_FOUND(404020, HttpServletResponse.SC_BAD_REQUEST, "< %s > 재시도할 JOB을 찾지 못했습니다."),
    DATA_NOT_FOUND(404021, HttpServletResponse.SC_NOT_FOUND, "%s에 해당하는 정보를 찾을 수 없습니다."),
    COMP_TRNSC(404022, HttpServletResponse.SC_NOT_FOUND, "이미 결제 처리된 거래 입니다. TxCode: %s"),
    TOKEN_PART_INFO_NOT_FOUND(404023, HttpServletResponse.SC_NOT_FOUND, "토큰[%s]에 해당하는 참여기관 정보를 찾을 수 없습니다."),
    PART_INFO_NOT_FOUND(404024, HttpServletResponse.SC_NOT_FOUND, "[%s]에 해당하는 참여기관 정보를 찾을 수 없습니다."),
    CONTRACT_INFO_NOT_FOUND(404025, HttpServletResponse.SC_NOT_FOUND, "[%s]에 해당하는 컨트랙트 정보를 찾을 수 없습니다."),
    BLACKLIST_INFO_NOT_FOUND(404026, HttpServletResponse.SC_NOT_FOUND, "[%s]에 해당하는 블랙리스트 정보를 찾을 수 없습니다."),
    BLACKLIST_NOT_FOUND(404027, HttpServletResponse.SC_NOT_FOUND, "블랙리스트 정보를 찾을 수 없습니다."),
    BLACKLIST_INIT_DATE_FOUND(404028, HttpServletResponse.SC_NOT_FOUND, "블랙리스트 적용 날짜를 찾을 수 없습니다."),
    BLACKLIST_TARGET(404029, HttpServletResponse.SC_NOT_FOUND, "블랙리스트 적용대상 입니다."),
    PART_ID_INFO_NOT_FOUND(404030, HttpServletResponse.SC_NOT_FOUND, "[%s]에 해당하는 PART_ID 정보를 찾을 수 없습니다."),
    SIGNER_INFO_NOT_FOUND(404031, HttpServletResponse.SC_NOT_FOUND, "SIGNER 정보를 찾을 수 없습니다."),
    PATH_INFO_NOT_FOUND(404032, HttpServletResponse.SC_NOT_FOUND, "PATH 정보를 찾을 수 없습니다."),
    PART_NOT_FOUND(404033, HttpServletResponse.SC_NOT_FOUND, " %s 참여기관을 못찾았습니다."),
    PART_IP_NOT_FOUND(404034, HttpServletResponse.SC_NOT_FOUND, " %s 참여기관 IP[%s]을 못찾았습니다."),
    STATISTICS_INFO_NOT_FOUND(404035, HttpServletResponse.SC_NOT_FOUND, "해당하는 통계 정보를 찾을 수 없습니다."),
    WALLET_INFO_NOT_FOUND(404036, HttpServletResponse.SC_BAD_REQUEST, "지갑 정보가 존재하지 않습니다."),
    VCPART_INFO_NOT_FOUND(404037, HttpServletResponse.SC_NOT_FOUND, "해당하는 바우처기관 정보를 찾을 수 없습니다."),
    FIND_USER_NOT_FOUND(404038, HttpServletResponse.SC_NOT_FOUND, "%s에 해당되는 사용자 ID를 찾을 수 없습니다."),
    SERVER_ID_NOT_FOUND(404039, HttpServletResponse.SC_NOT_FOUND, " 서버 ID 세팅이 안됐습니다. "),


    // 409 CONFLICT
    DUPLICATE_USER_ID(409000, HttpServletResponse.SC_CONFLICT, "중복된 아이디입니다."),
    DUPLICATE_CODE_GROUP(409001, HttpServletResponse.SC_CONFLICT, "중복된 코드 그룹입니다."),
    DUPLICATE_RECORD(409002, HttpServletResponse.SC_CONFLICT, "해당 정보로 이미 적용중인 내역이 존재합니다. 다시 확인해주세요."),
    DUPLICATE_ALIAS(409003, HttpServletResponse.SC_CONFLICT, "해당 정보로 이미 적용중인 내역이 존재합니다. 다시 확인해주세요."),
    CODE_GROUP_CREATION_NOT_AVAILABLE(409004, HttpServletResponse.SC_CONFLICT, "코드 그룹 생성이 불가능합니다."),
    CODE_GROUP_CREATION_NOT_ALLOWED(409005, HttpServletResponse.SC_CONFLICT, "코드 그룹 생성이 불가능합니다."),
    DELETE_NOT_AVAIL_IF_CHILDREN_EXISTS(409006, HttpServletResponse.SC_CONFLICT, "하위메뉴가 있는 항목은 삭제할 수 없습니다."),
    DUPLICATE_CUSTOMER_ID(409007, HttpServletResponse.SC_CONFLICT, "중복된 고객 ID입니다."),
    SMART_CONTRACT_DUPLICATE_ERROR(409008, HttpServletResponse.SC_CONFLICT, "이미 사용중인 스마트 계약건이 존재합니다."),
    WALLET_DUPLICATE_ERROR(409009, HttpServletResponse.SC_CONFLICT, "이미 사용중인 지갑이 있습니다."),
    ACCOUNT_REJOIN_DENIED(409009, HttpServletResponse.SC_CONFLICT, "서비스 기간내 재가입 불가입니다."),
    DUPLICATE_USER_ID_OR_ERROR(409010, HttpServletResponse.SC_CONFLICT, "동일 ID 중복 접근이거나 잘못된 중복요청입니다."),
    DUPLICATE_BANK_INSTT_CD(409011, HttpServletResponse.SC_CONFLICT, "이미 등록된 기관 코드입니다."),
    DUPLICATE_BANK_BANK_CD(409012, HttpServletResponse.SC_CONFLICT, "이미 등록된 은행 코드입니다."),
    DUPLICATE_BANK_INSTT_NM(409013, HttpServletResponse.SC_CONFLICT, "이미 등록된 기관명입니다."),
    // Encoding / Decoding 에러
    ENCODING_ERROR(409014, HttpServletResponse.SC_CONFLICT, "Decoding 된 데이터를 다시 Encoding 할 수 없습니다"),
    DECODING_ERROR(409015, HttpServletResponse.SC_CONFLICT, "Encoding 된 데이터를 다시 Decoding 할 수 없습니다"),


    // 500 INTERNAL_SERVER_ERROR
    INVALID_KAFKA_MESSAGE(500000, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "Kafka error : {error_message}"),
    BLOCKCHAIN_ERROR(500001, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "블록체인 호출에 문제가 생겼습니다."),
    FILE_READ_ERROR(500002, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "파일 읽기중 오류가 발생하였습니다."),
    SERVER_ERROR(500003, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "서버 오류가 발생했습니다."),
    EXTERNAL_SERVICE_ERROR(500004, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "외부 서비스 호출 오류가 발생하였습니다."),
    BLOCKCHAIN_INVOCATION_ERROR(500005, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "블록체인 호출에 문제가 생겼습니다."),
    FILE_UPLOAD_FAILED(500006, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "파일 업로드에 실패하였습니다."),
    KAFKA_ERROR(500007, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "Kafka 호출 오류가 발생했습니다."),
    FILE_UPLOAD_ERROR(500008, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "파일 업로드에 실패하였습니다."),
    FILE_DOWNLOAD_ERROR(500009, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "파일 다운로드 처리중 오류가 발생하였습니다."),
    BLOCKCHAIN_CALL_ERROR(500010, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "블록체인 호출 오류가 발생하였습니다."),
    WALLET_USABLE_ERROR(500011, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "현재 지갑을 사용할 수 없습니다. 중앙은행에 문의 부탁드립니다"),
    WALLET_CALL_ERROR(500012, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "중앙은행에서 폐기지갑 정보를 가져오지 못 했습니다. \n 중앙 은행에 문의 부탁드립니다"),
    MANU_WALLET_CALL_ERROR(500013, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "중앙은행에서 제조지갑 정보를 가져오지 못 했습니다. \n 중앙 은행에 문의 부탁드립니다"),
    REQUEST_HASH_GENERATION_ERROR(500014, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "Error generating request hash"),
    LOCK_BALANCE_ERROR(500015, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "금액 LOCK에 실패했습니다."),
    BATCH_RESOURCE_NOT_FOUND(500016, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "배치 리소스를 찾을 수 없습니다."),
    SIGN_RESOURCE_NOT_FOUND(500017, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "미서명 거래 생성이 실패됐습니다."),
    CA_RESOURCE_ERROR(500018, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "CA 지갑 설정 작업이 실패했습니다."),
    CRATE_FILEPATH_ERROR(500019, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "디렉토리 생성 중 오류가 발생했습니다."),
    SEND_AMOUNT_EMPTY(500020, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "송금 금액을 입력하여야 합니다."),
    SEND_AMOUNT_EXCEEDS_BALANCE(500021, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "송금 금액이 CBDC 당좌 지갑의 잔액보다 큽니다\n 다시 확인 해주세요"),
    WALLET_UPDATE_ERROR(500022, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "지갑 정보 수정 중 오류가 발생 하였습니다."),
    WALLET_DELETE_ERROR(500023, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "지갑 삭제 중 오류가 발생 하였습니다."),
    CSTMR_DELETE_ERROR(500024, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "고객 정보 삭제 중 오류가 발생 하였습니다."),
    BLOCKCHAIN_TRANSFER_ERROR(500025, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "(당,티헹) 예금이체 오류. 블록체인 호출에 문제가 생겼습니다."),
    DATA_ACCESS_ERROR(500026, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "요청 처리 중 데이터베이스 오류가 발생했습니다. 관리자에게 문의하세요."),
    SQL_SYNTAX_ERROR(500027, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "데이터 처리 중 문제가 발생했습니다. 관리자에게 문의하세요."),
    BOK_API_ERROR(500028, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "중앙은행 API 요청 처리 중 오류가 발생했습니다."),
    REDEMP_BALANCE_LCOK_ERROR(500029, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "당좌지갑내 환수액 Lock이 실패했습니다."),
    UPDATE_MAX_BALANCE_LCOK_ERROR(500030, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "수취 잔고 최대 보유 가능 수량 조정에 실패했습니다."),
    RESTRICT_ACCESS_SERVER_ERROR(500031, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "BLOCK STATUS 확인 중 서버 오류가 발생했습니다."),
    BOK_TOKEN_TRANSFER_ERROR(500032, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "한국은행에 참가은행 정보전달 중 오류가 발생했습니다."),
    REDEMP_REQUEST_ERROR(500033, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "중앙은행 환수 요청 오류.. 관리자에게 문의하세요."),
    DISTRIBUTED_LOCK_ERROR(500034, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, " 처리중입니다. 다시 시도하세요"),

    // 402 PAYMENT_REQUIRED
    INSUFFICIENT_BALANCE(402000, HttpServletResponse.SC_PAYMENT_REQUIRED, "잔액이 부족합니다."),
    BURN_WALLET_INSUFFICIENT_BALANCE(402001, HttpServletResponse.SC_PAYMENT_REQUIRED, "폐기지갑의 잔액이 없습니다.\n다시 확인해주세요."),
    INSUFFICIENT_ACCOUNT_BALANCE(402002, HttpServletResponse.SC_PAYMENT_REQUIRED, "전환 입금 금액이 계좌 잔액 보다 큽니다. 다시 확인해주세요."),
    TRANSFER_AMOUNT_EXCEEDS_BALANCE(402003, HttpServletResponse.SC_PAYMENT_REQUIRED, "전환 입금 금액이 계좌 잔액 보다 큽니다. 다시 확인해주세요."),
    TRANSFER_AMOUNT_EXCEEDS_TD_BALANCE(402004, HttpServletResponse.SC_PAYMENT_REQUIRED, "전환 입금 금액이 예금 토큰 발행준비 잔액 보다 큽니다. 다시 확인해주세요."),
    TRANS_AMOUNT_EXCEEDS_BALANCE(402005, HttpServletResponse.SC_PAYMENT_REQUIRED, "이체 금액이 예금 토큰 잔액 보다 큽니다. 다시 확인해주세요."),
    TRANS_ERROR(402006, HttpServletResponse.SC_PAYMENT_REQUIRED, "(당,티헹) 예금이체 오류. 블록체인 호출에 문제가 생겼습니다."),
    DUPPLICATE_ACCOUNT(402007, HttpServletResponse.SC_PAYMENT_REQUIRED, "중복된 계좌입니다. 다시 확인해주세요."),
    ACCOUNT_NOT_ZERO(402008, HttpServletResponse.SC_PAYMENT_REQUIRED, "계좌에 잔액이 남아있는 경우 삭제 할수 없습니다."),
    INVALID_BALANCE_REQUIRED(402009, HttpServletResponse.SC_PAYMENT_REQUIRED, "잔액조회를 실패했습니다."),
    PAYMENT_AMOUNT_EXCEEDS_BALANCE(402010, HttpServletResponse.SC_PAYMENT_REQUIRED, "결제 금액이 예금 토큰 잔액 보다 큽니다. 다시 확인해주세요."),
    INSUFFICIENT_ISU_ACCOUNT_BALANCE(402011, HttpServletResponse.SC_PAYMENT_REQUIRED, "전환 입금 금액이 예금 토큰 발행준비 잔액 보다 큽니다. 다시 확인해주세요."),
    RESERVE_RATIO_QUERY_FAILED(402012, HttpServletResponse.SC_PAYMENT_REQUIRED, "지급 준비율 조회를 실패했습니다."),


    // 422 UNPROCESSABLE ENTITY
    INVALID_TRANSACTION(422000, HttpServletResponse.SC_UNPROCESSABLE_CONTENT, "유효하지 않은 트랜잭션입니다."),
    INVALID_CURRENCY(422001, HttpServletResponse.SC_UNPROCESSABLE_CONTENT, "유효하지 않은 통화입니다."),
    TRANSACTION_SIGNATURE_MISSING(422002, HttpServletResponse.SC_UNPROCESSABLE_CONTENT, "트랜잭션 서명을 받지 못했습니다."),
    TRANSACTION_SIGNATURE_NOT_FOUND(422003, HttpServletResponse.SC_UNPROCESSABLE_CONTENT, "트랜잭션 서명을 받지 못했습니다."),
    SIGNATURE_VERIFICATION_FAILED(422004, HttpServletResponse.SC_UNPROCESSABLE_CONTENT, "트랜잭션 서명을 받지 못했습니다."),
    INVALID_TRANSACTION_SIGNATURE(422005, HttpServletResponse.SC_UNPROCESSABLE_CONTENT, "유효하지 않은 트랜잭션 서명입니다."),
    TRANSACTION_HASH_MISSING(422006, HttpServletResponse.SC_UNPROCESSABLE_CONTENT, "트랜잭션 HASH 값이 없습니다."),
    INVALID_CUSTOMER_STATE(422007, HttpServletResponse.SC_UNPROCESSABLE_CONTENT, "간편비밀번호 검증 실패"),
    SESSION_EXPIRED_ERROR(422008, HttpServletResponse.SC_UNPROCESSABLE_CONTENT,"접근 오류로 인해 세션이 만료되었습니다"),

    // Push Msg
    PUSH_MSG_APPROVAL_S(801000, HttpServletResponse.SC_UNPROCESSABLE_CONTENT,"%s 님 에게 %s, %s 원을 결제 했습니다"),
    PUSH_MSG_APPROVAL_F(801001, HttpServletResponse.SC_UNPROCESSABLE_CONTENT,"%s 님 에게 결제 요청한 %s, %s 원은 결제 실패하였습니다"),
    PUSH_MSG_REFUND_S(801002, HttpServletResponse.SC_UNPROCESSABLE_CONTENT,"%s 님 에게 %s, %s 원을 환불 했습니다"),
    PUSH_MSG_REFUND_F(801003, HttpServletResponse.SC_UNPROCESSABLE_CONTENT,"%s 님 에게 환불 요청한 %s, %s 원은 환불 실패하였습니다"),
    PUSH_MSG_RECEIVE_S(801004, HttpServletResponse.SC_UNPROCESSABLE_CONTENT,"%s 님 에게서 %s, %s 원을 받았습니다"),
    PUSH_MSG_SENDER_S(801005, HttpServletResponse.SC_UNPROCESSABLE_CONTENT,"%s 님 에게 %s, %s 원을 송금했습니다"),
    PUSH_MSG_SENDER_F(801006, HttpServletResponse.SC_UNPROCESSABLE_CONTENT,"%s 님 에게 송금 요청한 %s, %s 원은 송금 실패하였습니다"),
    PUSH_MSG_TRN_TOKEN_S(801007, HttpServletResponse.SC_UNPROCESSABLE_CONTENT,"예금 %s 원을 %s 으로 전환 하였습니다"),
    PUSH_MSG_TRN_TOKEN_F(801008, HttpServletResponse.SC_UNPROCESSABLE_CONTENT,"예금 %s 원의 %s 으로의 전환은 실패하였습니다"),
    PUSH_MSG_TRN_DEPOSIT_S(801009, HttpServletResponse.SC_UNPROCESSABLE_CONTENT,"예금 토큰 %s 원을 예금으로 전환 하였습니다"),
    PUSH_MSG_TRN_DEPOSIT_F(801010, HttpServletResponse.SC_UNPROCESSABLE_CONTENT,"예금 토큰 %s 원의 예금 전환은 실패 하였습니다"),

    // 503 SERVICE_UNAVAILABLE
    NETWORK_ERROR(503000, HttpServletResponse.SC_SERVICE_UNAVAILABLE, "네트워크 오류가 발생했습니다.","네트워크 오류가 발생했습니다."),
    BOK_NETWORK_ERROR(503001, HttpServletResponse.SC_SERVICE_UNAVAILABLE, "한국은행으로 데이터 전송중 오류가 발생하였습니다"),
    PARSING_ERROR(503002, HttpServletResponse.SC_SERVICE_UNAVAILABLE, "파싱오류가 발생했습니다."),
    RESTRICT_ACCESS_NETWORK_ERROR(503003, HttpServletResponse.SC_SERVICE_UNAVAILABLE, "BLOCK STATUS 확인 중 네트워크 오류가 발생했습니다."),
    RESTRICT_ACCESS_DEPLOY_ERROR(503004, HttpServletResponse.SC_SERVICE_UNAVAILABLE, "한국은행 시스템에서 배포 중 오류가 발생했습니다."),
    CORE_BANKING_CALL_ERROR(503005, HttpServletResponse.SC_SERVICE_UNAVAILABLE, "계정계 연결 중 오류가 발생했습니다."),
    BRIDGE_CALL_ERROR(503006, HttpServletResponse.SC_SERVICE_UNAVAILABLE, "브릿지 게이트웨이 연결 중 오류가 발생했습니다.");

    private final int code;
    private final int httpCode;
    private final String logMessage;
    private final String userMessage;

    ErrorCode(int code, int httpCode, String logMessage, String userMessage) {
        this.code = code;
        this.httpCode = httpCode;
        this.logMessage = logMessage;
        this.userMessage = userMessage;
    }

    ErrorCode(int code, int httpCode, String logMessage) {
        this.code = code;
        this.httpCode = httpCode;
        this.logMessage = logMessage;
        this.userMessage = logMessage;
    }

    public int getCode() {
        return code;
    }

    public int getHttpCode() {
        return httpCode;
    }

    public String getMessage() {
        return logMessage;
    }

    public String getUserMessage() {
        return userMessage;
    }

    public String getFormat(Object... args) {
        return String.format(this.logMessage, args); // 메시지 내의 포맷팅을 변경

    }

    public String getUserFormat(Object... args) {
        Object modifiedArgs[] = Arrays.stream(args).map(x-> x.equals("DC1") ? "예금 토큰" : x).toArray();
        return String.format(this.userMessage, modifiedArgs); // 메시지 내의 포맷팅을 변경

    }

    public static ErrorCode findByHttpCode(int httpCode) {
        return Arrays.stream(values())
                .filter(errorCode -> errorCode.getHttpCode() == httpCode)
                .findFirst()
                .orElse(ErrorCode.SERVER_ERROR); // 매칭되는 항목이 없으면 null 반환
    }
}

--
package kr.or.cbdc.infrastructure.util;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

import org.springframework.stereotype.Component;

import lombok.extern.slf4j.Slf4j;

@Component
@Slf4j
public class SeqNoGenerator {
    private static final String SEQ_FORMAT = "%08d";
    private String currentDate;
    private int currentSeq;

    private final Object lock = new Object();

    public String generateDateSeqNo() {
        synchronized(lock) {
            String today = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyMMdd"));
            
            if (today.equals(currentDate)) {
                currentSeq++;
            }
            else {
                currentDate = today;
                currentSeq = 1;
            }
            
            return currentDate + String.format(SEQ_FORMAT, currentSeq);
        }
    }
}

--
package kr.or.cbdc.infrastructure.util;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import jakarta.servlet.http.HttpServletRequest;
import kr.or.cbdc.application.common.user.model.LoginUser;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.BizException;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.ErrorCode;
import kr.or.cbdc.infrastructure.framework.web.context.request.RequestContextUtil;
import kr.or.cbdc.interfaces.OneTimeTokenStore;
import kr.or.cbdc.interfaces.RequestIdCache;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.ObjectUtils;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;
import javax.xml.bind.DatatypeConverter;

import java.text.SimpleDateFormat;
import java.util.*;
import java.util.stream.Collectors;

@Slf4j
@Component
public class TokenUtils {

    public static final String PERSON_ID = "person_id";
    public static final String USER_ID = "user_id";
    public static final String USER_NAME = "user_nm";
    public static final String USER_DIV = "user_div";
    public static final String ROLE_BANK = "[\"ROLE_BANK\"]";

    public static final int BANK_ROLE_ONLY = 4;
    public static final int OPT_CHECK = 3;

    private static final String OTP_KEY = "otp";
    private static final String GRANT_TYPE = "Bearer";
    private static final String EXPIRE_TIME = "expireTime";
    private static final String LOGIN_NAME = "loginNm";
    private static final String ROLE = "role";
    private static final String AUTH_HEADER = "Authorization";
    private static final String BEARER_PREFIX = "Bearer ";

    @Value("${spring.jwt.access-expired}")
    private Long accessTokenExpired;

    @Value("${spring.jwt.refresh-expired}")
    private Long refreshTokenExpired;

    @Value("${spring.jwt.one-time-expired:60}")
    private Long oneTimeTokenExpired;

    @Value(value = "${spring.jwt.prtCmpny-access-expired}")
    private Long prtCmpnyAccessTokenExpired;

    @Value(value = "${spring.profiles.active}")
    private String active;

    private static SecretKey key;
    private @Autowired ObjectMapper objectMapper;
    private @Autowired OneTimeTokenStore oneTimeTokenStore;

    public TokenUtils(@Value("${spring.jwt.key}") String secretKey) {
        key = createSigningKey(secretKey);
    }
    
    private SecretKey createSigningKey(String secretKey) {
        byte[] apiKeySecretBytes = DatatypeConverter.parseBase64Binary(secretKey);
        return new SecretKeySpec(apiKeySecretBytes, Jwts.SIG.HS256.key().build().getAlgorithm());
    }

    public TokenInfo generateToken(LoginUser user) {
        log.info("Generating access and refresh tokens");
        Date now = new Date();

        String accessToken = createToken(user, now, accessTokenExpired);
        String refreshToken = createRefreshToken(user, now, refreshTokenExpired);

        return TokenInfo.builder()
                .isFirstLogin(user.getIsFirstLogIn())
                .userName(user.getPersonNm())
                .authority(user.getAuthorities().toString())
                .grantType(GRANT_TYPE)
                .otpKey(ObjectUtils.isNotEmpty(user.getOtpKey()))
                .accessToken(accessToken)
                .refreshToken(refreshToken)
                .userId(user.getUserId())
                .build();
    }

    public String generateIFToken(String userId, String cstmrNo, String personId, String personNm) {
        log.info("generateIFToken start");

        long now = (new Date()).getTime();
        Date accessTokenExpiresIn = new Date(now + (1000 * accessTokenExpired)); // 30분
        //Date accessTokenExpiresIn = new Date(now + (1000 * 10)); // 10초
        Date refreshTokenExpiresIn = new Date(now + (1000 * refreshTokenExpired)); // 14일

        String accessToken = Jwts.builder()
                .signWith(key)
                .expiration(accessTokenExpiresIn)
                .subject(userId)
                .claims(createIFClaims(userId, personId, personNm))
                .compact();

        log.info(getClaimsFormToken(accessToken).toString());

        String refreshToken = Jwts.builder()
                .signWith(key)
                .expiration(refreshTokenExpiresIn)
                .subject(userId)
                .compact();

        log.info("accessToken: {}", accessToken);
        log.info("refreshToken: {}", refreshToken);
        return accessToken;
    }

    private Claims getClaimsFormToken(String token) {
        return Jwts.parser()
                .verifyWith(key)
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }
    
    public TokenInfo generateTokenForPrtCmpny(LoginUser user) {
        log.info("Generating token for prtCmpny");
        Date now = new Date();
        String accessToken = createToken(user, now, prtCmpnyAccessTokenExpired);

        return TokenInfo.builder()
                .isFirstLogin(user.getIsFirstLogIn())
                .userName(user.getPersonNm())
                .authority(user.getAuthorities().toString())
                .grantType(GRANT_TYPE)
                .accessToken(accessToken)
                .build();
    }

    public TokenInfo generateOneTimeToken(LoginUser user) {
        log.info("Generating one-time token");
        Date now = new Date();
        String oneTimeToken = createToken(user, now, oneTimeTokenExpired);
        String refreshToken = createRefreshToken(user, now, refreshTokenExpired);

        oneTimeTokenStore.put(oneTimeToken, true);
        return TokenInfo.builder()
                .isFirstLogin(user.getIsFirstLogIn())
                .userName(user.getPersonNm())
                .authority(user.getAuthorities().toString())
                .grantType(GRANT_TYPE)
                .otpKey(ObjectUtils.isNotEmpty(user.getOtpKey()))
                .accessToken(oneTimeToken)
                .refreshToken(refreshToken)
                .userId(user.getUserId())
                .build();
    }

    public boolean validateOneTimeToken(String token) {
        log.info("Validating one-time token");
        if ( ObjectUtils.isEmpty(oneTimeTokenStore.get(token)) || !oneTimeTokenStore.get(token)) {
            throw new BizException(ErrorCode.UNAUTHORIZED_REQUESTiD);
        }
        oneTimeTokenStore.remove(token);
        return true;
    }

    public int isValidToken(String token, String otpUrl) {
        Claims claims = parseToken(token);
        log.info("expireTime: {}, id: {}, role: {}", claims.getExpiration(), claims.get(USER_ID), claims.get(USER_DIV));

        if (StringUtils.isNotEmpty(otpUrl) && otpUrl.contains("common")) {
            return OPT_CHECK;
        }
        if (ObjectUtils.isNotEmpty(claims.get(USER_DIV)) && claims.get(USER_DIV).toString().contains(ROLE_BANK)) {
            return BANK_ROLE_ONLY;
        }
        if (active.contains("ewa")) {
            return 2;
        }
        if (ObjectUtils.isEmpty(claims.get(OTP_KEY)) || !(Boolean) claims.get(OTP_KEY)) {
            throw new BizException(ErrorCode.UNAUTHORIZED_OTP_ACCESS);
        }
        return 1;
    }

    public Date getExpiration() {
        String token = resolveToken(RequestContextUtil.getRequest());
        if (StringUtils.isEmpty(token)) {
            return null;
        }
        try {
            Claims claims = parseToken(token);
            return claims.getExpiration();
        } catch (ExpiredJwtException e) {
            log.error("Token expired", e);
            return null;
        }
    }

    private Map<String, Object> createClaims(LoginUser user) {
        Map<String, Object> claims = new HashMap<>();
        claims.put(USER_ID, user.getUserId());
        claims.put(PERSON_ID, user.getPersonId());
        claims.put(USER_NAME, user.getPersonNm());
        claims.put(OTP_KEY, OtpUtil.SUCCESS.equals(user.getOtpKeyCorrect()));

        try {
            claims.put(USER_DIV, objectMapper.writeValueAsString(user.getAuthorities().stream()
                    .map(GrantedAuthority:getAuthority)
                    .collect(Collectors.toList())));
        } catch (JsonProcessingException e) {
            log.error("Error converting authorities to JSON", e);
        }

        return claims;
    }

    private Map<String, Object> createIFClaims(String userId, String personId, String personNm) { // String id, Collection<GrantedAuthority> right)
        // 공개 클레임에 사용자의 이름과 이메일을 설정하여 정보를 조회할 수있다.
        Map<String, Object> claims = new HashMap<>();
        claims.put(TokenUtils.USER_ID, userId);
        claims.put(TokenUtils.PERSON_ID, personId);

        claims.put(TokenUtils.USER_NAME, personNm);

        claims.put("user_div", "[\"ROLE_USER\"]");

        log.debug("====> user information ==>{}", claims);
        return claims;
    }

    public String getUserIdFromToken(String token) {
        Claims claims = parseToken(token);
        return claims.get(USER_ID, String.class);
    }

    public LoginUser getLoginUserFromToken() {
        HttpServletRequest request = RequestContextUtil.getRequest();
        if (ObjectUtils.isEmpty(request)) {
            return createSystemUser();
        }
        String token = resolveToken(request);
        if (StringUtils.isEmpty(token)) {
            return null;
        }
        Claims claims = parseToken(token);
        return createLoginUserFromClaims(claims);
    }

    public Authentication getAuthentication(String token) {
        Claims claims = parseToken(token);
        return new UsernamePasswordAuthenticationToken(getUserIdFromToken(token), null, parseAuthorities(claims));
    }

    public Map<String, Object> getTokenInfo(String token) {
        try {
            return extractTokenInfo(parseToken(token));
        } catch (ExpiredJwtException e) {
            return extractTokenInfo(e.getClaims());
        }
    }

    private String createToken(LoginUser user, Date now, Long expiration) {
        Date expiryDate = new Date(now.getTime() + expiration * 1000);
        Map<String, Object> claims = createClaims(user);

        return Jwts.builder()
                .signWith(key)
                .expiration(expiryDate)
                .subject(user.getUserId())
                .claims(claims)
                .compact();
    }
    private String createRefreshToken(LoginUser user, Date now, Long expiration) {
        Date expiryDate = new Date(now.getTime() + expiration * 1000);

        return Jwts.builder()
                .signWith(key)
                .expiration(expiryDate)
                .subject(user.getUserId())
                .compact();
    }

    public static Claims parseToken(String token) {
        return Jwts.parser()
                .verifyWith(key)
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }

    public static String getCIFromToken(String userKey) {

        String token = getToken();
        if ( StringUtils.isEmpty(token)) {
            return null;
        }
        try {
            Claims claims = parseToken(getToken());
            return claims.get(userKey, String.class);
        } catch (ExpiredJwtException eJwt) {
            return eJwt.getClaims().get(userKey, String.class);
        }

    }

    private List<GrantedAuthority> parseAuthorities(Claims claims) {
        String userDivJson = claims.get(USER_DIV, String.class);
        try {
            List<String> authorities = objectMapper.readValue(userDivJson, new TypeReference<>() {
            });
            return authorities.stream().map(SimpleGrantedAuthority::new).collect(Collectors.toList());
        } catch (JsonProcessingException e) {
            log.error("Error parsing user_div JSON", e);
            return Collections.emptyList();
        }
    }

    private LoginUser createSystemUser() {
        List<GrantedAuthority> authorities = List.of(new SimpleGrantedAuthority("ROLE_ADMIN"));
        return new LoginUser("SYSTEM", "system", true, true, true, true, authorities, "SYSTEM", null, "SYSTEM", null);
    }

    private LoginUser createLoginUserFromClaims(Claims claims) {
        if (ObjectUtils.isEmpty(claims.get(USER_NAME)) || ObjectUtils.isEmpty(claims.get(PERSON_ID))) {
            return null;
        }
        return new LoginUser(
                claims.get(USER_NAME, String.class),
                "123", true, true, true, true,
                parseAuthorities(claims),
                claims.get(USER_ID, String.class),
                null, claims.get(PERSON_ID, String.class), null);
    }

    private Map<String, Object> extractTokenInfo(Claims claims) {
        Map<String, Object> map = new HashMap<>();
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        map.put(EXPIRE_TIME, sdf.format(claims.getExpiration()));
        map.put(LOGIN_NAME, claims.get(USER_NAME));
        map.put(ROLE, claims.get(USER_DIV));
        return map;
    }

    public String resolveToken(HttpServletRequest request) {
        if (ObjectUtils.isNotEmpty(request)) {
            String bearerToken = request.getHeader("Authorization");
            if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
                return bearerToken.substring(7);
            }
        }
        return null;
    }

    public static String getToken() {
        HttpServletRequest request = RequestContextUtil.getRequest();
        if (request == null) {
            return null;
        }
        String bearerToken = request.getHeader(AUTH_HEADER);
        if (bearerToken != null && bearerToken.startsWith(BEARER_PREFIX)) {
            return bearerToken.substring(BEARER_PREFIX.length());
        }
        return null;
    }

    public List<GrantedAuthority> getRoleFromToken(String token) {
        Claims claims = parseToken(token);
        return parseAuthorities(claims);

    }    
}
--
```