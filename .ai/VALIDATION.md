# Validation

아래는 `.github/workflows/validate.yml`이 실제로 실행하는 검증이다. CI는 Linux 기준이며 Windows에서는 `*.py` 글롭을 풀어서 실행한다.

## Pre-check

- `git status`
- placeholder 검사: `<REQUIRED:`

## Backend

- `python -m pip install -r requirements.txt` 와 `pip install pyyaml`
- `python -m py_compile *.py`
- `python -m unittest`

## Frontend

- 없음 (정적 보고서)

## Database

- 없음 (JSON 상태 파일)

## Final

- 워크플로·이슈 템플릿 YAML 파싱 (`validate.yml`의 "Parse GitHub YAML" 단계)
- 템플릿 빌드: `python build_template.py --output <저장소 밖 임시 폴더>` 후 `trip-settings` 관련 파일 존재 확인
- `git diff --check`
- `git diff`
- 예상 외 파일 변경 여부 확인
