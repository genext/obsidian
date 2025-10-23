---
title: "November 12th, 2024"
created: 2024-11-12 08:59:37
updated: 2024-11-12 15:48:39
---
  * 08:59 본사 출근
  * 09:26 **"Oh My Zsh"** 설치 ^w7uw4PkwN
    * 필요조건
      * curl 설치
      * git 설치
        * ```shell
sudo apt install git```
      * zsh 설치
        * **"Oh My Zsh"**은 zsh을 위한 framework이므로 미리 zsh(5.0.8 이상)이 설치되어 있어야 한다.
        * 아래 명령어 실행 후 잊지 말고 **Logout** 실행할 것
          * ```shell
$ sudo apt install zsh
$ zsh --version
$ chsh -s `which zsh
$ echo $SHELL```

    * **"Oh My Zsh"** 설치
      * ```shell
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"```
    * 10:46 "Oh My Zsh"의 theme 중 powerlevel10k 설치
      * font 4개 다운로드하고 설치
        * 한참 기다려도 이상하게 installing이 installed로 바뀌지 않는다.
      * powerlevel10k 설치
        * ```shell
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k```
      * zsh theme 설정
        * ~/.zshrc를 수정해서 ZSH_THEME="powerlevel10k/powerlevel10k"로 바꾼다.
        * source .zshrc를 하면 세부 설정을 묻는 과정 진행.
      * plugin 설치
        * syntax highlight
          * ```shell
cd ~/.oh-my-zsh/plugins
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git
echo "source ${(q-)PWD}/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" >> ${ZDOTDIR:-$HOME}/.zshrc
#.zshrc의 plugins에 다음과 같이 추가
plugins=(git zsh-syntax-highlighting)```
        * auto suggestions
          * ```shell
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
.zsrhc에 다음과 같이 추가
plugins=(git ... zsh-autosuggestions)```
  * 10:18 battery protection 설정 ^QfHLfy8RF
    * Thinkpad용 배터리 관리 모듈(tlp) 다운로드
      * ```shell
~ sudo add-apt-repository ppa:linrunner/tlp
~ sudo apt update
~ sudo apt install tlp```
    * 상태 확인(tlp-stat)
      * ```shell
# Check what package needed for battery:
~ sudo tlp-stat -b
--- TLP 1.7.0 --------------------------------------------

+++ Battery Care
Plugin: thinkpad
Supported features: charge thresholds, recalibration
Driver usage:
* natacpi (thinkpad_acpi) = active (charge thresholds, recalibration)
Parameter value ranges:
* START_CHARGE_THRESH_BAT0/1:  0(off)..96(default)..99
* STOP_CHARGE_THRESH_BAT0/1:   1..100(default)

+++ ThinkPad Battery Status: BAT0 (Main / Internal)
/sys/class/power_supply/BAT0/manufacturer                   = SMP
/sys/class/power_supply/BAT0/model_name                     = 5B11B79217
/sys/class/power_supply/BAT0/cycle_count                    =     11
/sys/class/power_supply/BAT0/energy_full_design             =  90090 [mWh]
/sys/class/power_supply/BAT0/energy_full                    =  91750 [mWh]
/sys/class/power_supply/BAT0/energy_now                     =  77920 [mWh]
/sys/class/power_supply/BAT0/power_now                      =  15213 [mW]
/sys/class/power_supply/BAT0/status                         = Discharging

/sys/class/power_supply/BAT0/charge_control_start_threshold =      0 [%]
/sys/class/power_supply/BAT0/charge_control_end_threshold   =    100 [%]
/sys/class/power_supply/BAT0/charge_behaviour               = [auto] inhibit-charge force-discharge

Charge                                                      =   84.9 [%]
Capacity                                                    =  101.8 [%]
```
    * config(/etc/tlp.conf)에서 아래 줄 comment 푼다.
      * ```plain text
START_CHARGE_THRESH_BAT0=75
STOP_CHARGE_THRESH_BAT0=80```
    * tlp start
      * ```shell
~ sudo tlp start```
    * 다시 상태 확인하여 threshold가 설정된  확인.
      * ```shell
~ sudo tlp start
TLP started in battery mode (auto).
➜  ~ sudo tlp-stat -b
--- TLP 1.7.0 --------------------------------------------

+++ Battery Care
Plugin: thinkpad
Supported features: charge thresholds, recalibration
Driver usage:
* natacpi (thinkpad_acpi) = active (charge thresholds, recalibration)
Parameter value ranges:
* START_CHARGE_THRESH_BAT0/1:  0(off)..96(default)..99
* STOP_CHARGE_THRESH_BAT0/1:   1..100(default)

+++ ThinkPad Battery Status: BAT0 (Main / Internal)
/sys/class/power_supply/BAT0/manufacturer                   = SMP
/sys/class/power_supply/BAT0/model_name                     = 5B11B79217
/sys/class/power_supply/BAT0/cycle_count                    =     11
/sys/class/power_supply/BAT0/energy_full_design             =  90090 [mWh]
/sys/class/power_supply/BAT0/energy_full                    =  91750 [mWh]
/sys/class/power_supply/BAT0/energy_now                     =  75510 [mWh]
/sys/class/power_supply/BAT0/power_now                      =  10355 [mW]
/sys/class/power_supply/BAT0/status                         = Discharging

/sys/class/power_supply/BAT0/charge_control_start_threshold =     75 [%]
/sys/class/power_supply/BAT0/charge_control_end_threshold   =     80 [%]
/sys/class/power_supply/BAT0/charge_behaviour               = [auto] inhibit-charge force-discharge

Charge                                                      =   82.3 [%]
Capacity                                                    =  101.8 [%]
```
  * 12:59 java 설치 ^mkX1oiSY4
    * App center에서 synaptic 찾아서 설치해서 synaptic을 통해서 java를 설치할까 했지만 apt로 설치하기로 변경
      * ```shell
sudo apt update
sudo apt install openjdk-17-jdk
java --version```
    * $JAVA_HOME 설정도 있지만 생략
  * 13:30 Decrease swap use ^pAIsYWvAQ
    * ```plain text
why should i use swap even when i still have available RAM?

— Even if there is still available RAM, the Linux Kernel will move memory pages that 
are hardly ever used into swap space.
— It’s better to swap out memory pages that have been inactive for a while, keeping 
often-used data in cache, and this should happen when the server is most idle, which is
 the aim of the Kernel.
— Avoid setting your swap space too large if it will result in prolonging performance 
issues, outages, or your response time (without proper monitoring/alerts).

Kernel cache pressure and swappiness
On a healthy server with lots of available memory, use the following:

vm.swappiness=10
vm.vfs_cache_pressure=50
This will decrease the cache pressure. Since caching is good for performance, we want 
to keep cached data in memory longer. Since the cache will grow larger, we still want 
to reduce swapping to not cause increased swap I/O.

source: https://haydenjames.io/linux-performance-almost-always-add-swap-space/```
    * /proc/sys/vm/swappiness는 60, /proc/sys/vm/vfs_cache_pressure는 100으로 되어 있음.
      * /etc/sysctl.conf을 열어서 끝에 vm.swappiness=10와 vm.vfs_cache_pressure=50를 추가하고 리부팅
  * 13:44 Reduce SSD write ^YmI6i_Wrs
    * /etc/fstab을 수정해서 default로만 되어 있는 것을 다음과 같이 noatime 추가.
      * ```plain text
# / was on /dev/nvme0n1p5 during curtin installation
/dev/disk/by-uuid/e59406c6-43dd-4dc2-a821-5c458cfb6e0d / ext4 defaults,noatime 0 1```
  * 14:05 gnome sushi 설치 ^PTtr54WHC
    * 파일 탐색기에서 특정 파일 선택 후 space 누르면 해당 파일을 열지 않고도 빠르게 파악 가능.
  * 14:11 설정의 online account에서 google 계정 연결
  * 14:15 xkill 명령어를 shortcut(ctrl + esc)에 연결
  * 14:16 synaptic에서 tweak, gnome-tweak-tool, chrome-gnome-shell, gnome-shell-extensions 설치
  * 14:33 gnome-shell-extensions 홈페이지에 가서 arc와 dash-to-panel를 ON하여 설치하여 윈도우와 비슷하게 설정
  * 14:38 gufw firewall 설치
  * 14:52 vim 설치
  * 15:28 vscode에서 vim 쓰려면 neovim이 제일 낫고 그래서 어쩔 수 없이 neovim도 설치. 그런데 vsc neovim extension은 version 0.10.0 이상이 필요하다네...그래서 neovim 최신 버전 재설치
  * 15:48 시작 프로그램 보이기 ^ALvKdVxMV
    * ```shell
sudo sed -i 's/NoDisplay=true/Nodisplay=false/g' /etc/xdg/autostart/*.desktop```