# minimax-video-harness

[한국어](README.ko.md)

Tested recipes and a small execution harness for **MiniMax H3** video generation.
It holds only what the official docs don't tell you: prompt structures that actually produced a usable result, and the pitfalls hit on real runs.

## What's inside

```
harness/minimax.py     # shared: validate + auto-transcode inputs → submit → poll → download, duplicate-safe ledger
recipes/<name>/        # README (when / how / what to do when it fails) + prompt.template.txt + job.example.json
skills/                # SKILL.md for Claude Code / Codex (pick a recipe → run rules)
docs/gotchas.md        # things that break even when you follow the docs
```

## Recipes

| Recipe | What it does | Status |
|---|---|---|
| [camera-transfer](recipes/camera-transfer/README.md) | Moves only the camera path and cut timing of a reference video onto your own subject and scene ("Genjutsu" / teleport-camera style) | ✅ tested |

## Install

### Claude Code (plugin)

```
/plugin marketplace add NariP/minimax-video-harness
/plugin install minimax-video-harness@minimax-video-harness
```

### Codex CLI (plugin)

```bash
git clone https://github.com/NariP/minimax-video-harness
cd minimax-video-harness
codex plugin marketplace add "$(pwd)"
codex plugin add minimax-video-harness@minimax-video-harness
```

### Without plugins

Clone and run `harness/minimax.py` directly (see Quick start). No dependencies beyond the Python standard library and ffmpeg.

For prompt format, also install MiniMax's official skill:
`npx skills add https://github.com/MiniMax-AI/MiniMax-H3 --skill h3-prompt-writing`

## Quick start

```bash
# Requirements: Python 3.9+, ffmpeg/ffprobe, a MiniMax Pay-as-you-go API key
export MINIMAX_API_KEY=...            # or put MINIMAX_API_KEY=... in ~/.config/minimax/.env

mkdir my-shot && cd my-shot
cp <repo>/recipes/camera-transfer/job.example.json job.json   # edit id and input paths
cp <repo>/recipes/camera-transfer/prompt.template.txt prompt.txt   # fill it in
python3 <repo>/harness/minimax.py check  job.json   # estimated billed seconds
python3 <repo>/harness/minimax.py submit job.json
python3 <repo>/harness/minimax.py poll   camera-transfer-v1   # → raw/<id>/<id>.mp4
```

## Principles

- **Only recipes that actually worked** get added. No idea-stage recipes.
- **One submit per job id.** A failed job gets a new id. The ledger (`raw/<id>/record.json`) is never deleted.
- **Respect reference copyright.** Use other people's videos only as local references; never commit them.

## Docs

- Pitfalls: [docs/gotchas.md](docs/gotchas.md) — API paths, billing, codecs, prompt conflicts
- Camera transfer: [recipes/camera-transfer/README.md](recipes/camera-transfer/README.md) — measure cuts → prompt → run → fix failures
- Changes: [CHANGELOG.md](CHANGELOG.md)

Recipe and gotcha docs are currently in Korean.

## License

MIT
