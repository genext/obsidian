---
title: "October 18th, 2024"
created: 2024-10-18 06:01:03
updated: 2024-10-18 17:53:26
---
  * 06:00 출근
  * 오늘 할 일
    * 업무 메일 확인
    * 검색 조건에 따른 조회결과 보내주도록 모두 수정.

  * 명경지수 -> 명징한 생각
  * 06:48 일단 오라클, 배포주소 관리 검색조건 보완 완료.
  * 디지털 바우처 참가기관 시스템 front(React+grid) ^0mU51jCYp
    * git: ![[100. media/archives/s4I0XVjt3y.zip]]
  * 13:36 서버에서 시간을 보내줄 때 완전하게 보내지 않는 경우가 있다.  ^hThMM6XGD
    * DB에는 2024-10-16 04:44:00로 들어가 있지만 쿼리 결과를 DTO 객체에 저장한 결과는 2024-10-16T04:44로 초를 나타내는 값이 빠졌다.
    * 서버에서 받는 응답을 저장하는 타입 정의
      * ```javascript
export interface VoucherRequest {
  deploy_request_id: string;
  company_name: string;
  voucher_name: string;
  template_name: string;
  template_type_name: string;
  status_name: string;
  created_at: [number, number, number, number, number, number];
  approved_at: [number, number, number, number, number, number] | null;
  deployed_at: [number, number, number, number, number, number] | null;
  created_by: string;
  deployed_by: string;
}

// Converted VoucherRequest, to show on the table
export interface VoucherResult {
  deployRequestId: string;
  companyName: string;
  voucherName: string;
  templateName: string;
  templateType: string;
  statusName: string;
  requestDate: string;
  approvalDate: string | null;
  deployedDate: string | null;
  createdBy: string;
  deployedBy: string;
}```
    * 그럼 다음과 같은 코드는 runtime 에러 발생
      * ```javascript
try {
      const response = await SystemService.GET<WithPagination<VoucherRequest>>(
        VOUCHER_SEARCH_DEPLOY_REQUESTS,
        {
          params: searchCriteria,
        },
      );

      if (response.success) {
        const { list, currentPage, totalCount } = response.data; // Correctly typed as VoucherRequest[]

        if (list === null || list.length === 0) {
          setResults([]);
          setCurrentPage(1);
          setTotalCount(0);
          setLoading(false);
          return;
        }
        // Map the VoucherRequest to VoucherResult
        const parsedResults = list.map((item: VoucherRequest) => ({
          deployRequestId: item.deploy_request_id,
          companyName: item.company_name,
          voucherName: item.voucher_name,
          templateName: item.template_name,
          templateType: item.template_type_name,
          statusName: item.status_name,
          requestDate: format(
            new Date(
              item.created_at[0],
              item.created_at[1] - 1,
              item.created_at[2],
            ),
            "yyyy-MM-dd",
          ),
          approvalDate: item.approved_at
            ? format(
                new Date(
                  item.approved_at[0],
                  item.approved_at[1] - 1,
                  item.approved_at[2],
                ),
                "yyyy-MM-dd",
              )
            : "-",
          deployedDate: item.deployed_at
            ? format(
                new Date(
                  item.deployed_at[0],
                  item.deployed_at[1] - 1,
                  item.deployed_at[2],
                ),
                "yyyy-MM-dd",
              )
            : "-",
          createdBy: item.created_by,
          deployedBy: item.deployed_by,
        }));

        setResults(parsedResults);
        setTotalCount(totalCount);
        setCurrentPage(currentPage);
      }
      setLoading(false);
    } catch (error) {
      handleAxiosError(
        error,
        "An error occurred while fetching the voucher requests",
        toastErrorMessage,
      );
      setError("An error occurred while fetching the voucher requests.");
      setLoading(false);
    }```
    * 따라서 정확히 0초일 때 저장된 시간값도 처리하기 위해서 다음 함수 만들어서 처리
      * Fallback 처리함수
        * ```javascript
const getDateWithFallback = (
    dateArray: [number, number, number, number, number, number],
  ) => {
    const [year, month, day, hour, minute, second = 0] = dateArray; // Default second to 0 if not provided
    return new Date(year, month - 1, day, hour, minute, second);
  };```
      * 수정 결과
        * ```javascript
try {
      const response = await SystemService.GET<WithPagination<VoucherRequest>>(
        VOUCHER_SEARCH_DEPLOY_REQUESTS,
        {
          params: searchCriteria,
        },
      );

      if (response.success) {
        const { list, currentPage, totalCount } = response.data; // Correctly typed as VoucherRequest[]

        if (list === null || list.length === 0) {
          setResults([]);
          setCurrentPage(1);
          setTotalCount(0);
          setLoading(false);
          return;
        }
        // Map the VoucherRequest to VoucherResult
        const parsedResults = list.map((item: VoucherRequest) => ({
          deployRequestId: item.deploy_request_id,
          companyName: item.company_name,
          voucherName: item.voucher_name,
          templateName: item.template_name,
          templateType: item.template_type_name,
          statusName: item.status_name,
          requestDate: format(
            getDateWithFallback(item.created_at),
            "yyyy-MM-dd HH:mm:ss",
          ),
          approvalDate: item.approved_at
            ? format(
                getDateWithFallback(item.approved_at),
                "yyyy-MM-dd HH:mm:ss",
              )
            : "-",
          deployedDate: item.deployed_at
            ? format(
                getDateWithFallback(item.deployed_at),
                "yyyy-MM-dd HH:mm:ss",
              )
            : "-",
          createdBy: item.created_by,
          deployedBy: item.deployed_by,
        }));

        setResults(parsedResults);
        setTotalCount(totalCount);
        setCurrentPage(currentPage);
      }
      setLoading(false);
    } catch (error) {
      handleAxiosError(
        error,
        "An error occurred while fetching the voucher requests",
        toastErrorMessage,
      );
      setError("An error occurred while fetching the voucher requests.");
      setLoading(false);
    }```
  * 16:56 sql 정리 시작
  * 17:52 바우처 관리 deployMapper.xml sql 정리 종료