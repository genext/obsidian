---
title: "Kubernetes"
created: 2024-04-02 16:53:12
updated: 2025-01-27 09:00:49
---
  * [source](https://kubernetes.io/docs)
  * Orchestration platform
  * Install Tools
    * Kubectl
      * CLI against kubernetes cluster
    * For local environment
      * kind(**K**ubernetes **IN D**ocker)
        * with docker container
        * multiple nodes
      * minukube
        * with VM
        * single node
    * kubeadm
      * create and manage kubernetes cluster
  * Concepts
    * Component
      * Cluster architecture
        * 시스템 구성도
          * ![[100. media/image/YqAKlgCJHa.png]]
          * ![[100. media/image/D-rQfce1xe.png]]
        * Node
          * virtual or physical machine on which pods run
          * added to API server by
            * kubelet self-register
            * [[json]] manifest
              * ```json
{
  "kind": "Node",
  "apiVersion": "v1",
  "metadata": {
    "name": "10.240.79.157",
    "labels": {
      "name": "my-first-k8s-node"
    }
  }
}```
        * Controllers
          * control loop to get current state closer to the desired state
        * Lease
          * lock the shared resource or coordinate activities between members
        * Cloud controller manager
          * embeds cloud specific control logic
          * plugin structure
      * Control plane component
        * kube-apiserver
          * front end for the kubernetes control plane
          * scale horizontally
        * etcd
          * key-value store for all cluster data
        * kube-scheduler
          * watch newly created pods and assign them on nodes
        * kube-controller-manager
          * runs controller
            * Node controller
            * Job controller
            * endpointSlice(Services - pods) controller
            * ServiceAccount controller
        * cloud-controller-manager
          * dependent on cloud service provider
          * links your cluster to cloud provider API
      * Nodes component
        * kubelet
          * from PodSpecs -> run containers in a pod
        * kube-proxy
          * maintains network rule on nodes, allowing network communications to pods.
        * container runtime
          * containerd + Kubernetes CRI(Container Runtime Interface) => manage the life-cycle of containers
      * Addons
        * DNS
        * Web-UI
        * monitoring, logging, etc
    * api server
      * The core of kubernetes' control plane.
  * node > pods > application workload
  * container orchestration
    * Essential concepts
      * **Pod**: the smallest deployable unit, typically containing one or more contrainers.
      * **Service**: An abstract layer that defines a logical set of pods and a policy to access them.
      * **Ingress**: Manages external access to services in a cluster
      * **ConfigMap and Secret**: for configuation management
      * ![[100. media/image/ZKYX6GycWu.png]]