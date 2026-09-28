#!/usr/bin/env python3
"""MiniMax H3 video harness: build → submit → poll → download, with a ledger.

    python3 harness/minimax.py check  job.json      # validate inputs, show billed-seconds estimate
    python3 harness/minimax.py submit job.json      # one POST per job id (ledger refuses duplicates)
    python3 harness/minimax.py poll   <job-id>      # wait, then download the mp4

A job file describes one request; see recipes/*/job.example.json.
Local paths in a job file are resolved relative to the job file.
"""
import base64
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.error
import urllib.request

API = "https://api.minimax.io"
CREATE = f"{API}/v2/video_generation"
QUERY = f"{API}/v2/query/video_generation/{{task_id}}"  # docs say /v2/video_generation/{id} → 404
OK_VCODECS = {"h264", "hevc"}
LEDGER = pathlib.Path(os.environ.get("MMH_LEDGER", "raw"))
MAX_BODY = 64 * 1024 * 1024


def api_key():
    if os.environ.get("MINIMAX_API_KEY"):
        return os.environ["MINIMAX_API_KEY"]
    env = pathlib.Path(os.environ.get("MINIMAX_ENV_FILE", "~/.config/minimax/.env")).expanduser()
    if env.exists():
        for line in env.read_text().splitlines():  # read only the key line, never source the file
            if line.startswith("MINIMAX_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"')
    sys.exit("MINIMAX_API_KEY not set (env var, MINIMAX_ENV_FILE, or ~/.config/minimax/.env)")


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=codec_name,r_frame_rate:format=duration", "-of", "json", str(path)],
        capture_output=True, text=True, check=True).stdout
    info = json.loads(out)
    num, den = info["streams"][0]["r_frame_rate"].split("/")
    return info["streams"][0]["codec_name"], float(info["format"]["duration"]), float(num) / float(den)


def prepare_video(path):
    """Return a path H3 accepts; transcode VP9/AV1 (e.g. Instagram reels) to H.264."""
    codec, dur, fps = probe(path)
    if not 2 <= dur <= 15:
        sys.exit(f"{path}: reference video must be 2-15s, got {dur:.2f}s")
    if not 23.976 <= round(fps, 3) <= 60:
        sys.exit(f"{path}: frame rate must be 23.976-60fps, got {fps:.3f}")
    if codec in OK_VCODECS:
        return path, dur
    out = path.with_name(path.stem + ".h264.mp4")
    if not out.exists():
        print(f"transcoding {path.name} ({codec}) → {out.name}")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-crf", "18", "-c:a", "aac", "-movflags", "+faststart", str(out)], check=True)
    return out, dur


def media_url(ref, kind):
    if ref.startswith(("http://", "https://", "mm_file://", "data:")):
        return ref
    p = pathlib.Path(ref)
    mime = {"image": f"image/{p.suffix.lstrip('.').lower().replace('jpg', 'jpeg')}",
            "video": "video/mp4", "audio": f"audio/{p.suffix.lstrip('.').lower()}"}[kind]
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def load_job(job_path):
    job_path = pathlib.Path(job_path)
    job = json.loads(job_path.read_text())
    base = job_path.parent

    def local(ref):
        return ref if ref.startswith(("http://", "https://", "mm_file://", "data:")) else str((base / ref).resolve())

    for k in ("reference_images", "reference_videos", "reference_audios"):
        job[k] = [local(r) for r in job.get(k, [])]
    for k in ("first_frame", "last_frame"):
        if job.get(k):
            job[k] = local(job[k])
    job["prompt"] = (base / job["prompt_file"]).read_text() if "prompt_file" in job else job["prompt"]
    return job


