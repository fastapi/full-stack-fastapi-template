"""Compare comet-svc against the in-process COMET models in the backend.

Covers both deployments of this image:
  --model qe      CometKiwi (reference-free)  vs /api/v1/metrics/quality-estimation
  --model comet   wmt22-comet-da              vs /api/v1/metrics/comet

Run BEFORE cutting the backend over, while both paths are live.

    uv run --with httpx python scripts/parity_check.py --model comet

Override endpoints with SVC_URL / WORKBENCH_URL if your ports differ.
"""

from __future__ import annotations

import argparse
import os
import sys

import httpx

WORKBENCH_URL = os.environ.get("WORKBENCH_URL", "http://localhost:8070")
DEFAULT_URLS = {"qe": "http://localhost:8072", "comet": "http://localhost:8073"}

# src, mt, ref
TRIPLES = [
    ("The minister tabled the report yesterday.", "Le ministre a déposé le rapport hier.", "Le ministre a déposé le rapport hier."),
    ("Please submit your application before the deadline.", "Veuillez soumettre votre demande avant la date limite.", "Veuillez soumettre votre demande avant l'échéance."),
    ("This sentence is not a translation at all.", "Le chat dort sur le canapé.", "Cette phrase n'est pas une traduction."),
    ("Open the door.", "Ouvrez la porte.", "Ouvrez la porte."),
    ("The budget was approved by a narrow margin.", "Le budget a été approuvé de justesse.", "Le budget a été adopté de justesse."),
    ("All employees must complete the training.", "Les pommes de terre sont rouges.", "Tous les employés doivent suivre la formation."),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=["qe", "comet"], default="comet")
    args = parser.parse_args()

    svc_url = os.environ.get("SVC_URL", DEFAULT_URLS[args.model])

    if args.model == "comet":
        # Reference-based.
        svc_rows = [{"src": s, "mt": m, "ref": r} for s, m, r in TRIPLES]
        wb_path = "/api/v1/metrics/comet"
        wb_body = [{"src": s, "mt": m, "ref": r} for s, m, r in TRIPLES]
    else:
        # Reference-free: ref omitted entirely, so prepare_sample sees {src, mt}.
        svc_rows = [{"src": s, "mt": m} for s, m, _ in TRIPLES]
        wb_path = "/api/v1/metrics/quality-estimation"
        wb_body = [{"src": s, "mt": m} for s, m, _ in TRIPLES]

    with httpx.Client(timeout=900.0) as client:
        svc = client.post(f"{svc_url}/v1/score", json={"rows": svc_rows})
        svc.raise_for_status()
        svc_scores = svc.json()["scores"]

        wb = client.post(f"{WORKBENCH_URL}{wb_path}", json=wb_body)
        wb.raise_for_status()
        wb_scores = [e["score"] for e in wb.json()["estimates"]]

    print(f"model={args.model}")
    print(f"{'src':<48} {'service':>10} {'workbench':>10} {'delta':>10}")
    worst = 0.0
    for (s, _, _), a, b in zip(TRIPLES, svc_scores, wb_scores, strict=True):
        delta = abs(a - b)
        worst = max(worst, delta)
        print(f"{s[:46]:<48} {a:>10.6f} {b:>10.6f} {delta:>10.2e}")

    print(f"\nmax |delta| = {worst:.2e}")
    if worst > 1e-4:
        print("DIVERGENT — check the checkpoint path and FORCE_CPU on both sides.")
        return 1
    print("OK — float-level agreement.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
