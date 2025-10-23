---
title: "REST API"
created: 2023-08-27 14:50:46
updated: 2024-07-04 13:23:54
---
  * REST API 설계 원칙 from [Building Effective and Secure API](https://www.youtube.com/watch?v=_gQaygjm_hg)
    * 명명 규칙
      * https://example.com/api/v1/carts/123/items/321
        * plural
          * API URL에 동사 사용하지 않는다. 단지 Resource를 의미한는 명사로 url 만든다. 대개 명사는 복수형. 단수는 Resource 하부구조가 있을 때 key로 쓸 수 있는 것...영화 제목 같은 unique identifier.
        * idempotence
          * yes: GET, PUT, DELETE
          * no: POST, PATCH
        * [[Versioning API]]
          * 첫번째 버전: /api/v1/...
          * 이후 버전: /api/v2/... 처럼 v 다음 숫자를 증가.
        * [[Pagination]]
          * page + offset
            * 단점: 전체 데이터 갯수를 알아야 한다.
          * cursor based
            * 데이터가 자주 바뀔 때 유용?
        * use clear query strings for sorting and filtering API data
          * GET /users?sort_by=registered
          * GET /products?filter=color:blue
        * security first - make keep yourself up to date with the latest best practices
          * leverage HTTP Headers(Authorization) for API keys
          * use TLS to protect Authorization field in HTTP Headers
        * keep cross-resource reference simple
          * Don't use query strings to reference resources.
            * 나쁜 예: https://example.com/api/v1/items?card_id=123&item_id=321
        * Plan for rate limiting
          * set request quotas based on source IP addresses, user account, endpoint categories, etc -> protect APIs from overload, abuse.

  * 실제 수행하는 작업은 HTTP method로 구분. DELETE /movies/{movieID}...