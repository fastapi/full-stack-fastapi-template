"""Compare metricx-svc against the in-process MetricX in the backend.

Run BEFORE cutting the backend over, while both paths are live.

    uv run --with httpx python scripts/parity_check.py

This one matters more than the others: the service resolved transformers 5.x
while the backend runs 4.51.3, and MT5ForRegression subclasses transformers
internals. A clean delta here is the evidence that the major-version jump is
safe for this model.
"""

from __future__ import annotations

import os
import sys

import httpx

SVC_URL = os.environ.get("METRICX_SVC_URL", "http://localhost:8074")
WORKBENCH_URL = os.environ.get("WORKBENCH_URL", "http://localhost:8070")

# src, mt, ref
TRIPLES = [
    ("The minister tabled the report yesterday.", "Le ministre a déposé le rapport hier.", "Le ministre a déposé le rapport hier."),
    ("Please submit your application before the deadline.", "Veuillez soumettre votre demande avant la date limite.", "Veuillez soumettre votre demande avant l'échéance."),
    ("This sentence is not a translation at all.", "Le chat dort sur le canapé.", "Cette phrase n'est pas une traduction."),
    ("Open the door.", "Ouvrez la porte.", "Ouvrez la porte."),
    ("All employees must complete the training.", "Les pommes de terre sont rouges.", "Tous les employés doivent suivre la formation."),
]


def main() -> int:
    with httpx.Client(timeout=1800.0) as client:
        svc = client.post(
            f"{SVC_URL}/v1/score",
            json={"rows": [{"src": s, "mt": m, "ref": r} for s, m, r in TRIPLES]},
        )
        svc.raise_for_status()
        svc_scores = svc.json()["scores"]

        wb = client.post(
            f"{WORKBENCH_URL}/api/v1/metrics/metricx",
            json=[{"src": s, "mt": m, "ref": r} for s, m, r in TRIPLES],
        )
        wb.raise_for_status()
        wb_scores = [e["score"] for e in wb.json()["estimates"]]

    print(f"{'src':<48} {'service':>10} {'workbench':>10} {'delta':>10}")
    worst = 0.0
    for (s, _, _), a, b in zip(TRIPLES, svc_scores, wb_scores, strict=True):
        delta = abs(a - b)
        worst = max(worst, delta)
        print(f"{s[:46]:<48} {a:>10.6f} {b:>10.6f} {delta:>10.2e}")

    # MetricX is an error metric roughly on 0-25, and both sides run bf16, so
    # small last-bit differences are expected. A big gap means the transformers
    # major-version difference actually changed behaviour.
    print(f"\nmax |delta| = {worst:.2e}")
    if worst > 1e-2:
        print("DIVERGENT — likely the transformers 4.x -> 5.x jump. Pin <5 and re-lock.")
        return 1
    print("OK — within bf16 noise.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
