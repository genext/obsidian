---
title: "Spring boot"
created: 2024-10-22 08:57:11
updated: 2025-10-02 11:00:03
---
# 필수지식
### 1. **Core Spring Framework Concepts**
* **Inversion of Control (IoC) and Dependency Injection (DI)**:
* Understand how Spring Boot uses IoC to manage dependencies and how DI works through constructor, setter, or field injection.
* Familiarity with @Component, @Service, @Repository, and @Autowired annotations.
* **Bean Lifecycle**:
	* Learn about the bean lifecycle (instantiation, initialization, destruction) and how to customize it using @PostConstruct, @PreDestroy, or implementing InitializingBean/DisposableBean.
	* **Spring Boot Auto-Configuration**:
		* Understand how Spring Boot auto-configures components (e.g., DataSource, Security, etc.) based on the classpath and properties.
		* Know how to disable or customize auto-configuration using @SpringBootApplication and @EnableAutoConfiguration.
        * @Bean
          * method level annotation
          * used to manually declare Spring-managed bean inside java configuration class that is annotated with @Configuration
 ### 2. **Spring Boot Basics**
      * **Starter Dependencies**:
        * Understand how Spring Boot “starters” simplify adding dependencies and configurations for specific use cases like web development (spring-boot-starter-web), data access (spring-boot-starter-data-jpa), security (spring-boot-starter-security), etc.
      * **Spring Boot Configuration**:
        * Learn how to configure applications using application.properties or application.yml.
        * Master the use of @ConfigurationProperties and externalized configuration (e.g., environment variables, profiles).
      * **Profiles and Environments**:
        * Understand how to manage multiple environments (e.g., dev, prod) using Spring Profiles (@Profile, spring.profiles.active).
      * **Customizing the Application Context**:
        * Know how to modify the application context using ApplicationContextInitializer, ApplicationRunner, and CommandLineRunner.
    * ### 3. **Spring Boot MVC and REST**
      * **Spring MVC (Model-View-Controller)**:
        * Learn how Spring Boot simplifies REST API development through annotations like @RestController, @RequestMapping, @GetMapping, @PostMapping, etc.
        * Handle input/output data with @RequestBody, @ResponseBody, and content negotiation (application/json, application/xml, etc.).
      * **Exception Handling**:
        * Master exception handling at both the controller level (@ExceptionHandler) and globally (@RestControllerAdvice).
      * **Validation**:
        * Use @Valid or @Validated to validate request bodies and query parameters, along with handling validation errors.
    * ### 4. **Data Access with Spring Data**
      * **Spring Data JPA / JDBC**:
        * Learn to use @Repository, JpaRepository, and CrudRepository for interacting with relational databases.
        * Master JPA and Hibernate concepts like entities, relationships, lazy loading, and fetch strategies.
        * Understand JPQL, native queries, and Criteria API.
      * **Transaction Management**:
        * Use @Transactional for managing transactions at the service level, understand isolation levels, propagation, and rollbacks.
      * **Database Migrations**:
        * Use tools like Flyway or Liquibase for database versioning and schema management.
    * ### 5. **Security**
      * **Spring Security**:
        * Understand authentication and authorization with Spring Security, including the configuration of custom authentication mechanisms, user details, and security context.
        * Learn how to secure endpoints using annotations like @Secured, @PreAuthorize, and @RolesAllowed.
        * Understand how to handle stateless security with JWT (JSON Web Tokens) and OAuth2/OpenID Connect.
      * **Filter Chain**:
        * Know how to customize the Spring Security filter chain with filters like OncePerRequestFilter or by adding custom filters.
        * Understand AuthenticationManager and how to use custom authentication providers.
      * security 관리 두 가지 방법
        * [x] Spring Security의 FilterSecurityInterceptor(filter chain)를 활용
          * Steps to Set Up FilterSecurityInterceptor:
            * **Create a Configuration Class**
            * **Implement Security Metadata Source**
This provides information about the security constraints on your resources (such as URLs and methods). You need to configure the security metadata source, which tells FilterSecurityInterceptor which permissions are required for accessing different resources.
            * **Configure Access Decision Manager**
The AccessDecisionManager works with security voters (e.g., RoleHierarchyVoter, custom voters) to decide whether the current user can access a resource.
            * **Add FilterSecurityInterceptor to the Filter Chain**
You need to add the FilterSecurityInterceptor to the Spring Security filter chain. This is typically done in your HttpSecurity configuration.
          * 기본 예
            * custom metadata example
```java
import org.springframework.security.web.access.intercept.FilterInvocationSecurityMetadataSource;
import org.springframework.stereotype.Component;
import java.util.LinkedHashMap;
import java.util.List;

@Component
public class ReloadableFilterInvocationSecurityMetadataSource implements FilterInvocationSecurityMetadataSource {

    private LinkedHashMap<String, List<String>> resourceMap = new LinkedHashMap<>();

    // Initialize with your resource patterns and required roles
    public ReloadableFilterInvocationSecurityMetadataSource() {
        resourceMap.put("/admin/**", List.of("ROLE_ADMIN"));
        resourceMap.put("/user/**", List.of("ROLE_USER"));
    }

    @Override
    public Collection<ConfigAttribute> getAttributes(Object object) throws IllegalArgumentException {
        // Logic to retrieve security metadata for a specific resource
        String requestUrl = ((FilterInvocation) object).getRequestUrl();
        List<String> roles = resourceMap.get(requestUrl);
        return roles.stream().map(SecurityConfig:new).collect(Collectors.toList());
    }

    // Other required method implementations...
}
```
            * SecurityConfig with FilterSecurityInterceptor:
```javascript
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.access.AccessDecisionManager;
import org.springframework.security.access.AccessDecisionVoter;
import org.springframework.security.access.vote.AffirmativeBased;
import org.springframework.security.access.vote.RoleHierarchyVoter;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.access.intercept.FilterSecurityInterceptor;

import java.util.ArrayList;
import java.util.List;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Autowired
    private ReloadableFilterInvocationSecurityMetadataSource securityMetadataSource;

    @Autowired
    private RoleHierarchyVoter roleHierarchyVoter;

    @Autowired
    private JwtTokenFilter jwtTokenFilter;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(authorizeRequests -> authorizeRequests
                .requestMatchers("/v1/public/**", "/actuator/health", "/actuator/info").permitAll()
                .anyRequest().authenticated())
            .formLogin(formLogin -> formLogin
                .loginProcessingUrl("/users/login")
                .defaultSuccessUrl("/home", true)
                .permitAll())
            .exceptionHandling(exceptionHandling -> exceptionHandling
                .accessDeniedPage("/access-denied"));

        configureCustomFilters(http);

        return http.build();
    }

    private void configureCustomFilters(HttpSecurity http) throws Exception {
        // Access Decision Manager Setup
        List<AccessDecisionVoter<? extends Object>> voters = new ArrayList<>();
        voters.add(roleHierarchyVoter); // Voter based on role hierarchy
        AffirmativeBased accessDecisionManager = new AffirmativeBased(voters);

        // FilterSecurityInterceptor Setup
        FilterSecurityInterceptor filterSecurityInterceptor = new FilterSecurityInterceptor();
        filterSecurityInterceptor.setSecurityMetadataSource(securityMetadataSource);
        filterSecurityInterceptor.setAccessDecisionManager(accessDecisionManager);
        filterSecurityInterceptor.setAuthenticationManager(http.getSharedObject(AuthenticationManager.class));

        // Add the custom FilterSecurityInterceptor to the filter chain
        http.addFilterAt(filterSecurityInterceptor, FilterSecurityInterceptor.class);

        // Optionally, add a JWT token filter before authentication
        http.addFilterBefore(jwtTokenFilter, FilterSecurityInterceptor.class);
    }

    @Bean
    public RoleHierarchyVoter roleHierarchyVoter() {
        // Configuring role hierarchy voter
        return new RoleHierarchyVoter(roleHierarchy());
    }

    @Bean
    public RoleHierarchyImpl roleHierarchy() {
        // Role hierarchy definition, e.g., ROLE_ADMIN > ROLE_USER
        RoleHierarchyImpl roleHierarchy = new RoleHierarchyImpl();
        roleHierarchy.setHierarchy("ROLE_ADMIN > ROLE_USER");
        return roleHierarchy;
    }
}
```
          * 디지털 바우처 시스템 실제 사용 예: with custom filter.
            * custom filter
```java
package kr.or.cbdc.application.common.user.filter;

import java.io.IOException;
import java.util.List;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import kr.or.cbdc.infrastructure.error.model.ErrorMessage;
import kr.or.cbdc.infrastructure.framework.core.support.security.JwtUtil;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Component
public class JwtTokenFilter extends OncePerRequestFilter {

    @Autowired
    private JwtUtil jwtUtil;

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        String token = resolveToken(request);
        log.info("Attempting to filter request. Resolved token: {}", token);

        try {
            if (token != null && isTokenValid(token)) {
                // 토큰에서 userId를 가져와서 인증 객체를 생성하여 SecurityContext에 설정
                String userId = Jwts.parser().verifyWith(jwtUtil.getKey()).build().parseSignedClaims(token).getPayload()
                        .getSubject();

                log.info("Token valid. Retrieved userId: {}", userId);

                Authentication auth = createAuthentication(userId);
                SecurityContextHolder.getContext().setAuthentication(auth);
                log.info("Authentication set for userId: {}", userId);
            } else {
                log.warn("Token is either null or invalid.");
            }
            filterChain.doFilter(request, response);
        } catch (ExpiredJwtException e) {
            log.error("Expired JWT token: {}", e.getMessage(), e);
            sendErrorResponse(response, HttpServletResponse.SC_UNAUTHORIZED, "Expired JWT token.");
        } catch (JwtException e) {
            log.error("Invalid JWT token: {}", e.getMessage(), e);
            sendErrorResponse(response, HttpServletResponse.SC_UNAUTHORIZED, "Invalid or expired token.");
        } catch (Exception e) {
            log.error("Unexpected error while processing JWT token: {}", e.getMessage(), e);
            sendErrorResponse(response, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "Internal server error.");
        }
    }

    private String resolveToken(HttpServletRequest request) {
        String bearerToken = request.getHeader("Authorization");
        if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
            log.info("Bearer token found in request header.");

            return bearerToken.substring(7);
        }
        log.warn("Authorization header not found or does not contain Bearer token.");

        return null;
    }

    private boolean isTokenValid(String token) {
        try {
            // 만료 여부를 검증
            Jwts.parser().verifyWith(jwtUtil.getKey()).build().parseSignedClaims(token);
            log.info("Token is valid.");
            
            return true;
        } catch (ExpiredJwtException e) {
            log.warn("JWT token is expired: {}", e.getMessage());
            return false;
        } catch (JwtException e) {
            log.error("Invalid JWT token: {}", e.getMessage());
            return false;
        }
    }

    private Authentication createAuthentication(String userId) {
        log.info("Creating authentication for userId: {}", userId);
        List<SimpleGrantedAuthority> authorities = List.of(new SimpleGrantedAuthority("ROLE_USER"));
        return new UsernamePasswordAuthenticationToken(userId, null, authorities);
    }

    private void sendErrorResponse(HttpServletResponse response, int status, String message) throws IOException {
        log.info("Sending error response with status {}: {}", status, message);
        response.setStatus(status);
        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");
        ErrorMessage errorMessage = ErrorMessage.builder().status(String.valueOf(status)).message(message).build();
        response.getWriter().write(errorMessage.toJson());
    }

}
```
            * custom metadata
```java
package kr.or.cbdc.infrastructure.security.intercept;

import java.util.Collection;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import jakarta.servlet.http.HttpServletRequest;
import kr.or.cbdc.infrastructure.security.service.SecuredResourceServiceImpl;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.InitializingBean;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.ConfigAttribute;
import org.springframework.security.access.hierarchicalroles.RoleHierarchyImpl;
import org.springframework.security.web.FilterInvocation;
import org.springframework.security.web.access.intercept.FilterInvocationSecurityMetadataSource;
import org.springframework.security.web.util.matcher.RequestMatcher;
import org.springframework.stereotype.Component;

@Component
public class ReloadableFilterInvocationSecurityMetadataSource
        implements FilterInvocationSecurityMetadataSource, InitializingBean {

    private static final Logger log = LoggerFactory.getLogger(ReloadableFilterInvocationSecurityMetadataSource.class);

    private @Autowired SecuredResourceServiceImpl securedResourceService;
    private @Autowired RoleHierarchyImpl roleHierarchy;

    private Map<RequestMatcher, List<ConfigAttribute>> requestMap;

    @Override
    public Collection<ConfigAttribute> getAttributes(Object object) throws IllegalArgumentException {
        HttpServletRequest request = ((FilterInvocation) object).getRequest();
        Collection<ConfigAttribute> result = null;

        for (Map.Entry<RequestMatcher, List<ConfigAttribute>> entry : this.requestMap.entrySet()) {
            if (entry.getKey().matches(request)) {
                result = entry.getValue();
                break;
            }
        }

        return result;
    }

    @Override
    public Collection<ConfigAttribute> getAllConfigAttributes() {
        Set<ConfigAttribute> allAttributes = new HashSet<ConfigAttribute>();

        for (Map.Entry<RequestMatcher, List<ConfigAttribute>> entry : this.requestMap.entrySet()) {
            allAttributes.addAll(entry.getValue());
        }

        return allAttributes;
    }

    @Override
    public boolean supports(Class<?> clazz) {
        return FilterInvocation.class.isAssignableFrom(clazz);
    }

    @Override
    public void afterPropertiesSet() throws Exception {
        this.requestMap = securedResourceService.getAuthorsAndUrl();
    }

    public void reloadAll() {
        this.reloadRequestMap();
        this.reloadHierarchy();
    }

    public void reloadRequestMap() {
        LinkedHashMap<RequestMatcher, List<ConfigAttribute>> requestMap = securedResourceService.getAuthorsAndUrl();

        this.requestMap.clear();
        this.requestMap.putAll(requestMap);

        log.info("Secured URL Resources - Role Mappings reloaded at Runtime!");
    }

    public void reloadHierarchy() {
        this.roleHierarchy.setHierarchy(securedResourceService.getRoleHierarchyStringRepresentation());
    }

}
```
            * SecurityConfig with FilterSecurityInterceptor
