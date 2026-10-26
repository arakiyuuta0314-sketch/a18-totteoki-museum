# Totteoki Museum - Web playtest

Development source of truth: `web-tools-preview/a18/layout-test` on `main`, based on the validated P7-C lineage (`f5ce0c7`) and v10 art/quality fixes (`f19ba57`), merged as `af29122`.

**Do not edit GitHub Pages as the source.** Before publishing, compare the release copy with the authoritative development tree using `python a18/verify_v10_release_parity.py <release-repo-root>` from the `web-tools-preview` repository (17 runtime files, SHA-256 verified). See `docs/A18_ENTRANCE_V10_RELEASE_20261026.md`.

For image quality regression, the current isolated-Chrome test is `qa-v10-quality.cjs`; previous `qa-game-entrance-v09.cjs` covers the archived fixed-mask architecture and is not the current image-renderer acceptance gate.

Game photos are stored only in the browser IndexedDB; GitHub Pages hosts static HTML, JS, and image assets.
This is a public playtest build, not the iOS App Store version.

## Entrance art handoff (2026-10-26)

The entrance art asset-production phase is closed for now. **Frame OFF** is the future design baseline; the Lv.1 layout is not yet selected. See [the handoff record](docs/ENTRANCE_ART_HANDOFF_20261026.md) and [source checksum manifest](docs/entrance_art_baseline_20261026.json).
