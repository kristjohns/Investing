# Video: the Visa report, explained

`visa_explained.mp4` is a narrated, animated walk-through of `../visa_report.md`
(analysis date 17 October 2026, not personal financial advice). It has 15 chapters
(MP4 chapter markers), soft English subtitles, and a separate `visa_explained.srt`.

Pipeline, all offline once the models are downloaded:

| Step | File | What it does |
|---|---|---|
| Script | `narration.py` | Every narration line, keyed so scenes can sync to it |
| Speech | `speech.py` | Turns the text into speakable words, synthesises each line with Kokoro TTS, and checks every clip by transcribing it back with Whisper (`--check`) |
| Data | `data.py` | Loads the numbers from `analysis/output/` (run `analysis/run_all.py` first) |
| Look | `style.py` | Palette, type, chart helpers, and the `Chapter` base class that times animations to the narration |
| Scenes | `scenes/chNN_*.py` | One Manim scene per chapter |
| Build | `build.py` | Renders chapters in parallel, lays the narration under each at its recorded start times, normalises loudness (EBU R128), adds subtitles and chapters, and writes the MP4 |

```
pip install manim kokoro-onnx soundfile num2words sherpa-onnx   # plus LaTeX and ffmpeg
# models (≈1.2 GB, not in the repo) into video/models/:
#   kokoro-v1.0.onnx, voices-v1.0.bin   from github.com/thewh1teagle/kokoro-onnx/releases (model-files-v1.0)
#   sherpa-onnx-whisper-small.en/       from github.com/k2-fsa/sherpa-onnx/releases (asr-models), only for --check
python video/speech.py --check
python video/build.py render --final
python video/build.py assemble --final
```

Checking a change without watching 33 minutes of video:

- `python video/build.py review [--final] KEY ...` writes contact sheets (one frame near the end of
  every narration line) to `build/review/KEY/`, and names any frame with content closer than
  0.3 scene units (about 40 px at 1080p) to the left or right edge.
- `python video/build.py check [KEY ...]` runs the scenes at a tiny resolution and names any
  animation call that animates a group and one of its own members together, which in Manim leaves
  the member invisible.
- `python video/speech.py --check` transcribes every narration clip back to text and lists lines
  whose transcript drifts from the script (mispronunciations).
