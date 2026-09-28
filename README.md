# minimax-video-harness

MiniMax H3 영상 생성을 **검증된 레시피 + 공통 실행 하네스**로 묶은 모음.
공식 문서에는 없는 실전 함정과, 실제로 결과가 나온 프롬프트 구조만 담는다.

## 구성

```
harness/minimax.py     # 공통: 입력 검증·자동 변환 → 제출 → 조회 → 다운로드, 원장(중복 제출 방지)
recipes/<name>/        # 레시피: README(언제·어떻게·실패 시) + prompt.template.txt + job.example.json
skills/                # Claude Code / Codex용 SKILL.md (레시피 선택 → 실행 규칙)
docs/gotchas.md        # 공식 문서대로 했는데 안 되는 것
```

## 레시피

| 레시피 | 하는 일 | 상태 |
|---|---|---|
| [camera-transfer](recipes/camera-transfer/README.md) | 레퍼런스 영상의 카메라 경로·컷 타이밍만 새 피사체/공간으로 옮김 (Genjutsu 스타일) | ✅ 검증 |

## 빠른 시작

```bash
# 준비: Python 3.9+, ffmpeg/ffprobe, MiniMax Pay-as-you-go API 키
export MINIMAX_API_KEY=...            # 또는 ~/.config/minimax/.env 에 MINIMAX_API_KEY=...

cd recipes/camera-transfer
cp job.example.json job.json          # 입력 경로·id 수정, prompt.txt 작성
python3 ../../harness/minimax.py check  job.json
python3 ../../harness/minimax.py submit job.json
python3 ../../harness/minimax.py poll   camera-transfer-v1   # → raw/<id>/<id>.mp4
```

외부 의존성 없음(표준 라이브러리 + ffmpeg).

## 스킬로 쓰기

```bash
ln -s "$PWD/skills/minimax-video-harness" ~/.claude/skills/minimax-video-harness   # Claude Code
ln -s "$PWD/skills/minimax-video-harness" ~/.codex/skills/minimax-video-harness    # Codex
```

프롬프트 형식은 MiniMax 공식 스킬을 함께 설치해 쓴다: `npx skills add https://github.com/MiniMax-AI/MiniMax-H3 --skill h3-prompt-writing`

## 원칙

- **레시피는 실제로 성공한 것만** 올린다. 아이디어 단계는 올리지 않는다.
- **제출은 id당 한 번.** 실패하면 새 id로. 원장(`raw/<id>/record.json`)을 지우지 않는다.
- **참조 소재 저작권.** 남의 영상은 로컬 레퍼런스로만 쓰고 저장소에 넣지 않는다.

## 상세 문서

- 함정 모음: [docs/gotchas.md](docs/gotchas.md) — API 경로, 과금, 코덱, 프롬프트 충돌
- 카메라 트랜스퍼: [recipes/camera-transfer/README.md](recipes/camera-transfer/README.md) — 컷 측정 → 프롬프트 → 실행 → 실패 대처

## License

MIT
