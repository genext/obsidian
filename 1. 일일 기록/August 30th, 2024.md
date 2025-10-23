---
title: "August 30th, 2024"
created: 2024-08-30 06:00:53
updated: 2025-01-27 08:57:55
---
  * 06:00 출근
  * 오늘 할 일
    * 업무 메일 확인
    * 바우처 배포 실행 endpoint 개발
    * 배포 실행 트랜잭션 조회가 무엇이지 파악.
  * 명경지수 -> 명징한 생각
  * 06:23 ERD 살펴보면서 업무 파악하기 시작
    * 검증 시스템은 스마트 계약 형태로 된 바우처를 검증한다는 의미가 아닌지?
      * 검증 시스템에서 말하는 스마트 계약은 바우처 뿐이 맞는지?
      * 이정주 팀장: 현재는 바우처만 하지만 한국은행이 원하는 것은 포괄적인 의미에서 스마트계약 전반 검증. 
    * 바우처 정보는 어디에? 이 시스템의 핵심 데이터는?
      * 이정주 팀장: 바우처 검증 관련된 데이터 전부, 즉 바우처 검증 의뢰 템플릿과 거기서 뻗어 나간 테이블
      * 바우처 오라클은 따로 떨어져 있는데...오라클은 특정 바우처와 연결되어야 하는 것이 아닌지?
        * 이정주 팀장: 금결원에서 관리. 사용처 정보 검증 역할
    * 바우처 검증 의뢰 템플릿이라는 것이 실제로 있는 것인지? 그냥 검증 의뢰 내역 관리 아닌지?
      * 마찬가지로 바우처 검증 템플릿이라는 것도 검증 완료된 바우처 스마트 컨트랙트를 저장하는 것이 아닌지?
    * 검증된 바우처를 배포 신청하는 것이 여러 번 있을 수 있나?
      * 이정주 팀장: 바우처 검증 의뢰가 여러 번 있을 수 있다. 최종 컨트랙트 ID는 검증 완료될 때, 프로그램에서 바우처 검증 템플릿에 저장.
        * 마찬가지로 검증된 바우처를 여러 번 신청할 수 있는데 이런 경우는 비슷한 바우처 사업이 여러 개 있을 때
    * 바우처 계약에서 계약이라는 것이 스마트 컨트랙트를 의미하는 것인지 아니면 원래 계약이 의미하는 바로서 계약인지?
      * 이정주 팀장: 바우처 배포 주소 관리하는 것. 금결원 관리사항
    * 프로그램 목록에서 바우처 승인 현황 목록과 바우처 승인 목록이 같은 얘기가 아닌지?
      * 이정주 팀장: 승인 현황은 참가기관 화면, 승인 목록은 금결원 화면
  * 09:25 callback 필요한 이유 파악
    * 블록체인 sdk의 callback은 results 배열 돌려준다.
    * countdownlatch와 KafkaMessageConsumerThread를 비교해서 concurrent 처리 방식 차이 파악
      * 원래 웹 프레임워크에서 모든 요청에 대해서 쓰레드를 새로 생성해서 처리하기 때문에 큰 차이는 없지만 countdownLatch가 병렬 수행에서 좀 더 낫기는 하다.
      * 하지만 금결원이 혼자 쓰는 시스템이고 담당자가 하나씩 보고 승인하는 업무 성격상 부하가 크지 않다.
      * 그냥 ==KafkaMessageConsumerThread== 생성해서 쓰는 걸로 한다.
  * 바우처 배포 승인 rest controller 개발 시작
  * 11:15 wallet sdk demo에서 try catch를 사용하지만 사용하지 않을 수 있는 방법 고민.
    * 이미 global exception handler가 있고 WalletSdkException 처리 방법을 이미 정의했다.
      * ErrorHandleController.java
        * ```java
package kr.or.cbdc.infrastructure.error.controller;

import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.exception.ExceptionUtils;
import org.apache.ibatis.exceptions.PersistenceException;
import org.apache.ibatis.exceptions.TooManyResultsException;
import org.mybatis.spring.MyBatisSystemException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.web.ServerProperties;
import org.springframework.boot.autoconfigure.web.servlet.error.BasicErrorController;
import org.springframework.boot.autoconfigure.web.servlet.error.ErrorViewResolver;
import org.springframework.boot.web.error.ErrorAttributeOptions;
import org.springframework.boot.web.servlet.error.ErrorAttributes;
import org.springframework.context.annotation.Bean;
import org.springframework.dao.DataAccessException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotWritableException;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.validation.BindException;
import org.springframework.validation.FieldError;
import org.springframework.validation.ObjectError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.context.request.ServletWebRequest;
import org.springframework.web.context.request.WebRequest;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;

import io.jsonwebtoken.ExpiredJwtException;
import jakarta.servlet.RequestDispatcher;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.ConstraintViolationException;
import kr.or.bok.wallet.sdk.errorhandling.WalletSdkException;
import kr.or.cbdc.infrastructure.error.model.ErrorHandleModel;
import kr.or.cbdc.infrastructure.error.model.ErrorMessage;
import kr.or.cbdc.infrastructure.error.service.ErrorHandleServiceImpl;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.BizException;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.BlockChainTxException;
import kr.or.cbdc.infrastructure.framework.core.support.context.ApplicationContextUtil;
import kr.or.cbdc.infrastructure.framework.web.context.support.MessageUtil;
import kr.or.cbdc.infrastructure.framework.web.servlet.error.ServletErrorConfig;
import kr.or.cbdc.infrastructure.framework.web.servlet.error.ServletErrorInfo;
import lombok.extern.slf4j.Slf4j;
import java.io.IOException;
import java.sql.SQLException;
import java.sql.SQLSyntaxErrorException;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.Iterator;
import java.util.List;

@Slf4j
@RestControllerAdvice
public class ErrorHandleController extends BasicErrorController {

    private final ErrorAttributes errorAttributes;
    private @Autowired ErrorHandleServiceImpl errorHandleService;

    public ErrorHandleController(ErrorAttributes errorAttributes, ServerProperties serverProperties,
            List<ErrorViewResolver> errorViewResolvers) {
        super(errorAttributes, serverProperties.getError(), errorViewResolvers);

        this.errorAttributes = errorAttributes;
    }

    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<?> handleAccessDeniedException(HttpServletRequest req, AccessDeniedException ex)
            throws IOException {
        log.error("{}",ex.getMessage(),  ex);
        String displayMessage = ex.getLocalizedMessage();
        int status = HttpStatus.NOT_ACCEPTABLE.value();
        if (req != null) {
            this.createLog(req);
        }
        return ResponseEntity.status(HttpStatus.FORBIDDEN.value()).body("test");
    }

    @ExceptionHandler(DataAccessException.class)
    public ResponseEntity<?> handleDataAccessException(HttpServletRequest req, DataAccessException ex)
            throws IOException {
        log.error("{}",ex.getMessage(),  ex);
        String displayMessage = ex.getLocalizedMessage();
        int status = HttpStatus.BAD_REQUEST.value();
        if (req != null) {
            displayMessage = this.createLog(req);
        }

        return ResponseEntity.status(status)
                .body(ErrorMessage.builder().status(String.valueOf(status)).message(displayMessage).build());
    }

    @ExceptionHandler(SQLSyntaxErrorException.class)
    public ResponseEntity<?> handleSQLSyntaxErrorException(HttpServletRequest req, SQLSyntaxErrorException ex)
            throws IOException {
        log.error("{}",ex.getMessage(),  ex);
        String displayMessage = ex.getLocalizedMessage();
        int status = HttpStatus.INTERNAL_SERVER_ERROR.value();
        if (req != null) {
            displayMessage = this.createLog(req);
        }
        return ResponseEntity.status(status)
                .body(ErrorMessage.builder().status(String.valueOf(status)).message(displayMessage).build());

    }

    @ExceptionHandler(SQLException.class)
    public ResponseEntity<?> handleSQLException(HttpServletRequest req, SQLException ex) throws IOException {
        log.error("{}",ex.getMessage(),  ex);
        String displayMessage = ex.getLocalizedMessage();
        int status = HttpStatus.INTERNAL_SERVER_ERROR.value();
        if (req != null) {
            displayMessage = this.createLog(req);
        }
        return ResponseEntity.status(status)
                .body(ErrorMessage.builder().status(String.valueOf(status)).message(displayMessage).build());

    }

    @ExceptionHandler(PersistenceException.class)
    public ResponseEntity<?> handlePersistenceException(HttpServletRequest req, PersistenceException ex)
            throws IOException {
        log.error("{}",ex.getMessage(),  ex);
        String displayMessage = ex.getLocalizedMessage();
        int status = HttpStatus.BAD_REQUEST.value();
        if (req != null) {
            displayMessage = this.createLog(req);
        }

        return ResponseEntity.status(status)
                .body(ErrorMessage.builder().status(String.valueOf(status)).message(displayMessage).build());
    }

    @ExceptionHandler(BizException.class)
    public ResponseEntity<?> handleBizException(HttpServletRequest req, BizException ex) throws IOException {
        log.error("{}",ex.getMessage(),  ex);
        String displayMessage = ex.getLocalizedMessage();
        int status = HttpStatus.INTERNAL_SERVER_ERROR.value();
        if (req != null) {
            String message = this.createLog(req);
            if (StringUtils.isNotEmpty(message)) {
                displayMessage = message;
            }
        }
        return ResponseEntity.status(status)
                .body(ErrorMessage.builder().status(String.valueOf(status)).message(displayMessage).build());
    }

    @ExceptionHandler(ExpiredJwtException.class)
    public ResponseEntity<?> handleExpiredJwtException(HttpServletRequest req, ExpiredJwtException ex)
            throws IOException {
        log.error("{}",ex.getMessage(),  ex);
        String displayMessage = "access token expired";
        int status = HttpStatus.UNAUTHORIZED.value();
        if (req != null) {
            this.createLog(req);
        }
        return ResponseEntity.status(status)
                .body(ErrorMessage.builder().status(String.valueOf(status)).message(displayMessage).build());
    }

    @ExceptionHandler(MyBatisSystemException.class)
    public ResponseEntity<?> handleMyBatisSystemException(HttpServletRequest req, MyBatisSystemException ex)
            throws IOException {
        String displayMessage = "데이터베이스 처리가 실패했습니다.";
        Throwable cause = ex.getCause();

        if (cause != null) {
            String message = cause.getMessage();

            // 중요한 정보를 추출하기 위한 패턴 정의 (예: SQL 쿼리)
            String pattern = "Cause: (\\d+)";
            Pattern r = Pattern.compile(pattern);

            // 정규 표현식을 사용하여 메시지에서 정보 추출
            Matcher m = r.matcher(message);
            if (m.find()) {
                message = m.group(1);
            } else {
                message = ex.getLocalizedMessage();
            }
            if (!StringUtils.isEmpty(message)) {
                displayMessage = message;
            }
        }
        log.error("{}",ex.getMessage(),  ex);
        int status = HttpStatus.INTERNAL_SERVER_ERROR.value();
        if (req != null) {
            this.createLog(req);
        }
        return ResponseEntity.status(status)
                .body(ErrorMessage.builder().status(String.valueOf(status)).message(displayMessage).build());
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<?> handleIllegalArgumentException(HttpServletRequest req, IllegalArgumentException ex)
            throws IOException {
        log.error("{}",ex.getMessage(),  ex);
        String displayMessage = ex.getLocalizedMessage();
        int status = HttpStatus.BAD_REQUEST.value();
        if (req != null) {
            this.createLog(req);
        }
        return ResponseEntity.status(status)
                .body(ErrorMessage.builder().status(String.valueOf(status)).message(displayMessage).build());

    }

    @ExceptionHandler(TooManyResultsException.class)
    public ResponseEntity<?> handleTooManyResultsException(HttpServletRequest req, TooManyResultsException ex)
            throws IOException {
        log.error("{}",ex.getMessage(),  ex);
        String displayMessage = ex.getLocalizedMessage();
        int status = HttpStatus.BAD_REQUEST.value();
        if (req != null) {
            this.createLog(req);
        }
        return ResponseEntity.status(status)
                .body(ErrorMessage.builder().status(String.valueOf(status)).message(displayMessage).build());

    }

    @ExceptionHandler(MethodArgumentNotValidException.class) // 유효성 검사 실패 시 발생하는 예외를 처리
    protected ResponseEntity<ErrorMessage> handleMethodArgumentException(HttpServletRequest req,
            MethodArgumentNotValidException e) {
        List<ObjectError> allErrors = e.getBindingResult().getAllErrors();
        String displayMessage = getMessage(allErrors.iterator());
        int status = HttpStatus.BAD_REQUEST.value();
        if (req != null) {
            this.createLog(req);
        }

        return ResponseEntity.status(status)
                .body(ErrorMessage.builder().status(String.valueOf(status)).message(displayMessage).build());
    }

    @ExceptionHandler(BindException.class) // 유효성 검사 실패 시 발생하는 예외를 처리
    protected ResponseEntity<ErrorMessage> handleBindException(HttpServletRequest req, BindException e) {
        List<ObjectError> allErrors = e.getBindingResult().getAllErrors();
        String displayMessage = getMessage(allErrors.iterator());
        int status = HttpStatus.BAD_REQUEST.value();
        if (req != null) {
            this.createLog(req);
        }

        return ResponseEntity.status(status)
                .body(ErrorMessage.builder().status(String.valueOf(status)).message(displayMessage).build());
    }

    @ExceptionHandler(WalletSdkException.class) // 블록체인 접속시 에러
    protected ResponseEntity<ErrorMessage> handleWalletSdkException(HttpServletRequest req, WalletSdkException e) {

        String displayMessage = e.getDetail().getErrorMessage();

        // log.error(" WalletSdkException : reqId[{}], message[{}], returnCode[{}]",
        // e.getDetail().getRequestId(), e.getDetail().getErrorMessage(),
        // e.getDetail().getReturnCode());
        log.error(e.getDetail().getErrorMessage());
        if (e.getDetail().getDecodedErrorMessage() != null) {
            try {
                ObjectMapper objectMapper = new ObjectMapper();
                ObjectWriter objectWriter = objectMapper.writerWithDefaultPrettyPrinter();
                String jsonString = objectWriter.writeValueAsString(e.getDetail().getDecodedErrorMessage());
                log.error(jsonString);
            } catch (JsonProcessingException var3) {
                log.error(var3.getMessage());
            }
        }
        int status = HttpStatus.BAD_REQUEST.value();
        if (req != null) {
            this.createLog(req);
        }

        return ResponseEntity.status(status)
                .body(ErrorMessage.builder().status(String.valueOf(status)).message(displayMessage).build());
    }


    @ExceptionHandler(BlockChainTxException.class) // 블록체인 접속시 에러
    protected ResponseEntity<ErrorMessage> handleBlockChainTxException(HttpServletRequest req, BlockChainTxException e) {

        String displayMessage = e.getMessage();

        // log.error(" WalletSdkException : reqId[{}], message[{}], returnCode[{}]",
        // e.getDetail().getRequestId(), e.getDetail().getErrorMessage(),
        // e.getDetail().getReturnCode());
        int status = HttpStatus.BAD_REQUEST.value();
        if (req != null) {
            this.createLog(req);
        }
        return ResponseEntity.status(status)
                .body(ErrorMessage.builder().status(String.valueOf(status)).message(displayMessage).build());
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorMessage> handleException(HttpServletRequest req, Exception ex) throws IOException {
        log.error("{}",ex.getMessage(),  ex);
        String displayMessage = ex.getLocalizedMessage();
        int status = HttpStatus.INTERNAL_SERVER_ERROR.value();
        if (req != null) {
            this.createLog(req);
        }
        return ResponseEntity.status(status)
                .body(ErrorMessage.builder().status(String.valueOf(status)).message(displayMessage).build());

    }

    @ExceptionHandler(ConstraintViolationException.class) // 유효성 검사 실패 시 발생하는 예외를 처리
    protected ResponseEntity<ErrorMessage> handleException(HttpServletRequest req, ConstraintViolationException ex) {
        Iterator<ConstraintViolation<?>> allErrors = ex.getConstraintViolations().iterator();
        String displayMessage = getResultMessage(allErrors);
        int status = HttpStatus.BAD_REQUEST.value();
        if (req != null) {
            this.createLog(req);
        }

        return ResponseEntity.status(status)
                .body(ErrorMessage.builder().status(String.valueOf(status)).message(displayMessage).build());
    }

    private String getMessage(Iterator<ObjectError> errorIterator) {
        final StringBuilder resultMessageBuilder = new StringBuilder();
        while (errorIterator.hasNext()) {
            ObjectError error = errorIterator.next();
            resultMessageBuilder
                    .append("['")
                    .append(((FieldError) error).getField()) // 유효성 검사가 실패한 속성
                    .append("' is '")
                    .append(((FieldError) error).getRejectedValue()) // 유효하지 않은 값
                    .append("' : ")
                    .append(error.getDefaultMessage()) // 유효성 검사 실패 시 메시지
                    .append("]");

            if (errorIterator.hasNext()) {
                resultMessageBuilder.append(", ");
            }
        }

        return resultMessageBuilder.toString();
    }

    private String getResultMessage(final Iterator<ConstraintViolation<?>> violationIterator) {
        final StringBuilder resultMessageBuilder = new StringBuilder();
        while (violationIterator.hasNext()) {
            final ConstraintViolation<?> constraintViolation = violationIterator.next();
            resultMessageBuilder
                    .append("['")
                    .append(getPropertyName(constraintViolation.getPropertyPath().toString())) // 유효성 검사가 실패한 속성
                    .append("' is '")
                    .append(constraintViolation.getInvalidValue()) // 유효하지 않은 값
                    .append("' :: ")
                    .append(constraintViolation.getMessage()) // 유효성 검사 실패 시 메시지
                    .append("]");

            if (violationIterator.hasNext()) {
                resultMessageBuilder.append(", ");
            }
        }

        return resultMessageBuilder.toString();
    }

    private String getPropertyName(String propertyPath) {
        return propertyPath.substring(propertyPath.lastIndexOf('.') + 1); // 전체 속성 경로에서 속성 이름만 가져온다.
    }

    private String createLog(HttpServletRequest request) {
        Object status = request.getAttribute(RequestDispatcher.ERROR_STATUS_CODE);
        ServletErrorConfig servletErrorConfig = ApplicationContextUtil.getConfigBean(ServletErrorConfig.class);
        WebRequest webRequest = new ServletWebRequest(request);
        Throwable throwable = this.errorAttributes.getError(webRequest);
        ServletErrorInfo servletErrorInfo = null;
        String displayMessage = null;

        if (throwable != null) {
            servletErrorInfo = servletErrorConfig.getServletErrorInfo(throwable.getClass());
        }

        if (servletErrorInfo == null || !servletErrorInfo.isVisible()) {
            String systemErrorMessage = MessageUtil.getMessage("common.message.systemError", "시스템 에러가 발생했습니다.");

            displayMessage = MessageUtil.getMessage("common.message.errorStatusCode." + status,
                    StringUtils.defaultIfEmpty(systemErrorMessage, "System Error."));
        }

        try {
            this.createLog(request, throwable);
        } catch (RuntimeException e) {
            log.error(e.getMessage(), e);
        }

        return displayMessage;
    }

    private void createLog(HttpServletRequest request, Throwable throwable) {
        Map<String, Object> errorAttributes2 = super.getErrorAttributes(request, ErrorAttributeOptions.defaults());

        if (throwable != null && this.isLogWriteThrowable(throwable)) {
            log.error(throwable.getMessage(), throwable);
        }

        ErrorHandleModel errorHandleModel = new ErrorHandleModel(errorAttributes2, throwable);

        if (!StringUtils.endsWith(errorHandleModel.getPath(), ".map")) {
            this.errorHandleService.createLog(errorHandleModel);
        }
    }

    private boolean isLogWriteThrowable(Throwable throwable) {
        if (throwable instanceof MissingServletRequestParameterException) {
            return true;
        }

        if (throwable instanceof HttpMessageNotWritableException) {
            return true;
        }

        return false;
    }

}
```
      * @RestControllerAdvice and [[Roam/genext-2025-10-05-02-18-30/java#^B8_I075qT|AOP ^B8_I075qT]]
        * **Advice:** In AOP terminology, "advice" refers to the action taken by an aspect at a particular join point. @RestControllerAdvice can be considered a form of advice that gets applied across multiple controllers, especially in handling exceptions and modifying the response bodies.
    * 그런데 수호쪽은 rest controller return type으로 ApiResponse를 사용한다.
      * ApiResponse
      * ```java
package kr.or.cbdc.config.messages;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@Schema(description = "공통 API 응답 객체")
public class ApiResponse<T> {

	@Schema(description = "http status 코드", example = "200")
	private int statusCode;

	@Schema(description = "응답 성공 여부", example = "true")
	private boolean success;

	@Schema(description = "응답 메시지", example = "처리가 성공적으로 완료되었습니다.")
	private String message;

	@Schema(description = "응답 데이터")
	private T data;

	public ApiResponse(int statusCode, boolean success, String message, T data) {
		this.statusCode = statusCode;
		this.success = success;
		this.message = message;
		this.data = data;
	}

}
```
    * 그 둘을 공존시킬 방법을 찾아 보니 ErrorMessage와 ApiResponse가 공통점이 있다.
      * ErrorMessage.java
      * ```java
package kr.or.cbdc.infrastructure.error.model;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class ErrorMessage {
    private String status;
    private String message;

    public String toJson() throws JsonProcessingException {
        ObjectMapper mapper = new ObjectMapper();
        String jsonString = mapper.writeValueAsString(this);
        return jsonString;

    }

}
```
    * ApiResponse가 ErrorMessage를 상속하면 된다.
      * 다만 상속에서 한 가지 고려해야 할 점은 부모 클래스 속성도 초기화하는 것을 빠뜨리지 말아야 한다는 것.
      * 변경한 ApiResponse.java
        * factory method가 추가됨.
          * ApiResponse를 만들 때 new를 쓰지 않고도 간단하게 만들 수 있게 함.
          * 비교
            * ```java
// factory method가 있을 때
ApiResponse<String> response = ApiResponse.success(200, "Operation successful", "Data");

// factory method가 없을 때
ApiResponse<String> response = new ApiResponse<>(200, true, "Operation successful", "Data");```
          * [ ] Factory desing pattern
            * sample - Logger
              * ```java
// The Product interface
public interface Logger {
    void log(String message);
}

// Concrete Product 1
public class FileLogger implements Logger {
    @Override
    public void log(String message) {
        System.out.println("Logging to a file: " + message);
        // Implement file logging logic here
    }
}

// Concrete Product 2
public class ConsoleLogger implements Logger {
    @Override
    public void log(String message) {
        System.out.println("Logging to console: " + message);
        // Implement console logging logic here
    }
}

// The Creator class with the Factory Method
public abstract class LoggerFactory {
    public abstract Logger createLogger();

    public void logMessage(String message) {
        Logger logger = createLogger();
        logger.log(message);
    }
}

// Concrete Creator 1
public class FileLoggerFactory extends LoggerFactory {
    @Override
    public Logger createLogger() {
        return new FileLogger(); // Create and return a FileLogger
    }
}

// Concrete Creator 2
public class ConsoleLoggerFactory extends LoggerFactory {
    @Override
    public Logger createLogger() {
        return new ConsoleLogger(); // Create and return a ConsoleLogger
    }
}

// Client code
public class Client {
    public static void main(String[] args) {
        LoggerFactory loggerFactory;

        // Decide which logger to create based on some runtime condition
        if (args.length > 0 && args[0].equals("file")) {
            loggerFactory = new FileLoggerFactory();
        } else {
            loggerFactory = new ConsoleLoggerFactory();
        }

        loggerFactory.logMessage("Hello, Factory Method Pattern!");
    }
}
```
        * ApiResponse.java
          * ```java
package kr.or.cbdc.config.messages;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import lombok.EqualsAndHashCode;
import kr.or.cbdc.infrastructure.error.model.ErrorMessage;

@Data
@EqualsAndHashCode(callSuper = true)
@Schema(description = "공통 API 응답 객체")
public class ApiResponse<T> extends ErrorMessage {

    @Schema(description = "응답 성공 여부", example = "true")
    private boolean success;

    @Schema(description = "응답 데이터")
    private T data;

    public ApiResponse(String status, boolean success, String message, T data) {
        super(status, message);
        this.success = success;
        this.data = data;
    }

    // Factory method for success responses
    public static <T> ApiResponse<T> success(String status, String message, T data) {
        return new ApiResponse<>(status, true, message, data);
    }

    // Factory method for error responses
    public static <T> ApiResponse<T> error(String status, String message) {
        return new ApiResponse<>(status, false, message, null);
    }
}```
      * @EqualsAndHashCode(callSuper = true)
        * Lombok generate equals() and hashCode() methods with @Data
        * ApiResponse extends ErrorMessage, Lombok should consider superclass's properties.
      * 하지만 ApiResponse의 super(status, message)에서 문제
        * intelliJ complaints at the line "super(String.valueOf(status), message); " saying ErrorMessage is not public, can't be accessed from other packages.
          * cause: There is no public constructor of ErrorMessage
          * solution: 생성자 추가
            * ```java
public ErrorMessage(String status, String message) {
        this.status = status;
        this.message = message;
    }```
        * 위 문제를 해결하니 @Data에서 다른 에러 메시지가 뜸.
          * "Lombok needs basic class to have default constructor".
          * 위에서 내가 직접 생성자를 만들었기 때문에 Lombok이 자동으로 default 생성자(no-argument)를 만들지 못했다. 일부 프레임워크는 default constructor가 필요하다. 
          * @NoArgsConstructor를 ErrorMessage에 추가
      * ErrorMessage 최종본
        * ```java
package kr.or.cbdc.infrastructure.error.model;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
public class ErrorMessage {
    private String status;
    private String message;

    public ErrorMessage(String status, String message) {
        this.status = status;
        this.message = message;
    }

    public String toJson() throws JsonProcessingException {
        ObjectMapper mapper = new ObjectMapper();
        String jsonString = mapper.writeValueAsString(this);
        return jsonString;

    }

}
```
    * http status가 int인데 ErrorMessage의 속성인 status를 굳이 String으로 한 이유.
      * ### 1. **Consistency in Data Types**:
        * In [[json]] APIs, it's common practice to represent most data as strings, especially when the data might be displayed in a user interface, logged, or used in various contexts. By keeping the status as a String, you ensure that all data within the ErrorMessage class is treated uniformly as text, which can simplify processing and display.
      * ### 2. **Ease of Use**:
        * When dealing with error handling, converting the status code to a string can make it easier to concatenate or format it with other strings without needing to cast or convert it elsewhere in the codebase. For instance, in some cases, you might want to append text or log the status along with other string messages.
      * ### 3. **Potential for Custom Status Codes**:
        * By using a String for the status, you allow for more flexibility. For example, you might want to represent custom or non-standard status codes that include alphabetic characters, such as "ERR001" or "CUSTOM_STATUS". Using a String allows the system to easily accommodate these kinds of codes.
      * ### 4. **[[json]] Serialization**:
        * When the ErrorMessage object is serialized to JSON (as shown in the toJson method), keeping status as a String ensures that it's serialized exactly as expected without any need for further conversion. JSON keys and values are typically represented as strings, so this avoids any type inconsistency issues.
      * ### 5. **Avoiding Unintended Conversions**:
        * By explicitly using a String, you avoid the potential pitfalls of Java's type system when dealing with different representations. For instance, handling numeric types could lead to unintended precision loss or require additional parsing logic if the type were an int.
      * ### 6. **Alignment with Common Practices**:
        * Many web APIs, frameworks, and libraries expect status codes as strings when they are part of a response message, particularly when generating human-readable error messages or logs. Converting it to a string aligns with these common practices.
        * In summary, while HttpStatus.BAD_REQUEST.value() returns an int, converting it to a String in the ErrorMessage class provides greater flexibility, consistency, and ease of use across different contexts in the application.
  * 12:34 ApiResponse를 적용하고 컴파일 시도
    * 에러
      * CodeRestController.java에 ApiResponse<String> response = new ApiResponse<>(HttpStatus.OK.value(), true, msg, msg);에서 에러
      * String.valueOf() 사용
  * 14:12 ApiResponse가 ErrorMessage 상속하게 만들면서 안 새로운 지식 정리 시작
  * 16:21 wallet Initializer 작업을 다른 개발자가 했는데 그 이후로 에러가 나면서 백엔드가 안 뜬다.
    * InParam is null --> main이 뜨면서 환경 파일을 읽어야 하는데 환경 파일이 없었다는 뜻.
    * 이건 wallet.sdk.properties 파일이 없어서 생긴 에러.
  * 16:36 일단 화면에 필요한 데이터를 조회하는 sql부터 짜야 한다.
  * 17:22 의문점
    * [x] 배포 승인 요청할 때는 바우처 계약 관리 정보에 있는 바우처 관리주소를 얻을 수가 없다.