---
title: "Versioning API"
created: 2024-07-04 13:23:38
updated: 2024-07-04 14:28:27
---
  * API 변경 시 필수
  * Additive chage strategy (without breaking change)
    * add new field
    * add new endpoint
    * change a response if the user opts in via request parameters
  * Explicit change strategy (with breaking change)
    * URI components versioning
      * ![[100. media/image/iWzua288ln.png]]
      * be prepared to support **300-level HTTP status codes**. These codes indicate redirection for resources that have moved or are moving.
    * HTTP Header versioning
      * ![[100. media/image/R_fbdG_aIV.png]]
      * hard to debug
      * not good when there is client caching. Client systems might think 2 requests sent to different version are the same.
    * Request parameter versioning
      * ![[100. media/image/qPSG9xBr_J.png]]
      * query string parameters are resolved after it reaches  specific application endpoint -> complex logic
  * Sunset Header
    * add to HTTP Header to indicate when resources are not available.
  * Tools and Libraries for API Versioning
    * Swagger/OpenAPI
    * Apigee
    * Postman
    * Spring framework