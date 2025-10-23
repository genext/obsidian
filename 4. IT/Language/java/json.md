---
title: "json"
created: 2025-01-27 08:41:32
updated: 2025-01-27 08:52:09
---
  * web browser -> server or server -> openAPI server에서 interface로 json을 사용하는데 이 때 annotation을 이용해서 정의하는 방법.
    * ```java
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class CbsErrorDto {
  @JsonProperty("msgCd")
  @JsonAlias({ "MSG_CD" })
  private String msgCd;
  
  @JsonProperty("mainMsgTxt")
  @JsonAlias({ "MAIN_MSG_TXT" })     
    private String mainMsgTxt;      
} ```
    * ```java
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class CbsErrorDto {
    @JsonAlias({ "msgCd", "MSG_CD" })    
    private String msgCd;      
    
    @JsonAlias({ "mainMsgTxt", "MAIN_MSG_TXT" })     
    private String mainMsgTxt;      
} ```
  * sql에서 json 형태로 응답을 만들 때 도움 되는 함수.