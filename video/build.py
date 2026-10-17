"""Build the explainer video.

    python video/speech.py --check                 # 1. narration audio (+ speech-recognition check)
    python video/build.py render [--final] [keys]  # 2. render chapters with Manim (parallel)
    python video/build.py assemble [--final]       # 3. audio + video + subtitles + chapters -> MP4
    python video/build.py frames KEY t1 t2 ...     #    stills from a rendered chapter, for review
    python video/build.py review [--final] KEY ... #    contact sheets, one frame per line; flags edge crowding
    python video/build.py check [keys]             #    flags animations that would leave a mobject invisible

Preview quality is 854x480 at 15 fps; --final is 1920x1080 at 30 fps.
Needs: manim (with LaTeX), ffmpeg, numpy, soundfile.
"""
import json
import math
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from narration import chapters  # noqa: E402
from speech import shown  # noqa: E402

BUILD = HERE / "build"
SCENES = HERE / "scenes"
OUT_NAME = "visa_explained"
SR_OUT = 48000

QUALITY = {False: {"res": "854,480", "fps": 15, "dir": "480p15"},
           True: {"res": "1920,1080", "fps": 30, "dir": "1080p30"}}


def scene_files():
    """{chapter key: (file, class name)} from scenes/chNN_key.py."""
    out = {}
    for _, key, _, _ in chapters():
        f = next(SCENES.glob(f"ch*_{key}.py"), None)
        if f is None:
            continue
        cls = next(l.split()[1].split("(")[0] for l in f.read_text().splitlines() if l.startswith("class Ch"))
        out[key] = (f, cls)
    return out


def render_one(key, final):
    f, cls = scene_files()[key]
    q = QUALITY[final]
    cmd = ["manim", "render", "--disable_caching", "-r", q["res"], "--fps", str(q["fps"]),
           "--media_dir", str(BUILD / "media" / key), "-v", "WARNING", "--progress_bar", "none", str(f), cls]
    # each chapter gets its own media dir: parallel renders sharing Manim's text cache race on temp files
    log = BUILD / "logs" / f"{key}-{q['dir']}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(log, "w") as fh:
        r = subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT, cwd=HERE)
    status = "ok" if r.returncode == 0 else f"FAILED (see {log.relative_to(HERE)})"
    print(f"render {key}: {status}", flush=True)
    return r.returncode


def render(keys, final, jobs):
    keys = keys or [k for _, k, _, _ in chapters()]
    with ThreadPoolExecutor(max_workers=jobs) as ex:
        codes = list(ex.map(lambda k: render_one(k, final), keys))
    if any(codes):
        sys.exit(1)


def video_path(key, final):
    f, cls = scene_files()[key]
    return BUILD / "media" / key / "videos" / f.stem / QUALITY[final]["dir"] / f"{cls}.mp4"


