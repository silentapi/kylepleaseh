# Storytime TikTok, Part 1 (Ben & Tina)

Final video: `../storytime_part1.mp4` (1080x1920, 30fps, 1:50, -14 LUFS). The script (`script.py`) is written as a storytime: cold open, dramatic irony, narrator asides, escalation in threes, a callback and a false ending before the cliffhanger. Delivery, quote-card labels and music cue points are set per line in the script. `../storytime_part1_nomusic.mp4` has narration and sound effects only, so you can add a TikTok sound in the app.

The older Kokoro pipeline (`tts.py` and `audio.py`) is still in the folder but is no longer used.

Everything is free and runs locally. There are no API keys and no paid services.

| Step | Tool |
|---|---|
| Narration | [Chatterbox](https://github.com/resemble-ai/chatterbox) (open-source, MIT). Every line is cloned from one fixed reference clip (`assets/voice/narrator_ref.wav`, a calm read made with the open Kokoro voice `am_onyx`), so it is the same deep, natural voice throughout. Delivery is calm by default and dramatic only on key beats (`tts_cb.py`). Two takes per line; `arrange.py` keeps the one Whisper hears correctly and whose pitch stays in the narrator's normal range. There is no pitch shifting and no reverb, only one uniform 9% pace-up |
| Beat sync | Every line starts on the music's beat grid. Quote cards land on beats, "She says no." gets a tape-stop and silence, and "Thursday" comes in on the saxophone entry |
| Word timing and pronunciation check | faster-whisper `small.en` |
| Images | CC0 stock from Openverse (see credits) plus generated graphics |
| Music | "ʀᴏsᴇᴍᴀʀʏʟʏɴɴ |sʟᴏᴡ|" by ᴍōʀᴇᴅōᴅɴᴀ (Jamendo, CC BY 3.0, https://www.jamendo.com/track/1511790). Credit is required: put it in the TikTok caption |
| Sound effects | Synthesized in numpy (`audio_music.py`) |
| Frames | Pillow (`render.py`), encoded with ffmpeg |

## Rebuild
```bash
pip install soundfile faster-whisper librosa
# Chatterbox needs torch 2.6 (CPU): pip install torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cpu && pip install chatterbox-tts
python tts_cb.py build_s3 2           # 2 takes per line in the fixed narrator voice (about 25 min on CPU)
python arrange.py build_s3            # pick takes, beat-grid layout
python align.py build_s3              # word timestamps for captions
python audio_music.py build_s3        # sax track, tape-stop, ducking, sfx
python render.py build_s3 ../storytime_part1.mp4
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
