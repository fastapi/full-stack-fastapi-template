# Model services

The five models that used to load into the `workbench-services` backend process
now run in their own containers. The backend keeps its API surface, swagger,
auth and validation, and calls these over HTTP.

```
                    backend  (1.57 GB, no torch, no weights, no mount)
                    routing · schemas · swagger · auth · faiss · TMX
                              │
      ┌───────────┬───────────┼───────────┬───────────┐
      ▼           ▼           ▼           ▼           ▼
  labse-svc      qe       comet-svc  metricx-svc  langid-svc
  LaBSE       CometKiwi  wmt22-da    MetricX-24   lingua en+fr
      └──────── /data/aimodels (mounted) ────────┘   (no mount)
```

| Service | Model | Image | Size | Port | Client |
|---|---|---|---|---|---|
| `labse` | LaBSE | `labse-svc` | 5.51 GB | 8071 | `labse_client.py` |
| `qe` | CometKiwi | `comet-svc` | 5.58 GB | 8072 | `qe_client.py` |
| `comet` | wmt22-comet-da | `comet-svc` | 5.58 GB | 8073 | `comet_client.py` |
| `metricx` | MetricX-24 hybrid | `metricx-svc` | 5.55 GB | 8074 | `metricx_client.py` |
| `langid` | lingua (en+fr) | `langid-svc` | **338 MB** | 8075 | `langid_client.py` |

`qe` and `comet` are **two deployments of one image**. Their dependency trees
resolve identically, so separate images would duplicate rather than isolate.
They differ only by `MODEL_PATH` and `MODEL_NAME`.

`langid` is the odd one out: no weights, no GPU, no torch, no mount — lingua
ships its n-gram data inside the wheel. It replaced fastText, which was the last
in-process model and the only blocker on moving the backend to a newer Python
(`fasttext-wheel` publishes no binary wheels at all). See
[`langid/README.md`](langid/README.md) for the en+fr accuracy trade-off.

**The backend now holds no weights of any kind.** `app/core/ml.py`, the lifespan
model loading, and the `/data/aimodels` mount are all gone.

## What the split actually bought

**Backend image: 7.39 GB → 1.57 GB.** `torch`, `unbabel-comet`,
`sentence-transformers`, `transformers`, `sentencepiece` and `fasttext-wheel`
are gone from `backend/pyproject.toml`; the lock dropped from 145 to 101
packages.

**Startup: ~2 minutes → ~2 seconds.** `load_models()` used to load five models
serially inside `lifespan`, so nothing served until all five were resident.
There is no lifespan model loading left at all.

**Build context: 11 GB → nil.** `backend/aimodels` was being shipped to the
daemon on every build (never into the image — the `COPY` was already commented
out). Now `.dockerignore`d, and the backend no longer mounts it either.

**Fault isolation.** Stopping any one model service returns `503` +
`Retry-After` on only its own route. Every other metric, plus auth and CRUD,
keeps working. Services self-heal when they come back — verified.

**Independent dependency resolution.** This is the one that cannot be faked in a
single lock:

| | labse-svc | qe / comet-svc | metricx-svc | backend before |
|---|---|---|---|---|
| `transformers` | **5.14.1** | **4.57.6** | **4.51.3** (pinned) | 4.51.3 |
| `numpy` | **2.5.1** | **1.26.4** | 2.x | 1.26.4 |
| `torch` | 2.13.0 | 2.13.0 | 2.13.0 | 2.7.0 |

Three different `transformers` versions across two major releases. One shared
lock forces all of them to the intersection, which is what the last column is.

## Verified parity

Each model was compared against the in-process version **before** cutover, with
both paths live:

| Model | max abs delta | Notes |
|---|---|---|
| CometKiwi | `0.00e+00` | bit-identical |
| wmt22-comet-da | `0.00e+00` | bit-identical |
| LaBSE | `4.38e-05` | exactly the backend's 4dp rounding |
| MetricX | `5.86e-03` | ~3 bf16 ulps on a 0–25 scale; large values match exactly |

Re-run any of them with `scripts/parity_check.py` in the relevant service
directory. They now exercise the full backend → client → service path.

## Three traps found the hard way

**1. setuptools 81 removes `pkg_resources`.** `unbabel-comet` pins
`torchmetrics 0.10.3`, which imports it at module scope. A fresh resolution
installs setuptools 83 and the container dies on import. Pinned `setuptools<81`
in `comet/pyproject.toml`. The backend has the same `torchmetrics` and only
survives because its lock froze setuptools at 80.7.1 — `uv lock --upgrade`
there would have broken it identically. That trap predates the split.

**2. transformers is a minefield for MetricX.** `MT5ForRegression` subclasses
transformers' MT5 internals and broke twice:
- `5.14.1` → `ImportError`, `__HEAD_MASK_WARNING_MSG` removed
- `4.57.6` → `RuntimeError` in `MT5Attention`, `position_bias` and `causal_mask`
  disagree by one during the forward pass

Pinned to `4.51.3` exactly. Meanwhile labse-svc runs 5.14.1 happily — which is
the whole argument for per-service locks.

**3. triton JIT needs a C compiler at runtime.** torch's triton backend compiles
its CUDA utils on first use. `python:*-slim` ships no compiler, so MetricX died
during warmup with "Failed to find C compiler". `services/metricx/Dockerfile`
installs `gcc g++ libc6-dev`. The backend never hit this because it runs the
full `python:3.10` image. Only the CUDA variant needs it.

## Conventions every service follows

- **Weights are mounted, never baked in.** `HF_HUB_OFFLINE=1` so a cold start
  can't become a surprise download.
- **`/health` vs `/ready`.** The model loads on a background thread, so
  `/health` answers immediately during a cold start and `/ready` gates traffic.
  Requests during load get `503` + `Retry-After: 10` — the signal a batch worker
  already knows how to handle.
- **One worker.** Each worker is a full copy of the weights. Scale with
  replicas, not processes.
- **Batch server-side, concurrency client-side.** `MAX_CONCURRENT_BATCHES=1`:
  one GPU, one forward pass at a time. Throughput comes from batch size.
- **Request caps.** Oversized requests get `413` rather than an OOM mid-batch.
- **No auth, no traefik labels.** These are internal-only services on the
  compose network. That assumption breaks if any of them gets a public hostname.
- **No `depends_on`.** The backend starts fine with every model service down.

## Deploying to Azure

Build CPU-only images unless the workload justifies a GPU:

```bash
docker build --build-arg TORCH_VARIANT=cpu -t labse-svc:cpu services/labse
```

On labse that is **5.51 GB → 1.51 GB**. The `cpu` extra resolves torch from the
pytorch-cpu index; `cuda` takes the default PyPI build.

Suggested replica policy — hot models stay warm, batch models scale to zero:

| Service | min replicas | Why |
|---|---|---|
| `langid` | 1 | 338 MB, ~6 s cold start, trivially cheap to keep warm |
| `labse` | 1 | small, hot, interactive |
| `qe` | 1 | interactive |
| `comet` | 0 | batch-only, callers are background workers |
| `metricx` | 0 | batch-only, expensive |

Cold start is a model load (~30–90 s), which is fine behind a retrying worker
and not fine behind an interactive request. That split is only possible now that
they are separate deployments.