def probe_duration(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _balanced(words, n):
    """Split a word list into n chunks of roughly equal character length."""
    total = sum(len(w) + 1 for w in words)
    out, cur, acc = [], [], 0
    for w in words:
        cur.append(w)
        acc += len(w) + 1
        if acc >= total * (len(out) + 1) / n and len(out) < n - 1:
            out.append(" ".join(cur))
            cur = []
    if cur:
        out.append(" ".join(cur))
    return out


def _split_long(text, max_chars):
    if len(text) <= max_chars:
        return [text]
    # prefer a clause boundary near the middle
    cands = [m.end() for m in re.finditer(r"[,:;] ", text)]
    good = [c for c in cands if len(text[:c].strip()) <= max_chars and len(text[c:].strip()) <= max_chars]
    if good:
        c = min(good, key=lambda c: abs(c - len(text) / 2))
        return [text[:c].strip(), text[c:].strip()]
    if cands:
        c = min(cands, key=lambda c: abs(c - len(text) / 2))
        return _split_long(text[:c].strip(), max_chars) + _split_long(text[c:].strip(), max_chars)
    return _balanced(text.split(), math.ceil(len(text) / max_chars))


def _two_rows(c):
    if len(c) <= 42:
        return c
    ws = c.split()
    best = min(range(1, len(ws)), key=lambda i: max(len(" ".join(ws[:i])), len(" ".join(ws[i:]))))
    return " ".join(ws[:best]) + "\n" + " ".join(ws[best:])


def split_caption(text, max_chars=84):
    """Subtitle cues of at most two ~42-character rows, split at sentences, then clauses."""
    sentences = re.split(r"(?<=[.?!])\s+", text.strip())
    cues = []
    for sent in sentences:
        for piece in _split_long(sent, max_chars):
            if cues and len(cues[-1]) + 1 + len(piece) <= max_chars and (len(piece) < 30 or len(cues[-1]) < 30):
                cues[-1] = f"{cues[-1]} {piece}"
            else:
                cues.append(piece)
    return [_two_rows(c) for c in cues]


def assemble(final):
    q = QUALITY[final]
    durations = json.loads((BUILD / "durations.json").read_text())
    texts = {f"{ck}/{k}": shown(t) for _, ck, _, ls in chapters() for k, t in ls}
    work = BUILD / f"assemble-{q['dir']}"
    work.mkdir(parents=True, exist_ok=True)
    concat, cues, chapter_marks, offset = [], [], [], 0.0
    audio_parts = []
    for i, key, title, _ in chapters():
        tl = json.loads((BUILD / "timeline" / q["dir"] / f"{key}.json").read_text())
        vp = video_path(key, final)
        vdur = probe_duration(vp)
        # audio bed for this chapter: each clip placed at its recorded start time
        bed = np.zeros(int(round(vdur * SR_OUT)) + SR_OUT, dtype=np.float32)
        for line in tl["lines"]:
            clip_key = f"{key}/{line['key']}"
            x, sr = sf.read(BUILD / durations[clip_key]["file"], dtype="float32")
            if sr != SR_OUT:
                g = math.gcd(SR_OUT, sr)
                x = resample_poly(x, SR_OUT // g, sr // g).astype(np.float32)
            a = int(round(line["start"] * SR_OUT))
            bed[a:a + len(x)] += x[:max(0, len(bed) - a)]
            # subtitles: spread the line's duration over its cues by character count
            parts = split_caption(texts[clip_key])
            total_chars = sum(len(p) for p in parts)
            t0 = offset + line["start"]
            for p in parts:
                dt = line["duration"] * len(p) / total_chars
                cues.append((t0, t0 + dt, p))
                t0 += dt
        bed = bed[:int(round(vdur * SR_OUT))]
        audio_parts.append(bed)
        concat.append(vp)
        chapter_marks.append((offset, title if i else "Introduction"))
        offset += vdur
    audio = np.concatenate(audio_parts)
    peak = np.abs(audio).max()
    raw_wav = work / "narration_raw.wav"
    sf.write(raw_wav, audio / max(peak, 1e-9) * 0.9, SR_OUT, subtype="PCM_24")

    # loudness-normalise the narration (EBU R128, -16 LUFS, true peak -1.5 dBTP)
    wav = work / "narration.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(raw_wav), "-af",
                    "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", str(SR_OUT), str(wav)], check=True)

    # subtitles
    srt = work / f"{OUT_NAME}.srt"
    srt.write_text("".join(f"{n}\n{srt_time(a)} --> {srt_time(b)}\n{t}\n\n" for n, (a, b, t) in enumerate(cues, 1)),
                   encoding="utf-8")
    # chapters metadata
    meta = work / "chapters.txt"
    lines = [";FFMETADATA1", "title=Visa (NYSE: V): the investment report, explained",
             "comment=Analysis date 17 October 2026. Not personal financial advice."]
    for j, (t, name) in enumerate(chapter_marks):
        end = chapter_marks[j + 1][0] if j + 1 < len(chapter_marks) else offset
        lines += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={int(t * 1000)}", f"END={int(end * 1000)}",
                  f"title={j:02d} {name}" if j else "title=00 Introduction"]
    meta.write_text("\n".join(lines) + "\n", encoding="utf-8")
    # video concat (same codec settings in every chapter, so stream copy works)
    lst = work / "concat.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in concat))
    video = work / "video.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                    str(video)], check=True)
    out = HERE / (f"{OUT_NAME}.mp4" if final else f"{OUT_NAME}_preview.mp4")
    # Manim already wrote H.264; copy it unless REENCODE=1 asks for a smaller (slower, second-generation) file
    vcodec = (["-c:v", "libx264", "-preset", "slow", "-crf", os.environ.get("CRF", "20"), "-tune", "animation",
               "-pix_fmt", "yuv420p"] if os.environ.get("REENCODE") == "1" else ["-c:v", "copy"])
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-i", str(wav), "-i", str(srt), "-i", str(meta),
                    "-map", "0:v", "-map", "1:a", "-map", "2:s", "-map_metadata", "3", "-map_chapters", "3", *vcodec,
                    "-c:a", "aac", "-b:a", "96k", "-c:s", "mov_text", "-metadata:s:s:0", "language=eng",
                    "-metadata:s:a:0", "language=eng", "-movflags", "+faststart", str(out)], check=True)
    (HERE / f"{OUT_NAME}.srt").write_text(srt.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"wrote {out.relative_to(HERE.parent)} ({out.stat().st_size / 1e6:.1f} MB, {offset / 60:.1f} min) "
          f"and {OUT_NAME}.srt ({len(cues)} cues)")


def frames(key, times, final):
    vp = video_path(key, final)
    out = BUILD / "frames" / key
    out.mkdir(parents=True, exist_ok=True)
    for t in times:
        p = out / f"{key}_{float(t):07.2f}.png"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", str(vp), "-frames:v", "1", str(p)], check=True)
        print(p)


