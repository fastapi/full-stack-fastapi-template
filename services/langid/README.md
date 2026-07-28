# langid-svc

Language identification using [lingua](https://github.com/pemistahl/lingua-rs),
restricted to English and French.

The odd one out among the services: **no weights, no GPU, no torch, no mount.**
lingua ships its n-gram data inside the wheel, so this container has no `/data`
dependency at all. 338 MB, ready in ~6 s.

## Why it exists

It replaced fastText (`lid.176.bin`), which was the last in-process model in the
backend. Removing it let the backend drop `app/core/ml.py`, its lifespan model
loading, and the `/data/aimodels` mount entirely — the backend now holds no
weights of any kind.

fastText was also the single blocker on moving the backend to a newer Python:
`fasttext-wheel` 0.9.2 publishes **no binary wheels at all**, only an sdist, so
any Python without a prebuilt wheel means compiling a 2023 C++ extension.

## Package naming, because it is genuinely confusing

| Thing | Version line |
|---|---|
| `lingua-rs` (the Rust crate on GitHub) | 1.8.x |
| `lingua-language-detector` (the PyPI package used here) | **2.x** |

They are different artifacts with independent versioning. PyPI's Homepage field
points at `lingua-rs`, which does not help.

Pinned `>=2.1.1` and deliberately not capped: 2.2.0+ requires Python >=3.12, and
uv honours `requires-python`, so this upgrades itself if the base image moves to
3.12+. On the current 3.11 base it resolves to 2.1.1, which has `cp310`–`cp313`
manylinux wheels.

## The en+fr restriction — and what it costs

Measured against fastText on the same inputs before switching:

| Case | fastText | lingua en+fr | lingua 7-lang |
|---|---|---|---|
| EN long | en 0.919 | **en 0.978** | en 0.897 |
| FR med | fr 0.970 | **fr 1.000** | fr 0.997 |
| EN short | en 0.952 | en 0.897 | **nl 0.519** ❌ |
| FR short | fr 0.696 | **fr 0.831** | fr 0.262 |
| EN tiny "Yes." | en 0.866 | en 0.634 | en 0.277 |
| Spanish | **es 0.915** ✅ | **en 0.553** ❌ | pt 0.368 ✅ |
| German | **de 0.989** ✅ | **en 0.639** ❌ | de 0.927 ✅ |
| "12345 67.89" | en 0.167 | **none** ✅ | none ✅ |

**On genuine EN/FR, en+fr-restricted lingua beats fastText**, including on short
segments — which is the actual workload (10–200 char bitext).

**The cost, accepted knowingly:** with only two languages, confidences are
normalised across those two, so the detector cannot say "this is Spanish".
Non-EN/FR text is reported as whichever of the two it resembles. No threshold
fixes this — German-as-English scores **0.639** while a genuine `"Yes."` scores
**0.634**; the distributions overlap.

Widening the language set restores rejection but wrecks short-segment accuracy
(`"Open the door."` comes back as Dutch). Since the corpus is Canadian EN/FR
bitext, the restriction is the right trade. **It would be the wrong trade for
mixed-language input** — set `LANGUAGES` wider if that ever changes, and re-tune
the caller-side threshold.

lingua does still return no language when its own minimum-relative-distance rule
can't decide, so digits, symbols and empty strings correctly come back as
`null` — that part of the old behaviour survives.

## API

| Route | Purpose |
|---|---|
| `GET /health` | Liveness |
| `GET /ready` | Readiness — 503 until the n-gram models are loaded |
| `GET /v1/info` | Languages, accuracy mode, thresholds |
| `POST /v1/detect` | `{texts[]}` → `{results: [{language, score}]}` in input order |

```bash
curl -s localhost:8075/v1/detect -H 'content-type: application/json' \
  -d '{"texts":["Open the door.","Ouvrez la porte.","12345"]}'
```

`language` is an ISO 639-1 code or `null`. Detection is batched and parallelised
in Rust via `compute_language_confidence_values_in_parallel`.

## Configuration

| Var | Default | Notes |
|---|---|---|
| `LANGUAGES` | `en,fr` | ISO 639-1, comma separated. At least two required. |
| `MIN_CONFIDENCE` | `0.0` | Extra floor below which language is reported as null. Off by default. |
| `MAX_TEXTS_PER_REQUEST` | `8192` | Returns 413 rather than a huge request. |
| `LOW_ACCURACY_MODE` | `false` | Lower memory, worse on short text — the opposite of why lingua was chosen. |
| `PRELOAD` | `true` | Build n-gram models at startup so `/ready` means ready. |

## Callers

`app/core/langid_client.py` in the backend, used by:

- `app/models_ml/language_detect.py` → the `/api/v1/sentences/*` routes
- `align_sentences_uni` in `app/models_ml/labse.py` → `/api/v1/memory/align-uni`,
  which splits a mixed list into EN and FR buckets before aligning

Text is passed through **unchanged**. The old fastText path lowercased first;
capitalisation is a signal lingua uses, so lowercasing would throw accuracy away.
