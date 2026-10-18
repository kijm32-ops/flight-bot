# Project

## Purpose

PTIS(Personal Template). SerpAPI로 할인된 Google Flights 운임을 찾아 GitHub Pages 보고서를 발행하고, 요약을 본인 KakaoTalk "나와의 채팅"으로 보낼 수 있다. 설치본마다 자기 GitHub 저장소, SerpAPI 키, Kakao Developers 앱을 쓴다. 이 저장소는 공개(public)다.

## Architecture

- Frontend: GitHub Pages로 발행되는 정적 보고서
- Backend: Python 스크립트(`main.py` 등)를 GitHub Actions가 실행. 의존성은 `requests`, `tenacity`, `cryptography`
- Database: 없음. `data/` 아래 JSON 상태 파일(`state.json`, 암호화된 `kakao_auth.json`)

## Important directories

- `.github/workflows/` — 정기 실행(`schedule.yml`), 갱신(`ptis-update.yml`), 템플릿 빌드(`build-template.yml`), 검증(`validate.yml`), 설정 이슈 처리 등
- `.ptis/update_manifest.json` — 템플릿에 포함되는 파일 목록(managed / seed_if_missing / protected)
- `data/` — 런타임 상태 파일
- `assets/` — 정적 자원
- `CHECKPOINT.md`, `TASK.md` — 프로젝트 인수인계 기록

## Environments

### Development

- 로컬 Python 환경. CI는 Python 3.11을 쓴다. 로컬 설치 상태는 확인하지 않았다.

### Production / Deployment target

- GitHub Actions 정기 실행과 GitHub Pages. 파생 템플릿은 `flight-bot-template`이다.

## Invariants

- Kakao 암호화 키(`KAKAO_TOKEN_ENCRYPTION_KEY`), Kakao Client Secret, 평문 refresh token, API 키를 절대 commit하지 않는다.
- `data/state.json`과 `data/kakao_auth.json`은 깨끗한 템플릿에 들어가면 안 된다. `build_template.py`가 막는다.
- 템플릿에 들어가는 파일은 `.ptis/update_manifest.json`이 정한다. 새 파일을 템플릿에 포함하려면 manifest를 갱신한다.
- `chore: 상태 데이터 갱신 [skip ci]` commit이 자동으로 쌓인다. 이 자동 갱신 흐름을 깨는 변경은 피한다.
- SerpAPI 호출 수와 정기 작업 수가 늘어나는 변경은 명시적으로 밝힌다(`CHECKPOINT.md`가 이를 추적한다).
- 이 저장소는 공개이므로 저장소 쓰기 권한을 제한한다. 쓰기 권한자는 secret을 읽는 워크플로를 바꿀 수 있다.