def build(job):
    frames = [k for k in ("first_frame", "last_frame") if job.get(k)]
    refs = job["reference_images"] + job["reference_videos"] + job["reference_audios"]
    if frames and refs:
        sys.exit("first/last frame and reference_* are mutually exclusive in H3")
    if len(job["reference_images"]) > 9 or len(job["reference_videos"]) > 3 or len(job["reference_audios"]) > 3:
        sys.exit("limits: ≤9 reference images, ≤3 reference videos, ≤3 reference audios")

    content = [{"type": "text", "text": job["prompt"]}]
    ref_seconds = 0.0
    for k in frames:
        content.append({"type": "image_url", "image_url": {"url": media_url(job[k], "image")}, "role": k})
    for r in job["reference_images"]:
        content.append({"type": "image_url", "image_url": {"url": media_url(r, "image")}, "role": "reference_image"})
    for r in job["reference_videos"]:
        if not r.startswith(("http", "mm_file", "data:")):
            path, dur = prepare_video(pathlib.Path(r))
            r, ref_seconds = str(path), ref_seconds + dur
        content.append({"type": "video_url", "video_url": {"url": media_url(r, "video")}, "role": "reference_video"})
    for r in job["reference_audios"]:
        content.append({"type": "audio_url", "audio_url": {"url": media_url(r, "audio")}, "role": "reference_audio"})
    if ref_seconds > 15:
        sys.exit(f"total reference video must be ≤15s, got {ref_seconds:.2f}s")

    body = {"model": job.get("model", "MiniMax-H3"), "content": content,
            "resolution": job.get("resolution", "768P"), "duration": int(job["duration"])}
    if job.get("ratio"):
        body["ratio"] = job["ratio"]
    if job.get("prompt_expansion_mode"):
        body["extra"] = {"prompt_expansion_mode": job["prompt_expansion_mode"]}
    size = len(json.dumps(body))
    if size > MAX_BODY:
        sys.exit(f"request body {size / 1e6:.1f}MB > 64MB; host large files and pass URLs instead")
    return body, ref_seconds


def cmd_check(job_path):
    job = load_job(job_path)
    body, ref_seconds = build(job)
    billed = body["duration"] + ref_seconds
    print(json.dumps({"id": job["id"], "model": body["model"], "resolution": body["resolution"],
                      "duration": body["duration"], "ratio": body.get("ratio", "adaptive"),
                      "reference_video_seconds": round(ref_seconds, 2),
                      "estimated_billed_seconds": round(billed, 2)}, indent=1))
    return job, body


def cmd_submit(job_path):
    job, body = cmd_check(job_path)
    rec = LEDGER / job["id"] / "record.json"
    rec.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(rec, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        sys.exit(f"{rec} exists: job already submitted. Use a new id (e.g. -v2) instead of resubmitting.")
    meta = {"id": job["id"], "job_file": str(job_path), "status": "submitting", "submitted_at": time.time()}
    os.write(fd, json.dumps(meta, indent=1).encode())
    os.close(fd)
    req = urllib.request.Request(CREATE, data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {api_key()}", "Content-Type": "application/json"})
    try:
        meta.update(status="submitted", response=json.load(urllib.request.urlopen(req, timeout=180)))
    except urllib.error.HTTPError as e:
        meta.update(status="failed", error=f"HTTP {e.code}: {e.read().decode()[:2000]}")
    except Exception as e:  # timeout etc: the task may exist — check the console, do not blindly resubmit
        meta.update(status="unknown", error=repr(e))
    rec.write_text(json.dumps(meta, indent=1))
    print(json.dumps({k: meta.get(k) for k in ("status", "response", "error") if k in meta}))


def cmd_poll(job_id, interval=20):
    rec = LEDGER / job_id / "record.json"
    meta = json.loads(rec.read_text())
    task_id = meta["response"]["task_id"]
    while True:
        req = urllib.request.Request(QUERY.format(task_id=task_id), headers={"Authorization": f"Bearer {api_key()}"})
        task = json.load(urllib.request.urlopen(req, timeout=60))
        task = task.get("task", task)
        if task.get("status") in ("succeeded", "failed", "cancelled"):
            break
        print(f"{task.get('status')}…", flush=True)
        time.sleep(interval)
    meta.update(status=task["status"], task=task)
    rec.write_text(json.dumps(meta, indent=1))
    if task["status"] != "succeeded":
        sys.exit(f"{task['status']}: {json.dumps(task)[:1500]}")
    out = rec.parent / f"{job_id}.mp4"
    urllib.request.urlretrieve(task["content"]["url"], out)  # download failure ≠ generation failure: rerun poll
    print(f"saved {out}  usage={task.get('usage')}")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("check", "submit", "poll"):
        sys.exit(__doc__)
    {"check": cmd_check, "submit": cmd_submit, "poll": cmd_poll}[sys.argv[1]](sys.argv[2])