```java
package kr.or.cbdc.config;

import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.access.AccessDecisionVoter;
import org.springframework.security.access.hierarchicalroles.RoleHierarchyImpl;
import org.springframework.security.access.vote.AffirmativeBased;
import org.springframework.security.access.vote.RoleHierarchyVoter;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configuration.WebSecurityCustomizer;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.annotation.web.configurers.CorsConfigurer;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.access.intercept.FilterSecurityInterceptor;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.security.web.util.matcher.AntPathRequestMatcher;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import jakarta.servlet.http.HttpServletResponse;
import kr.or.cbdc.application.common.user.filter.JwtTokenFilter;
import kr.or.cbdc.application.common.user.handler.UserAccessDeniedHandler;
import kr.or.cbdc.application.common.user.handler.UserLoginFailureHandler;
import kr.or.cbdc.application.common.user.handler.UserLoginSuccessHandler;
import kr.or.cbdc.application.common.user.handler.UserLogoutSuccessHandler;
import kr.or.cbdc.application.common.user.provider.UserLoginProvider;
import kr.or.cbdc.infrastructure.error.model.ErrorMessage;
import kr.or.cbdc.infrastructure.framework.core.foundation.exception.BaseException;
import kr.or.cbdc.infrastructure.security.intercept.ReloadableFilterInvocationSecurityMetadataSource;
import kr.or.cbdc.infrastructure.security.service.SecuredResourceServiceImpl;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

	@Value(value = "${spring.profiles.active}")
	private String active;
	private @Autowired SecuredResourceServiceImpl securedResourceService;
	private @Autowired ReloadableFilterInvocationSecurityMetadataSource filterInvocationSecurityMetadataSource;
	private @Autowired JwtTokenFilter jwtTokenFilter;
	private @Autowired UserAccessDeniedHandler userAccessDeniedHandler;
	private @Autowired UserLoginSuccessHandler userLoginSuccessHandler;

	private void configureCors(CorsConfigurer<HttpSecurity> cors) {
		if (active.contains("live")) {
			cors.disable();
		} else {
			cors.configurationSource(corsConfigurationSource());
		}
	}

	@Bean
	public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
		http
			.cors(cors -> configureCors(cors))
			.csrf(AbstractHttpConfigurer:disable)
			.authorizeHttpRequests(authorizeRequests -> authorizeRequests
				.requestMatchers("/v1/public/**", "/actuator/health", "/actuator/info").permitAll()
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

		try {
			filterSecurityInterceptor.setAuthenticationManager(http.getSharedObject(AuthenticationManager.class));
		} catch (Exception e) {
			throw new BaseException(e);
		}

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
			new AntPathRequestMatcher("/api-docs/**"),
			new AntPathRequestMatcher("/configuration/**"),
			new AntPathRequestMatcher("/swagger*/**"),
			new AntPathRequestMatcher("/webjars/**"),
			new AntPathRequestMatcher("/swagger-ui/**"),
			new AntPathRequestMatcher("/docs"),
			new AntPathRequestMatcher("/api/login"),
			new AntPathRequestMatcher("/ewa/common/confirmUser"),
			new AntPathRequestMatcher("/ewa/common/selfAuth"),
			new AntPathRequestMatcher("/ewa/common/createUser"),
			new AntPathRequestMatcher("/ewa/stplat/readList"),
			new AntPathRequestMatcher("/ewa/common/regPinNum"));
	}
}
```
        * Low-level interface인 Filter나 OncePerRequestFilter를 상속하여 custome filter를 구현
    * ### 6. **AOP (Aspect-Oriented Programming)** #memo
      * An Aspect is a **specialized class** annotated with @Aspect (or configured via XML) that contains advice methods and pointcut expressions to implement cross-cutting concerns.

Advice
The actual code that runs at join points. Types: Before, After, Around, After-returning, After-throwing.

Join Point
A specific point in program execution where an aspect can be applied (method calls, field access, exceptions).

Pointcut
An expression that selects which join points to apply advice to. Defines "where" the aspect runs.

Weaving
The process of linking aspects with regular code to create the final executable. Can happen at compile-time, load-time, or runtime.
```java
@Aspect  // Special annotation
@Component
public class LoggingAspect {  // Specialized class
    
    @Before("execution(* com.example.*.*(..))") // Pointcut + Advice
    public void logBefore(JoinPoint joinPoint) {
        // This runs automatically, not called directly
    }
}
```

![[100. media/image/G1zZs8ljV5.png]]

- usage: It's more commonly employed for tasks that are not easily handled by filters or that apply to different layers beyond HTTP requests.
        * Logging and Monitoring
```java
@Aspect
@Component
public class LoggingAspect {

    @Around("execution(* com.yourpackage..*(..))")
    public Object logMethodExecutionTime(ProceedingJoinPoint joinPoint) throws Throwable {
        long start = System.currentTimeMillis();
        Object result = joinPoint.proceed();
        long executionTime = System.currentTimeMillis() - start;
        
        System.out.println(joinPoint.getSignature() + " executed in " + executionTime + "ms");
        return result;
    }
}
```
        * Transaction Management
          * Spring’s @Transactional annotation is based on AOP.
```java
@Service
public class YourService {

    @Transactional
    public void processData() {
        // Transactional code
    }
}
```
        * Caching
```java
@Cacheable("dataCache")
public Data getDataById(Long id) {
    // If data is not in the cache, fetch from DB and cache the result
    return dataRepository.findById(id);
}
```
        * Auditing
```java
@Aspect
@Component
public class AuditAspect {

    @Before("execution(* com.yourpackage.service.*.*(..)) && @annotation(Auditable)")
    public void auditMethod(JoinPoint joinPoint) {
        // Capture user action and log it
        String methodName = joinPoint.getSignature().getName();
        System.out.println("Audit log: " + methodName + " executed by user");
    }
}
```
        * Error Handling
          * global exception handler(@RestControllerAdvice)와 함께 쓸 수 있음.
          * AOP는 service 이하 계층에서 database 관련 특정 에러만 처리하고 나머지(보통 runtime exception)는 그냥 rest controller로 보내기
```java
@Aspect
@Component
public class ExceptionHandlingAspect {

    @AfterThrowing(pointcut = "execution(* com.yourpackage..*(..))", throwing = "ex")
    public void handleException(JoinPoint joinPoint, Exception ex) {
        // Log or handle the exception
        System.out.println("Exception in method: " + joinPoint.getSignature().getName() + " - " + ex.getMessage());
    }
}
```
        * Security at method level
```java
@Service
public class AdminService {

    @PreAuthorize("hasRole('ADMIN')")
    public void performAdminTask() {
        // Admin task logic
    }
}
```
        * Rate Limiting / Throttling
