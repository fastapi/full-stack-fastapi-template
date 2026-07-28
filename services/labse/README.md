# labse-svc

The reference model container for splitting `workbench-services`. One model, one
job: **text in, vectors out**.

It does not know about alignment, faiss, TMX, Postgres, or auth. Those stay in
`workbench-services`, which keeps `faiss-cpu` + `numpy` (small, no torch) and
calls this service for embeddings.

## Why this boundary

`backend/app/models_ml/labse.py` currently mixes two different things: encoding
(a reusable primitive) and bitext alignment + TMX generation (LQA business
logic). Only the first belongs behind a model boundary. Splitting there means:

- `workbench-services` drops `torch`, `sentence-transformers` and `transformers`
  entirely — the auth/CRUD/frontend image gets small and its dependency
  resolution stops being a negotiation with four ML stacks.
- The embedding primitive stays usable by any future consumer, not just
  `/memory/align`.
- Each model container owns its own dependency tree. `unbabel-comet`,
  MetricX and `sentence-transformers` no longer have to agree on a single
  `transformers` version.

## API

| Route | Purpose |
|---|---|
| `GET /health` | Liveness. 200 as soon as the process is up, *including during model load*. |
| `GET /ready` | Readiness. 503 until the weights are resident. Use this for probes. |
| `GET /v1/info` | Device, dtype, dim, batch size, last load error. |
| `POST /v1/embed` | `{texts[], normalize, encoding}` → vectors. |
| `POST /v1/similarity` | `{src[], trg[]}` → row-wise cosine + system score. |

Swagger is at `/docs`.

`/similarity` exists so the `/metrics/labse` path doesn't have to ship `2N x 768`
floats over the wire just to read the diagonal. `/embed` is what `/memory/align`
uses.

```bash
curl -s localhost:8071/v1/similarity -H 'content-type: application/json' -d '{
  "src": ["Open the door."],
  "trg": ["Ouvrez la porte."]
}'

curl -s localhost:8071/v1/embed -H 'content-type: application/json' -d '{
  "texts": ["Open the door.", "Ouvrez la porte."],
  "encoding": "base64"
}'
```

`encoding: "base64"` returns the whole matrix as one C-order float32 blob —
about 4x smaller than JSON floats and far cheaper to parse. Decode with:

```python
np.frombuffer(base64.b64decode(r["data"]), dtype=np.float32).reshape(r["count"], r["dim"])
```

## Configuration

All plain env vars, no prefix, matching the backend's idiom.

| Var | Default | Notes |
|---|---|---|
| `MODEL_PATH` | `/data/aimodels/LaBSE` | Must be a directory. The service never downloads. |
| `FORCE_CPU` | `false` | Same flag name the backend already uses. |
| `FP16` | `false` | Off by default so scores match the in-process model exactly. |
| `BATCH_SIZE` | `64` | The throughput knob. |
| `MAX_TEXTS_PER_REQUEST` | `8192` | Returns 413 rather than OOM-ing mid-batch. |
| `MAX_CONCURRENT_BATCHES` | `1` | One GPU, one forward pass at a time. |
| `WARMUP` | `true` | One tiny encode after load, so request #1 isn't the slow one. |

## Throughput notes

`sentence-transformers` sorts each `encode` call by length before batching, so
the padding win is automatic **as long as the caller passes the whole list in one
call** rather than looping. That is why the service takes a list and why
`MAX_CONCURRENT_BATCHES` defaults to 1: throughput comes from batch size, not
from parallel forward passes on one GPU.

Identical strings are encoded once per request and scattered back — translation
memories repeat heavily, so this is usually free money.

## Cold starts

The model loads in a background thread, so the process serves `/health`
immediately and `/ready` flips to 200 when the weights land (~30–90s from the
mount). Requests during load get `503` + `Retry-After: 10`, which is exactly the
"come back later" signal a batch worker already knows how to handle.

For Azure: LaBSE is small and hot, so run it with `min-replicas: 1`. Reserve
`min-replicas: 0` for the cold batch models (MetricX, COMET) whose callers are
background workers.

## Running locally

```bash
docker compose up -d labse
docker compose logs -f labse          # watch for "LaBSE ready on cuda"
curl -s localhost:8071/v1/info | python -m json.tool
```

The backend now depends on this service: `/api/v1/metrics/labse` and
`/api/v1/memory/align*` call it over HTTP via `app/core/labse_client.py`, and
`load_labse()` is gone from `app/core/ml.py`.

There is deliberately no `depends_on` between them. The backend starts fine with
`labse` down — only those two routes return `503`, and they recover on their own
once it comes up. Every other metric keeps working.

Before the cutover, both paths were live and compared clean:

```
max |delta| = 4.38e-05   (backend rounds to 4dp, so max possible error is 5e-5)
```

[`scripts/parity_check.py`](scripts/parity_check.py) still runs — it now compares
the service against the backend route that proxies to it, which is an end-to-end
check of the client, chunking and rounding rather than a model comparison. To
re-run a true model-vs-model parity check, restore `load_labse()` on a branch.

Note that both `backend` and `labse` reserve one NVIDIA device in
`docker-compose.override.yml`. That is fine on the 2x A6000 box; on a single-GPU
machine, set `FORCE_CPU=true` on one of them.

## Torch variant

`uv.lock` is committed and the Dockerfile builds `--frozen`, so builds are
reproducible. Pick the torch build at image build time:

```bash
docker build --build-arg TORCH_VARIANT=cpu  -t labse-svc:cpu  .   # 1.51 GB
docker build --build-arg TORCH_VARIANT=cuda -t labse-svc:cuda .   # 5.51 GB
```

Default is `cuda` because compose runs this on the local GPU box. Use `cpu` for
CPU-only Container Apps — verified working, scoring `0.9552170038` against the
CUDA build's `0.9552167654` (a 2.4e-07 device-float delta).

## Still open

**Auth.** This service has none. That is correct for a private Container Apps
environment where it is not externally routable — it is deliberately not behind
traefik in `docker-compose.yml`. If it ever gets a public hostname, that
assumption breaks.

**Base image CVEs.** Now on `python:3.14-slim-trixie`, which flags 1 critical
and 2 high — down from 1 critical and 4 high on the previous
`python:3.11-slim-bookworm`. The remaining critical is unfixed upstream in
Debian, so it does not clear by rebuilding.
