# Locate the locates — one command

    cd ~/src/work/milbird/hackathons/fig/locates
    ../.venv-tts/bin/python find_locates.py ~/Downloads/<your-video>.mov

Writes next to the video:
  locates_map.html   ← open this. Leaflet map, a pin per detection, frame thumbnail in each popup
  locates.geojson    ← the same detections as data
  frames/            ← sampled frames with the paint outlined and labelled

No API key, no network, no vendor. Runs on this laptop.

## Knobs if the first pass is wrong
  SAMPLE_EVERY_S   1.0   → 0.5 for denser sampling
  MIN_AREA_PX      900   → lower if real marks are being missed
  GROUND_FRACTION  0.45  → raise if the camera was held higher

## GPS
iPhone writes one ISO6709 point per clip, not a track. With it, detections are
anchored at the real corner and laid along the walk. Without it, they fall on a
synthetic line from 724 Pine St. Either way the map draws.
