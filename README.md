
> wheel local download 
>
> `pip download {package_name} -d {directory}`
> `pip download {package_name} -d wheels-for-offline`


#### `venv` 생성
```bash
python -m venv .venv
```

#### `venv` 활성화
```bash
# Windows
.\.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

#### `.wheels` 설치 방법(Offline)
```bash
pip install --no-index --find-links ".\wheels-for-offline" -r requirements.txt
```

#### `requirements.txt` 설치 방법(Online)
```bash
pip install -r requirements.txt
```

#### `uvicorn` 실행 방법
```bash
cd app
uvicorn main:app --reload
```

