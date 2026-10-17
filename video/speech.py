"""Narration text -> speakable words -> audio clips (Kokoro TTS), plus an ASR check.

    python video/speech.py            # synthesise every changed line, write durations
    python video/speech.py --check    # also transcribe each clip back and flag mismatches
    python video/speech.py --print    # just print the spoken text

Models (not in the repo, ~360 MB): kokoro-v1.0.onnx and voices-v1.0.bin from
https://github.com/thewh1teagle/kokoro-onnx/releases (tag model-files-v1.0), and for
--check the sherpa-onnx Whisper small.en export from
https://github.com/k2-fsa/sherpa-onnx/releases (tag asr-models). Point MODELS_DIR /
ASR_DIR at them.
"""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

import numpy as np
from num2words import num2words

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from narration import chapters  # noqa: E402

BUILD = HERE / "build"
AUDIO = BUILD / "audio"
DURATIONS = BUILD / "durations.json"
MODELS_DIR = Path(os.environ.get("MODELS_DIR", HERE / "models"))
ASR_DIR = Path(os.environ.get("ASR_DIR", MODELS_DIR / "sherpa-onnx-whisper-small.en"))
VOICE, SPEED, LANG = "af_heart", 1.05, "en-us"
SR = 24000

MONTHS = ("January February March April May June July August September October November "
          "December").split()

# whole-word replacements applied to the spoken text (after numbers are expanded)
WORDS = [
    ("S&P", "S and P"), ("P/E", "P E"), ("non-GAAP", "non-gap"), ("GAAP", "gap"),
    ("DCF", "D C F"), ("CAPM", "cap M"), ("EPS", "E P S"), ("IRR", "I R R"),
    ("ROIC", "R O I C"), ("CAGR", "kagger"), ("UPI", "U.P.I."), ("ASK", "A.S.K."),
    ("US", "U S"), ("UK", "U K"), ("EU", "E U"), ("VisaNet", "Visa Net"),
]
RESPELL = [(r"\bkrone\b", "krona")]  # TTS reads "krone" as one syllable ("crone"); "krona" gives KROH-nuh
PROTECT = ["W-8BEN"]  # tokens with digits that must not be expanded


def _int_words(s: str) -> str:
    return num2words(int(s.replace(",", ""))).replace(",", "")


def _num_words(s: str) -> str:
    """'1,894.90' -> 'one thousand eight hundred and ninety-four point nine' (trailing zeros dropped)."""
    s = s.replace(",", "")
    if "." in s:
        whole, frac = s.split(".")
        frac = frac.rstrip("0")
        if frac:
            return _int_words(whole or "0") + " point " + " ".join(num2words(int(d)) for d in frac)
        s = whole
    return _int_words(s)


def _year_words(y: int) -> str:
    if 2000 <= y <= 2009:
        return "two thousand" + ("" if y == 2000 else " " + num2words(y - 2000))
    hi, lo = divmod(y, 100)
    return num2words(hi) + " " + (num2words(lo) if lo >= 10 else f"oh {num2words(lo)}" if lo else "hundred")


def shown(text: str) -> str:
    return re.sub(r"\{([^|{}]*)\|([^{}]*)\}", r"\1", text)


def spoken(text: str) -> str:
    t = re.sub(r"\{([^|{}]*)\|([^{}]*)\}", r"\2", text)
    keep = {}
    for i, tok in enumerate(PROTECT):
        if tok in t:
            ph = f"\x00{chr(65 + i)}\x00"  # placeholder must not contain digits
            keep[ph] = tok
            t = t.replace(tok, ph)
    month = "|".join(MONTHS)
    t = re.sub(rf"\b(\d{{1,2}}) ({month})(?: (\d{{4}}))?",
               lambda m: f"the {num2words(int(m.group(1)), to='ordinal')} of {m.group(2)}"
                         + (f", {_year_words(int(m.group(3)))}" if m.group(3) else ""), t)
    t = re.sub(r"\$(\d[\d,]*(?:\.\d+)?)\s?(bn|m|k)\b",
               lambda m: f"{_num_words(m.group(1))} {dict(bn='billion', m='million', k='thousand')[m.group(2)]} dollars", t)
    t = re.sub(r"\$(\d[\d,]*(?:\.\d+)?) (trillion|billion|million)",
               lambda m: f"{_num_words(m.group(1))} {m.group(2)} dollars", t)
    t = re.sub(r"\$(\d[\d,]*)\.(\d\d)\b",
               lambda m: f"{_int_words(m.group(1))} dollars and {_int_words(m.group(2))} cents", t)
    t = re.sub(r"\$(\d[\d,]*)\b", lambda m: f"{_int_words(m.group(1))} dollars", t)
    t = re.sub(r"(\d[\d,]*(?:\.\d+)?)%", lambda m: f"{_num_words(m.group(1))} percent", t)
    t = re.sub(r"(\d+(?:\.\d+)?)×", lambda m: f"{_num_words(m.group(1))} times", t)
    t = re.sub(r"\b(\d+)(st|nd|rd|th)\b", lambda m: num2words(int(m.group(1)), to="ordinal"), t)
    t = re.sub(r"(?<![\d,.])(1[89]\d\d|20\d\d)(?!\d|[,.]\d)", lambda m: _year_words(int(m.group(1))), t)
    t = re.sub(r"\d[\d,]*(?:\.\d+)?", lambda m: _num_words(m.group(0).rstrip(",")) + ("," if m.group(0).endswith(",") else ""), t)
    for a, b in WORDS:
        t = re.sub(rf"(?<![\w/-]){re.escape(a)}(?![\w/-])", b, t)
    for a, b in RESPELL:
        t = re.sub(a, b, t)
    for k, v in keep.items():
        t = t.replace(k, v)
    assert not re.search(r"\d|\$|%", re.sub("|".join(map(re.escape, PROTECT)), "", t)), t
    t = re.sub(r"\s+", " ", t).strip()
    return re.sub(r"(^|[.?!] )([a-z])", lambda m: m.group(1) + m.group(2).upper(), t)


