"""Search-space-partition BO — a separate process mimicking the JetBrains NeurIPS 2020
BBO Challenge entry (Sazanovich et al., "Solving Black-Box Optimization Challenge via
Learning Search Space Partition for Local Bayesian Optimization", 3rd place).

The idea, adapted to our maximisation setting:
  1. Cluster all known points into 2 groups by their score (KMeans on y).
  2. Train an SVM (RBF kernel) to predict the group from the *inputs* — this learns
     the geometric boundary between the "good" region and the "bad" region.
  3. Keep only the points the SVM classifies as good; recurse (split again) until
     max_depth or until too few points remain to model.
  4. Fit a LOCAL Gaussian Process on the final region's points only, and propose the
     next query by maximising Expected Improvement over Sobol candidates that fall
     INSIDE the learned region (i.e. pass every SVM gate along the path).

Why this addresses our current pain points:
  - Non-stationarity: the local GP only models the good region, so one lengthscale
    no longer has to describe both the sharp peak corner and the flat interior.
  - Over-confidence: candidates are confined to territory that historically scores
    well, so the acquisition cannot wander into unmapped cliffs (the f4/W6 failure).

Differences from the paper (deliberate, for our setting):
  - The paper minimises; we maximise (good cluster = HIGHER mean score).
  - The paper has 16 iterations x 8 suggestions; we have 1 suggestion/week, so no
    reset schedule and no trust-region decay — the partition is rebuilt every run.
  - Their split-regularisation C and depth come from meta-BO; we use sensible fixed
    defaults (C=100, depth<=5) since we can't afford meta-optimisation rounds.
"""
import numpy as np
from scipy.stats import norm, qmc
from sklearn.cluster import KMeans
from sklearn.svm import SVC

import bo


MAX_DEPTH = 5


def _min_region_points(d):
    """Smallest point count worth fitting a local GP on — below this, stop splitting."""
    return max(2 * d, 8)


def build_partition(U, y, d, C=100.0, seed=0):
    """Recursively learn the good-region path: a list of fitted SVMs, plus the row
    mask of points that survive every split.

    Returns (svms, mask, depth_reached). Empty svms = no split possible (e.g. f1,
    where nearly every score is identical and KMeans has nothing to separate).
    """
    svms = []
    mask = np.ones(len(y), dtype=bool)
    for depth in range(MAX_DEPTH):
        idx = np.where(mask)[0]
        if len(idx) < 2 * _min_region_points(d):
            break                                    # too few points to split further
        y_node = y[idx]
        if float(np.std(y_node)) < 1e-12:
            break                                    # scores all identical - nothing to learn
        km = KMeans(n_clusters=2, n_init=10, random_state=seed).fit(y_node.reshape(-1, 1))
        means = [y_node[km.labels_ == k].mean() for k in (0, 1)]
        good = int(np.argmax(means))                 # we maximise: good = higher mean
        labels = (km.labels_ == good).astype(int)
        if labels.sum() < _min_region_points(d) or labels.sum() == len(labels):
            break                                    # good side too small, or no split
        svm = SVC(kernel="rbf", C=C, gamma="scale", random_state=seed)
        svm.fit(U[idx], labels)
        pred = svm.predict(U[idx])
        keep = idx[pred == 1]
        if len(keep) < _min_region_points(d):
            break                                    # SVM boundary strands too few points
        svms.append(svm)
        new_mask = np.zeros(len(y), dtype=bool)
        new_mask[keep] = True
        mask = new_mask
    return svms, mask, len(svms)


def _in_region(svms, U_cand):
    """Boolean mask of candidates that pass every SVM gate along the partition path."""
    ok = np.ones(len(U_cand), dtype=bool)
    for svm in svms:
        ok &= svm.predict(U_cand) == 1
        if not ok.any():
            break
    return ok


def propose(func_id, C=100.0, seed=0, n_candidates_base2=None):
    """Full partition-BO proposal for one function. Returns a dict mirroring
    bo.propose_next's output, plus partition diagnostics."""
    X, y, d = bo.load(func_id)
    b = bo.bounds(func_id, d)
    U = bo.to_unit(X, b)

    svms, mask, depth = build_partition(U, y, d, C=C, seed=seed)

    # Local GP on the surviving region's points (falls back to all points if no split).
    U_loc, y_loc = U[mask], y[mask]
    gp = bo.build_gp("matern", d)
    gp.fit(U_loc, y_loc)
    model = bo.Model(func_id, "matern", gp, bo.from_unit(U_loc, b), y_loc, b)

    # Sobol candidates over the whole cube, filtered to the learned region.
    m = n_candidates_base2 or bo._n_base2(d) + 1     # extra density: filtering discards many
    sob = qmc.Sobol(d=d, scramble=True, seed=seed)
    U_cand = sob.random_base2(m)
    if svms:
        ok = _in_region(svms, U_cand)
        # If the region is so tight that nothing passes, fall back progressively:
        # drop the deepest gate until candidates survive.
        path = list(svms)
        while not ok.any() and path:
            path = path[:-1]
            ok = _in_region(path, U_cand)
        U_cand = U_cand[ok] if ok.any() else U_cand

    # Expected Improvement over the region's own best (the local incumbent).
    mean, std = model.predict(U_cand)
    y_best_loc = float(y_loc.max())
    vals = bo.ei(mean, std, y_best_loc, xi=0.01)
    i = int(np.argmax(vals))
    best_u = U_cand[i]
    mu, sd = model.predict(best_u.reshape(1, -1))
    x = bo.from_unit(best_u, b)
    return dict(
        x=x, u=best_u, mean=float(mu[0]), std=float(sd[0]),
        acq="partition_ei", acq_value=float(vals[i]),
        submission=bo.format_submission(x),
        depth=depth, n_region=int(mask.sum()), n_total=len(y),
        region_best=y_best_loc, global_best=float(y.max()),
        n_candidates=len(U_cand),
    )


def run_all(C=100.0, seed=0):
    return {fid: propose(fid, C=C, seed=seed) for fid in bo.FUNC_IDS}
