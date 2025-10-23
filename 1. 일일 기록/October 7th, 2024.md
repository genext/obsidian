---
title: "October 7th, 2024"
created: 2024-10-07 00:00:00
updated: 2024-10-24 11:08:17
---
  * 06:00 출근
  * HTTP Authorization Header에 들어가는 값 종류
    * Bearer: OAuth2 tokens
    * Basic:
    * Digest:
    * Custom:
  * [x] 배포 주소 관리에서 유일성과 deployed 여부 미리 판단.
  * [x]  참가기관이 바우처 배포 실행한 후 결과 표시 창 필요.
  * 13:52 의사소통 상 오류로 의뢰기관을 공통코드로 관리하는 것으로 알았지만 서민균 매니저는 은행을 의미했던 것으로 확인됨.
  * [x] pagination
    * 예제
      * front: /src/app/regulator/system/logs/ useApiLogs  -> /v1/sys/user/history
        * ```javascript
import { SystemService } from "@/service/http/system.service";
import { UserLog } from "@/domain/userLog";
import { WithPagination } from "@/domain/http";

const { GET } = SystemService;

export const useApiLogs = () => {
  const getUserLogs = async (page: number, limit: number, email: string) => {
    const response = await GET<WithPagination<UserLog>>(
      `/v1/sys/user/history?limit=${limit}&page=${page}&email=${email}`,
    );
    if (response.success) {
      return response.data;
    }
    return undefined;
  };

  return {
    getUserLogs,
  };
};
```
      * backend: SysRestController
        * controller
          * ```java
	@GetMapping(value = "/user/history")
	public ResponseEntity<ApiResponse<PageData>> selectUserLoginHistory(
		@ModelAttribute UserHistoryDTO userHistoryDTO) {

		BaseMapList userLogs = this.sysService.selectUserLoginHistory(userHistoryDTO);
		PageData pageData = new PageData(userLogs, userHistoryDTO.getPage(), userHistoryDTO.getLimit());

		ApiResponse<PageData> response = new ApiResponse<>(String.valueOf(HttpStatus.OK.value()), true,
			"Successfully Read", pageData);

		return ResponseEntity.ok().body(response);
	}
```
        * service
          * ```java
@Slf4j
@Service
@RequiredArgsConstructor
public class SysServiceImpl {
	private final SysMapper sysMapper;

	public BaseMapList selectUserLoginHistory(UserHistoryDTO userHistoryDTO) {
		return this.sysMapper.selectUserLoginHistory(userHistoryDTO);
	}
}```
        * Data type
          * ```java
@Data
@EqualsAndHashCode(callSuper = false)
@NoArgsConstructor
@Schema(description = "UserHistory DTO 객체")
public class UserHistoryDTO extends PagingDTO {
	@Schema(description = "이메일", example = "")
	protected String email;
}
-------------------------
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
        * query
          * ```java
<select id="selectUserLoginHistory"
            resultType="kr.or.cbdc.infrastructure.framework.core.support.collection.CamelKeyMap">
        SELECT
          ...
        FROM
        (SELECT COUNT(*) AS total_count FROM tb_ca_user_login_hist B JOIN tb_ca_user A ON A.user_id = B.user_id WHERE
        1=1
        <if test=' query.email != null and query.email != "" '>
            <![CDATA[
                AND A.email LIKE CONCAT('%', #{query.email}, '%')
                ]]>
        </if>
        ) AS T,
        tb_ca_user A
        JOIN tb_ca_user_login_hist B ON A.user_id = B.user_id
        WHERE 1=1
        <if test=' query.email != null and query.email != "" '>
            <![CDATA[
        AND A.email LIKE CONCAT('%', #{query.email}, '%')
        ]]>
        </if>
        ORDER BY B.connected_at DESC
        <if test='query.offset != null and query.limit != null'>
            <![CDATA[
        LIMIT #{query.limit} OFFSET #{query.offset}
        ]]>
        </if>
    </select>```
    * pagination 적용 대상
      * participants
        * ~~dashboard/page.tsx~~
        * ~~deployed/page.tsx~~
      * regulator
        * ~~dashboard/approved-vouchers/page.tsx~~
        * ~~dashboard/deployed-vouchers/page.tsx~~
        * ~~dashboard/vouchers/page.tsx~~
        * ~~deploy-address/management/page.tsx~~
        * ~~manage/vouchers/page.tsx~~
        * ~~oracle/management/page.tsx~~
  * [x] 17:45 승인된 바우처 목록의 상세 페이지가 안 뜬다. 바로 수정 완료