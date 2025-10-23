---
title: "MSA"
created: 2023-12-24 17:28:38
updated: 2024-10-21 17:26:16
---
  * interview questions

    * What is an API Gateway?
      * acts as a single entry point for client requests. The API gateway is responsible for request routing, composition, and protocol translation. It also provides additional features like authentication, authorization, caching, and rate limiting.
      * Besides request routing, the API gateway can also aggregate responses from microservices into a single response for the client.
      * The API gateway is different from a load balancer. While both handle network traffic, the API gateway operates at the **application layer**, **mainly handling HTTP requests;** the load balancer mostly operates at the **transport layer, dealing with TCP/UDP protocols**. The API gateway offers more functions as it sees the request payload.
      * The API gateway differs from a load balancer in that it typically operates at the application layer to handle HTTP requests and understand message payloads, while traditional load balancers work at the transport layer to handle TCP/UDP connections **without looking at the application data**.
      * However, the lines can blur between these two types of infrastructure. Some advanced load balancers are gaining application layer visibility and routing capabilities resembling API gateways.
      * But in general, API gateways focus on application-level concerns like security, routing, composition, and resilience based on the payload, while traditional load balancers map requests to backend servers mainly based on transport-level metadata like IP and port numbers.
      * general api gateway
        * ![[100. media/image/v79fEt_lzM.png]]
        * separate api gateway
          * ![[100. media/image/NMzRhFjJ7L.png]]

    * What are the differences between REST and RPC?
      * REST (Representational State Transfer) and RPC (Remote Procedure Call) are two common architectural patterns used for communications in distributed systems. REST is used for **client-server communications**, and RPC is used for **server-server communication**s, as illustrated in the diagram below.
      * ![[100. media/image/uKj1Xt3bm8.png]]
    * What is a configuration manager?
    * What are common microservices fault tolerance approaches?
    * How do we manage distributed transactions?
    * How do we choose between monolithic and microservices architectures?
  * API Gateway
    * ![[100. media/image/3v5QH9_gbT.png]]
