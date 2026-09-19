"""Render any two-voice dialogue markdown to MP3 with local Kokoro.

    ../.venv-tts/bin/python tts.py prep-brief-script.md prep-brief.mp3
"""
import os, re, subprocess, sys, time
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SR, MAX = 24000, 380
V = {"R": ("af_heart", "en-us"), "J": ("bm_george", "en-gb")}

def clean(t):
    t = re.sub(r"\*\*(.*?)\*\*", r"\1", t); t = re.sub(r"[*_`#>]", "", t)
    return re.sub(r"\s+", " ", t).strip()

def chunk(t, lim=MAX):
    if len(t) <= lim: return [t]
    out, cur = [], ""
    for s in re.split(r"(?<=[.!?])\s+", t):
        if len(cur) + len(s) + 1 <= lim: cur = f"{cur} {s}".strip()
        else:
            if cur: out.append(cur)
            cur = s
    if cur: out.append(cur)
    return out

def main():
    src, out_mp3 = sys.argv[1], sys.argv[2]
    k = Kokoro(os.path.join(ROOT, ".tts-models", "kokoro-v1.0.onnx"),
               os.path.join(ROOT, ".tts-models", "voices-v1.0.bin"))
    sil = lambda s: np.zeros(int(SR * s), dtype=np.float32)
    t0 = time.time()

    raw_text = open(os.path.join(HERE, src)).read()
    turns = []
    for line in raw_text.splitlines():
        m = re.match(r"^\*\*([RJ])[:\*]+\s*(.*)", line.strip())
        if m and clean(m.group(2)): turns.append((m.group(1), clean(m.group(2))))

    if turns:                      # dialogue: alternating voices
        audio, prev = [sil(0.4)], None
        for who, text in turns:
            if prev is not None: audio.append(sil(0.22 if who == prev else 0.42))
            voice, lang = V[who]
            for piece in chunk(text):
                sm, sr = k.create(piece, voice=voice, speed=1.06, lang=lang)
                audio.append(sm.astype(np.float32))
            prev = who
    else:                          # narration: one voice, paragraph breaths
        voice, lang = V["J"]
        paras = [clean(x) for x in re.split(r"\n\s*\n", raw_text.split("---", 1)[-1])
                 if clean(x) and set(clean(x)) != {"-"}]
        turns = paras
        audio = [sil(0.4)]
        for i, para in enumerate(paras):
            if i: audio.append(sil(0.85))
            for piece in chunk(para):
                sm, sr = k.create(piece, voice=voice, speed=0.94, lang=lang)
                audio.append(sm.astype(np.float32))
    audio.append(sil(0.6))

    a = np.concatenate(audio); peak = float(np.max(np.abs(a))) or 1.0
    wav = out_mp3.replace(".mp3", ".wav")
    sf.write(os.path.join(HERE, wav), (a / peak * 0.89).astype(np.float32), SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(HERE, wav),
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-codec:a", "libmp3lame", "-b:a", "128k",
                    os.path.join(HERE, out_mp3)], check=True)
    os.remove(os.path.join(HERE, wav))
    print(f"{out_mp3}: {len(a)/SR/60:.1f} min, {len(turns)} turns, rendered in {time.time()-t0:.0f}s")

if __name__ == "__main__":
    main()
