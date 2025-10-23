---
title: "August 17th, 2024"
created: 2024-08-17 11:53:07
updated: 2024-08-17 19:18:07
---
  * 11:53 디지털 바우처 React 프로젝트 소스 분석 ^CTKILAsjX
    * Key component
      * Routing(/src/component/route/index.tsx)
        * page navigations using react-router-dom.
        * dynamic component loading based on the path and permission checks
      * Layout(/src/component/layout/index.tsx)
        * main structure of the page, including sidebar(BankSideBar) and content area
      * Error handling(/src/component/error/...)
        * 404(Not found), Forbidden access, runtime error
      * Grid and filters(/src/component/grid/...)
        * rendering and managing data tables, including filtering, sorting, pagination
      * Feature hooks
        * reading and filtering data from the server
        * handling grid functionality
        * perform actions
    * Dynamic loading and error handling
      * loadPage function in "index.tsx" imports pages based on URL.
      * Suspense
        * allows for lazy loading components
    * UI/UX
      * Bootstrap(react-bootstrap)
        * modal handling and custom styling
      * Recoil
        * manage state across components, such as use login status/configuring settings
    * Data management
      * communication with API using hook "useCommonApi"
  * 19:18 Death 읽기 시작
