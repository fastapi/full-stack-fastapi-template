import numpy as np
from typing import List


def calc_awareness_stability_index(boas_daily) -> float:
    """
    Calculates the awareness stability Index
    :param boas_daily: daily Brand Overall Awareness Score
    """
    boas = np.array(boas_daily)
    if len(boas) < 3:
        return -0.1

    # clip outliers
    p10, p90 = np.percentile(boas, [10, 90])
    boas = np.clip(boas, p10, p90)

    mean = np.mean(boas)
    std = np.std(boas)

    if mean == 0:
        return 0

    cv = std / mean
    asi = 1 / (1 + cv)
    return round(asi, 3)


def calc_simple_brand_awareness_score(visibility: int, ranking: int) -> float:
    """
    Simple Brand Awareness Score (v1 baseline)

    Parameters
    ----------
    visibility : int
        Brand AI visibility, 0 or 1
    ranking : int
        Average AI ranking position (1 is best)

    Returns
    -------
    float
        Brand Awareness Score in range [0, 100]

    Rationale
    ---------
    - Visibility reflects whether AI mentions the brand at all
    - Ranking reflects priority in AI recommendation
    - Ranking is inverted so smaller rank -> higher score
    """

    rank_score = 0.0
    if ranking > 0:
        # Invert ranking: rank=1 -> 1.0, rank=5 -> 0.2
        rank_score = 1.0 / ranking

    # Weighted combination
    awareness = 0.6 * visibility + 0.4 * rank_score

    # Scale to 0–100 for business readability
    return round(min(awareness * 100, 100), 2)


def calc_smoothed_brand_awareness_score(
    visibility_daily: List[float],
    ranking_daily: List[int],
    w_visibility: float = 0.6,
    w_rank: float = 0.4
) -> float:
    """
    Smoothed Weekly Brand Awareness Score (production version)

    Parameters
    ----------
    visibility_daily : List[float]
        Daily visibility values in [0, 1] over a week
    ranking_daily : List[int]
        Daily average ranking positions (1 is best)
    w_visibility : float
        Weight for visibility component
    w_rank : float
        Weight for ranking component

    Returns
    -------
    float
        Weekly Brand Awareness Score in range [0, 100]

    Design choices
    --------------
    1. Median visibility:
       - Robust to daily prompt sampling spikes
    2. Mean ranking:
       - Reflects long-term AI preference position
    3. Percentile clipping:
       - Removes extreme noise before aggregation
    """

    if len(visibility_daily) != len(ranking_daily):
        raise ValueError("visibility and ranking must have same length")

    if len(visibility_daily) < 3:
        raise ValueError("need at least 3 data points")

    vis = np.array(visibility_daily)
    rank = np.array(ranking_daily)

    # ---- Noise clipping (robustness) ----
    vis_p10, vis_p90 = np.percentile(vis, [10, 90])
    vis_clipped = np.clip(vis, vis_p10, vis_p90)

    rank_p10, rank_p90 = np.percentile(rank, [10, 90])
    rank_clipped = np.clip(rank, rank_p10, rank_p90)

    # ---- Weekly aggregation ----
    # Visibility: median reduces impact of one-off spikes
    visibility_week = float(np.median(vis_clipped))

    # Ranking: mean reflects central tendency of AI preference
    ranking_week = float(np.mean(rank_clipped))

    if ranking_week <= 0:
        raise ValueError("invalid ranking value after aggregation")

    # ---- Ranking inversion ----
    rank_score = 1.0 / ranking_week

    # ---- Awareness calculation ----
    awareness = (
        w_visibility * visibility_week
        + w_rank * rank_score
    )

    return round(min(awareness * 100, 100), 2)
