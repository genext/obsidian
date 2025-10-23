---
title: "February 23rd, 2024"
created: 2024-02-23 11:15:22
updated: 2024-08-27 16:13:20
---
  * How to design a good (REST) API
    * Requirements Gathering
      * Our job is to have users walk us through core use cases to uncover those fundamental needs, even when hidden at first glance.
      * Start the design process by drafting a high-level functional specification. Speed and flexibility are more important than comprehensive details at this early experimental stage.
    * One API, One Purpose
      * limit the scope of each API we build. Ensure the purpose stays clear and focused. Align all capabilities directly to that goal of fulfilling a distinct user need. Anything peripheral should be removed.
    * Clarity and Consistency
      * Choosing intuitive names
        * ![[100. media/image/VmakkzNVhV.png]]
        * ![[100. media/image/SGmgKHgfMJ.png]]
      * Consistent data formats
        * ![[100. media/image/Ew0QQdbG1O.png]]
    * Documentation is Key
      * check good examples
        * ![[100. media/image/3aGNra2lnD.png]]
      * Describe endpoints and methods
        * For example, if our API provides weather data, the documentation for the "/weather" endpoint should explain its purpose, accepted parameters, and response format.
      * Provide examples and tutorials
        * offer concise yet illustrative code snippets in multiple programming languages.
      * Keep documentation up-to-date
      * Sharing it with peer developers
        * If they cannot achieve basic integration, our documentation needs reworking.
    * Achieving Stability Through Versioning
      * URL versioning
        * ![[100. media/image/6NWfIzz1Q1.png]]
      * Parameter versioning
        * example:  https://myapi.com/api/widgets?version=1
        * This approach keeps the URL cleaner but can complicate caching strategies as some CDNs might stripe query parameters when caching.
      * Header versioning
        * for example, Accept-version: v1, ,but requires clients to modify header information, which might not be as straightforward for all users.
    * Effective Error Handling
      * Clear Error Codes and Messages
        * For instance, differentiating between client-side errors (like a 400 Bad Request) and server-side issues (like a 500 Internal Server Error) with clear messages
      * Consistent error structure
      * Providing contextual information
        * For instance, if a request fails due to invalid parameters, specify which parameter is invalid and why.
    * Security Measures
      * API keys
        * ![[100. media/image/KE8WuIp76C.png]]
      * Advanced authentication and authorization
        * consider implementing more sophisticated authentication mechanisms, such as OAuth 2.0, for scenarios requiring fine-grained access control over user data. For instance, a health data API might leverage OAuth to provide third-party applications with controlled access permissions.
      * Comprehensive rate limiting
      * Handling sensitive data
        * ![[100. media/image/26AC4RTVn7.png]]
      * Security headers and [[CORS]]
        * Utilize HTTP security headers to add an extra layer of protection for the API and its consumers. Headers such as Content-Security-Policy, X-Content-Type-Options, and X-Frame-Options can prevent several classes of attacks, including cross-site scripting and clickjacking. Additionally, configure Cross-Origin Resource Sharing ([[CORS]]) policies carefully to control which domains are allowed to access your API, preventing unauthorized cross-domain requests.
  * [[vectorization]]
  * numpy: array-processing library