---
title: "CORS"
created: 2024-08-27 16:12:58
updated: 2025-09-17 12:48:55
---
  * Cross-Origin Resource Sharing
    * Origin
      * Protocol(HTTP) + domain(example.com) + port
    * Resources
      * APIs, fonts, etc.
  * A **security mechanism** enforced by **web browsers**.
    * control how resource can be requested from different origins
    * https://frontend.com  --> https://api.backend.com
      * the browser checks if the target server allows **cross-origin** requests
      * server send HTTP headers
        * {{table}}
          * Access-Control-Allow-Origin
            * https://example.com or *
          * Access-Control-Allow-Methods
            * GET or POST
          * Access-Control-Allow-Headers
            * Authorization or Content-Type
          * Access-Control-Allow-Credentials
            * true or false