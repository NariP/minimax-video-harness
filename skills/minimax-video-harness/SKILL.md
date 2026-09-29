---
name: minimax-video-harness
description: Run MiniMax H3 video jobs through a tested harness and recipes. Use when the user wants to recreate a reference video's camera work with their own subject (Genjutsu / motion-transfer / "teleport camera" / orbit jump cut style), or to submit, poll and download H3 reference-to-video jobs safely. Korean triggers - 카메라 레퍼런스 따라하기, 이 영상처럼 카메라만, 겐주츠, 모션 트랜스퍼, 텔레포트 캠, 미니맥스로 생성.
---

# MiniMax Video Harness

## 0. Locate the repo root

`ROOT` = `${CLAUDE_PLUGIN_ROOT}` when that variable is set (Claude Code plugin install). Otherwise it is two directories above this SKILL.md (resolve symlinks), i.e. the directory that contains `harness/minimax.py`. Check it exists before continuing.

Work files (job.json, prompt.txt, inputs, the `raw/` ledger) live in the user's project directory, never inside `ROOT`.

## 1. Pick a recipe

| User wants | Recipe |
|---|---|
| Subject stays still, camera follows a reference video | `ROOT/recipes/camera-transfer/README.md` |

If nothing fits, say so; do not stretch a recipe.

## 2. Before writing anything

- Read `ROOT/docs/gotchas.md` once.
- Requirements: Python 3.9+, `ffmpeg`/`ffprobe`, `MINIMAX_API_KEY` (env var or `~/.config/minimax/.env`).
- For the prompt format, use the official `h3-prompt-writing` skill (Ref2VA six sections). If missing: `npx skills add https://github.com/MiniMax-AI/MiniMax-H3 --skill h3-prompt-writing`.

## 3. Run (from the user's project directory)

```bash
python3 "$ROOT/harness/minimax.py" check  job.json   # show estimated billed seconds to the user before submitting
python3 "$ROOT/harness/minimax.py" submit job.json
python3 "$ROOT/harness/minimax.py" poll   <job-id>   # → raw/<job-id>/<job-id>.mp4
```

Rules:
- Tell the user the estimated billed seconds before `submit`; generation costs money.
- Never resubmit the same id. A failed or unclear job gets a new id (`-v2`). Status `unknown` means check the provider console first.
- A download failure is not a generation failure: rerun `poll`.
- Hand the video to the user to review; do not claim it looks right without them.
