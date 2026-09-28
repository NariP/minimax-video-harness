---
name: minimax-video-harness
description: Run MiniMax H3 video jobs through a tested harness and recipes. Use when the user wants to recreate a reference video's camera work with their own subject (Genjutsu / motion-transfer / "teleport camera" / orbit jump cut style), or to submit, poll and download H3 reference-to-video jobs safely. Korean triggers - 카메라 레퍼런스 따라하기, 이 영상처럼 카메라만, 겐주츠, 모션 트랜스퍼, 텔레포트 캠, 미니맥스로 생성.
---

# MiniMax Video Harness

Repo root = the directory containing `harness/minimax.py`. Paths below are relative to it.

## 1. Pick a recipe

| User wants | Recipe |
|---|---|
| Subject stays still, camera follows a reference video | `recipes/camera-transfer/README.md` |

If nothing fits, say so; do not stretch a recipe.

## 2. Before writing anything

- Read `docs/gotchas.md` once.
- For the prompt format, use the official `h3-prompt-writing` skill (Ref2VA six sections). Install: `npx skills add https://github.com/MiniMax-AI/MiniMax-H3 --skill h3-prompt-writing`.

## 3. Run

```bash
python3 harness/minimax.py check  <job.json>   # show estimated billed seconds to the user before submitting
python3 harness/minimax.py submit <job.json>
python3 harness/minimax.py poll   <job-id>
```

Rules:
- Tell the user the estimated billed seconds before `submit`; generation costs money.
- Never resubmit the same id. A failed or unclear job gets a new id (`-v2`). Status `unknown` means check the provider console first.
- A download failure is not a generation failure: rerun `poll`.
- Hand the video to the user to review; do not claim it looks right without them.
