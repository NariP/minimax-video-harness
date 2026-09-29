# Changelog

이 프로젝트의 주요 변경사항을 기록합니다.
형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)를 따르며,
[유의적 버전](https://semver.org/lang/ko/)을 사용합니다.

## [0.1.0] - 2026-09-29

첫 릴리스. 실제 호출로 검증한 레시피 1개와 공통 하네스.

### Added
- **harness/minimax.py** — `check` / `submit` / `poll` 3개 명령. 입력 한도 검증(참조 개수·길이·fps·요청 64MB),
  VP9/AV1 참조 영상 H.264 자동 변환, 참조 영상 길이를 포함한 예상 과금 초 표시,
  id당 1회 제출을 강제하는 원장(`raw/<id>/record.json`, 타임아웃은 `unknown`으로 기록),
  문서와 다른 실제 조회 경로(`/v2/query/video_generation/{id}`) 사용. 표준 라이브러리 + ffmpeg만 필요.
- **recipes/camera-transfer** — 레퍼런스 영상의 카메라 경로·컷 타이밍만 새 피사체/공간으로 옮기는 레시피
  (Genjutsu / 텔레포트 캠 스타일). 컷 시점 측정 명령, Ref2VA 6섹션 프롬프트 템플릿, 실패 증상별 수정표.
- **docs/gotchas.md** — API·과금·코덱·프롬프트 충돌 함정 모음(확인 날짜 표기).
- **skills/minimax-video-harness** — Claude Code / Codex 공용 스킬. 플러그인·심링크·클론 어디서든 레포 루트를 찾음.
- Claude Code / Codex 플러그인 매니페스트(`.claude-plugin/`, `.codex-plugin/`), 영문 README.

[0.1.0]: https://github.com/NariP/minimax-video-harness/releases/tag/v0.1.0
