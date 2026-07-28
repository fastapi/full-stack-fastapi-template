"""Margin-based bitext alignment over LaBSE vectors.

Moved here from the workbench backend. The vectors this operates on are
produced a few lines away in GPU memory; running the kNN in the backend meant
copying them to host, base64-ing them, pushing ~4 KB per sentence over HTTP and
rebuilding them with `np.frombuffer`, purely to hand them to a faiss index. The
backend never kept an embedding — it only ever wanted the resulting pairs.

The maths is unchanged from the original (Artetxe & Schwenk margin scoring):
bidirectional kNN, ratio margin against the mean neighbour similarity, then a
greedy one-to-one selection over the merged candidate list.
"""

from __future__ import annotations

import logging
import time

import faiss
import numpy as np

logger = logging.getLogger("labse.aligner")


def _knn(
    x: np.ndarray,
    y: np.ndarray,
    k: int,
    use_ann: bool,
    ann_num_clusters: int,
    ann_num_cluster_probe: int,
) -> tuple[np.ndarray, np.ndarray]:
    start = time.time()

    # faiss pads with -1 when k exceeds the index size, and a -1 index silently
    # wraps to the last row downstream. The backend never clamped this, so a
    # corpus smaller than k scored against garbage and fell below threshold.
    k = min(k, y.shape[0])

    if use_ann:
        n_cluster = min(ann_num_clusters, int(y.shape[0] / 1000))
        quantizer = faiss.IndexFlatIP(y.shape[1])
        index = faiss.IndexIVFFlat(
            quantizer, y.shape[1], n_cluster, faiss.METRIC_INNER_PRODUCT
        )
        index.nprobe = ann_num_cluster_probe
        index.train(y)
        index.add(y)
        sim, ind = index.search(x, k)
        mode = f"approx (nlist={n_cluster}, nprobe={ann_num_cluster_probe})"
    else:
        idx = faiss.IndexFlatIP(y.shape[1])
        idx.add(y)
        sim, ind = idx.search(x, k)
        mode = "exact"

    logger.info(
        "kNN %s: %d x %d, k=%d in %.2fs", mode, x.shape[0], y.shape[0], k, time.time() - start
    )
    return sim, ind


def _score_candidates(
    x: np.ndarray,
    y: np.ndarray,
    candidate_inds: np.ndarray,
    fwd_mean: np.ndarray,
    bwd_mean: np.ndarray,
) -> np.ndarray:
    """Ratio margin: cos(x_i, y_k) / mean of the two sides' neighbour means.

    Vectorised. The original walked this with a Python double loop doing one
    768-dim dot per iteration; here it is a single gather plus an einsum, which
    is the same arithmetic in the same order per element.
    """
    # (n, k, dim) gather of each row's candidates, then row-wise dot with x.
    cand = y[candidate_inds]
    sims = np.einsum("ij,ikj->ik", x, cand)
    denom = (fwd_mean[:, None] + bwd_mean[candidate_inds]) / 2
    return sims / denom


def align(
    src_vecs: np.ndarray,
    trg_vecs: np.ndarray,
    k: int = 4,
    min_score: float = 1.1,
    use_ann: bool = False,
    ann_num_clusters: int = 32768,
    ann_num_cluster_probe: int = 3,
) -> list[tuple[int, int, float]]:
    """Return (src_idx, trg_idx, score) triples, best score first.

    Each index appears at most once: selection is greedy over the merged
    forward/backward candidate list, which is what makes the result one-to-one.
    """
    if src_vecs.shape[0] == 0 or trg_vecs.shape[0] == 0:
        return []

    # The encoder already returns unit vectors; the backend re-normalised here
    # anyway. Kept so the arithmetic is identical to what it replaces.
    x = src_vecs / np.linalg.norm(src_vecs, axis=1, keepdims=True)
    y = trg_vecs / np.linalg.norm(trg_vecs, axis=1, keepdims=True)

    x2y_sim, x2y_ind = _knn(x, y, k, use_ann, ann_num_clusters, ann_num_cluster_probe)
    x2y_mean = x2y_sim.mean(axis=1)

    y2x_sim, y2x_ind = _knn(y, x, k, use_ann, ann_num_clusters, ann_num_cluster_probe)
    y2x_mean = y2x_sim.mean(axis=1)

    fwd_scores = _score_candidates(x, y, x2y_ind, x2y_mean, y2x_mean)
    bwd_scores = _score_candidates(y, x, y2x_ind, y2x_mean, x2y_mean)

    fwd_best = x2y_ind[np.arange(x.shape[0]), fwd_scores.argmax(axis=1)]
    bwd_best = y2x_ind[np.arange(y.shape[0]), bwd_scores.argmax(axis=1)]

    indices = np.stack(
        [
            np.concatenate([np.arange(x.shape[0]), bwd_best]),
            np.concatenate([fwd_best, np.arange(y.shape[0])]),
        ],
        axis=1,
    )
    scores = np.concatenate([fwd_scores.max(axis=1), bwd_scores.max(axis=1)])

    seen_src: set[int] = set()
    seen_trg: set[int] = set()
    pairs: list[tuple[int, int, float]] = []

    for i in np.argsort(-scores):
        if scores[i] < min_score:
            break
        src_ind, trg_ind = int(indices[i][0]), int(indices[i][1])
        if src_ind in seen_src or trg_ind in seen_trg:
            continue
        seen_src.add(src_ind)
        seen_trg.add(trg_ind)
        pairs.append((src_ind, trg_ind, float(scores[i])))

    return pairs