def lines():
    for ci, ck, title, ls in chapters():
        for k, text in ls:
            yield ck, k, text


def clip_path(ck, k, text):
    h = hashlib.sha1(f"{VOICE}|{SPEED}|{spoken(text)}".encode()).hexdigest()[:10]
    return AUDIO / ck / f"{k}-{h}.wav"


def trim(x, sr=SR, thresh_db=-45.0, keep=0.04):
    """Cut leading/trailing silence, keeping `keep` seconds on each side."""
    env = np.abs(x)
    th = 10 ** (thresh_db / 20) * max(env.max(), 1e-9)
    idx = np.nonzero(env > th)[0]
    if not len(idx):
        return x
    a, b = max(idx[0] - int(keep * sr), 0), min(idx[-1] + int(keep * sr), len(x))
    return x[a:b]


def synthesise():
    import soundfile as sf
    from kokoro_onnx import Kokoro
    tts = Kokoro(str(MODELS_DIR / "kokoro-v1.0.onnx"), str(MODELS_DIR / "voices-v1.0.bin"))
    durations = {}
    for ck, k, text in lines():
        p = clip_path(ck, k, text)
        if not p.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
            for old in p.parent.glob(f"{k}-*.wav"):
                old.unlink()
            samples, sr = tts.create(spoken(text), voice=VOICE, speed=SPEED, lang=LANG)
            assert sr == SR
            sf.write(p, trim(samples.astype(np.float32)), SR, subtype="FLOAT")
            print(f"synth {ck}/{k}")
        info = sf.info(p)
        durations[f"{ck}/{k}"] = {"file": str(p.relative_to(BUILD)), "duration": info.frames / info.samplerate,
                                  "shown": shown(text), "spoken": spoken(text)}
    DURATIONS.write_text(json.dumps(durations, indent=1))
    total = sum(d["duration"] for d in durations.values())
    words = sum(len(d["spoken"].split()) for d in durations.values())
    print(f"{len(durations)} clips, {total / 60:.1f} min of speech, {words / (total / 60):.0f} words/min")


def _canon(s: str) -> list[str]:
    """Comparable word list: numbers spelled out the same way, punctuation dropped,
    and runs of single letters joined ('d c f' == 'dcf')."""
    try:
        s = spoken(s)
    except AssertionError:  # ASR output with a pattern spoken() doesn't cover
        s = re.sub(r"\d[\d,]*(?:\.\d+)?", lambda m: " " + _num_words(m.group(0).rstrip(",")) + " ", s)
    s = re.sub(r"[^a-z' ]+", " ", s.lower().replace("-", " ")).replace("'", "")
    out, prev_single = [], False
    for w in s.split():
        if len(w) == 1 and prev_single:
            out[-1] += w
        else:
            out.append(w)
        prev_single = len(w) == 1
    return out


def _wer(ref, hyp):
    d = list(range(len(hyp) + 1))
    for i, r in enumerate(ref, 1):
        prev, d[0] = d[0], i
        for j, h in enumerate(hyp, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (r != h))
    return d[-1] / max(len(ref), 1)


def check(limit=0.12):
    import sherpa_onnx
    import soundfile as sf
    rec = sherpa_onnx.OfflineRecognizer.from_whisper(
        encoder=str(ASR_DIR / "small.en-encoder.int8.onnx"), decoder=str(ASR_DIR / "small.en-decoder.int8.onnx"),
        tokens=str(ASR_DIR / "small.en-tokens.txt"), num_threads=os.cpu_count() or 2)
    durations = json.loads(DURATIONS.read_text())
    report, flagged = [], 0
    for key, d in durations.items():
        x, sr = sf.read(BUILD / d["file"], dtype="float32")
        hyp_text = ""
        # Whisper sees at most 30 s at a time: transcribe long clips in pieces
        step = 25 * sr
        for a in range(0, len(x), step):
            st = rec.create_stream()
            st.accept_waveform(sr, x[a:a + step + sr // 2])
            rec.decode_stream(st)
            hyp_text += " " + st.result.text
        ref, hyp = _canon(d["spoken"]), _canon(hyp_text)
        w = _wer(ref, hyp)
        flagged += w > limit
        report.append({"key": key, "wer": round(w, 3), "spoken": d["spoken"], "heard": hyp_text.strip()})
    report.sort(key=lambda r: -r["wer"])
    (BUILD / "asr_check.json").write_text(json.dumps(report, indent=1))
    print(f"ASR check: {flagged} of {len(report)} clips above WER {limit:.0%}")
    for r in report[:25]:
        print(f"{r['wer']:.2f} {r['key']}\n   said : {r['spoken']}\n   heard: {r['heard']}")


if __name__ == "__main__":
    if "--print" in sys.argv:
        for ck, k, text in lines():
            print(f"[{ck}/{k}] {spoken(text)}")
        sys.exit()
    synthesise()
    if "--check" in sys.argv:
        check()
