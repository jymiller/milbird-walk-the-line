"""Render the briefing and story to MP3 with Kokoro — a local neural TTS.

No API key, no account, no network at render time. The model lives in
../.tts-models and runs on CPU at roughly 4x realtime on Apple Silicon.

    ../.venv-tts/bin/python render_kokoro.py
"""
import os, re, subprocess, sys, time

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MODEL = os.path.join(ROOT, ".tts-models", "kokoro-v1.0.onnx")
VOICES = os.path.join(ROOT, ".tts-models", "voices-v1.0.bin")

# R: the researcher, American, warm, a little pleased with herself.
# J: the sceptic, British, dry. Keeps the accent contrast the script was written for.
VOICE_R, LANG_R = "af_heart", "en-us"
VOICE_J, LANG_J = "bm_george", "en-gb"

SR = 24000
MAX_CHARS = 380          # keep each synth call well inside Kokoro's token window


def clean(t):
    t = re.sub(r"\*\*(.*?)\*\*", r"\1", t)
    t = re.sub(r"[*_`#>]", "", t)
    return re.sub(r"\s+", " ", t).strip()


def chunk(text, limit=MAX_CHARS):
    """Split on sentence boundaries so no single call overruns the model."""
    if len(text) <= limit:
        return [text]
    parts, cur = [], ""
    for sent in re.split(r"(?<=[.!?])\s+", text):
        if len(cur) + len(sent) + 1 <= limit:
            cur = f"{cur} {sent}".strip()
        else:
            if cur:
                parts.append(cur)
            cur = sent
    if cur:
        parts.append(cur)
    return parts


def silence(seconds):
    return np.zeros(int(SR * seconds), dtype=np.float32)


def main():
    for p in (MODEL, VOICES):
        if not os.path.exists(p):
            sys.exit(f"missing model file: {p}")

    k = Kokoro(MODEL, VOICES)
    t0 = time.time()

    def synth(text, voice, lang, speed=1.0):
        out = []
        for piece in chunk(text):
            samples, sr = k.create(piece, voice=voice, speed=speed, lang=lang)
            assert sr == SR, sr
            out.append(samples.astype(np.float32))
        return np.concatenate(out) if out else silence(0)

    def to_mp3(audio, out_mp3):
        wav = out_mp3.replace(".mp3", ".wav")
        peak = float(np.max(np.abs(audio))) or 1.0
        sf.write(wav, (audio / peak * 0.89).astype(np.float32), SR)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav,
                        "-codec:a", "libmp3lame", "-b:a", "128k", out_mp3], check=True)
        os.remove(wav)

    # ---------- briefing ----------
    turns = []
    for raw in open(os.path.join(HERE, "podcast-script.md")):
        m = re.match(r"^\*\*([RJ])[:\*]+\s*(.*)", raw.strip())
        if m and clean(m.group(2)):
            turns.append((m.group(1), clean(m.group(2))))

    audio, prev = [silence(0.4)], None
    for i, (who, text) in enumerate(turns):
        if prev is not None:
            # a shorter beat when the same person continues, longer on a handover
            audio.append(silence(0.22 if who == prev else 0.42))
        if who == "R":
            audio.append(synth(text, VOICE_R, LANG_R))
        else:
            audio.append(synth(text, VOICE_J, LANG_J))
        prev = who
        if (i + 1) % 20 == 0:
            print(f"  briefing {i+1}/{len(turns)} turns  ({time.time()-t0:.0f}s)")
    audio.append(silence(0.8))
    to_mp3(np.concatenate(audio), os.path.join(HERE, "executable-world-briefing.mp3"))
    print(f"  briefing done: {len(turns)} turns ({time.time()-t0:.0f}s)")

    # ---------- story ----------
    body = open(os.path.join(HERE, "story.md")).read().split("---", 1)[1]
    paras = [clean(x) for x in re.split(r"\n\s*\n", body)
             if clean(x) and set(clean(x)) != {"-"}]
    audio = [silence(0.4)]
    for i, para in enumerate(paras):
        if i:
            audio.append(silence(0.85))
        audio.append(synth(para, VOICE_J, LANG_J, speed=0.94))
        if (i + 1) % 10 == 0:
            print(f"  story {i+1}/{len(paras)} paragraphs  ({time.time()-t0:.0f}s)")
    audio.append(silence(0.8))
    to_mp3(np.concatenate(audio), os.path.join(HERE, "three-thirty-one.mp3"))
    print(f"  story done: {len(paras)} paragraphs ({time.time()-t0:.0f}s)")

    for f in ("executable-world-briefing.mp3", "three-thirty-one.mp3"):
        p = os.path.join(HERE, f)
        d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                            "-of", "default=nw=1:nk=1", p], capture_output=True, text=True).stdout
        print(f"{f}: {float(d)/60:.1f} min, {os.path.getsize(p)//1024} KB")


if __name__ == "__main__":
    main()
