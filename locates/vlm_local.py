"""Ask a local vision model whether a photo shows utility locate paint.

The hand-written colour detector scores 0/25 against the ground-truth set: it was
built for fresh fluorescent pigment and 84% of real marks are faded. This runs an
open-weights model over the same images so the two can be compared on the same
evidence.

    ../.venv-vision/bin/python vlm_local.py <photo dir> [--limit N]

Nothing leaves the machine.
"""
import sys, os, json, time, argparse, re
import torch
from transformers import AutoModelForImageTextToText, AutoProcessor
from PIL import Image

MID = "Qwen/Qwen2.5-VL-7B-Instruct"

# Named so the model cannot pass by reciting the colour list back — a failure a
# hosted model produced on the first frame we tried.
PROMPT = (
    "Look at this photograph of a pavement.\n\n"
    "Utility locate marks are spray paint applied to the ground before digging. "
    "APWA colour code: orange = communications/fiber, red = electric, yellow = gas, "
    "green = sewer, blue = water, pink = survey, purple = reclaimed water. "
    "They look like arrows, dashes, lines, ticks or short hand-lettering, sprayed "
    "freehand so the edges are soft. They are OFTEN FADED, dusty or worn — a faded "
    "mark is still a mark.\n\n"
    "NOT locate marks: painted kerbs, brick or terracotta paving, fallen leaves, "
    "road markings, manhole and vault covers, vehicles, graffiti, stains.\n\n"
    "Answer in exactly three lines, nothing else:\n"
    "PAINT: yes or no\n"
    "COLOURS: only the colours you can actually see, comma separated, or none\n"
    "WHAT: one short phrase describing the marking, or none"
)


def parse(text):
    paint = bool(re.search(r"PAINT:\s*yes", text, re.I))
    m = re.search(r"COLOURS:\s*([^\n]*)", text, re.I)
    cols = []
    if m:
        cols = [c.strip().lower() for c in m.group(1).split(",")
                if c.strip() and c.strip().lower() not in ("none", "n/a")]
    w = re.search(r"WHAT:\s*([^\n]*)", text, re.I)
    return paint, cols, (w.group(1).strip() if w else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("photodir")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default="vlm_results.json")
    a = ap.parse_args()

    files = sorted(f for f in os.listdir(a.photodir) if f.lower().endswith((".jpg", ".jpeg", ".png")))
    if a.limit:
        files = files[:a.limit]

    print(f"loading {MID} ...", flush=True)
    proc = AutoProcessor.from_pretrained(MID)
    model = AutoModelForImageTextToText.from_pretrained(MID, dtype=torch.bfloat16, device_map="mps")

    out = []
    for i, fn in enumerate(files, 1):
        img = Image.open(os.path.join(a.photodir, fn)).convert("RGB")
        msgs = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": PROMPT}]}]
        text = proc.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        inputs = proc(text=[text], images=[img], return_tensors="pt").to("mps")
        t0 = time.time()
        with torch.no_grad():
            ids = model.generate(**inputs, max_new_tokens=64, do_sample=False)
        reply = proc.batch_decode(ids[:, inputs.input_ids.shape[1]:], skip_special_tokens=True)[0].strip()
        paint, cols, what = parse(reply)
        # A model that names four or more colours is reciting the prompt, not reading
        # the image. Record it rather than scoring it as a detection.
        suspect = len(cols) >= 4
        out.append({"file": fn, "paint": paint, "colours": cols, "what": what,
                    "suspect_recital": suspect, "seconds": round(time.time() - t0, 1),
                    "raw": reply})
        print(f"  [{i:>3}/{len(files)}] {fn:<18} paint={str(paint):<5} "
              f"{','.join(cols) or '-':<22}{'  RECITAL?' if suspect else ''} {time.time()-t0:.1f}s", flush=True)

    json.dump(out, open(a.out, "w"), indent=1)
    print(f"\n  -> {a.out}")


if __name__ == "__main__":
    main()
