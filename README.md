# Limitless Ad Engine

Research competitor and aspirational-brand ads → write original Thai concepts → render creatives → review → deliver caption-and-image packs through a student gallery.

This is a working local-first MVP, derived from [Limitless Ad System](https://github.com/jetlauncher/limitless-ad-system). The original live deployment is unchanged. No paid scraper, AI generation, ad campaign or production deployment is started by cloning or building this repository.

## Start here

[Full Thai Google Doc](https://docs.google.com/document/d/1YpCwbuapteto5hN3khbKXZSGM7SilnHIjr4s4B4REbc/edit) — reverse engineering, operator SOP, student workflow, review rules and rollout plan.

Python 3.11 or later. The demo, pipeline and tests need no third-party packages.

```sh
git clone https://github.com/jetlauncher/limitless-ad-engine.git
cd limitless-ad-engine
python3 -m unittest discover -s tests -v
python3 engine.py build --catalog examples/rendered/catalog.json --pack-root examples/rendered --legacy legacy/manifest.json --out builds/my-preview
python3 -m http.server 8766 --bind 127.0.0.1 --directory builds/my-preview
```

Open http://localhost:8766. The demo contains 675 preserved legacy entries and three original, clearly marked training examples. Legacy media stays at its original public deployment; it is not bundled or granted a new license. Of the legacy records, 321 have captions and 354 do not. The three examples are not real offers and cannot pass the launch-export gate.

## Complete process

1. Create a local brand profile based on `examples/brand.json`. Supply the audience, actual offer, verified proof, CTA and real destination. Keep client data under `private/`.
2. Copy `config/watchlist.example.json` into `private/watchlist.json`. Distinguish direct competitors from aspirational brands. Verify exact Meta page IDs before enabling entries.
3. Preview the scrape request. The current actor uses `resultsLimit`, not the older `maxAds` parameter. Each brand is limited to 1–50 ads.

```sh
python3 engine.py scrape --watchlist private/watchlist.json
```

4. After choosing a total batch spend cap, supply `APIFY_TOKEN` as an environment variable and execute. This command incurs Apify charges; there is no paid run in CI.

```sh
python3 engine.py scrape --watchlist private/watchlist.json --out runs/first-scrape --execute --budget-usd 2
python3 engine.py collect --receipt runs/first-scrape/BRAND-run.json --out runs/first-collection
```

The $2 above is an example operator-selected maximum for the batch, not a quoted price. The cap is divided across brand runs. Collection is resumable: a running status asks you to collect later without starting a second scrape. Failed runs save a receipt and do not masquerade as complete data. If the initial POST has an uncertain network result, inspect Apify Runs before trying again. Page IDs, ad IDs, raw rows, capture time and run/dataset IDs are retained locally. Raw ads are excluded from Git and the static build.

5. Alternatively, import a downloaded Apify JSON export without paying for another run:

```sh
python3 engine.py normalize --raw examples/raw-ads.json --brand examples/reference-brand.json --out runs/fixture-references.json
python3 engine.py brief --references runs/fixture-references.json --brand examples/brand.json --out runs/creative-brief.json
```

The fixture is synthetic, not evidence of an actual advertiser. For production use, replace both fixture files with your real export and verified page record.

6. Generate three original concepts using your connected assistant and the resulting brief, or use the optional API adapter. The dry run prints a prompt. The paid run needs `OPENAI_API_KEY` and an explicitly selected `TEXT_MODEL` supporting Chat Completions JSON mode. No model price or availability is assumed.

```sh
python3 scripts/generate_copy.py --brief runs/creative-brief.json --out runs/concepts.json
# Paid API call, only when intended:
python3 scripts/generate_copy.py --brief runs/creative-brief.json --out runs/concepts.json --execute
```

7. Render PNGs with the included typography template, or create original images in Canva/image tools and populate the same pack schema. Install rendering dependencies in a virtual environment. Obtain Sarabun from its official font source and pass its local TTF path.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/render_pack.py --concepts examples/concepts.json --font /absolute/path/Sarabun-Bold.ttf --out runs/rendered-demo
```

The renderer creates actual 1080×1350 PNGs, individual JSON packs and `catalog.json`. It resets status to draft. It does not create photos or imitate reference brand identities. Human visual review is required, especially for Thai wrapping. For carousels, list every PNG in `assets` with consecutive `order` values; ZIPs preserve that order. Video reference viewing works; video launch packaging is a future extension.

8. Check each real pack, then record the human review into a new file. Demo packs cannot be approved. A changed caption, claim, destination or asset invalidates the approval hash.

```sh
python3 engine.py validate --pack runs/rendered/AD-ID.json --root runs/rendered
python3 scripts/approve_pack.py --pack runs/rendered/AD-ID.json --root runs/rendered --out runs/rendered/AD-ID-approved.json --reviewer "Actual reviewer name" --confirm-reviewed
python3 engine.py export --pack runs/rendered/AD-ID-approved.json --root runs/rendered --out runs/AD-ID-launch-pack.zip
```

Before using `--confirm-reviewed`, the named person must actually inspect the image, caption, offer, claims, rights and destination. This records a review; it does not make a campaign live. The archive includes ordered PNGs, verbatim caption, headline, destination/CTA, proof, approval metadata and manifest.

9. Assemble chosen pack objects and reference records into one JSON array, then build the gallery. Use the approved JSON object, not the previous draft object, in that array. All original asset paths are relative to `--pack-root`; copy or organize the files there. Every build needs a fresh output directory.

```sh
python3 engine.py build --catalog private/catalog.json --pack-root private/assets --out builds/student-cohort-01
```

Only approved original packs get ZIP download links. Drafts stay visibly draft; competitor references remain study-only. Serve only the build output. Do not deploy the repository root. `vercel.json` builds the demo into `dist/`; deployment and student access are deliberately manual. A private GitHub repo does not make a Vercel site private. The static MVP has no student login, per-student data isolation or durable favorites.

## Repository map

- `engine.py`: dry-run/paid scrape, receipt collection, normalization, brief assembly, legacy migration, pack QA, ZIP export and static build.
- `scripts/`: original copy generation, PNG rendering and recorded human approval.
- `web/`: Thai mobile-friendly gallery, search, angle/status filters, modal, caption copying and downloads.
- `legacy/`: exact original HTML/JS/CSS and the 675-entry manifest for migration/audit. Media is external.
- `examples/`: synthetic scraper fixture, brand profile, original demo concepts and rendered PNGs.
- `docs/PROCESS-TH.md`: operator and student handbook, architecture, curriculum, rollout and limitations.
- `docs/source-audit.json`: verified source match and SHA-256 checksums.
- `tests/`: export integrity, approval invalidation, identity checking, deduplication, safe builds and file safeguards.
- `.github/workflows/check.yml`: offline tests and a downloadable static preview artifact. No scraping schedule or deployment.

## What's verified and what's still manual

Implemented and locally tested: normalization, deduplication, source retention, draft generation contract, PNG rendering, legacy migration, filters, caption copy, validation, approval hash, ZIP integrity and safe static build. Paid Apify execution and paid OpenAI generation are adapter code verified against current documentation; they have not been exercised with paid live calls in this delivery. There is no autonomous end-to-end image generation, campaign launch, conversion measurement, authentication or scheduled refresh.

The complete historical creative-generation environment was not recovered from the deployed website. The legacy source and scripts show how the gallery was assembled; the new engine supplies a reproducible standard workflow. Do not infer competitor performance, ROAS or conversion rate from how long an ad is visible.

## License

Source code uses the original MIT license. That license does not grant rights to advertiser creatives, original-gallery imagery, personal likenesses, trademarks or third-party fonts. The three demo layouts/captions are original training examples. Use references to study mechanics and create your own work.

## Sources

[Original gallery](https://limitless-ad-gallery-deploy.vercel.app/) · [Original repository](https://github.com/jetlauncher/limitless-ad-system) · [Apify actor input](https://apify.com/apify/facebook-ads-scraper/input) · [Run API](https://docs.apify.com/api/v2/actors-runs-post) · [Dataset pagination](https://docs.apify.com/api/v2/dataset-items-get)
