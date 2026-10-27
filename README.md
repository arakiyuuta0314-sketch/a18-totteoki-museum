# Totteoki Museum - Web playtest

Development source of truth: `web-tools-preview/a18/layout-test` on `main`. Historical v10 lineage: validated P7-C (`f5ce0c7`) and quality fixes (`f19ba57`), previously merged as `af29122`.

**Current published entrance Lv.1 (approved 2026-10-28):** the v09 light-oak wall behind the counter, v11 layered five-paper notices, accepted L-shaped counter and right partition with photo registration. The official layout and coordinates are fixed in [A18 entrance Lv.1 baseline](docs/A18_ENTRANCE_LV1_BASELINE_20261028.md). Public game: https://arakiyuuta0314-sketch.github.io/a18-totteoki-museum/layout-test/index.html .

**Do not edit GitHub Pages as the source.** Before publishing, compare the release copy with the authoritative development tree using `python a18/verify_current_release_parity.py <release-repo-root>` from `web-tools-preview` (265 published runtime and art files, SHA-256 checked with text newlines normalized). The earlier v10 procedure is preserved in `docs/A18_ENTRANCE_V10_RELEASE_20261026.md` as history.

For Lv.1 v11 release, Chrome QA covered entrance startup, right-wall photo registration, IndexedDB save/reload and the fixed museum layout regression. The older `qa-v10-quality.cjs` and `qa-game-entrance-v09.cjs` remain historical regression tools.

Game photos are stored only in the browser IndexedDB; GitHub Pages hosts static HTML, JS, and image assets.
This is a public playtest build, not the iOS App Store version.

## Entrance art handoff (2026-10-26)

The entrance art asset-production phase is closed for now. **Historical note (2026-10-26):** Frame OFF was the handoff reference at that time; the entrance Lv.1 layout has now been formally selected on 2026-10-28. See [the handoff record](docs/ENTRANCE_ART_HANDOFF_20261026.md) and [source checksum manifest](docs/entrance_art_baseline_20261026.json).
