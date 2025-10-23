---
title: "February 21st, 2024"
created: 2024-02-21 00:00:08
updated: 2024-02-21 19:28:12
---
  * How does chatGPT work?
    * Input
    * Tokenization
    * Create embeddings
    * Multiply embedding by model weights
    * Sample a prediction
    * ![[100. media/image/rqOKIH_I3C.png]]
      * Note that tokenization doesn’t necessarily mean splitting text into words; tokens can be subsets of words as well.
    * ![[100. media/image/9QhZCI8q_B.png]]
    * ![[100. media/image/HHD1fqbx_G.png]]
    * ![[100. media/image/gTNtNYSMBC.png]]
  * Design for High Availability
    * measurement
      * ![[100. media/image/80KgRdaa4L.png]]
      * unit: hours
      * MTBF: Mean Time Between Failture
      * MTTR: Mean Time To Repair
    * The Nines
      * availability
        * ![[100. media/image/ba5B26zad5.png]]
        * MTBF / (MTBF + MTTR)
      * ![[100. media/image/wKVP8n_EKi.png]]

    * Typical Architecture
      * Hot-Cold
        * ![[100. media/image/aWVFPRGmUx.png]]
      * Hot-Warm
        * ![[100. media/image/LDTXWudv7k.png]]
      * Hot-Hot
        * ![[100. media/image/PuIplibjcj.png]]
        * scaled
          * ![[100. media/image/sHdKivwCIy.png]]
      * Single Leader(MySQL, PostgreSQL)
        * a cluster contains multiple nodes
          * with one designated leader node - handle all writes from clients
          * replica node - maintains leader node's data and handle reads
          * ![[100. media/image/J8ghRyMY4b.png]]
        * How does the leader propagate changes?
          * The leader focuses on processing writes. Instead of having it push changes, databases like MySQL record updated in a binlog. New replicas request this log to catch up on changes.
          * Replication can be asynchronous for performance or synchronous (with tunable durability guarantees) for consistency. Kafka offers both modes - we can configure the “acks” setting to be 1 or all, meaning Kafka commits the message when one replica acknowledges the replication or all replicas acknowledge.
        * What happens when the leader fails?
          * 3 things to handle
            * Failure detection
            * Leader election
            * Request rerouting
        * How do we handle replication lag?
          * The solution is "read-after-write" consistency, where reads immediately after writes are directed to the leader.
      * Multiple Leaders

        * ![[100. media/image/qG0jvapTPo.png]]
      * Leaderless
        * The Amazon Dynamo database uses a leaderless architecture where write requests are sent to multiple nodes (w) and read requests are also fanned out to multiple nodes (r). As long as the number of nodes written to and read from exceeds the total number of nodes, that is, r + w > n, this ensures the most up-to-date data can be read.
        * ![[100. media/image/kaU4-BmdNE.png]]
        * other complexities
          * read repair
            * If reading from several nodes returns different versions of data, the client uses the latest version and repairs the other nodes.
          * anti-entropy
            * With loose consistency requirements, many data differences can accumulate between nodes.  A background “anti-entropy” process continually looks for and fixes these differences.
      * Separation of Compute and Storage
        * microservice
        * serverless
    * Tradeoffs
      * other mechanisms to restrict incoming load
        * Rate limiting
        * Service degradation
          * provide only core services, removing non-essential ones.
        * Queuing
        * Circuit breaking
          * prevents cascading failures in distributed systems.
  * P2P Network
    * server-client vs p2p
      * ![[100. media/image/dHE_tzDG3j.png]]
    * Types of P2P models
      * Pure P2P model
        * ![[100. media/image/ksBs54RCrD.png]]
      * Hybrid P2P model
        * ![[100. media/image/0ch2zSxF5Q.png]]
      * Blockchain-based P2P model
        * ![[100. media/image/eLiQ7HGaU4.png]]
    * How the P2P network operates
      * Node Initialization
        * Usually, developers provide a list of trusted nodes written directly into the code of the P2P client application that can be used for initial peer discovery.
        * A node is usually identified by the following node triple: IP address, Port number, and node ID.
      * Discovery and Connection
        * Centralized Server / Tracker Server
          * ![[100. media/image/mbkluXZotL.png]]
        * Distributed Hash Tables (DHTs)
          * ![[100. media/image/aANT9N4kFI.png]]
        * Broadcasting and Multicasting
          * ![[100. media/image/83fTqi0cQ4.png]]
      * Routing and Lookup
        * lookup table: Every node maintains a lookup table (also called a routing table) where it stores the node information (IP, Port, and ID) of the closest peers it knows of.
      * Real-life applications of P2P network
        * ![[100. media/image/oNMxmR-vRP.png]]
