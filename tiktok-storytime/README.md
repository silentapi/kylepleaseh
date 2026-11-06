# Storytime TikTok, Part 1 (Ben & Tina)

Final video: `../storytime_part1.mp4` (1080x1920, 30fps, about 87s, H.264/AAC, loudness -14 LUFS).

Everything is free and runs locally. There are no API keys and no paid services.

| Step | Tool |
|---|---|
| Narration | [Kokoro-82M](https://github.com/thewh1teagle/kokoro-onnx) (open-weight TTS), voice `am_onyx` (deep male) at 1.17x |
| Word timing and pronunciation check | faster-whisper `small.en` |
| Images | CC0 stock from Openverse (see credits) plus generated graphics |
| Music and sound effects | Synthesized in numpy (`audio.py`), so there are no copyright claims |
| Frames | Pillow (`render.py`), encoded with ffmpeg |

## Rebuild
```bash
pip install kokoro-onnx soundfile faster-whisper
# model files: kokoro-v1.0.onnx + voices-v1.0.bin from the kokoro-onnx GitHub release "model-files-v1.0"
mkdir -p build
python3 tts.py <models_dir> build     # narration + timing
python3 align.py build                # word timestamps
python3 audio.py build                # music, sfx, mix
python3 render.py build ../storytime_part1.mp4
```
To change the wording, edit `script.py` and rerun all four steps.

## Image credits (all CC0 / public domain)
- clock_4: Carol M. Highsmith (rawpixel)
- hosp_6, hwy_3, hwy_7: rawpixel public domain
- hosp_3: Oles Kanebckuu (StockSnap)
- mom_1: Family First (StockSnap)
- desk_3: Matt Moloney (StockSnap)
- typing_5: One Idea LLC (StockSnap)
- typing_3: Glenn Carstens-Peters (StockSnap)
