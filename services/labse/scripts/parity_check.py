"""Compare labse-svc against the in-process model still living in the backend.

Both paths are up at the same time on purpose, so the numbers can be diffed
before anything is removed from workbench-services.

    uv run --with httpx python scripts/parity_check.py

Override the endpoints with LABSE_SVC_URL / WORKBENCH_URL if your ports differ.
"""

from __future__ import annotations

import os
import sys

import httpx

LABSE_SVC_URL = os.environ.get("LABSE_SVC_URL", "http://localhost:8071")
WORKBENCH_URL = os.environ.get("WORKBENCH_URL", "http://localhost:8070")

PAIRS = [
    ("The minister tabled the report yesterday.", "Le ministre a déposé le rapport hier."),
    ("Please submit your application before the deadline.", "Veuillez soumettre votre demande avant la date limite."),
    ("This sentence is not a translation at all.", "Le chat dort sur le canapé."),
    ("Open the door.", "Ouvrez la porte."),
    ("Duplicate line for dedup coverage.", "Ligne dupliquée pour la déduplication."),
    ("Duplicate line for dedup coverage.", "Ligne dupliquée pour la déduplication."),
]


def main() -> int:
    src = [s for s, _ in PAIRS]
    trg = [t for _, t in PAIRS]

    with httpx.Client(timeout=300.0) as client:
        svc = client.post(
            f"{LABSE_SVC_URL}/v1/similarity",
            json={"src": src, "trg": trg},
        )
        svc.raise_for_status()
        svc_scores = svc.json()["scores"]

        wb = client.post(
            f"{WORKBENCH_URL}/api/v1/metrics/labse",
            json=[{"src": s, "ref": t} for s, t in PAIRS],
        )
        wb.raise_for_status()
        wb_scores = [e["score"] for e in wb.json()["estimates"]]

    print(f"{'src':<52} {'service':>10} {'workbench':>10} {'delta':>10}")
    worst = 0.0
    for (s, _), a, b in zip(PAIRS, svc_scores, wb_scores, strict=True):
        delta = abs(a - b)
        worst = max(worst, delta)
        print(f"{s[:50]:<52} {a:>10.6f} {b:>10.6f} {delta:>10.2e}")

    # The backend rounds to 4dp; the service does not. Anything beyond that is a
    # real divergence (fp16, a different checkpoint, a different device).
    print(f"\nmax |delta| = {worst:.2e}")
    if worst > 5e-5:
        print("DIVERGENT — larger than the backend's 4dp rounding. Check FP16/device.")
        return 1
    print("OK — within the backend's rounding.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
