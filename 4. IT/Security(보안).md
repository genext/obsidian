## USB 보안
usb를 꽂아도 해당 usb 내 프로그램이 자동실행되지 않도록 해야 안전.
### 1.  ubuntu
1. gnome
```
	# USB 자동실행 설정 확인
	gsettings get org.gnome.desktop.media-handling autorun-never
	
	# USB 자동실행 불가 설정
	gsettings set org.gnome.desktop.media-handling autorun-never true
```
2. udev
	gnome을 사용하지 않을 때 추가로 udev 설정 필요.
3.  /etc/fstab
```
	# fstab 파일에 아래 줄이 없어도 기본값은 noexec지만 확실하게 하려면 추가.
	/dev/sdb1 /mnt/usb ext4 defaults,noexec,nosuid,nodev 0 0
```
	
### 2. 일반 windows
- `Win + R`을 눌러 `regedit`을 입력
- `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer` 이동
- 우측 패널에서 우클릭 → 새로 만들기 → DWORD(32비트) 값을 선택
- 이름을 `NoDriveTypeAutoRun`으로 입력하고, 이진수값을 `5`로 설정
	- 5는 USB와 네트웍 드라이브 자동실행 방지.
- 재시작
### 3. windows Pro
- `Win + R`을 눌러 실행 창을 열고 `gpedit.msc`를 입력
- 컴퓨터 구성 > 관리 템플릿 > Windows 구성 요소 > 자동 실행 정책 이동
- "모든 드라이브에서 자동 실행 해제"를 선택하고 **사용**으로 설정
- 적용 후 재시작
