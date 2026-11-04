# The Doomsday Map studio

Automated production for the YouTube channel The Doomsday Map (@TheDoomsdayMap): what-if scenarios for nuclear war,
great-power war and doomsday events, simulated minute by minute on real maps.

- `studio/` Python package: scenario engine, narration (Google Chirp 3 HD), YouTube upload, Telegram, QC.
- `video/` Remotion project: software-rendered globe (NASA Blue Marble and Black Marble), Natural Earth region maps,
  OpenStreetMap city maps with blast rings, HUD cards. Renders on CPU runners (no WebGL).
- `episodes/NNN-slug/` one folder per episode: research, scenario, script, shot list, metadata.
- `.github/workflows/` chunked renders and (later) the production, monitor and growth jobs.

Every simulation is labelled on screen and in the description. Nothing in a simulation segment has happened.
Map data: Natural Earth (public domain), OpenStreetMap contributors (ODbL) via OpenFreeMap and OpenMapTiles.
Imagery: NASA. Narration is AI-generated and disclosed.
