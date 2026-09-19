"""Render the briefing and story to audio with macOS `say`, concatenated with ffmpeg.

Picks the best voices actually installed (Premium > Enhanced > legacy) and inserts
real pauses between turns, which matters as much as timbre for listenability.

    python3 render.py            # auto-pick voices
    python3 render.py --list     # show what it would pick, render nothing
"""
import os, re, shutil, subprocess, sys

SEG = "seg"

# Preference order. Premium/Enhanced only exist after you download them in
# System Settings > Accessibility > Spoken Content > System Voice > Manage Voices.
FEMALE = ["Ava (Premium)", "Zoe (Premium)", "Allison (Premium)", "Susan (Premium)",
          "Joelle (Premium)", "Samantha (Enhanced)", "Ava (Enhanced)", "Samantha"]
MALE   = ["Evan (Premium)", "Nathan (Premium)", "Tom (Premium)", "Evan (Enhanced)",
          "Daniel (Enhanced)", "Daniel", "Alex"]


def installed_voices():
    out = subprocess.run(["say", "-v", "?"], capture_output=True, text=True).stdout
    names = []
    for line in out.splitlines():
        m = re.match(r"^(.*?)\s{2,}([a-z]{2}_[A-Z]{2})", line)
        if m:
            names.append(m.group(1).strip())
    return names


def pick(prefs, available, fallback):
    for p in prefs:
        if p in available:
            return p
    return fallback


def clean(t):
    t = re.sub(r"\*\*(.*?)\*\*", r"\1", t)
    t = re.sub(r"[*_`#>]", "", t)
    return re.sub(r"\s+", " ", t).strip()


def say(text, voice, path, rate):
    subprocess.run(["say", "-v", voice, "-r", str(rate), "-o", path, text], check=True)


def silence(path, seconds):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
                    "-i", f"anullsrc=r=22050:cl=mono", "-t", str(seconds),
                    "-c:a", "pcm_s16be", path], check=True)


def concat(paths, out):
    lst = os.path.join(SEG, "list.txt")
    with open(lst, "w") as f:
        for p in paths:
            f.write(f"file '{os.path.abspath(p)}'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", lst, "-c:a", "aac", "-b:a", "128k", out], check=True)


def duration(f):
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", f], capture_output=True, text=True).stdout
    return float(d.strip())


def main():
    avail = installed_voices()
    vf = pick(FEMALE, avail, "Samantha")
    vm = pick(MALE, avail, "Daniel")
    premium = "(Premium)" in vf or "(Premium)" in vm or "(Enhanced)" in vf or "(Enhanced)" in vm
    print(f"voices: R={vf!r}  J={vm!r}" + ("" if premium else "   <- legacy only; download Premium voices for a real improvement"))
    if "--list" in sys.argv:
        return

    os.makedirs(SEG, exist_ok=True)
    # Premium voices read more naturally slightly slower than the legacy ones.
    rate_pod, rate_story = (168, 156) if premium else (172, 158)

    gap_turn = os.path.join(SEG, "gap_turn.aiff")
    gap_para = os.path.join(SEG, "gap_para.aiff")
    silence(gap_turn, 0.35)
    silence(gap_para, 0.75)

    # ---- briefing: alternating voices, a beat between turns ----
    turns = []
    for raw in open("podcast-script.md"):
        m = re.match(r"^\*\*([RJ])[:\*]+\s*(.*)", raw.strip())
        if m and clean(m.group(2)):
            turns.append((m.group(1), clean(m.group(2))))
    voice = {"R": vf, "J": vm}
    paths = []
    for i, (who, text) in enumerate(turns):
        p = os.path.join(SEG, f"p{i:03d}.aiff")
        say(text, voice[who], p, rate_pod)
        paths += [p, gap_turn]
    concat(paths, "executable-world-briefing.m4a")
    print(f"  briefing: {len(turns)} turns")

    # ---- story: one voice, longer breaths between paragraphs ----
    body = open("story.md").read().split("---", 1)[1]
    paras = [clean(x) for x in re.split(r"\n\s*\n", body)
             if clean(x) and set(clean(x)) != {"-"}]
    spaths = []
    for i, para in enumerate(paras):
        p = os.path.join(SEG, f"s{i:03d}.aiff")
        say(para, vm, p, rate_story)
        spaths += [p, gap_para]
    concat(spaths, "three-thirty-one.m4a")
    print(f"  story: {len(paras)} paragraphs")

    for f in ("executable-world-briefing.m4a", "three-thirty-one.m4a"):
        print(f"{f}: {duration(f)/60:.1f} min, {os.path.getsize(f)//1024} KB")
    shutil.rmtree(SEG)


if __name__ == "__main__":
    main()
