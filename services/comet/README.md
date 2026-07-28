# qe-svc

Reference-free quality estimation (CometKiwi). Source + MT in, scores out.

Second container in the `workbench-services` split, following the same shape as
[`../labse`](../labse). See that README for the reasoning behind the pattern.

## Why this one earns its own container

`unbabel-comet` is the most constrained dependency in the stack. Locked on its
own it resolves very differently from the embedding service:

| | qe-svc | labse-svc | backend (one lock, all models) |
|---|---|---|---|
| `transformers` | **4.57.6** | **5.14.1** | 4.51.3 |
| `numpy` | **1.26.4** | **2.5.1** | 1.26.4 |
| `sentence-transformers` | — | 5.6.1 | 4.1.0 |
| `pytorch-lightning` | 2.6.5 | — | 2.5.1.post0 |

Different *major* versions of `transformers` and `numpy`. In a single lock both
models get held back to the intersection — which is exactly what the backend
column shows.

## API

| Route | Purpose |
|---|---|
| `GET /health` | Liveness. 200 as soon as the process is up, including during load. |
| `GET /ready` | Readiness. 503 until the checkpoint is resident. |
| `GET /v1/info` | Device, batch size, last load error. |
| `POST /v1/score` | `{pairs: [{src, mt}]}` → `{scores[], system_score}` |

```bash
curl -s localhost:8072/v1/score -H 'content-type: application/json' -d '{
  "pairs": [{"src": "Open the door.", "mt": "Ouvrez la porte."}]
}'
```

Scores are returned at full precision; rounding is the caller's concern.

## Configuration

| Var | Default | Notes |
|---|---|---|
| `MODEL_PATH` | `/data/aimodels/huggingface/checkpoints/model.ckpt` | Must exist; never downloaded. |
| `FORCE_CPU` | `false` | |
| `BATCH_SIZE` | `32` | Caps peak activation memory per forward pass. |
| `MAX_PAIRS_PER_REQUEST` | `4096` | Returns 413 rather than OOM-ing. |
| `MAX_CONCURRENT_BATCHES` | `1` | One GPU, one forward pass at a time. |
| `WARMUP` | `true` | |

Scoring uses `prepare_sample` + `forward` directly rather than `model.predict()`,
which spins up its own dataloader and progress bar per call. This is the same
fast path the backend used, moved here unchanged.

Requests are chunked at `BATCH_SIZE` internally, so peak memory tracks the batch
rather than the request. Each pair scores independently, so this is numerically
identical to one large forward pass — parity against the in-process model was
**exactly 0.00e+00** across all test pairs.

## The setuptools trap

`unbabel-comet` pins `torchmetrics 0.10.3`, which imports `pkg_resources` at
module scope. `pkg_resources` was **removed in setuptools 81**, so a fresh
resolution installs setuptools 83 and the container dies on import:

```
ModuleNotFoundError: No module named 'pkg_resources'
```

`pyproject.toml` therefore pins `setuptools<81`. Worth knowing: the workbench
backend has the same `torchmetrics 0.10.3` and only survives because its lock
froze setuptools at 80.7.1. A `uv lock --upgrade` there would break it
identically. That is a latent trap in the monolith, not something this split
introduced.

## Running locally

```bash
docker compose up -d qe
curl -s localhost:8072/v1/info | python -m json.tool
```

The backend calls this service via `app/core/qe_client.py`; `load_comekiwi()` is
gone from `app/core/ml.py`. There is no `depends_on` — the backend starts fine
with `qe` down, and only `/api/v1/metrics/quality-estimation` returns `503`.

[`scripts/parity_check.py`](scripts/parity_check.py) compared this service
against the in-process model before the cutover and now exercises the full
backend → client → service path.

## Before this goes to ACR

Same two items as labse: build with `--build-arg TORCH_VARIANT=cpu` for
CPU-only Container Apps (on labse that took the image from 5.51 GB to 1.51 GB),
and keep `uv.lock` committed so builds stay reproducible.
