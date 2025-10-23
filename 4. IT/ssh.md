---
title: "ssh"
created: 2024-07-25 17:04:14
updated: 2025-08-26 12:15:16
---
  * ## **ssh tunnel**
    * SSH tunneling creates encrypted "pipes" through SSH connections to securely route traffic between different ports and machines.
    * also know as ssh port forwarding, is a secure encrypted connection between the local machin and a remote server.
    * Types of ssh tunnels
      * Local port forwarding
        * Use case: Database connection that detours firewall.
        * from local port to remote port
        * command: ssh -L local_port:remote_host:remote_port user@ssh_server
        * ```shell
ssh -p 22022 -L9091:localhost:9091 bokv@000.000.000.000```
          * ![[100. media/image/pNppkppdi2.png]]
          * `-p 22022`: Connect to the remote SSH server's port 22022 (not default 22). This is where the SSH daemon (sshd) is listening on the remote server
          * `-L9091:localhost:9091`
            * Forward local port 9091 to remote localhost:9091. 
            * This port is opened locally for the tunnel.
            * Applications on your local machine connect to localhost:9091
          * `bokv@000.000.000.000`: SSH user and server IP
      * Remote port forwarding
        * from a remote port to local port
        * command: ssh -R remote_port:local_host:local_port user@ssh_server
      * Dydnamic port forwarding