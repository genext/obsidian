# 환경 구성
## 1. vsc
- 작업 디렉토리 생성
- 파이썬 가상환경 설정 `python -m venv .venv` 후
- jupyter extension 설치
	- 새 jupyter notebook 생성
	- jupyter kernel을 `.venv`로 설정
## 2. cli
시도하지 않았지만 이런 방법도 있다.
Link my environment to my IDE or Jupyter notebook??
```bash
python -m ipykernel install --user --name=.venv
```

# notebook download
웹에 있는 것을 ipynb 확장자 파일로 다운 받아서 vsc에서 바로 열 수 있다. 그 후 kernel만 내 환경 `.venv`를 선택하면 된다.