```java
@Aspect
@Component
public class RateLimitingAspect {

    @Around("execution(* com.yourpackage.api.*.*(..))")
    public Object rateLimit(ProceedingJoinPoint joinPoint) throws Throwable {
        // Implement rate limiting logic here
        return joinPoint.proceed();
    }
}
```
      * **Cross-Cutting Concerns**:
        * Master the usage of AOP to handle cross-cutting concerns like logging, security, caching, and transaction management.
        * Know how to define pointcuts and advices (@Before, @After, @Around) and use @Aspect for aspect-oriented programming.
      * Filter vs AOP
        * Filter: intercept http requests and applies cross-cutting concerns like authentication, authorization.
        * AOP: Intercept around method including http request
        * Similarity
          * Cross-cutting concerns
            * used to implement crusscutting concerns, such as logging, security, transaction management
          * Interception
          * Separation of concerns
        * Differences
          * Scope
            * Filters
              * are designed to intercept incoming requests on the web layer.
            * AOP
              * can intercept any method execution in the application. More general cross-cutting across all layers of an application.
          * Implementation
            * Filters
              * Filter or OncePerRequestFilter in Spring Security.
            * AOP
              * AspectJ or Spring AOP
      * [ ] Filter chain
    * ### 7. **Testing**
      * **Unit Testing**:
        * Write effective unit tests using JUnit 5 and Mockito. Learn to mock dependencies, verify method interactions, and write isolated tests for services and controllers.
      * **Integration Testing**:
        * Use Spring Boot’s testing framework to write integration tests with @SpringBootTest, @WebMvcTest, and @DataJpaTest.
        * Learn to use in-memory databases like H2 for testing data layers.
      * **TestContainers**:
        * Use TestContainers to run tests against real databases (or other services) in Docker containers, providing more accurate test environments.
    * ### 8. **Caching**
      * **Spring Cache**:
        * Understand how to use caching in Spring Boot via annotations like @Cacheable, @CachePut, and @CacheEvict.
        * Learn to configure caching backends like Redis, Ehcache, or Caffeine.
    * ### 9. **Messaging**
      * **Spring for Kafka / RabbitMQ**:
        * Learn to build event-driven microservices using message brokers like Kafka or RabbitMQ with Spring Boot. Use @KafkaListener or @RabbitListener to consume messages.
      * **Spring Boot with JMS**:
        * Learn how to integrate Java Messaging Service (JMS) for asynchronous messaging, including usage of @JmsListener.
    * ### 10. **Async Programming**
      * **Asynchronous Tasks**:
        * Learn to use @Async and @Scheduled to handle asynchronous method execution and scheduling background jobs.
        * Understand the use of ExecutorService, thread pools, and how to handle concurrency issues.
    * ### 11. **Microservices and Distributed Systems**
      * **Spring Cloud**:
        * Learn to build microservices with Spring Cloud, focusing on key concepts like service discovery (Eureka, Consul), API Gateway (Spring Cloud Gateway), and load balancing (Ribbon).
        * Understand how to handle configuration management with Spring Cloud Config, distributed tracing (Sleuth, Zipkin), and circuit breakers (Resilience4j).
      * **RESTful Microservices**:
        * Design RESTful microservices with proper error handling, security, and communication patterns between services using REST, gRPC, or messaging.
    * ### 12. **DevOps and Deployment**
      * **Spring Boot Actuator**:
        * Monitor and manage your Spring Boot application with Actuator, including built-in endpoints for health, metrics, and custom monitoring.
      * **Containerization**:
        * Learn to containerize Spring Boot applications using Docker and configure Kubernetes (K8s) for deploying, scaling, and managing microservices.
      * **CI/CD Pipelines**:
        * Set up continuous integration and continuous deployment pipelines using tools like Jenkins, GitLab CI, or GitHub Actions.
    * ### 13. **API Documentation and OpenAPI**
      * **Swagger / OpenAPI**:
        * Document your REST APIs using Swagger and OpenAPI with Springfox or Springdoc, providing clear documentation for developers and clients.
      * **Versioning and Pagination**:
        * Learn API versioning strategies and how to implement pagination, filtering, and sorting in your APIs.
    * ### Summary of Essential Knowledge:
      * AreaSkills
      * **Core Spring**IoC, DI, Bean lifecycle, Auto-configuration
      * **Spring Boot Basics**Starter dependencies, Configuration, Profiles
      * **Spring MVC & REST**REST API design, Exception handling, Validation
      * **Data Access**Spring Data JPA, Transactions, Database migrations
      * **Security**Spring Security, JWT, OAuth2, Filter chain
      * **AOP**Cross-cutting concerns, Pointcuts, Aspects
      * **Testing**Unit testing, Integration testing, TestContainers
      * **Caching**Spring caching, Redis, Ehcache
      * **Messaging**Kafka, RabbitMQ, JMS
      * **Async Programming**@Async, @Scheduled, Thread pools
      * **Microservices**Spring Cloud, Service discovery, API Gateway
      * **DevOps & Deployment**Actuator, Docker, Kubernetes, CI/CD
      * **API Documentation**Swagger, OpenAPI, API versioning
      * Mastering these areas will allow you to fully leverage the power of Spring Boot to build robust, scalable, and maintainable applications.
  * # Setup
    * **Set Up Your Project Structure:**
      * Spring Initializr (https://start.spring.io/)
      * dependencies
        * **Spring Web** (for REST APIs),
        * **DB**
          * **Spring Data JPA** (for database interaction)
          * **MyBatis**
        * **Spring Boot Starter JDBC** (this will include HikariCP, which is the default connection pool).
        * **MySQL Driver** (for MySQL connectivity)
        * **Spring Boot DevTools** (for development purposes)
          * 주의!! Automatic restart 때문에 일부 third-party library(kafka)에 문제를 일으킬 때가 있다.
        * **Lombok** (optional, to reduce boilerplate code)
      * Build system
        * maven
        * gradle
          * build.gradle 예
```plain text
plugins {
    id 'org.springframework.boot' version '3.1.0'
    id 'io.spring.dependency-management' version '1.1.0'
    id 'java'
}

group = 'com.example'
version = '0.0.1-SNAPSHOT'
sourceCompatibility = '17'

repositories {
    mavenCentral()
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'mysql:mysql-connector-java'
    implementation 'org.projectlombok:lombok'
    developmentOnly 'org.springframework.boot:spring-boot-devtools'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}

test {
    useJUnitPlatform()
}
```
          * 디지털 바우처 시스템 build.gradle
```plain text
/*
 * This file was generated by the Gradle 'init' task.
 */
plugins {
    id 'org.springframework.boot' version '3.1.6'
    id 'io.spring.dependency-management' version '1.1.4'
    id 'java'
    id 'war'
    id 'application'
}

repositories {
    mavenLocal()

    maven {
        url = uri('https://repo.ccmedia.co.kr/repository/maven-public/')
    }

}

compileJava {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}

ext {
    whichSdk = "voucher"
}

def env = hasProperty('env') ? project.env : 'dev'
def appVersion = hasProperty('version') ? project.version : '0.0.1'

task copyConfigProperties {
    doFirst {
        def configDir = "src/main/resources/config"
        def sdkFileName = "src/main/resources/wallet.sdk.${env}.properties"
        def appConfigFile = "${configDir}/application.${env}.yml"

        if (file(sdkFileName).exists()) {
            copy {
                from sdkFileName
                into 'build/resources/main'
                rename { fileName -> 'wallet.sdk.properties' }
            }
        } else {
            throw new GradleException("SDK 파일 ${sdkFileName}이 존재하지 않습니다.")
        }

        if (file(appConfigFile).exists()) {
            copy {
                from appConfigFile
                into 'build/resources/main/config'
                rename { fileName -> 'application.yml' }
            }
        } else {
            throw new GradleException("환경별 설정 파일 ${appConfigFile}이 존재하지 않습니다.")
        }
    }
}


bootWar {
    dependsOn copyConfigProperties

    archiveFileName = "voucher-cbdc-${appVersion}.war"

    into('WEB-INF/classes') {
        from('src/main/resources/configuration/message') {
            include '**/*.properties', '**/*.yml'
        }
    }
    duplicatesStrategy = DuplicatesStrategy.EXCLUDE
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-actuator'
    implementation 'org.springframework.boot:spring-boot-starter-security'
    implementation 'org.springframework.boot:spring-boot-starter-aop'
    implementation 'org.springframework.boot:spring-boot-starter-quartz'
    implementation 'org.springframework.boot:spring-boot-starter-mail'
    implementation 'org.mybatis.spring.boot:mybatis-spring-boot-starter:3.0.1'
    implementation 'org.apache.commons:commons-dbcp2:2.8.0'
    implementation 'org.apache.commons:commons-lang3:3.12.0'
    implementation 'commons-io:commons-io:2.14.0'
    implementation 'commons-codec:commons-codec:1.15'
    implementation 'org.apache.velocity:velocity:1.7'
    implementation 'org.apache.poi:poi:5.2.5'
    implementation 'org.apache.poi:poi-ooxml:5.2.5'
    implementation 'org.apache.poi:poi-scratchpad:5.2.5'
    implementation 'com.googlecode.json-simple:json-simple:1.1'
    implementation 'mysql:mysql-connector-java:8.0.33'
    implementation 'javax.servlet:javax.servlet-api:4.0.1'

    implementation group: 'io.minio', name: 'minio', version: '8.4.1'

    implementation 'org.springdoc:springdoc-openapi-starter-webmvc-ui:2.3.0'

    implementation group: 'com.google.code.gson', name: 'gson', version: '2.8.6'
    implementation 'io.jsonwebtoken:jjwt-impl:0.12.5'
    implementation 'io.jsonwebtoken:jjwt-api:0.12.5'
    implementation 'io.jsonwebtoken:jjwt-jackson:0.12.5'
    implementation 'com.sun.xml.bind:jaxb-impl:4.0.1'
    implementation 'com.sun.xml.bind:jaxb-core:4.0.1'
    // javax.xml.bind
    implementation 'javax.xml.bind:jaxb-api:2.4.0-b180830.0359'
    implementation 'com.fasterxml.jackson.datatype:jackson-datatype-jsr310'

    implementation 'com.fasterxml.jackson.core:jackson-databind:2.15.3'

    implementation 'org.springframework.kafka:spring-kafka:3.1.1'
    implementation 'org.springframework.boot:spring-boot-starter-validation'
    implementation 'com.google.firebase:firebase-admin:6.8.1'
    implementation group: 'com.squareup.okhttp3', name: 'okhttp', version: '4.11.0'
    implementation 'com.google.guava:guava:31.1-jre'

    implementation group: 'org.web3j', name: 'core', version: '4.12.0'

    // wallet-sdk.jar
    implementation files("libs/wallet-sdk-0.0.1-SNAPSHOT.jar")

    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'

    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testImplementation 'org.springframework.security:spring-security-test'
    testImplementation 'org.projectlombok:lombok'

}

bootRun {
    jvmArgs = [
            "-Xms1024m",
            "-Xms2048m"
    ]
}

tasks.withType(JavaCompile) {
    options.encoding = 'UTF-8'
    options.compilerArgs.add("-parameters")
}
```
    * **Configure MySQL Database in Spring Boot:**
      * configure database setting in application.properties or application.yml
        * application.properties
```plain text
spring.datasource.url=jdbc:mysql://localhost:3306/your_database_name
spring.datasource.username=your_username
spring.datasource.password=your_password
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver

# HikariCP settings (optional tuning)
spring.datasource.hikari.maximum-pool-size=10
spring.datasource.hikari.minimum-idle=5
```
        * application.yml
```plain text
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/your_database_name
    username: your_username
    password: your_password
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
```
        * 디지털 바우처 시스템(mybatis 설정 포함)
          * application.dev.yml
```plain text
server:
  servlet:
    encoding:
      charset: UTF-8
  tomcat:
    uri-encoding: UTF-8
    # additional-tld-skip-patterns: "*.jar"
  error:
    include-message: always

spring:
  servlet:
    multipart:
      max-file-size: 20MB
      max-request-size: 20MB
  datasource:
    hikari:
      maximum-pool-size: 20   # 커넥션 풀의 최대 크기 설정
      minimum-idle: 5         # 최소 유지할 커넥션 수 설정
      idle-timeout: 30000     # 커넥션이 유휴 상태일 때 제거되는 시간 설정 (밀리초)
      max-lifetime: 1800000   # 커넥션의 최대 수명 설정 (밀리초)
  kafka:
    listener:
      ack-mode: MANUAL_IMMEDIATE
      concurrency: 3
    consumer:
      enable-auto-commit: false
  main:
    allow-circular-references: true
  profiles:
    active: voucher-dev
    group:
      bank:
        - logging-console
        - logging-file
      #        - bank-scheduler
      voucher:
        - logging-console
        - logging-file

  jmx:
    enabled: false
  messages:
    cache-seconds: -1
  http:
    multipart:
      max-request-size: -1
      max-file-size: -1
  freemarker:
    enabled: false
  mvc:
    favicon:
      enabled: false
  jpa:
    database: mysql
  devtools:
    livereload:
      enabled: true
    restart:
      enabled: true
      additional-paths: src/main/java
      exclude: static/**,public/**,templates/**,build/**
  config:
    import: optional:file:.env[.properties]
logging:
  level: # trace < debug < info < warn < error < fatal < off
    root: error
    java.sql: info
    jdbc: warn
    jdbc.sqlonly: info
    jdbc.sqltiming: info
    jdbc.audit: warn
    jdbc.resultset: info
    jdbc.resultsettable: info
    jdbc.connection: warn
    sun.rmi: info
    org.apache: error
    #    org.quartz: info
    org.springframework: info
    org.springframework.kafka: off
    org.apache.kafka.client.consumer: off
    kr.or.cbdc.infrastructure.queue: debug

config:
  system-title: 금융결제원 | 스마트계약 관리시스템
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
  default-locale: ko_KR
  message:
    invalid-text:
      prefix:
      suffix:
  log:
    enable: true
    query:
      enable: false
    error:
      enable: true
      server-code: A
    login:
      enable: true
    menu:
      enable: true
  file:
    content-transfer-encoding: "binary;"
    download-filename-encoding: true
    repository:
      create-if-not-exists: true
      repositories:
        repository1: data/files
        repository1-file-policy: smartContract
        repository1-sub-path: /smartContract
        repository1-max-upload-size: 100MB
        repository1-date-folder: /
        repository1-include-extensions: abi, bin
        repository1-exclude-extensions: exe
    download-dir: data/download
  login:
    admin:
      enable: true
      ip-list:
        - "X"
      key: "Ng@q16O#27,u5})XHs:8d!98Y5HhL_1B[8~U91XWv8)Db22%tt"
      password: "0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c"
    fail:
      avail-count: 5
    default-author-code: ROLE_USER
  payment: #거액당좌계좌 목업시스템 위치
    url: "http://10.100.138.9:8080/bok-payment/search/SearchPayment"

springdoc:
  use-fqn: true
  packages-to-scan: kr.or.cbdc
  default-consumes-media-type: application/json;charset=UTF-8
  default-produces-media-type: application/json;charset=UTF-8
  swagger-ui:
    path: /swagger-ui.html            # Swagger UI 경로 => localhost:8000/demo-ui.html
    tags-sorter: alpha            # alpha: 알파벳 순 태그 정렬, method: HTTP Method 순 정렬
    operations-sorter: alpha      # alpha: 알파벳 순 태그 정렬, method: HTTP Method 순 정렬
    disable-swagger-default-url: true
  api-docs:
    enabled: true
    path: /api-docs/json
    groups:
      enabled: true
  cache:
    disabled: true

    #management:
    #  endpoints:
    #    web:
    #      exposure:
    #        include: health,info

navercloud:
  mailer:
    api:
      url: https://mail.apigw.ntruss.com/api/v1/mails
      accessKey: xxxxxxxxx  # NCP 계정관리 API 키 발급 Access Key
      secretKey: xxxxxxx # NCP 계정관리 API 키 발급 Secret Key
    sender: contact@sooho.io # Sender 메일 설정
    s
```
          * application-voucher-dev.yml
```plain text
################################################################################
# 기본
################################################################################
server:
  port: 8085
  servlet:
    context-path: /

spring:
  kafka:
    code: NHB         # code는 처리 기관을 의미하는 값임
    topicTxRequest: txIn_local    # Tx 처리요청 전달
    topicTxRequest2: txIn_local    # Tx 처리요청 전달
    topicTxResponse: txOut_local   # Tx 처리결과 전달
    # topicTxBlockChain: wallet-core.dev.transactions.response # blockchain tx 결과수신
    topicTxBlockChain: po-wallet-core.dev.transactions.response # blockchain tx 결과수신
    group: nhb_cbdc_bank_test234   # group id는 기관마다 상이하여야 함
    bc-group: nhb_cbdc_bank_test_yc_218   # bc-group id는 모든 서바가 unique하여야 함
    bootstrap-servers: 000.000.000.000:9091
    bootstrap-servers-blockchain: 000.000.000.000:9091
    consumer:
      auto-offset-reset: latest
    retry:
      #      TODO : 에러 발생으로 인해 retry 시도 시간 1초에서 변경
      delay: 10000
      count: 1
  #      delay: 1000
  #      count: 3
  jwt:
    access-expired: 180000 #30 * 60
    refresh-expired: 86400 #24 * 60 * 60
    prtCmpny-access-expired: 2629824 # 30.44 × 24× 60 × 60
    # 참여기관에서 한국은행에 접속할 때 사용하는 토큰
    bok-accessToken: "eyJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3MjgzMzcxMjQsInN1YiI6Ijc2QUJDRjdZUzRGNEREOEZDMCIsInVzZXJfaWQiOiI3NkFCQ0Y3WVM0RjRERDhGQzAiLCJ1c2VyX25tIjoiTkjrho3tmJEiLCJwZXJzb25faWQiOiI3NkFCQ0Y3WVM0RjRBRDdFQTAiLCJ1c2VyX2RpdiI6IltcIlJPTEVfQkFOS1wiXSJ9.otBzcknkgWBDnn4Zqh3KdzhgnlXgbpO0rzdC9GvRiaQ"

logging:
  level: # trace < debug < info < warn < error < fatal < off
    org.springframework.jdbc.core.JdbcTemplate: debug
    org.springframework.security: DEBUG
    kr.or.cbdc: debug
    kr.or.cbdc.infrastructure.framework.core.support.message: warn


config:
  bank-code: NHB  # kafka에서 참여 기관를 구분하는 코드로 사용, 간편서비스에서 참여기관 구분용 코드
  bank-no: "011"
  bank-nm: A은행
  wallet-version: "1.0"
  bok-cbdc: # 증앙은행 및 키관리 시스템 위치
    bok-server-rpc: "http://000.000.000.000:0000"
    key-server-rpc: "http://000.000.000.000:0000"
    x-api-key: "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    default-pub-key: "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"  # 은행 기본 지갑 ( owner 로 활요 )
    fromAddr: "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    toAddr: "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
  datasources:
    main:
      hikari:
        driver-class-name: "com.mysql.jdbc.Driver"
        jdbc-url: "jdbc:mysql://localhost:3306/bok-cbdc-voucher?characterEncoding=UTF-8"
        username: "root"
        password: "sooho"
        minimum-idle: 10
        maximum-pool-size: 20
        idle-timeout: 60000
        connection-timeout: 30000
        connection-test-query: "SELECT 1 "
    mirror:
      hikari:
        driver-class-name: "com.mysql.jdbc.Driver"
        jdbc-url: "jdbc:mysql://localhost:3306/bok-cbdc-voucher?characterEncoding=UTF-8"
        username: "root"
        password: "sooho"
        minimum-idle: 10
        maximum-pool-size: 20
        idle-timeout: 60000
        connection-timeout: 30000
        connection-test-query: "SELECT 1 "
  minio:
    bok:
      s3:
        bucket:
          contract: bok-cbdc-dev-analysis-content
          tar: bok-cbdc-dev-archived-analysis-content
          expert-report: bok-cbdc-dev-expert-report
          final-report: bok-cbdc-dev-final-report
    endpoint: http://localhost:9000
    accessKey: minioadmin
    secretKey: minioadmin
  analyzer:
    run:
      url: http://localhost:9090/analyses/run
    rerun:
      url: http://localhost:9090/analyses/rerun

contract:
  manager:
    url: http://localhost:8051/ContractManager

compile:
  manager:
    url: http://localhost:8085/v1/vc/compile

eoa:
  manager:
    url: http://localhost:8051/EoaWalletManager

```
    * **MyBatis Setup**:
      * Create a mybatis-config.xml file in your src/main/resources directory to configure MyBatis globally.
        * mybatis-config.xml
```xml
<configuration>
  <settings>
    <setting name="cacheEnabled" value="true" />
    <setting name="mapUnderscoreToCamelCase" value="true" />
  </settings>
</configuration>
```
      * 위 방법은 거의 필요없고 application.yml에 정의해도 됨
        * application.yml 예
```plain text
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/your_database_name
    username: your_username
    password: your_password
    driver-class-name: com.mysql.cj.jdbc.Driver
    hikari:
      maximum-pool-size: 10
      minimum-idle: 5
  mybatis:
    configuration:
      map-underscore-to-camel-case: true
      cache-enabled: false
```
      * 디지털 바우처에서는 application.yml에 정의
      * spring boot는 datasource 관련 환경을 자동으로 한다.(autoconfigure) 하지만 세부 조정하고 싶으면 configuration class를 직접 만들어서 설정 가능.
    * **Set Up Database and Tables:**
      * 디지털 바우처 금결원(docker로 mysql 시스템 생성)
        * /docker
          * docker-compose.yml
```plain text
services:
  bok-mysql:
    image: mysql:8.0
    platform: linux/amd64
    volumes:
      - ./data/mysql:/var/lib/mysql
      - ../database/config/my.cnf:/etc/mysql/my.cnf
      - ../database/01-init.sql:/docker-entrypoint-initdb.d/01-init.sql
      - ../database/02-func-all.sql:/docker-entrypoint-initdb.d/02-func-all.sql
      - ../database/03-init-data.sql:/docker-entrypoint-initdb.d/03-init-data.sql
      - ../database/04-init-custom-data.sql:/docker-entrypoint-initdb.d/04-init-custom-data.sql
      - ../database/05-add-voucher-data.sql:/docker-entrypoint-initdb.d/05-add-voucher-data.sql
    command: --character-set-server=utf8mb4 --collation-server=utf8mb4_general_ci
    environment:
      - MYSQL_ROOT_PASSWORD=sooho
      - MYSQL_DATABASE=bok-cbdc-voucher
      - MYSQL_CHARSET=utf8mb4
      - MYSQL_LOG_BIN_TRUST_FUNCTION_CREATORS=1
    ports:
      - "3306:3306"
    restart: unless-stopped
    networks:
      - shared_network
  bok-minio:
    image: minio/minio:RELEASE.2020-08-27T05-16-20Z
    platform: linux/amd64
    volumes:
      - ./data/minio:/data
    environment:
      - MINIO_ACCESS_KEY=minioadmin
      - MINIO_SECRET_KEY=minioadmin
    ports:
      - "9000:9000"
    command: server /data
    ulimits:
      nproc: 65535
      nofile:
        soft: 65535
        hard: 65535
    restart: unless-stopped
    networks:
      - shared_network
  bok-redis:
    image: redis:7.2.5
    platform: linux/amd64
    volumes:
      - ./data/redis:/data
    ports:
      - "6379:6379"
    ulimits:
      nproc: 65535
      nofile:
        soft: 65535
        hard: 65535
    restart: unless-stopped
    networks:
      - shared_network

networks:
  shared_network:
    driver: bridge
```
          * start.sh: git bash 띄워서 실행하면 /docker/data 디렉토리 만들고 거기에 mysql, minio, redis 생성.
```shell
#!/bin/bash

docker-compose -f docker-compose.yml up --remove-orphans
```
          * stop.sh
```shell
#!/bin/bash

PROJECT_NAME=cbdc-voucher

function stop()
{
  P1=$(docker ps -q)
  if [ "${P1}" != "" ]; then
    echo "Killing all running containers"  &2> /dev/null
    docker kill ${P1}
  fi

  P2=$(docker ps -aq)
  if [ "${P2}" != "" ]; then
    echo "Removing all containers"  &2> /dev/null
    docker rm ${P2} -f
  fi
}

# Function to remove the images as well
function remove()
{
  P=$(docker images -aq "${PROJECT_NAME}\/*")
  if [ "${P}" != "" ]; then
    echo "Removing images"  &2> /dev/null
    docker rmi ${P} -f
  fi
}

function prune()
{
  docker system prune -a --volumes
}

echo "For all Docker containers or images"
echo "1 - Kill and remove only the containers"
echo "2 - Kill and remove the containers and remove all the downloaded images"
echo "3 - Remove all stopped containers, unused images, networks and volumes not used by at least one container and all build cache"
echo "4 - Quit and not do anything"
echo
PS3="Please select which option > "
options=("Kill & Remove" "Remove Images" "Prune" "Quit")
select yn in "${options[@]}"; do
    case $yn in
        "Kill & Remove" ) stop;  break;;
        "Remove Images" ) stop;  remove; break;;
        "Prune" ) stop;  prune; break;;
        "Quit" ) exit;;
    esac
done
```
        * /database
          * /config
            * my.cnf
```plain text
[mysqld]
default-time-zone = 'Asia/Seoul'
innodb_file_per_table = 1
innodb_use_native_aio = 0
explicit_defaults_for_timestamp = 1
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci
init-connect='SET NAMES utf8mb4'
innodb_default_row_format=DYNAMIC
lower_case_table_names=2
max_connections = 200

[client]
default-character-set=utf8mb4

[mysql]
default-character-set=utf8mb4
```
          * 01-init.sql
```plain text
-- Initial DDL: valid from commit hash
CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.tb_ca_vc_verification_request (
    `req_id` varchar(18) not null comment '템플릿 검증 의뢰 ID (eg. REQ+YYYY+MM+DD+000001)',
    `template_name` varchar(500) not null comment '템플릿명',
    `template_type` varchar(100) not null comment '템플릿 타입 CODE(캐시백형, 쿠폰형) (그룹 코드 : G004)',
    `verification_status` varchar(100) not null comment '검증의뢰 상태 CODE (그룹 코드 : G003)',
    `requested_at` datetime null comment '검증의뢰신청일',
    `requested_by` int not null comment '검증의뢰신청인 ID',
    `verify_started_at` datetime default null comment '검증시작일',
    `verify_completed_at` datetime default null comment '검증종료일',
    `verified_by` int default null comment '검증인 ID',
    `verified_opinion` varchar(2000) default null comment '전문가 검증 승인 의견',
    `rejected_reason` varchar(2000) default null comment '검증 반려사유',
    `company_id` varchar(18) not null comment '기관(회사)ID',
    `created_at` datetime not null comment '등록일',
    `created_by` int not null comment '등록인 ID',
    `updated_at` datetime not null comment '수정일',
    `updated_by` int not null comment '수정인 ID',
    `callback_uri` text COLLATE utf8mb4_general_ci DEFAULT NULL, -- 추가
    `current_contract_id` bigint default NULL comment '현재 사용중인 컨트랙트 ID',
    primary key (`req_id`)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.tb_ca_verification_contract_info (
    `contract_id` bigint NOT NULL auto_increment,
    `content` longtext COLLATE utf8mb4_general_ci,
    `file_path` text COLLATE utf8mb4_general_ci DEFAULT NULL,
    `code_lines` int DEFAULT NULL,
    `file_name` varchar(191) COLLATE utf8mb4_general_ci DEFAULT NULL,
    `abi_info` longtext not null comment '계약코드 컴파일 정보 - ABI',
    `bytecode_info` longtext not null comment '계약코드 컴파일 정보 - 바이트코드',
    `created_at` datetime DEFAULT NULL,
    `updated_at` datetime DEFAULT NULL,
    `req_id` varchar(18) NOT NULL,
    PRIMARY KEY (`contract_id`),
    KEY `FK_contract_req_id_req_id` (`req_id`),
    CONSTRAINT `FK_contract_req_id_req_id` FOREIGN KEY (`req_id`) REFERENCES `tb_ca_vc_verification_request` (`req_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.tb_ca_verification_expert_report (
    `id` bigint NOT NULL auto_increment comment '전문가 평가 ID',
    `mid_report_file_path` varchar(200) null comment '검증 중간보고서 파일경로',
    `mid_report_file_name` varchar(200) null comment '검증 중간보고서 파일명',
    `mid_report_opinion` varchar(2000) null comment '검증 중간보고서 의견',
    `resolve_needed` boolean null comment '검증 중간보고서 의견',
    `verification_success` boolean NULL comment '검증 중간보고서 의견',
    `contract_id` bigint not NULL comment '컨트랙트 ID',
    `created_at` datetime not null comment '등록일',
    `created_by` int not null comment '등록인 ID',
    `updated_at` datetime not null comment '수정일',
    `updated_by` int not null comment '수정인 ID',
    PRIMARY KEY (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.tb_ca_vulnerability_report (
    `id` bigint NOT NULL auto_increment comment '취약점 발견 ID SEQ',
    `analyzer_name` varchar(191) COLLATE utf8mb4_general_ci DEFAULT NULL comment '취약점 발견 분석기명',
    `analyzer_type` varchar(191) COLLATE utf8mb4_general_ci DEFAULT NULL comment '취약점 발견 분석기타입 CODE (그룹 코드 : G005)',
    `description` longtext COLLATE utf8mb4_general_ci comment '취약점 발견 분석기 설명',
    `end_line` int DEFAULT NULL comment '취약점 코드 끝 라인',
    `subject` varchar(191) COLLATE utf8mb4_general_ci DEFAULT NULL comment '취약점 제목',
    `severity` varchar(191) COLLATE utf8mb4_general_ci DEFAULT NULL comment '취약점 수준 레벨',
    `start_line` int DEFAULT NULL comment '취약점 코드 시작 라인',
    `contract_id` bigint not NULL comment '컨트랙트 ID',
    `patch` longtext COLLATE utf8mb4_general_ci DEFAULT NULL,
    `created_at` datetime not null comment '등록일',
    `updated_at` datetime not null comment '수정일',
    PRIMARY KEY (`id`),
    KEY `FK_vulnerability_contract_id_contract_id` (`contract_id`),
    CONSTRAINT `FK_vulnerability_contract_id_contract_id` FOREIGN KEY (`contract_id`) REFERENCES `tb_ca_verification_contract_info` (`contract_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.tb_ca_analyzer_status (
    `id` bigint NOT NULL auto_increment comment '분석기 검증 수행 ID',
    `analyzer_name` varchar(191) COLLATE utf8mb4_general_ci DEFAULT NULL comment '취약점 발견 분석기명',
    `analyzer_type` varchar(191) COLLATE utf8mb4_general_ci DEFAULT NULL comment '취약점 발견 분석기타입 CODE (그룹 코드 : G005)',
    `status` varchar(191) COLLATE utf8mb4_general_ci DEFAULT NULL comment '분석 검증 수행 상태 CODE (그룹 코드 : G006)',
    `error_msg` longtext COLLATE utf8mb4_general_ci DEFAULT NULL comment '분석 검증 수행 오류 메시지',
    `elapsed_time` bigint DEFAULT NULL comment '검증 수행 실행 시간',
    `contract_id` bigint not NULL comment '컨트랙트 ID',
    `created_at` datetime not null comment '등록일',
    `updated_at` datetime not null comment '수정일',
    PRIMARY KEY (`id`),
    KEY `FK_contract_id_contract_id` (`contract_id`),
    CONSTRAINT `FK_contract_id_contract_id` FOREIGN KEY (`contract_id`) REFERENCES `tb_ca_verification_contract_info` (`contract_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

-- 추후 삭제 필요 테이블
CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.tb_ca_swc_template (
    `id` bigint NOT NULL auto_increment,
    `swc_id` varchar(191) COLLATE utf8mb4_general_ci DEFAULT NULL,
    `title` varchar(191) COLLATE utf8mb4_general_ci DEFAULT NULL,
    `description` longtext COLLATE utf8mb4_general_ci,
    `language` varchar(191) COLLATE utf8mb4_general_ci DEFAULT NULL,
    `case_link` text COLLATE utf8mb4_general_ci DEFAULT NULL,
    `reference_title` text COLLATE utf8mb4_general_ci DEFAULT NULL,
    `reference_link` text COLLATE utf8mb4_general_ci DEFAULT NULL,
    PRIMARY KEY (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.tb_ca_oracle_grant_bank (
    `id` bigint not null auto_increment comment '오라클 권한 EOA 주소 맵핑 SEQ',
    `company_id` varchar(18) not null comment '기관(회사) ID',
    `wallet_id` int not null comment '지갑 ID',
    `transaction_hash` varchar(100) null comment '트랜잭션 해시값',
    `transaction_status` varchar(100) null comment '트랜잭션 상태',
    `oracle_id` varchar(18) not null comment '오라클 ID',
    `created_at` datetime not null comment '생성일',
    `created_by` int not null comment '생성인',
    primary key (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.tb_ca_oracle_mgt_info (
    `oracle_id` varchar(18) not null comment '오라클 ID (eg. ORA+YYYY+MM+DD+000001)',
    `oracle_name` varchar(200) null comment '오라클 배포명',
    `code_content` longtext null comment '계약 코드 내용',
    `file_path` varchar(200) null comment 'Minio FilePath',
    `file_name` varchar(200) null comment 'Minio FileName',
    `abi_info` longtext not null comment '계약코드 컴파일 정보 - ABI',
    `bytecode_info` longtext not null comment '계약코드 컴파일 정보 - 바이트코드',
    `usage` boolean not null comment '사용 상태',
    `deployed_address` varchar(100) null comment '오라클 배포 주소값',
    `transaction_hash` varchar(100) null comment '트랜잭션 해시값',
    `transaction_status` varchar(100) null comment '트랜잭션 상태값',
    `created_at` datetime not null comment '생성일',
    `created_by` int not null comment '생성자 ID',
    `deployed_at` datetime null comment '배포일',
    `deployed_by` int null comment '배포자 ID',
    `updated_at` datetime not null comment '수정일',
    `updated_by` int not null comment '수정자 ID',
    primary key (`oracle_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.tb_ca_vc_mgt_info (
    `mgt_id` varchar(18) not null comment '바우처 배포 주소 관리 ID (eg. MGT+YYYY+MM+DD+000001)',
    `mgt_name` varchar(200) not null comment '바우처 배포 주소 관리명',
    `code_content` longtext not null comment '계약코드 내용',
    `file_path` varchar(200) null comment '계약코드 파일경로',
    `file_name` varchar(200) null comment '계약코드 파일명',
    `abi_info` longtext not null comment '계약코드 컴파일 정보 - ABI',
    `bytecode_info` longtext not null comment '계약코드 컴파일 정보 - 바이트코드',
    `usage` boolean not null comment '사용 상태',
    `deployed_address` varchar(100) null comment '배포 주소값',
    `transaction_hash` varchar(100) null comment '배포 트랜잭션 해시값',
    `transaction_status` varchar(100) null comment '배포 트랜잭션 상태',
    `created_at` datetime not null comment '생성일',
    `created_by` int not null comment '생성자 ID',
    `deployed_at` datetime comment '배포일',
    `deployed_by` int comment '배포자 ID',
    `updated_at` datetime not null comment '수정일',
    `updated_by` int not null comment '수정자 ID',
    primary key (`mgt_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.tb_ca_register_vc_deployed_address (
    `id` bigint not null auto_increment comment '바우처 배포 주소 관리 등록 ID',
    `transaction_hash` varchar(100) null comment '트랜잭션 해시값',
    `transaction_status` varchar(100) null comment '트랜잭션 상태',
    `mgt_id` varchar(18) not null comment '바우처 배포 주소 관리 ID',
    `deploy_request_id` varchar(18) not null comment '바우처 배포 생성 의뢰 ID',
    `created_at` datetime not null comment '생성일',
    `created_by` int not null comment '생성자 ID',
    `updated_at` datetime not null comment '수정일',
    `updated_by` int not null comment '수정자 ID',
    primary key (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.tb_ca_initl_factor_value (
    `factor_id` bigint not null auto_increment comment '바우처 배포 생성자 값 ID',
    `factor_name` varchar(200) not null comment '바우처 배포 생성자 값 명 (eg. 오라클 주소값)',
    `variable_name` varchar(200) not null comment '바우처 배포 생성자 값 명 (eg. 0x123123)',
    `data_type` varchar(100) not null comment 'Solidity 컨트랙트 데이터 타입 CODE',
    `data_value` varchar(200) null comment '컨트랙트 생성자 데이터 값',
    `deploy_request_id` varchar(18) not null comment '바우처 배포 주소 관리 ID',
    `created_at` datetime not null comment '생성일',
    `created_by` int not null comment '생성자 ID',
    `updated_at` datetime not null comment '수정일',
    `updated_by` int not null comment '수정자 ID',
    primary key (`factor_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.tb_ca_vc_deploy_request (
    `deploy_request_id` varchar(18) not null comment '바우처 배포 의뢰 ID (eg. VCD+YYYY+MM+DD+000001)',
    `voucher_name` varchar(200) not null comment '바우처 배포 의뢰명',
    `voucher_requested_agency` varchar(200) not null comment '바우처 의뢰 기관 CODE (그룹코드 : G008)',
    `status` varchar(100) not null comment '바우처 배포 상태 CODE (그룹코드 : G009)',
    `abi_info` longtext not null comment '계약코드 컴파일 정보 - ABI',
    `bytecode_info` longtext not null comment '계약코드 컴파일 정보 - 바이트코드',
    `deployed_address` varchar(100) null comment '배포 주소 값',
    `deployed_transaction_hash` varchar(100) null comment '배포 트랜잭션 해시값',
    `deployed_transaction_status` varchar(100) null comment '배포 트랜잭션 상태',
    `rejected_reason` varchar(2000) null comment '바우처 배포 의뢰 반려 사유',
    `approved_at` datetime null comment '바우처 배포 의뢰 승인일',
    `approved_by` int null comment '바우처 배포 의뢰 승인자 ID',
    `rejected_at` datetime null comment '바우처 배포 의뢰 반려일',
    `rejected_by` int null comment '바우처 배포 의뢰 반려자 ID',
    `deployed_at` datetime null comment '바우처 배포일',
    `deployed_by` int null comment '바우처 배포자 ID',
    `template_id` varchar(18) not null comment '바우처 검증완료 템플릿 ID',
    `created_at` datetime not null comment '생성일',
    `created_by` int not null comment '생성자 ID',
    `updated_at` datetime not null comment '수정일',
    `updated_by` int not null comment '수정자 ID',
    primary key (`deploy_request_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.tb_ca_vc_verification_result (
    `template_id` varchar(18) not null comment '바우처 검증 완료된 템플릿 ID (eg. VCT+YYYY+MM+DD+000001)',
    `template_name` varchar(200) not null comment '바우처 검증 완료된 템플릿명',
    `template_type` varchar(100) not null comment '바우처 검증 완료된 템플릿 타입 CODE (eg. 캐시백형, 쿠폰형) G004',
    `usage` boolean not null comment '사용상태',
    `contract_id` bigint not null comment '컨트랙트 ID',
    `final_report_file_path` varchar(200) null comment '최종 검증 레포트 파일경로',
    `final_report_file_name` varchar(200) null comment '최종 검증 레포트 파일명',
    `company_id` varchar(18) not null comment '기관(회사) ID',
    `created_at` datetime not null comment '생성일',
    `created_by` int not null comment '생성자 ID',
    `updated_at` datetime not null comment '수정일',
    `updated_by` int not null comment '수정자 ID',
    primary key (`template_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.tb_ca_menu (
    `menu_id` varchar(18) not null comment '메뉴 ID (eg. MENU+000000001)',
    `menu_name` varchar(200) COLLATE utf8mb4_general_ci not null comment '메뉴명',
    `parent_menu_id` varchar(18) not null comment '부모 메뉴 ID (eg. MENU+000000001)',
    `depth` int not null comment '메뉴 깊이',
    `sort` int null comment '메뉴 정렬',
    `route` varchar(200) not null comment '메뉴 경로 (route 정보)',
    `usage` boolean not null comment '사용 상태',
    `note` varchar(2000) not null comment '비고',
    `created_at` datetime not null comment '생성일',
    `created_by` int not null comment '생성자 ID',
    `updated_at` datetime not null comment '수정일',
    `updated_by` int not null comment '수정자 ID',
    primary key (`menu_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.tb_ca_grant_menu (
    `id` bigint not null auto_increment comment '권한별 메뉴 맵핑 ID',
    `grant_id` varchar(18) not null comment '권한그룹 ID',
    `company_type` varchar(18) not null comment '기관타입 CODE - 그룹코드 G001',
    `menu_id` varchar(18) not null comment '메뉴 ID',
    `created_at` datetime not null comment '생성일',
    `created_by` int not null comment '생성자 ID',
    `updated_at` datetime not null comment '수정일',
    `updated_by` int not null comment '수정자 ID',
    primary key (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.tb_ca_grant (
    `grant_id` varchar(18) not null comment '권한그룹 ID = GR + 0001',
    `company_type` varchar(18) not null comment '기관타입 CODE - 그룹코드 G001',
    `grant_name` varchar(100) not null comment '권한그룹명',
    `usage` boolean not null comment '사용상태',
    `note` varchar(2000) null comment '비고',
    `created_at` datetime not null comment '생성일',
    `created_by` int not null comment '생성자 ID',
    `updated_at` datetime not null comment '수정일',
    `updated_by` int not null comment '수정자 ID',
    primary key (`grant_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.tb_ca_user (
    `user_id` int not null auto_increment comment '유저 ID SEQ',
    `email` varchar(200) not null comment '유저 EMAIL',
    `password` varchar(100) not null comment '유저 PASSWORD',
    `user_type` varchar(100) not null comment '유저 타입 CODE - G010',
    `phone` varchar(100) null comment '사무실 번호',
    `note` varchar(2000) null comment '비고',
    `is_activated` boolean not null comment '활성화 상태',
    `is_blocked` boolean not null comment '계정 정지 상태(패스워드/OTP 연속 실패 사례)',
    `key_admin` boolean null comment '유저 타입 코드가 있으면 굳이???',
    `company_id` varchar(18) not null comment '기관(회사) ID',
    `grant_id` varchar(18) not null comment '권한그룹 ID',
    `created_at` datetime not null comment '생성일',
    `created_by` int not null comment '생성자 ID',
    `updated_at` datetime not null comment '수정일',
    `updated_by` int not null comment '수정자 ID',
    primary key (`user_id`),
    unique key `unique_email` (`email`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.tb_ca_user_login_hist (
    `id` bigint not null auto_increment comment '로그인 이력 ID',
    `otp_number` varchar(100) null comment '메일 OTP 번호 (6자리)',
    `ip_address` varchar(100) not null comment '접속 IP 주소',
    `user_agent` varchar(1000) not null comment '접속 클라이언트 UserAgent 정보',
    `login_success` boolean not null default false comment '로그인 성공여부 (OTP 인증까지)',
    `login_count` int not null comment '로그인 카운트(5회)이면 is_activated = false 로 바꾼다. tb_ca_user 테이블에서 note 에 비활성화된 이유를 넣는다.',
    `otp_success` boolean not null default false comment '로그인 성공여부 (OTP 인증까지)',
    `otp_count` int not null default 0 comment 'otp 카운트(5회)이면 is_blocked = false 로 바꾼다. tb_ca_user 테이블에서 note 에 비활성화된 이유를 넣는다.',
    `user_id` int not null comment '유저 ID',
    `connected_at` datetime not null comment '접속일',
    primary key (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.tb_ca_user_token (
    `user_id` INT NOT NULL, 
    `refresh_token` VARCHAR(255) NOT NULL, 
    `issued_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, 
    `expires_at` DATETIME NOT NULL, 
    `status` ENUM('active', 'revoked') DEFAULT 'active', 
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP, 
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    PRIMARY KEY (`user_id`), 
    FOREIGN KEY (`user_id`) REFERENCES `tb_ca_user` (`user_id`) ON DELETE CASCADE 
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE INDEX idx_refresh_token ON `bok-cbdc-voucher`.tb_ca_user_token (`refresh_token`);

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.tb_ca_central_eoa_info (
    `wallet_id` bigint not null auto_increment comment '월렛 ID',
    `wallet_address` varchar(100) not null comment '월렛 주소 값',
    `hd_key` varchar(500) not null comment 'HD 월렛 키 ID',
    `hd_key_access_token` varchar(500) not null comment 'HD 월렛 키 Access Token',
    `usage_type` varchar(100) not null comment '월렛 사용 타입 CODE - G011',
    `usage` boolean not null comment '월렛 사용 여부',
    `company_id` varchar(100) not null comment '기관 ID',
    `created_at` datetime not null comment '생성일',
    `created_by` int not null comment '생성자 ID',
    `updated_at` datetime not null comment '수정일',
    `updated_by` int not null comment '수정자 ID',
    primary key (`wallet_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.tb_ca_company (
    `company_id` varchar(18) not null comment '기관(회사) ID (eg. COMP+000000001)',
    `company_name` varchar(100) not null comment '기관(회사)명',
    `company_type` varchar(18) not null comment '기관 타입 (관리기관, 참가기관)',
    `bank_code` varchar(100) not null comment '은행코드 3자리 CODE',
    `sort` int not null comment '정렬',
    `usage` boolean not null comment '사용상태',
    `note` varchar(2000) null comment '비고',
    `created_at` datetime not null comment '생성일',
    `created_by` int not null comment '생성자 ID',
    `updated_at` datetime not null comment '수정일',
    `updated_by` int not null comment '수정자 ID',
    primary key (`company_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.tb_ca_initl_factor (
    `factor_id` bigint not null auto_increment comment '바우처 배포 생성자 항목 ID',
    `factor_name` varchar(500) null comment '바우처 배포 생성자 항목명',
    `variable_name` varchar(200) null comment '바우처 배포 생성자 변수명',
    `data_type` varchar(100) not null comment 'Solidity 컨트랙트 데이터 타입 CODE',
    `data_example` varchar(500) null comment '바우처 배포 생성자 변수 예시 값',
    `contract_id` bigint not null comment '컨트랙트 ID',
    `created_at` datetime not null comment '생성일',
    `created_by` int not null comment '생성자 ID',
    `updated_at` datetime not null comment '수정일',
    `updated_by` int not null comment '수정자 ID',
    `desc` varchar(500) null comment '설명',
    PRIMARY KEY (`factor_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.tb_ca_code (
    `group_code` varchar(8) not null comment '그룹코드 G0001',
    `group_code_name` varchar(100) COLLATE utf8mb4_general_ci not null comment '그룹코드명',
    `code` varchar(18) not null comment '코드 C00000001',
    `code_name` varchar(100) COLLATE utf8mb4_general_ci null comment '코드명',
    `sort` int not null comment '정렬 순서',
    `usage` boolean not null comment '사용상태',
    `note` varchar(1000) null comment '비고',
    `created_at` datetime not null comment '생성일',
    `created_by` int not null comment '생성자 ID',
    `updated_at` datetime not null comment '수정일',
    `updated_by` int not null comment '수정자 ID',
    PRIMARY KEY (`group_code`, `code`) -- 인덱스 길이 제한 설정을 제거
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.contract_address_abi (
    contract_address varchar(100) not null,
    abi LONGTEXT null default null,
    PRIMARY KEY (`contract_address`) using btree
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

-- 향후 없애야 할 테이블 (Spring 백엔드 서버 현재 의존 테이블)
CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.TB_SYS_TITLE (
    title_cd varchar(100) not null comment '타이틀 코드' primary key,
    title_locale varchar(5) not null comment '타이틀 로케일',
    crtr_id varchar(18) not null comment '생성자 ID',
    creat_dt datetime not null comment '생성 일시',
    updr_id varchar(18) null comment '수정자ID',
    updt_dt datetime null comment '수정 일시',
    title_cn varchar(500) not null comment '타이틀 내용'
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.TB_SYS_ROLE_HIERARCHY (
    role_hierarchy_id varchar(18) not null comment '역할 계층 ID' primary key,
    crtr_id varchar(18) not null comment '생성자 ID',
    creat_dt datetime not null comment '생성 일시',
    updr_id varchar(18) null comment '수정자ID',
    updt_dt datetime null comment '수정 일시',
    parnts_role_cd varchar(100) not null comment '부모 역할 코드',
    chldrn_role_cd varchar(100) not null comment '자식 역할 코드',
    sort_ordr int not null comment '정렬 순서',
    unique (
        parnts_role_cd,
        chldrn_role_cd
    )
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.TB_SYS_AUTHOR (
    author_id varchar(18) not null comment '권한 ID' primary key,
    crtr_id varchar(18) not null comment '생성자 ID',
    creat_dt datetime not null comment '생성 일시',
    updr_id varchar(18) null comment '수정자ID',
    updt_dt datetime null comment '수정 일시',
    author_cd varchar(100) not null comment '권한 코드',
    author_nm varchar(1000) not null comment '권한 이름',
    author_dc varchar(4000) null comment '권한 설명',
    sort_ordr int not null comment '정렬 순서',
    use_yn char not null comment '사용 여부(1/0)',
    bass_author_yn char not null comment '기본 권한 여부(1/0) => 1: 수정/삭제 불가',
    user_author_yn char not null comment '사용자별 권한관리 여부(1/0) => 1: 사용자별 권한 맵핑',
    view_yn char null comment '화면단에 보여질필요가 있는 경우'
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.TB_SYS_RESRCE (
    resrce_id varchar(18) not null comment '리소스 ID' primary key,
    crtr_id varchar(18) not null comment '생성자 ID',
    creat_dt datetime not null comment '생성 일시',
    updr_id varchar(18) null comment '수정자ID',
    updt_dt datetime null comment '수정 일시',
    resrce_ty varchar(20) not null comment '리소스 유형',
    resrce_pttrn varchar(200) not null comment '리소스 패턴',
    sort_ordr int null comment '정렬 순서',
    use_yn char not null comment '사용 여부(1/0)'
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.TB_SYS_RESRCE_AUTHOR (
    resrce_id varchar(18) not null comment '리소스 ID',
    author_id varchar(18) not null comment '권한 ID',
    crtr_id varchar(18) not null comment '생성자 ID',
    creat_dt datetime not null comment '생성 일시',
    updr_id varchar(18) null comment '수정자 ID',
    updt_dt datetime null comment '수정 일시',
    primary key (resrce_id, author_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.TB_SYS_MENU_AUTHOR (
    menu_id varchar(18) not null comment '메뉴 ID',
    author_id varchar(18) not null comment '권한 ID',
    crtr_id varchar(18) not null comment '생성 사용자 ID',
    creat_dt datetime not null comment '생성 일시',
    updr_id varchar(18) null comment '수정 사용자 ID',
    updt_dt datetime null comment '수정 일시',
    primary key (menu_id, author_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.TB_SYS_CODE_GROUP (
    cd_group_id varchar(18) not null comment '코드 그룹 ID' primary key,
    cd_group varchar(200) null comment '코드 그룹',
    cd_group_nm varchar(500) null comment '코드 그룹 이름',
    cd_group_dc varchar(2000) null comment '코드 그룹 설명',
    use_yn char null comment '사용 여부(1/0)',
    crtr_id varchar(18) null comment '생성자 ID',
    creat_dt datetime null comment '생성 일시',
    updr_id varchar(18) null comment '수정자ID',
    updt_dt datetime null comment '수정 일시'
);

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.TB_SYS_CODE_VALUE (
    cd_value_id varchar(18) not null comment '코드 값 ID' primary key,
    cd_group_id varchar(18) null comment '코드 그룹 ID',
    cd_value varchar(100) null comment '코드 값',
    cd_value_nm varchar(1000) null comment '코드 값 이름',
    cd_value_dc varchar(2000) null comment '코드 값 설명',
    sort_ordr int null comment '정렬 순서',
    use_yn char null comment '사용 여부(1/0)',
    atrb_1 varchar(1000) null comment '속성 1',
    atrb_2 varchar(1000) null,
    atrb_3 varchar(1000) null,
    atrb_4 varchar(1000) null,
    atrb_5 varchar(1000) null,
    crtr_id varchar(18) null comment '생성자 ID',
    creat_dt datetime null comment '생성 일시',
    updr_id varchar(18) null comment '수정자ID',
    updt_dt datetime null comment '수정 일시'
);

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.TB_SYS_UID (
    UID_VALUE varchar(18) not null comment 'UID 값' primary key,
    CRTR_ID varchar(18) not null comment '생성자 ID',
    CREAT_DT datetime not null comment '생성 일시',
    UPDR_ID varchar(18) null comment '수정자ID',
    UPDT_DT datetime null comment '수정 일시',
    UID_SE varchar(100) not null comment 'UID 구분 => 테이블명 또는 구분값'
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.TB_SYS_LOG (
    LOG_ID varchar(18) not null comment '로그 ID' primary key,
    USER_ID varchar(18) not null comment '사용자 ID',
    LOG_DT datetime not null comment '로그 일시',
    SERVER_IP varchar(15) not null comment '서버 아이피',
    REQUST_IP varchar(15) null comment '요청 아이피',
    REQUST_TY varchar(20) null comment '요청 유형 => ACTION, AJAX, URL_CONNECTION',
    REQUST_HOST varchar(200) null comment '요청 호스트',
    REQUST_PATH varchar(2000) null comment '요청 경로',
    REQUST_HDER varchar(4000) null comment '요청 헤더',
    REQUST_PARAMTR longtext null comment '요청 파라미터',
    REQUST_BODY longtext null comment '요청 BODY',
    RSPNS_STTUS_CD int null comment '응답 상태 코드',
    SUCCES_YN char null comment '성공 여부(Y/N)',
    REQUST_MTHD varchar(10) null comment '요청 방식',
    RESPONSE_BODY longtext null
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `bok-cbdc-voucher`.TB_SYS_MENU (
    MENU_ID varchar(18) not null comment '메뉴 ID' primary key,
    CRTR_ID varchar(18) not null comment '생성 사용자 ID',
    CREAT_DT datetime not null comment '생성 일시',
    UPDR_ID varchar(18) null comment '수정 사용자 ID',
    UPDT_DT datetime null comment '수정 일시',
    MENU_KND varchar(10) not null comment '메뉴 종류',
    UPPER_MENU_ID varchar(18) null comment '상위 메뉴 ID',
    MENU_LEVEL int not null comment '메뉴 레벨',
    MENU_NM varchar(500) not null comment '메뉴 이름',
    MENU_ORDR int not null comment '메뉴 순서',
    MENU_PATH varchar(1000) null comment '메뉴 경로',
    USE_YN char not null comment '사용 여부(1/0)',
    MENU_DC varchar(4000) null comment '메뉴 설명'
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;
```
          * 02-func-all.sql
```plain text
DELIMITER $$

create  DEFINER='root'@'%' function  `bok-cbdc-voucher`.FN_UID(
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

END$$

DELIMITER ;

DELIMITER $$

CREATE FUNCTION GET_CODE_NM(code_input VARCHAR(18))
RETURNS VARCHAR(100)
READS SQL DATA
BEGIN
    DECLARE code_name_result VARCHAR(100);

    SELECT code_name INTO code_name_result
    FROM `bok-cbdc-voucher`.tb_ca_code
    WHERE code = code_input;

    RETURN code_name_result;
END$$

DELIMITER ;

DELIMITER $$

CREATE FUNCTION GENERATE_ID(prefix VARCHAR(5))
RETURNS VARCHAR(18)
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
END$$

DELIMITER ;

DELIMITER $$

CREATE FUNCTION GET_USER_EMAIL(p_user_id INT)
    RETURNS VARCHAR(255)
    DETERMINISTIC
BEGIN
    DECLARE v_email VARCHAR(255);

    -- user_id로 email 가져오는 쿼리
    SELECT email
    INTO v_email
    FROM tb_ca_user
    WHERE user_id = p_user_id
    LIMIT 1;

    -- email 반환
    RETURN v_email;
END$$

DELIMITER ;
```
          * 03-init-data.sql
```sql
-- 코드 값 기초 데이터 셋팅 부분

-- 기초 코드 값 셋팅
INSERT INTO `bok-cbdc-voucher`.tb_ca_code (
    `group_code`, `group_code_name`, `code`, `code_name`, `sort`, `usage`, `note`, `created_at`, `created_by`, `updated_at`, `updated_by`
) VALUES
('G001', '기관 분류', 'C0010001', '관리기관', 1, TRUE, '', NOW(), 1, NOW(), 1),
('G001', '기관 분류', 'C0010002', '참가기관', 2, TRUE, '', NOW(), 1, NOW(), 1),
('G001', '기관 분류', 'C0010003', '검증기관', 3, TRUE, '', NOW(), 1, NOW(), 1),
('G002', '템플릿 검증 단계', 'C0020001', '검증 의뢰', 1, TRUE, '', NOW(), 1, NOW(), 1),
('G002', '템플릿 검증 단계', 'C0020002', '검증 수행', 2, TRUE, '', NOW(), 1, NOW(), 1),
('G002', '템플릿 검증 단계', 'C0020003', '검증 개선', 3, TRUE, '', NOW(), 1, NOW(), 1),
('G002', '템플릿 검증 단계', 'C0020004', '검증 완료', 4, TRUE, '', NOW(), 1, NOW(), 1),
('G003', '템플릿 검증 상태', 'C0030001', '검증 신청', 1, TRUE, '', NOW(), 1, NOW(), 1),
('G003', '템플릿 검증 상태', 'C0030002', '자동 검증 수행', 2, TRUE, '', NOW(), 1, NOW(), 1),
('G003', '템플릿 검증 상태', 'C0030003', '자동 검증 완료', 3, TRUE, '', NOW(), 1, NOW(), 1),
('G003', '템플릿 검증 상태', 'C0030004', '전문가 평가 수행', 4, TRUE, '', NOW(), 1, NOW(), 1),
('G003', '템플릿 검증 상태', 'C0030005', '전문가 평가 완료', 5, TRUE, '', NOW(), 1, NOW(), 1),
('G003', '템플릿 검증 상태', 'C0030006', '개선조치 요청', 6, TRUE, '', NOW(), 1, NOW(), 1),
('G003', '템플릿 검증 상태', 'C0030007', '검증 승인', 7, TRUE, '', NOW(), 1, NOW(), 1),
('G003', '템플릿 검증 상태', 'C0030008', '검증 반려', 8, TRUE, '', NOW(), 1, NOW(), 1),
('G004', '바우처 유형', 'C0040001', '캐시백형-정액', 1, TRUE, '', NOW(), 1, NOW(), 1),
('G004', '바우처 유형', 'C0040002', '캐시백형-정률', 2, TRUE, '', NOW(), 1, NOW(), 1),
('G004', '바우처 유형', 'C0040003', '보조금형-정액', 3, TRUE, '', NOW(), 1, NOW(), 1),
('G005', '자동 검증기 타입', 'C0050001', 'static-analysis', 1, TRUE, '', NOW(), 1, NOW(), 1),
('G005', '자동 검증기 타입', 'C0050002', 'dynamic-analysis', 2, TRUE, '', NOW(), 1, NOW(), 1),
('G006', '자동 분석 수행 상태', 'C0060001', 'PENDING', 1, TRUE, '', NOW(), 1, NOW(), 1),
('G006', '자동 분석 수행 상태', 'C0060002', 'RUNNING', 2, TRUE, '', NOW(), 1, NOW(), 1),
('G006', '자동 분석 수행 상태', 'C0060003', 'ERROR', 3, TRUE, '', NOW(), 1, NOW(), 1),
('G006', '자동 분석 수행 상태', 'C0060004', 'SUCCESS', 4, TRUE, '', NOW(), 1, NOW(), 1),
('G007', '컨트랙트 변수 데이터 타입', 'C0070001', 'string', 1, TRUE, '', NOW(), 1, NOW(), 1),
('G007', '컨트랙트 변수 데이터 타입', 'C0070002', 'uint', 2, TRUE, '', NOW(), 1, NOW(), 1),
('G007', '컨트랙트 변수 데이터 타입', 'C0070003', 'address', 3, TRUE, '', NOW(), 1, NOW(), 1),
('G007', '컨트랙트 변수 데이터 타입', 'C0070004', 'int', 4, TRUE, '', NOW(), 1, NOW(), 1),
('G008', '의뢰기관', 'C0080001', '서울시', 1, TRUE, '', NOW(), 1, NOW(), 1),
('G008', '의뢰기관', 'C0080002', '부산시', 2, TRUE, '', NOW(), 1, NOW(), 1),
('G009', '바우처 배포 상태', 'C0090001', '배포 신청', 1, TRUE, '', NOW(), 1, NOW(), 1),
('G009', '바우처 배포 상태', 'C0090002', '배포 승인', 2, TRUE, '', NOW(), 1, NOW(), 1),
('G009', '바우처 배포 상태', 'C0090003', '배포 반려', 3, TRUE, '', NOW(), 1, NOW(), 1),
('G009', '바우처 배포 상태', 'C0090004', '배포 완료', 4, TRUE, '', NOW(), 1, NOW(), 1),
('G010', '유저 타입', 'C0100001', '관리자', 1, TRUE, '', NOW(), 1, NOW(), 1),
('G010', '유저 타입', 'C0100002', '일반', 2, TRUE, '', NOW(), 1, NOW(), 1),
('G011', '지갑 유형', 'C0110001', '배포 키 생성 지갑', 1, TRUE, '', NOW(), 1, NOW(), 1),
('G011', '지갑 유형', 'C0110002', '권한 EOA 등록 지갑', 2, TRUE, '', NOW(), 1, NOW(), 1),
('G012', '은행코드', '001', '한국은행', 1, TRUE, '', NOW(), 1, NOW(), 1),
('G012', '은행코드', '002', '산업은행', 2, TRUE, '', NOW(), 1, NOW(), 1),
('G012', '은행코드', '003', '기업은행', 3, TRUE, '', NOW(), 1, NOW(), 1),
('G012', '은행코드', '004', '국민은행', 4, TRUE, '', NOW(), 1, NOW(), 1),
('G012', '은행코드', '011', '농협은행', 5, TRUE, '', NOW(), 1, NOW(), 1),
('G012', '은행코드', '020', '우리은행', 6, TRUE, '', NOW(), 1, NOW(), 1),
('G012', '은행코드', '027', '한국씨티은행', 7, TRUE, '', NOW(), 1, NOW(), 1),
('G012', '은행코드', '031', '대구은행', 8, TRUE, '', NOW(), 1, NOW(), 1),
('G012', '은행코드', '032', '부산은행', 9, TRUE, '', NOW(), 1, NOW(), 1),
('G012', '은행코드', '081', '하나은행', 10, TRUE, '', NOW(), 1, NOW(), 1),
('G012', '은행코드', '088', '신한은행', 11, TRUE, '', NOW(), 1, NOW(), 1),
('G012', '은행코드', '089', '케이뱅크', 12, TRUE, '', NOW(), 1, NOW(), 1),
('G012', '은행코드', '090', '카카오뱅크', 13, TRUE, '', NOW(), 1, NOW(), 1),
('G012', '은행코드', '092', '토스뱅크', 14, TRUE, '', NOW(), 1, NOW(), 1),
('G012', '은행코드', '099', '금융결제원', 15, TRUE, '', NOW(), 1, NOW(), 1),
('G012', '은행코드', '901', 'A은행', 16, TRUE, '', NOW(), 1, NOW(), 1),
('G012', '은행코드', '902', 'B은행', 17, TRUE, '', NOW(), 1, NOW(), 1);

-- 메뉴 코드 값 셋팅
INSERT INTO `bok-cbdc-voucher`.tb_ca_menu (
     `menu_id`, `menu_name`, `parent_menu_id`, `depth`, `sort`, `route`, `usage`, `note`, `created_at`, `created_by`, `updated_at`, `updated_by`
) VALUES
('M00001', '대시보드', 'M00001', 1, 0, '/regulator', TRUE, '관리기관용', NOW(), 1, NOW(), 1),
('M00002', '관리기관 기능', 'M00002', 1, 1, '', TRUE, '', NOW(), 1, NOW(), 1),
('M00003', '템플릿 검증 관리', 'M00002', 2, 101, '/regulator/manage/templates', TRUE, '', NOW(), 1, NOW(), 1),
('M00004', '바우처 승인 관리', 'M00002', 2, 102, '/regulator/manage/vouchers', TRUE, '', NOW(), 1, NOW(), 1),
('M00005', '참가기관 현황', 'M00005', 1, 2, '', TRUE, '', NOW(), 1, NOW(), 1),
('M00006', '검증된 템플릿 목록', 'M00005', 2, 201, '/regulator/dashboard/standard-templates', TRUE, '', NOW(), 1, NOW(), 1),
('M00007', '템플릿 검증 현황', 'M00005', 2, 202, '/regulator/dashboard/templates', TRUE, '', NOW(), 1, NOW(), 1),
('M00008', '승인된 바우처 목록', 'M00005', 2, 203, '/regulator/dashboard/approved-vouchers', TRUE, '', NOW(), 1, NOW(), 1),
('M00009', '배포된 바우처 목록', 'M00005', 2, 204, '/regulator/dashboard/deployed-vouchers', TRUE, '', NOW(), 1, NOW(), 1),
('M00010', '바우처 승인 현황', 'M00005', 2, 205, '/regulator/dashboard/vouchers', TRUE, '', NOW(), 1, NOW(), 1),
('M00011', '바우처 오라클', 'M00011', 1, 3, '', TRUE, '', NOW(), 1, NOW(), 1),
('M00012', '오라클 등록', 'M00011', 2, 301, '/regulator/oracle/registration', TRUE, '', NOW(), 1, NOW(), 1),
('M00013', '오라클 관리', 'M00011', 2, 302, '/regulator/oracle/management', TRUE, '', NOW(), 1, NOW(), 1),
('M00014', '바우처 배포주소', 'M00014', 1, 4, '', TRUE, '', NOW(), 1, NOW(), 1),
('M00015', '배포주소 등록(배포)', 'M00014', 2, 401, '/regulator/deploy-address/registration', TRUE, '', NOW(), 1, NOW(), 1),
('M00016', '배포주소 관리', 'M00014', 2, 402, '/regulator/deploy-address/management', TRUE, '', NOW(), 1, NOW(), 1),
('M00017', '시스템', 'M00017', 1, 5, '', TRUE, '', NOW(), 1, NOW(), 1),
('M00018', '참가기관 권한용 EOA 목록', 'M00017', 2, 501, '/regulator/system/permission-eoa', TRUE, '', NOW(), 1, NOW(), 1),
('M00019', '참가기관 배포용 EOA 목록', 'M00017', 2, 502, '/regulator/system/deploy-eoa', TRUE, '', NOW(), 1, NOW(), 1),
('M00020', '계정 로그인 이력', 'M00017', 2, 503, '/regulator/system/logs', TRUE, '', NOW(), 1, NOW(), 1),
('M00021', '기관 관리', 'M00017', 2, 504, '/regulator/system/grants', TRUE, '', NOW(), 1, NOW(), 1),
('M00022', '대시보드', 'M00022', 1, 6, '/participants', TRUE, '참가기관용', NOW(), 1, NOW(), 1),
('M00023', '바우처', 'M00023', 1, 7, '', TRUE, '', NOW(), 1, NOW(), 1),
('M00024', '생성', 'M00023', 2, 701, '/participants/voucher/issue', TRUE, '', NOW(), 1, NOW(), 1),
('M00025', '배포 승인 현황', 'M00023', 2, 702, '/participants/voucher/dashboard', TRUE, '', NOW(), 1, NOW(), 1),
('M00026', '배포된 바우처 목록', 'M00023', 2, 703, '/participants/voucher/deployed', TRUE, '', NOW(), 1, NOW(), 1),
('M00027', '템플릿', 'M00027', 1, 8, '', TRUE, '', NOW(), 1, NOW(), 1),
('M00028', '신규 템플릿 생성', 'M00027', 2, 801, '/participants/templates/issue', TRUE, '', NOW(), 1, NOW(), 1),
('M00029', '템플릿 검증 현황', 'M00027', 2, 802, '/participants/templates/dashboard', TRUE, '', NOW(), 1, NOW(), 1),
('M00030', '검증된 템플릿 목록', 'M00027', 2, 803, '/participants/templates/standards', TRUE, '', NOW(), 1, NOW(), 1);
```
          * 이후 데이터 필요할 때마다 생성 스크립트 작성
    * **Define Entities, Repositories, and Services(JPA):**
      * Entity
```java
import jakarta.persistence.*;

@Entity
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, unique = true)
    private String email;

    // Getters and Setters
}
```
      * Repository
```java
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserRepository extends JpaRepository<User, Long> {
    // Custom query methods if necessary
}
```
      * Service
```java
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class UserService {
    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public List<User> getAllUsers() {
        return userRepository.findAll();
    }

    public User saveUser(User user) {
        return userRepository.save(user);
    }
}
```
    * **Create REST Controllers:**
    * **Run the Application:**
```shell
./gradlew bootRun
```
    * **Appendix**
      * Manual Configuration class 예
        * Data source configuration(HikariCP)
```java
package com.example.config;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import javax.sql.DataSource;

@Configuration
public class DataSourceConfig {

    @Bean
    public DataSource dataSource() {
        HikariConfig hikariConfig = new HikariConfig();
        hikariConfig.setJdbcUrl("jdbc:mysql://localhost:3306/your_database_name");
        hikariConfig.setUsername("your_username");
        hikariConfig.setPassword("your_password");
        hikariConfig.setDriverClassName("com.mysql.cj.jdbc.Driver");
        hikariConfig.setMaximumPoolSize(10);
        hikariConfig.setMinimumIdle(5);

        return new HikariDataSource(hikariConfig);
    }
}
```
        * MyBatis confiuration
```java
package com.example.config;

import org.apache.ibatis.session.SqlSessionFactory;
import org.mybatis.spring.SqlSessionFactoryBean;
import org.mybatis.spring.annotation.MapperScan;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;

import javax.sql.DataSource;

@Configuration
@MapperScan("com.example.mapper")  // Specify the package where mappers are located
public class MyBatisConfig {

    @Bean
    public SqlSessionFactory sqlSessionFactory(DataSource dataSource) throws Exception {
        SqlSessionFactoryBean sessionFactory = new SqlSessionFactoryBean();
        sessionFactory.setDataSource(dataSource);
        sessionFactory.setMapperLocations(
            new PathMatchingResourcePatternResolver().getResources("classpath:mappers/*.xml")
        );
        return sessionFactory.getObject();
    }
}
```
        * Transaction management configuration
```java
package com.example.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.transaction.annotation.EnableTransactionManagement;

@Configuration
@EnableTransactionManagement
public class TransactionConfig {
    // Any custom transaction management settings can go here
}
```
        * MyBatis Properties Configuration (Optional):
          * application.properties
```plain text
spring.mybatis.configuration.map-underscore-to-camel-case=true
spring.mybatis.configuration.cache-enabled=false
```
          * configuration class
```java
package com.example.config;

import org.apache.ibatis.session.Configuration;
import org.mybatis.spring.boot.autoconfigure.ConfigurationCustomizer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class MyBatisCustomConfig {

    @Bean
    public ConfigurationCustomizer configurationCustomizer() {
        return new ConfigurationCustomizer() {
            @Override
            public void customize(Configuration configuration) {
                configuration.setMapUnderscoreToCamelCase(true);
            }
        };
    }
}
```
        * Setting Up Logging and Monitoring (Optional):
          * application.properties
```plain text
logging.level.com.zaxxer.hikari=DEBUG
```
        * Directory structure
```plain text
src/main/java/com/example
    ├── config
    │   ├── DataSourceConfig.java
    │   ├── MyBatisConfig.java
    │   └── TransactionConfig.java
    ├── mapper
    │   └── UserMapper.java
    ├── model
    │   └── User.java
    ├── service
    │   └── UserService.java
    └── controller
        └── UserController.java
```
      * 디지털 바우처 Manual Configuration 설명
        * ### **Classes Overview and Responsibilities:**
          * **DatabaseProperties**:
            * Holds HikariCP and JNDI configuration.
            * Centralizes database properties like JNDI or Hikari configurations.
          * **DataSourceAnalysisConfig**:
            * Configures a data source specifically for the **"analysis"** use case.
            * Sets up a SqlSessionFactory and SqlSessionTemplate for the analysis data source.
            * Defines MyBatis settings, mappers, interceptors, and type handlers for the "analysis" database.
          * **DataSourceAspect**:
            * An AOP aspect that dynamically switches the data source based on the annotation @UseDataSource.
            * Decides which data source to use for a specific method or class using AOP.
          * **DataSourceMainConfig**:
            * Configures the main data source.
            * Uses routing for dynamic data sources between main and mirror databases.
            * Defines multiple beans: data sources, transaction managers, and SqlSessionTemplate for the **"main"** data source.
          * **DynamicDataSource**:
            * Extends MyBatisDynamicDataSource and creates a custom implementation for handling dynamic data sources.
            * It’s responsible for creating and closing data sources.
          * **RoutingDataSourceMain**:
            * Extends Spring’s AbstractRoutingDataSource to dynamically choose between data sources (main, mirror).
            * Uses a ThreadLocal variable to determine which data source should be used at runtime.
          * **UseDataSource**:
            * A custom annotation that allows you to specify which data source (e.g., main or mirror) should be used for a particular method or class.
        * ### **Relationships and Flow of Control:**
          * **DatabaseProperties**: Acts as a configuration holder that is referenced by both DataSourceMainConfig and DataSourceAnalysisConfig. It provides the necessary properties for each data source (either main, mirror, or analysis).
          * **DataSourceMainConfig**:
            * Configures both the **main** and **mirror** data sources.
            * The **routingDataSource** bean in this class uses RoutingDataSourceMain, which dynamically switches between main and mirror data sources.
            * Defines transaction management, SqlSessionFactory, and SqlSessionTemplate for **main** data source operations.
          * **RoutingDataSourceMain**: Works with DataSourceMainConfig and provides a mechanism to dynamically switch between **main** and **mirror** data sources using a ThreadLocal variable. This allows for runtime data source switching depending on the context.
          * **DataSourceAspect**:
            * Adds AOP-based dynamic data source switching. When a method annotated with @UseDataSource is called, this aspect intercepts the call and dynamically sets the current data source (e.g., main or mirror) using RoutingDataSourceMain.
          * **DynamicDataSource**:
            * It extends MyBatisDynamicDataSource and is used in DataSourceAnalysisConfig to define a custom dynamic data source for the **"analysis"** purpose.
            * It provides more specific data source creation logic for analysis-related database operations.
          * **DataSourceAnalysisConfig**:
            * Configures the **"analysis"** data source separately from the main one.
            * Uses a DynamicDataSource for the **"analysis"** environment and configures a custom SqlSessionFactory and SqlSessionTemplate.
          * **UseDataSource**:
            * This annotation is used to explicitly tell the system which data source (main or mirror) should be used by applying it to methods or classes. It works in conjunction with DataSourceAspect and RoutingDataSourceMain.
        * **Textual Diagram of Class Relationships:**
```plain text
                            +-------------------+
                            |   DatabaseProperties |
                            +-------------------+
                                       |
           -----------------------------------------------------
          |                                                   |
+--------------------------+                       +----------------------------+
|    DataSourceMainConfig   |                       |  DataSourceAnalysisConfig  |
+--------------------------+                       +----------------------------+
| - Configures main &       |                       | - Configures "analysis"    |
|   mirror datasources      |                       |   data source              |
| - Uses DatabaseProperties |                       | - Uses DynamicDataSource   |
+--------------------------+                       +----------------------------+
         |                                                       |
+-------------------------------+                  +-------------------------------+
|      RoutingDataSourceMain     |                  |     DynamicDataSource         |
+-------------------------------+                  +-------------------------------+
| - Chooses between main & mirror|                  | - Creates data sources for    |
|   datasources dynamically      |                  |   "analysis" DB               |
+-------------------------------+                  +-------------------------------+
                 |
        +-----------------+
        |  @UseDataSource  |
        +-----------------+
                 |
        +---------------------+
        |  DataSourceAspect    |
        +---------------------+
        | - Switches data source|
        |   dynamically using   |
        |   AOP and ThreadLocal |
        +---------------------+

```
        * ### **Flow of Operations**:
          * **Data Source Setup**:
            * DataSourceMainConfig defines two data sources: **main** and **mirror**.
            * It uses RoutingDataSourceMain to dynamically switch between them.
            * DatabaseProperties provides configurations (e.g., HikariCP, JNDI) for these data sources.
          * **Dynamic Data Source Switching**:
            * The **RoutingDataSourceMain** class manages which data source to use (e.g., main or mirror) based on the current thread.
            * The @UseDataSource annotation, when applied to a method or class, triggers **DataSourceAspect**, which dynamically sets the current data source for the execution context.
          * **Analysis Data Source**:
            * DataSourceAnalysisConfig configures a completely separate data source for analysis-related operations.
            * This uses a custom DynamicDataSource, not relying on the RoutingDataSourceMain switching mechanism.
          * **MyBatis Configuration**:
            * Both DataSourceMainConfig and DataSourceAnalysisConfig configure MyBatis settings (e.g., SqlSessionFactory, SqlSessionTemplate) for their respective data sources, including MyBatis-specific properties like interceptors, type handlers, etc.
        * ### Conclusion:
          * This structure allows you to handle **multiple data sources** dynamically and **switch between them** using annotations and AOP. It also supports MyBatis configurations tailored to each data source, with various customizations such as interceptors and type handlers.
      * Configuration classes가 제대로 올라가기 위해서 @SpringBootApplication이 붙은 클래스가 있어야 한다.
        * 예
```java
package kr.or.cbdc;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class CbdcApplication {
    public static void main(String[] args) {
        SpringApplication.run(CbdcApplication.class, args);
    }
}
```
        * 디지털 바우처 시작 클래스
          * Application.java
```java
package kr.or.cbdc;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

import javax.sql.DataSource;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;
import org.springframework.context.annotation.EnableAspectJAutoProxy;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;

import kr.or.bok.wallet.sdk.WalletSDKInitializer;
import kr.or.cbdc.config.EnvConstants;
import kr.or.cbdc.infrastructure.kafka.KafkaMessageConsumerThread;

@SpringBootApplication(exclude = {DataSourceAutoConfiguration.class})
@EnableAspectJAutoProxy(proxyTargetClass = true)
public class Application {

	private static final Logger logger = LoggerFactory.getLogger(Application.class);

	public static void main(String[] args) {
		try {
			DataSource dataSource = createDataSource();
			WalletSDKInitializer.initialize(dataSource);

			KafkaMessageConsumerThread.startKafkaConsumerThread();
		} catch (Exception e) {
			logger.error(e.getMessage());
			return;
		}

		SpringApplication.run(Application.class, args);
	}

	private static DataSource createDataSource() throws IOException {
		String walletSdkPropertiesFileName = EnvConstants.APPLICATION_PROPERTIES;
		InputStream input = WalletSDKInitializer.class.getClassLoader()
			.getResourceAsStream(walletSdkPropertiesFileName);

		Properties properties = new Properties();
		properties.load(input);
		String mysqlJdbcUrl = properties.getProperty("mysql.jdbc.url");
		String mysqlUsername = properties.getProperty("mysql.username");
		String mysqlPassword = properties.getProperty("mysql.password");

		logger.debug("App properties: {}, {}, {}", mysqlJdbcUrl, mysqlUsername, mysqlPassword);

		HikariConfig config = new HikariConfig();
		config.setJdbcUrl(mysqlJdbcUrl);
		config.setUsername(mysqlUsername);
		config.setPassword(mysqlPassword);
		config.setMaximumPoolSize(100);
		config.setMinimumIdle(10);
		config.addDataSourceProperty("cachePrepStmts", "true");
		config.addDataSourceProperty("prepStmtCacheSize", "250");
		config.addDataSourceProperty("prepStmtCacheSqlLimit", "2048");
		return new HikariDataSource(config);
	}

}
```
          * **Check Component Scanning Scope (If Needed)**:
```plain text
@SpringBootApplication(scanBasePackages = "kr.or.cbdc")
```
          * **Manual Bean Registration (Optional)**:
```java
import kr.or.cbdc.config.datasources.DataSourceMainConfig;
import kr.or.cbdc.config.datasources.DataSourceAnalysisConfig;

@SpringBootApplication
@Import({DataSourceMainConfig.class, DataSourceAnalysisConfig.class})
public class CbdcApplication {
    // Main method
}
```
          * **Ensure the YAML/Properties Files Are Configured Correctly**:
```yaml
config:
  datasources:
    main:
      hikari:
        jdbc-url: jdbc:mysql://localhost:3306/main_db
        username: your_main_db_username
        password: your_main_db_password
        driver-class-name: com.mysql.cj.jdbc.Driver
      transaction:
        timeout: 30s
    mirror:
      hikari:
        jdbc-url: jdbc:mysql://localhost:3306/mirror_db
        username: your_mirror_db_username
        password: your_mirror_db_password
        driver-class-name: com.mysql.cj.jdbc.Driver
    analysis:
      hikari:
        jdbc-url: jdbc:mysql://localhost:3306/analysis_db
        username: your_analysis_db_username
        password: your_analysis_db_password
        driver-class-name: com.mysql.cj.jdbc.Driver
```
        * container용 WAR 생성
          * Application.java와 같은 디렉토리에 initializer 클래스를 두었다.
          * ServletInitializer.java
```java
package kr.or.cbdc;

import org.springframework.boot.builder.SpringApplicationBuilder;
import org.springframework.boot.web.servlet.support.SpringBootServletInitializer;
import org.springframework.web.WebApplicationInitializer;

public class ServletInitializer extends SpringBootServletInitializer implements WebApplicationInitializer {

    @Override
    protected SpringApplicationBuilder configure(SpringApplicationBuilder application) {
        return application.sources(Application.class);
    }

} 
```
          * ### 1. **ServletInitializer Purpose**:
            * Normally, Spring Boot applications are packaged as standalone JAR files that include an embedded servlet container (like Tomcat or Jetty). You can run them with java -jar yourapp.jar.
            * However, if you want to deploy your Spring Boot application as a **WAR file** to a traditional servlet container (like Tomcat or Jetty running **separately**), the ServletInitializer class is necessary.
            * ServletInitializer extends SpringBootServletInitializer to configure the application when it is launched by the servlet container. This class overrides the configure() method to specify the source of the Spring application (Application.class).
          * ### 2. **How It Works**:
            * ServletInitializer ensures that the Spring Boot application can start in a servlet environment by hooking into the servlet container lifecycle.
            * When deploying a WAR file, the servlet container calls this class to initialize the Spring application and pass the configuration to SpringApplicationBuilder.
          * ### 3. **When Do You Need It?**:
            * **You need ServletInitializer when you want to deploy your Spring Boot application as a WAR file** to a traditional servlet container.
            * If you’re running your application as a standalone JAR (with an embedded Tomcat), you don’t need this class, and you can package it as a JAR without any issues.
          * ### Summary:
            * **Application.java** is used for running the Spring Boot application as a standalone JAR file.
            * **ServletInitializer.java** is needed to deploy the application as a WAR file to a traditional servlet container (e.g., Tomcat running separately). It initializes the Spring Boot application when the servlet container starts.
  * # MDC(Mapped Diagnostic Context)
    * multi-thread 환경에서 thread별 로그 추적 시 필요.
    * A **logging mechanism** used in logging framework like Log4j, Slf4j, and Logbak.
    * Stores information in a **per-thread context** --> user ID, session ID, transaction ID that are relevant to a **specific thread** of execution
  * # AI
    * 자동 구성(AutoConfiguration) ^lvTvzFuJf
      * mindmap
        * ![[100. media/image/D8PjS_I4Tq.png]]
      * 작동
        * Spring AI start(org.springframework.ai:spring-ai-starter-model-anthropic) 추가하면 작동
      * [작동 전제 조건](https://docs.spring.io/spring-ai/reference/api/chatmodel.html)
        * application.yaml for Anthropic
```yaml
spring:
  application:
    name: mcp1
  ai:
    anthropic:
      api-key: sk-ant-api03-...
      chat:
        options:
          model: claude-3-5-sonnet-20241022
          temperature: 0.7
          max-tokens: 1000
```
      * 생성되는 주요 구성 요소
        * ChatModel 구현체
          * AnthropicChatModel
          * OpenAiChatModel Bean
        * ChatClient.Builder(prototype Bean)
          * ChatModel을 감싸는 wrapper
          * 사용하려면 반드시 .build()로 객체를 생성해서 사용해야 한다.
      * 계층 구조 이해
        * ChatModel
          * 기반 계층. 하위 추상화. ChaClient보다 먼저 생성
          * AI model API와 직접 통신.
        * ChatClient
          * ChatModel 위에 구축된 Fluent API
            * WebClient가 HTTP 요청을 처리할 수 있는 인터페이스 제공하는 것과 비슷.
          * 프롬프트 템플릿, RAG 어드바이저, 대화 메모리, 구조화된 출력 등 개발 용이하게 하는 API 포함.
      * AI 모델을 하나만 쓸 때, 자동 구성을 이용한 코드

```java
@RestController
@RequestMapping("/api/chatbot")
public class ChatbotController {
    private final ChatClient chatClient;
    
    // Spring injects the autoconfigured ChatClient.Builder
    public ChatbotController(ChatClient.Builder chatClientBuilder) {
        // Build the ChatClient with custom system message
        this.chatClient = chatClientBuilder
            .defaultSystem("You are a helpful assistant specialized in Spring Boot.")
            .build();
    }
    
    @PostMapping("/ask")
    public ChatResponse askQuestion(@RequestBody ChatRequest request) {
        var response = chatClient.prompt()
                .user(request.question())
                .call()
                .chatResponse();
        
        return new ChatResponse(
            response.getResult().getOutput().getContent(),
            response.getMetadata().getUsage().getTotalTokens()
        );
    }
    
    @GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> streamResponse(@RequestParam String question) {
        return chatClient.prompt()
                .user(question)
                .stream()
                .content();
    }
}

record ChatRequest(String question) {}
record ChatResponse(String answer, Long tokensUsed) {}
```
      * 서비스 컴포넌트 만들 때 단일 모델 코딩, 복수 AI 모델 코딩 비교
        * 단일 모델
```java
@Component
public class AutoconfiguredChatService {
    private final ChatClient chatClient;
    
    // This constructor receives the autoconfigured builder
    public AutoconfiguredChatService(ChatClient.Builder builder) {
        this.chatClient = builder.build();
    }
    
    public String generateResponse(String prompt) {
        return chatClient.prompt()
                .user(prompt)
                .call()
                .content();
    }
}
```
        * 복수 모델
          * 반드시 spring.ai.chat.client.enabled=false를 설정.
```java
@Configuration
@EnableConfigurationProperties(ChatClientProperties.class)
public class ManualChatConfiguration {
    
    // Disable autoconfiguration in application.properties:
    // spring.ai.chat.client.enabled=false
    
    @Bean
    @Primary
    public ChatClient openAiChatClient(OpenAiChatModel openAiModel) {
        return ChatClient.builder(openAiModel)
            .defaultSystem("You are using OpenAI GPT-4")
            .build();
    }
    
    @Bean
    @Qualifier("ollama")
    public ChatClient ollamaChatClient(OllamaChatModel ollamaModel) {
        return ChatClient.builder(ollamaModel)
            .defaultSystem("You are using a local Ollama model")
            .build();
    }
}
```
    * Chat Client API
      * Offers **a** fluent API
        * ![[100. media/image/pVOaC-OHfF.png]]
      * Creating a ChatClient
        * Inject autoconfigured ChatClient.builder Bean
          * 간단한 예
```java
@RestController
Class MyController() {
  private final ChatClient chatClient;

  public MyController(ChatClient.builder chatClientBuilder) {
    this.chatClient = chatClientBuilder.builder();
  }

  @GetMapping("/ai")
  String generation(String userInput) {
    return this.chatClient.prompt()
            .user(userInput)
            .call()
            .content()
  }
}
```
      * multiple Chat Models
        * disable the `ChatClient.Builder` autoconfiguration by setting the property `spring.ai.chat.client.enabled=false` -> create multiple ChatCient manually.
  * Annotation
    * Json
      * @JsonIgnoreProperties(ignoreUnknown = true) is a Jackson annotation that tells the JSON deserializer to ignore any properties in the JSON that don't have corresponding fields in your Java class.
    * Value from other sources #memo ^P3A7fn0yS
      * The @Value annotation can inject:
Property values from application.properties or application.yml
Environment variables
System properties
Static values
SpEL (Spring Expression Language) expressions

```javascript
// Property from application.properties/yml
@Value("${app.name}")
private String applicationName;

// With default value
@Value("${app.timeout:30}")
private int timeout;

// Environment variable
@Value("${JAVA_HOME}")
private String javaHome;

// Static value
@Value("Hello World")
private String greeting;

// SpEL expression
@Value("#{systemProperties['user.home']}")
private String userHome;

// Resource files
@Value("classpath:data.json")
private Resource dataFile;
@Value("file:/path/to/external/file.txt")
private Resource externalFile;
```

classpath: - This is a Spring resource prefix that tells Spring to look for the file in the classpath (typically in src/main/resources or any JAR dependencies).
Resource - The field type is Resource, which is a Spring abstraction for accessing various types of resources (files, URLs, etc.).
    * Validation
      * @Validated: Spring's Enhancement
        * Enables validation infrastructure
        * **Groups**: Supports validation groups for conditional validation
        * **Requires**: Spring AOP proxy to work
      * @Valid: Standard Bean Validation
        * **Field/Parameter level**: Validates objects passed to methods or nested properties
      * RULE 1: Data classes (User, Address) don't need @Validated
- They just define what constraints exist
- @Valid on fields enables nested validation
      * RULE 2: Service/Controller classes need @Validated to enable validation infrastructure
- Without @Validated: parameter constraints are ignored
- With @Validated: parameter constraints are enforced

      * RULE 3: @Valid works everywhere for object validation
- Validates the entire object and its nested objects
- Works whether the class has @Validated or not
      * RULE 4: Parameter validation (like @NotNull @Positive Long id) only works if:
- The containing class has @Validated annotation
- Spring AOP can intercept the method call

      * PRACTICAL DECISION TREE:
1. Validating an entire object? → Use @Valid
2. Validating individual parameters (primitives)? → Use @Validated on class + constraints on parameters  
3. Need validation groups? → Use @Validated
4. Need nested object validation? → Use @Valid on the field/paramete__
    * configuration
      * ### @Configuration
```java
@Configuration
public class AppConfig {
    @Bean
    public MyService myService() {
        return new MyServiceImpl();
    }
}
```
          * Marks a class as a source of bean definitions
          * Equivalent to XML configuration files
          * Classes annotated with @Configuration are processed by Spring container
      * ### @ConfigurationProperties
```java
@ConfigurationProperties(prefix = "app.database")
@Component
public class DatabaseProperties {
    private String url;
    private String username;
    private String password;
    // getters and setters
}
```
          * Binds external configuration properties to Java objects
          * Supports type-safe configuration binding
          * Can be used with records in Java 17+
      * ### @EnableConfigurationProperties
```java
@Configuration
@EnableConfigurationProperties({DatabaseProperties.class, CacheProperties.class})
public class AppConfig {
}
```
          * Enables support for @ConfigurationProperties beans
          * Alternative to using @Component on properties classes
      * ## Bean Definition Annotations
      * ### @Bean
```java
@Configuration
public class ServiceConfig {
    @Bean
    @Primary
    public DataSource primaryDataSource() {
        return new HikariDataSource();
    }
    
    @Bean("customService")
    @Scope("prototype")
    public MyService myService() {
        return new MyServiceImpl();
    }
}
```
          * Declares a method as a bean producer
          * Method return value is registered as a bean
          * Can specify bean name, scope, and other properties
      * ### @Primary
```java
@Bean
@Primary
public EmailService primaryEmailService() {
    return new SmtpEmailService();
}
```
          * Marks a bean as primary when multiple candidates exist
          * Used for autowiring disambiguation
      * ### @Qualifier
```java
@Bean
@Qualifier("fast")
public PaymentProcessor fastProcessor() {
    return new FastPaymentProcessor();
}

@Autowired
@Qualifier("fast")
private PaymentProcessor processor;
```
          * Provides additional metadata for autowiring
          * Used to specify which bean to inject when multiple candidates exist
      * ## Conditional Configuration
      * ### @ConditionalOnProperty
```java
@Configuration
@ConditionalOnProperty(
    name = "app.feature.enabled", 
    havingValue = "true", 
    matchIfMissing = false
)
public class FeatureConfig {
}
```
          * Conditionally enables configuration based on property values
          * Can check for property existence or specific values
      * ### @ConditionalOnClass
```java
@Configuration
@ConditionalOnClass(RedisTemplate.class)
public class RedisConfig {
    @Bean
    public RedisTemplate<String, Object> redisTemplate() {
        return new RedisTemplate<>();
    }
}
```
          * Enables configuration only if specified classes are present on classpath
      * ### @ConditionalOnMissingBean
```java
@Bean
@ConditionalOnMissingBean(DataSource.class)
public DataSource defaultDataSource() {
    return new H2DataSource();
}
```
          * Creates bean only if no bean of specified type exists
          * Useful for providing default implementations
      * ### @ConditionalOnBean
```java
@Bean
@ConditionalOnBean(DataSource.class)
public JdbcTemplate jdbcTemplate(DataSource dataSource) {
    return new JdbcTemplate(dataSource);
}
```
          * Creates bean only if specified bean exists
      * ## Profile and Environment
      * ### @Profile
```java
@Configuration
@Profile("production")
public class ProductionConfig {
    @Bean
    public DataSource dataSource() {
        return new PostgreSQLDataSource();
    }
}

@Configuration
@Profile("!production")
public class DevelopmentConfig {
    @Bean
    public DataSource dataSource() {
        return new H2DataSource();
    }
}
```
          * Activates configuration for specific profiles
          * Supports negation with "!" and expressions with "&", "|"
      * ### @ActiveProfiles (Testing)
```java
@SpringBootTest
@ActiveProfiles("test")
class MyServiceTest {
}
```
          * Activates specific profiles for testing
      * ## Auto-Configuration
      * ### @EnableAutoConfiguration
```java
@SpringBootApplication // includes @EnableAutoConfiguration
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```
          * Enables Spring Boot's auto-configuration mechanism
          * Usually included via @SpringBootApplication
      * ### @AutoConfigureAfter / @AutoConfigureBefore
```java
@Configuration
@AutoConfigureAfter(DataSourceAutoConfiguration.class)
public class MyDatabaseConfig {
}
```
          * Controls the order of auto-configuration classes
          * Ensures dependencies are configured in correct order
      * ## Import and Component Scanning
      * ### @Import
```java
@Configuration
@Import({DatabaseConfig.class, CacheConfig.class})
public class AppConfig {
}
```
          * Imports additional configuration classes
          * Can import @Configuration classes, ImportSelector, or ImportBeanDefinitionRegistrar
      * ### @ComponentScan
```java
@Configuration
@ComponentScan(basePackages = "com.example.services")
public class AppConfig {
}
```
          * Configures component scanning
          * Usually included via @SpringBootApplication
      * ## Validation
      * ### @Validated
```java
@ConfigurationProperties("app")
@Validated
public class AppProperties {
    @NotBlank
    private String name;
    
    @Min(1)
    @Max(100)
    private int maxConnections;
}
```
          * Enables validation for configuration properties
          * Works with JSR-303/JSR-380 validation annotations
      * ## Property Sources
      * ### @PropertySource
```java
@Configuration
@PropertySource("classpath:custom.properties")
@PropertySource(value = "file:${app.config.path}/app.properties", ignoreResourceNotFound = true)
public class AppConfig {
}
```
          * Adds property sources to Spring Environment
          * Can load from classpath, file system, or URLs
      * ### @TestPropertySource (Testing)
```java
@SpringBootTest
@TestPropertySource(properties = {
    "app.feature.enabled=true",
    "app.timeout=5000"
})
class MyServiceTest {
}
```
          * Configures property sources for testing
      * ## Refresh and Dynamic Configuration
      * ### @RefreshScope
```java
@Component
@RefreshScope
public class ConfigurableService {
    @Value("${app.message}")
    private String message;
}
```
          * Allows beans to be refreshed when configuration changes
          * Requires Spring Cloud Context dependency
      * ## Value Injection
      * ### @Value
```java
@Component
public class MyService {
    @Value("${app.timeout:30}")
    private int timeout;
    
    @Value("#{systemProperties['java.version']}")
    private String javaVersion;
}
```
          * Injects property values directly into fields/methods
          * Supports default values and SpEL expressions
    * HTTP Request
      * HTTP POST request with json input #memo ^i11lNFCsS
        * @RequestBody
```java
POST /users
Content-Type: application/json

{
  "username": "john",
  "email": "john@example.com"
}

// This FAILS for JSON POST requests
@PostMapping("/users")
public String createUser(@RequestParam String username) {
  // Can't extract from {"username": "john", "email": "john@example.com"}
}

@PostMapping("/users")
public ResponseEntity<String> createUser(@RequestBody User user) {
  // Works with JSON in request body
  return ResponseEntity.ok("Created user: " + user.getUsername());
}

public class User {
  @NotBlank(message = "Username is required")
  private String username;
    
  @Email(message = "Invalid email format")
  private String email;
    
  @Min(value = 18, message = "Must be at least 18 years old")
  private int age;
    
  // Getters and Setters...
}
```
      * Map with @RequestParam in dynamic form. Map 메소드 중 키,값 쌍을 효율적으로 묶어서 쓸 수 있는 것은?
        * Map.entrySet() 이용
```java
// Less efficient - multiple map lookups
for (String key : map.keySet()) {
    String value = map.get(key);  // This is a lookup operation
    System.out.println(key + " = " + value);
}

// More efficient - single iteration, no lookups
for (Map.Entry<String, String> entry : map.entrySet()) {
    String key = entry.getKey();    // Direct access
    String value = entry.getValue(); // Direct access
    System.out.println(key + " = " + value);
}
```

The Map approach works with application/x-www-form-urlencoded content type
All values in the map are Strings (Spring doesn't auto-convert when using Map)
For type conversion, you'd need to handle it manually or use individual @RequestParam parameters

```javascript
@PostMapping("/dynamic-form")
public String processDynamicForm(@RequestParam Map<String, String> formData) {
  StringBuilder response = new StringBuilder("Received data:\n");
    
  for (Map.Entry<String, String> entry : formData.entrySet()) {
    response.append(entry.getKey()).append(" = ").append(entry.getValue()).append("\n");
&nbsp;&nbsp;}
    
  return response.toString();
}
```
      * Multiple values as in GET collection
```java
// Multiple values per parameter name
@PostMapping("/multi") 
public String handleMulti(@RequestParam MultiValueMap<String, String> params) {
  // params.get("categories") returns List<String>
  List<String> categories = params.get("categories");
}
```
      * @RequestParam Basic in POST
        * Spring boot annotation used to extract query parameters, **form data, and parts in multiple requests** from HTTP requests and bind them method parameters in your controller.
Form data (POST with application/x-www-form-urlencoded): form fields in request body

Single value
POST request body
username=john&email=john
```java
@PostMapping("/users")
public String createUser(
  @RequestParam String username,
  @RequestParam String email) {
    
  // Spring extracts username and email from the form data in request body
  return "Created user: " + username + " with email: " + email;
}


@PostMapping("/users")
public String createUser(@RequestParam Map<String, String> formData) {
  String username = formData.get("username");
  String email = formData.get("email");
    
  return "Created user: " + username + " with email: " + email;
}
```

  * RestClient
    * RestTemplate보다 최신.
```java
RestClient restClient = RestClient.builder()
    .baseUrl(BASE_URL)
    .defaultHeader("Accept", "application/geo+json")
    .defaultHeader("User-Agent", "WeatherApiClient/1.0")
    .build();

Points points = restClient.get()
    .uri("/points/{latitude},{longitude}", latitude, longitude)
    .retrieve()
    .body(Points.class);
```
  * Spring Milestones #memo ^2DfcxZcYB
    * Pre-release versions of Spring projects (e.g., 1.0.0-M6)
More stable than SNAPSHOTs, less stable than RELEASE versions
"M" stands for Milestone (M1, M2, M3, etc.)

Spring Version Hierarchy
```plain text
SNAPSHOT → Daily builds (most unstable)
MILESTONE (M) → Pre-release with new features
RC → Release Candidate (almost final)
RELEASE → Production-ready (most stable)
```

Why Add Milestone Repository?
Maven Central only contains stable RELEASE versions
To use milestone versions, you must add:
xml
spring-milestones
https://repo.spring.io/milestone

Example Use Case
Using Spring AI 1.0.0-M6 → Milestone 6 version

Contains latest features
Good for development/learning
Not yet production-ready