FRAME_WIDTH = 8 * 16 / 9          # Manim scene units across the frame
SAFE = 0.3                        # content closer than this to the left or right edge gets flagged


def side_margins(png):
    """Gap (scene units) between each side edge and the nearest non-background pixel, below the chapter tag."""
    from PIL import Image
    a = np.asarray(Image.open(png).convert("RGB")).astype(int)
    h, w, _ = a.shape
    ink = (np.abs(a[h * 90 // 1080:] - (0x1a, 0x1a, 0x19)).sum(axis=2) > 40).any(axis=0)
    cols = np.flatnonzero(ink)
    if not len(cols):
        return None
    return cols[0] * FRAME_WIDTH / w, (w - 1 - cols[-1]) * FRAME_WIDTH / w


def review(key, final, per_sheet=12):
    """Contact sheets: one frame near the end of every narration line, labelled with its key."""
    from PIL import Image, ImageDraw, ImageFont
    q = QUALITY[final]
    tl = json.loads((BUILD / "timeline" / q["dir"] / f"{key}.json").read_text())
    vp = video_path(key, final)
    out = BUILD / "review" / key
    out.mkdir(parents=True, exist_ok=True)
    shots = []
    for line in tl["lines"]:
        t = line["start"] + max(line["duration"] - 0.3, 0.1)
        p = out / f"{line['key']}.png"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", str(vp), "-frames:v", "1", str(p)], check=True)
        shots.append((line["key"], p))
        m = side_margins(p)
        if m and min(m) < SAFE:
            print(f"  {key}/{line['key']}: content {min(m):.2f} units from the {'left' if m[0] < m[1] else 'right'} edge")
    font = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Regular.otf", 22)
    sheets = []
    for n in range(0, len(shots), per_sheet):
        chunk = shots[n:n + per_sheet]
        ims = [Image.open(p) for _, p in chunk]
        w, h = ims[0].size
        cols = 3
        rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * w, rows * (h + 30)), "white")
        d = ImageDraw.Draw(sheet)
        for i, ((k, _), im) in enumerate(zip(chunk, ims)):
            x, y = (i % cols) * w, (i // cols) * (h + 30)
            sheet.paste(im, (x, y + 30))
            d.text((x + 6, y + 2), k, fill="black", font=font)
        sp = out / f"sheet{n // per_sheet + 1}.png"
        sheet.save(sp)
        sheets.append(sp)
        print(sp)
    return sheets


def check(keys):
    """Run every scene at a tiny resolution and flag play() calls that animate a mobject together with one of its
    ancestors. The second animation's begin() snapshots the state the first one has just reset (a FadeIn's zero
    opacity), so the child silently ends in that state: invisible."""
    import importlib.util
    import shutil
    from manim import Scene, config
    from manim.animation.animation import Animation
    from manim.animation.composition import AnimationGroup

    config.pixel_width, config.pixel_height, config.frame_rate = 64, 36, 5
    config.write_to_movie, config.disable_caching = False, True
    config.media_dir, config.verbosity, config.progress_bar = str(BUILD / "media" / "_check"), "ERROR", "none"

    def leaves(a):
        if isinstance(a, AnimationGroup):
            for b in a.animations:
                yield from leaves(b)
        elif isinstance(a, Animation):
            yield a
        elif hasattr(a, "build"):                     # mob.animate builder
            yield a.build()

    found = []
    play = Scene.play

    def checked_play(scene, *args, **kwargs):
        mobs = [a.mobject for x in args for a in leaves(x)]
        for m in mobs:
            family = {id(f) for f in m.get_family()}
            for n in mobs:
                if n is not m and id(n) in family:
                    line = scene.timeline[-1]["key"] if getattr(scene, "timeline", None) else "title"
                    found.append(f"{scene.KEY}/{line}: {type(n).__name__} animated together with a group containing it")
        return play(scene, *args, **kwargs)

    Scene.play = checked_play
    try:
        for key, (f, cls) in scene_files().items():
            if keys and key not in keys:
                continue
            spec = importlib.util.spec_from_file_location(f.stem, f)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            getattr(mod, cls)().render()
    finally:
        Scene.play = play
        shutil.rmtree(BUILD / "timeline" / f"{config.pixel_height}p{config.frame_rate}", ignore_errors=True)
    print("\n".join(found) or "no conflicting animations")
    return len(found)


if __name__ == "__main__":
    args = sys.argv[1:]
    final = "--final" in args
    args = [a for a in args if a != "--final"]
    jobs = int(os.environ.get("JOBS", "4"))
    if not args:
        print(__doc__)
    elif args[0] == "render":
        render(args[1:], final, jobs)
    elif args[0] == "assemble":
        assemble(final)
    elif args[0] == "frames":
        frames(args[1], args[2:], final)
    elif args[0] == "review":
        for k in args[1:]:
            review(k, final)
    elif args[0] == "check":
        sys.exit(1 if check(args[1:]) else 0)
