---
title: "Pagination"
created: 2024-07-03 11:08:26
updated: 2025-09-17 12:50:22
---
![[100. media/image/EhntppauXb.png]]
  * Offset-based Pagination
    * {{table}}
      * Example
        * Pros
          * Cons
      * GET /orders?offset=0&limit=3
        * Simple to implement and understand.
          * Can become inefficient for large offsets, as it requires scanning and skipping rows.
  * Cursor-based Pagination
    * {{table}}
      * Example
        * Pros
          * Cons
      * GET /orders?cursor=xxx
        * More efficient for large datasets, as it doesn't require scanning skipped records.
          * Slightly more complex to implement and understand.
  * Page-based Pagination
    * {{table}}
      * Example
        * Pros
          * Cons
      * GET /items?page=2&size=3
        * Easy to implement and use.
          * Similar performance issues as offset-based pagination for large page numbers.
  * Keyset-based Pagination
    * {{table}}
      * Example
        * Pros
          * Cons
      * GET /items?after_id=102&limit=3
        * Efficient for large datasets and avoids performance issues with large offsets.
          * Requires a unique and indexed key, and can be complex to implement.
  * Time-based Pagination
    * {{table}}
      * Example
        * Pros
          * Cons
      * GET /items?start_time=xxx&end_time=yyy
        * Useful for datasets ordered by time, ensures no records are missed if new ones are added.
          * Requires a reliable and consistent timestamp.
  * Hybrid Pagination
    * {{table}}
      * Example
        * Pros
          * Cons
      * GET /items?cursor=abc&start_time=xxx&end_time=yyy
        * Can offer the best performance and flexibility for complex datasets.
          * More complex to implement and requires careful design.
  * SK에서 한 프로젝트 pagination 구현 코드는?