---
title: "September 23rd, 2025"
created: 2025-09-22 13:13:41
updated: 2025-09-24 13:27:33
---
  * 08:35 cig 1
  *  {{[[∆]]:1+2}}
    * To develop an effective resource monitoring system on Linux, you'll need to master several key areas of Linux system administration and programming. Here's a structured breakdown of the essential knowledge:
    * **Core Linux System Concepts**
      * 1. **Process Management**
        * Understanding process lifecycle, PIDs, and process states
        * Process hierarchy and parent-child relationships
        * Process scheduling and priority management
      * 2. **File System Structure**
        * `/proc` filesystem - crucial for system information
        * `/sys` filesystem - hardware and kernel parameter information
        * `/dev` filesystem - device files and hardware interfaces
    * **Essential Commands for Resource Monitoring**
      * 1. **CPU Monitoring Commands**
        * `top` and `htop` - real-time process and CPU usage
        * `vmstat` - virtual memory and CPU statistics
        * `iostat` - CPU utilization and I/O statistics
        * `sar` - system activity reporter
        * `mpstat` - multi-processor usage statistics
      * 2. **Memory Monitoring Commands**
        * `free` - memory usage overview
        * `cat /proc/meminfo` - detailed memory information
        * `pmap` - process memory mapping
        * `smem` - memory usage reporting
      * 3. **GPU Monitoring Commands**
        * `nvidia-smi` - NVIDIA GPU monitoring (if using NVIDIA GPUs)
        * `rocm-smi` - AMD GPU monitoring
        * `intel_gpu_top` - Intel GPU monitoring
      * 4. **System Information Commands**
        * `lscpu` - CPU architecture information
        * `lshw` - hardware information
        * `lspci` - PCI devices information
        * `dmidecode` - hardware details from BIOS
    * **File System Knowledge for Data Collection**
      * 1. **Critical `/proc` Files**
        * `/proc/stat` - CPU and system statistics
        * `/proc/meminfo` - memory information
        * `/proc/loadavg` - system load averages
        * `/proc/cpuinfo` - CPU details
        * `/proc/[pid]/stat` - per-process statistics
      * 2. **Important `/sys` Paths**
        * `/sys/class/thermal/` - temperature sensors
        * `/sys/devices/system/cpu/` - CPU information
        * `/sys/class/drm/` - GPU information
    * **Programming and Scripting Skills**
      * 1. **Shell Scripting**
        * Bash scripting for automation
        * Text processing with `awk`, `sed`, `grep`
        * Regular expressions for data parsing
      * 2. **Programming Languages**
        * **Python** - excellent libraries like `psutil`, `py3nvml`
        * **C/C++** - for high-performance monitoring tools
        * **Go** - popular for system tools and monitoring applications
    * **System Administration Concepts**
      * 1. **User and Permission Management**
        * Understanding file permissions and ownership
        * Running processes with appropriate privileges
        * Security considerations for monitoring tools
      * 2. **Service Management**
        * `systemd` - modern service management
        * Creating and managing daemon processes
        * Log management with `journalctl`
    * **Networking and Communication**
      * 1. **Inter-Process Communication**
        * Sockets for data transmission
        * Named pipes and shared memory
        * Message queues
      * 2. **Network Monitoring**
        * `netstat` - network connections
        * `ss` - modern socket statistics
        * `iftop` - network bandwidth monitoring
    * **Development Tools and Debugging**
      * 1. **Debugging and Profiling**
        * `strace` - system call tracing
        * `gdb` - debugging applications
        * `perf` - performance analysis tools
      * 2. **Build and Development Environment**
        * Package management (`apt`, `yum`, `pacman`)
        * Compilation tools (`gcc`, `make`, `cmake`)
        * Version control with `git`
    * **Recommended Learning Path**
      * 1. Start with basic Linux commands and file system navigation
      * 2. Master process and resource monitoring commands
      * 3. Learn to parse `/proc` and `/sys` filesystems
      * 4. Practice shell scripting for data collection
      * 5. Choose a programming language (Python recommended for beginners)
      * 6. Build simple monitoring scripts and gradually add complexity
      * 7. Study existing monitoring tools' source code for inspiration
    * The key is to start with manual monitoring using command-line tools, then gradually automate and build your own system based on the underlying mechanisms these tools use.
  * 할 일 - 2분 규칙과 과제 세분화
    * roam research extension for mochi 만들기 --> 불편하더라도 내가 직접 타이핑하면서 기록하는 것도 몸에 남을 거라는 생각이라도 안 하기로 함.
  * 명경지수 -> 명징한 생각
  * 09:38 cig 2
  * extension 만들기 시작
  * {{[[Roam/genext-2025-10-05-02-18-30/roam/js|roam/js]]}}
    * ```javascript
function isHomePage() {
  return ( window.location.hash.split("/")[3] == null );
}

if (isHomePage()) {
  console.log("isHomePage is true!");
  window.roamAlphaAPI.ui.mainWindow
    .openPage({page: {title: "Developer Hub"}});
}```
  * 11:10 cig 3
  * 12:48 cig 4
  * 15:41 cig 5
  * 17:47 cig 6
  * 18:25 jwt 토큰이 일반 access token과 다른 점은 해시할 때 쓰는 키를 서버가 가지고 있다는 것.
    * jwt 토큰에는 사용자 정보, 권한, 등이 다 있다. 다만 구조가 나눠어져 있을 뿐.
      * 헤더: 토큰에 대한 메타데이터
      * payload: 토큰 정보
      * 서명?: 헤더와 payload의 해시값을 자신의 키로 암호화하고 base64로 바꾼 것.
    * 서버에서 처음에 토큰 발행할 때 특정 키를 가지고 헤더+payload의 해시값을 서명했기 때문에 돌렸기 때문에 중간에 토큰에 변조가 있으면 서버에서 서명이 틀리게 나오기 때문에 변조를 바로 안다.
    * 결국 db에 토큰을 저장해서 비교할 필요 없어서 확장성에 좋다.
  * 19:05 cig 7
  * 19:52 cig 8
