#!/bin/bash
# FALLBACK: no Memories.ai needed. Pull frames + contact sheets from the sidewalk
# video so a vision model (Claude, right here in this session) can read the locates.
#   ./fallback_frames.sh /path/to/sidewalk.mp4 [fps]
set -euo pipefail
IN="${1:?usage: fallback_frames.sh video.mp4 [fps]}"
FPS="${2:-0.5}"                      # 0.5 = one frame every 2s -> ~90 frames for 3 min
OUT="$(pwd)/frames_$(basename "${IN%.*}")"
mkdir -p "$OUT"
# individual frames, downscaled but still legible for 2-inch paint lines
ffmpeg -y -hide_banner -loglevel error -i "$IN" -vf "fps=$FPS,scale=-2:1080" -q:v 2 "$OUT/f_%04d.jpg"
# contact sheets, 12 frames each - one image per sheet to hand a model.
# drawtext burns the timestamp in, but not every ffmpeg build ships it, so fall back.
if ! ffmpeg -y -hide_banner -loglevel error -i "$IN" \
      -vf "fps=$FPS,drawtext=text='%{pts\\:hms}':x=8:y=8:fontsize=28:fontcolor=yellow:box=1:boxcolor=black@0.6,scale=-2:540,tile=3x4" \
      "$OUT/sheet_%02d.jpg" 2>/dev/null; then
  echo "(this ffmpeg has no drawtext - building plain sheets, read time off the frame number)"
  ffmpeg -y -hide_banner -loglevel error -i "$IN" \
    -vf "fps=$FPS,scale=-2:540,tile=3x4" "$OUT/sheet_%02d.jpg"
fi
echo "frames : $(ls "$OUT"/f_*.jpg | wc -l | tr -d ' ')  in $OUT"
echo "sheets : $(ls "$OUT"/sheet_*.jpg 2>/dev/null | wc -l | tr -d ' ')  in $OUT"
echo
echo "Frame N is at t = (N-1)/$FPS seconds."
echo "Now: drag $OUT/sheet_01.jpg into Claude and ask ->"
echo "  'Utility locate markings, APWA color code. For each painted mark: timestamp,"
echo "   color, shape (line/dash/arrow/text/box), and what it means. Say UNCLEAR"
echo "   rather than guessing between orange and red. Do not call traffic paint,"
echo "   crosswalks, curb paint or ADA pads a locate.'"
