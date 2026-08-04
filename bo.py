"""Toolkit for the Stage 2 capstone — 8 mystery functions, find the highest output.

Each function is a black box: I give it numbers between 0 and 1, it returns a single score,
I never see the formula inside. The job is to find the inputs that make that score as big
as possible, using as few queries as I can.

Same routine every round, for each function:
  1. `load(func)`        — read the input/output pairs gathered so far.
  2. `fit(...)`          — train a model that guesses outputs (and how unsure it is) anywhere.
  3. `propose_next(...)` — pick the next input to try, using a "scoring rule" (acquisition).
  4. `plot_*`            — show what the model thinks and where it wants to look next.
  5. `format_submission` — turn the chosen input into the string the portal expects.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, Matern, WhiteKernel, ConstantKernel
from sklearn.neural_network import MLPRegressor
from scipy.stats import norm, qmc
from scipy.optimize import minimize
from scipy.spatial.distance import cdist

ROOT = os.path.dirname(os.path.abspath(__file__))
INITIAL_DIR = os.path.join(ROOT, "initial_data")
DATA_DIR = os.path.join(ROOT, "data")
OUTPUT_DIR = os.path.join(ROOT, "outputs")
REFLECT_DIR = os.path.join(ROOT, "weekly", "reflections")

FUNC_IDS = list(range(1, 9))
ACQ_NAMES = ["ei", "ucb", "pi", "var"]

# Short blurb for each function — what it represents and what shape its surface tends to have.
# Copied from the portal's "Descriptions of functions" handout so I can read it from code.
FUNCTION_INFO = [
    dict(func=1, dims=2, n_seed=10, goal="maximise",
         application="Radiation/contamination source detection in a 2D field; only proximity gives a non-zero reading.",
         character="Sparse/flat (mostly ~0 except near sources); may have two optima (strong + weak source).",
         note="Explore to locate both sources."),
    dict(func=2, dims=2, n_seed=10, goal="maximise",
         application="Mystery ML model returning a noisy log-likelihood score.",
         character="Noisy + multimodal with many local peaks.",
         note="Use noise (WhiteKernel) and explore to escape local optima."),
    dict(func=3, dims=3, n_seed=15, goal="maximise",
         application="Drug discovery: combinations of three compounds; output = negative of adverse reactions.",
         character="Maximise a negated cost (toward 0).",
         note="Framed as maximisation of a transformed (negated) objective."),
    dict(func=4, dims=4, n_seed=30, goal="maximise",
         application="Warehouse product-placement surrogate; output = (neg) gap vs an expensive baseline.",
         character="Dynamic with many local optima.",
         note="Needs robust tuning/validation."),
    dict(func=5, dims=4, n_seed=20, goal="maximise",
         application="Chemical-process yield.",
         character="Typically unimodal, a single peak.",
         note="Exploitation-leaning; large output scale (up to ~1089)."),
    dict(func=6, dims=5, n_seed=20, goal="maximise",
         application="Cake recipe with five ingredients; combined negative score (flavour/cost/waste...).",
         character="Negative-by-design; maximise toward 0.",
         note="Maximise the negative of the total penalty."),
    dict(func=7, dims=6, n_seed=30, goal="maximise",
         application="ML hyperparameter tuning (lr, reg, #layers...); output = performance (accuracy/F1).",
         character="Black-box; literature priors can inform the search space.",
         note=""),
    dict(func=8, dims=8, n_seed=40, goal="maximise",
         application="8-param ML hyperparameter tuning (lr, batch, layers, dropout, reg, activation, optimiser, init range).",
         character="High-dimensional; global optimisation hard.",
         note="Target strong local maxima. Portal's '0-1 score' is illustrative; actual outputs differ."),
]

# The portal says every input is between 0 and 1. If that ever turns out to be wrong for
# a function, add `{func_id: [[low, high], ...]}` here to override.
BOUNDS_OVERRIDE = {}


# --------------------------------------------------------------------------- data
def _csv_path(func_id):
    return os.path.join(DATA_DIR, f"f{func_id}.csv")


def seed_csvs(overwrite=False):
    """Copy the starter inputs/outputs into a working CSV per function.

    The originals live in initial_data/ as read-only .npy files. We work off CSVs in
    data/ so we can add a new row each round without touching the originals.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    paths = {}
    for fid in FUNC_IDS:
        path = _csv_path(fid)
        if os.path.exists(path) and not overwrite:
            paths[fid] = path
            continue
        d = os.path.join(INITIAL_DIR, f"function_{fid}")
        X = np.load(os.path.join(d, "initial_inputs.npy"))
        y = np.load(os.path.join(d, "initial_outputs.npy")).reshape(-1)
        df = pd.DataFrame(X, columns=[f"x{j + 1}" for j in range(X.shape[1])])
        df["y"] = y
        df.to_csv(path, index=False)
        paths[fid] = path
    return paths


def write_descriptions():
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, "function_descriptions.csv")
    pd.DataFrame(FUNCTION_INFO).to_csv(path, index=False)
    return path


def load(func_id):
    """Read this function's known points: inputs `X`, outputs `y`, and how many inputs `d`.

    If we haven't created the working CSV yet, copy it from the starter data first.
    """
    path = _csv_path(func_id)
    if not os.path.exists(path):
        seed_csvs()
    df = pd.read_csv(path)
    y = df["y"].to_numpy(dtype=float)
    X = df.drop(columns=["y"]).to_numpy(dtype=float)
    return X, y, X.shape[1]


def append_result(func_id, x, y):
    """Record the latest portal result — add the input I queried and the score it returned."""
    x = np.asarray(x, dtype=float).reshape(-1)
    path = _csv_path(func_id)
    df = pd.read_csv(path)
    row = {f"x{j + 1}": x[j] for j in range(len(x))}
    row["y"] = float(y)
    df.loc[len(df)] = row
    df.to_csv(path, index=False)
    return path


def bounds(func_id, d):
    if func_id in BOUNDS_OVERRIDE:
        return np.asarray(BOUNDS_OVERRIDE[func_id], dtype=float)
    return np.column_stack([np.zeros(d), np.ones(d)])


def to_unit(X, b):
    return (X - b[:, 0]) / (b[:, 1] - b[:, 0])


def from_unit(U, b):
    return b[:, 0] + U * (b[:, 1] - b[:, 0])


# --------------------------------------------------------------------------- surrogate
def build_gp(kind, d, n_restarts=10, length_scale=0.2, alpha=1e-6):
    """Make an empty Gaussian Process — a model that will learn 'what output to expect
    here, and how unsure am I' once we feed it the known points.

    `kind="matern"` — the smart choice: it tunes one bumpiness setting per input, and
    estimates how noisy the function is. Used everywhere.
    `kind="rbf"`    — a simpler smooth fallback with no noise term.
    """
    if kind == "matern":
        kernel = (ConstantKernel(1.0, (1e-3, 1e3))
                  * Matern(length_scale=[1.0] * d, length_scale_bounds=(1e-2, 1e2), nu=2.5)
                  + WhiteKernel(noise_level=1e-3, noise_level_bounds=(1e-6, 1e1)))
        return GaussianProcessRegressor(kernel=kernel, normalize_y=True,
                                        n_restarts_optimizer=n_restarts, random_state=0)
    if kind == "rbf":
        kernel = RBF(length_scale=length_scale, length_scale_bounds="fixed")
        return GaussianProcessRegressor(kernel=kernel, alpha=alpha, normalize_y=True)
    raise ValueError(f"unknown kind: {kind}")


class Model:
    """One trained model bundled with everything I need to query and plot it.

    Holds the raw inputs/outputs, the search box, the inputs rescaled into [0, 1]^d
    (so the model only ever sees unit-cube coordinates), and the best point so far
    — that "incumbent" is what every scoring rule has to beat.
    """

    def __init__(self, func_id, kind, gp, X, y, b):
        self.func_id = func_id
        self.kind = kind
        self.gp = gp
        self.X = X
        self.y = y
        self.b = b
        self.d = X.shape[1]
        self.U = to_unit(X, b)
        i = int(np.argmax(y))
        self.x_best = X[i]
        self.u_best = self.U[i]
        self.y_best = float(y[i])

    def predict(self, U):
        """At each candidate input, give the model's best guess and how unsure it is."""
        U = np.atleast_2d(U)
        mean, std = self.gp.predict(U, return_std=True)
        return mean.reshape(-1), std.reshape(-1)


def fit(func_id, kind="matern", **kw):
    """Load this function's known points and train a fresh model on them."""
    X, y, d = load(func_id)
    b = bounds(func_id, d)
    gp = build_gp(kind, d, **kw)
    gp.fit(to_unit(X, b), y)
    return Model(func_id, kind, gp, X, y, b)


# --------------------------------------------------------------------------- neural-net surrogate
class NNSurrogate:
    """Small MLP regressor — a comparison surrogate against the GP.

    Sized deliberately small (hidden layers default (16, 8) ≈ 200 weights) because
    we only have 13-43 points per function. ReLU activations, Adam optimiser, L2
    weight decay tuned to discourage memorisation. Outputs are mean/std normalised
    because function scales span ~1e-87 (f1) to ~8e3 (f5) and a raw-scale fit would
    silently bias toward the big functions.

    Exposes three things the BO loop cares about:
    - `predict(U)`     — mean prediction at each unit-cube point.
    - `gradient(u)`    — per-dimension finite-difference gradient at one point.
    - `sensitivities(U)` — mean-absolute gradient per input dim across U; useful
                          for "which inputs does the network think actually matter".
    """

    def __init__(self, hidden=(16, 8), alpha=1e-2, max_iter=5000, random_state=0):
        self.mlp = MLPRegressor(
            hidden_layer_sizes=hidden, activation="relu", solver="adam",
            max_iter=max_iter, alpha=alpha, random_state=random_state,
            learning_rate_init=1e-3, tol=1e-6,
        )
        self.y_mean = None
        self.y_std = None

    def fit(self, U, y):
        self.y_mean = float(np.mean(y))
        self.y_std = float(np.std(y)) if np.std(y) > 1e-12 else 1.0
        self.mlp.fit(U, (y - self.y_mean) / self.y_std)
        return self

    def predict(self, U):
        U = np.atleast_2d(U)
        return self.mlp.predict(U) * self.y_std + self.y_mean

    def gradient(self, u, eps=1e-3):
        """Central-difference gradient of the predicted mean at point u."""
        u = np.asarray(u, dtype=float)
        d = len(u)
        g = np.empty(d)
        for j in range(d):
            up = u.copy(); up[j] = min(1.0, u[j] + eps)
            dn = u.copy(); dn[j] = max(0.0, u[j] - eps)
            g[j] = (self.predict(up.reshape(1, -1))[0] -
                    self.predict(dn.reshape(1, -1))[0]) / (up[j] - dn[j])
        return g

    def sensitivities(self, U):
        """Mean absolute gradient per input dimension across a batch of points.

        High value → the network believes that input meaningfully affects the
        output. Near-zero → the network has effectively ignored that input
        (analogue of a GP's large ARD lengthscale).
        """
        U = np.atleast_2d(U)
        sens = np.zeros(U.shape[1])
        for u in U:
            sens += np.abs(self.gradient(u))
        return sens / len(U)


def fit_nn(func_id, hidden=(16, 8), alpha=1e-2, max_iter=5000, seed=0):
    """Load this function's data, fit a fresh `NNSurrogate` on the unit cube."""
    X, y, d = load(func_id)
    b = bounds(func_id, d)
    nn = NNSurrogate(hidden=hidden, alpha=alpha, max_iter=max_iter, random_state=seed)
    nn.fit(to_unit(X, b), y)
    return nn, X, y, b


# --------------------------------------------------------------------------- acquisition
# An "acquisition function" is a scoring rule for candidate inputs: it takes the model's
# guess and its uncertainty at a point, and returns one number saying "how worth querying
# is this?". Each rule weighs "I think it's high here" vs "I have no idea here" differently.

def ucb(mean, std, beta=2.0, **_):
    """Upper Confidence Bound — guess + β × uncertainty. Bigger β = more exploring."""
    return mean + beta * std


def ei(mean, std, y_best, xi=0.01, **_):
    """Expected Improvement — by how much do I expect this point to beat the best so far?"""
    std = np.maximum(std, 1e-12)
    imp = mean - y_best - xi
    z = imp / std
    out = imp * norm.cdf(z) + std * norm.pdf(z)
    out[std < 1e-9] = 0.0
    return out


def pi(mean, std, y_best, xi=0.01, **_):
    """Probability of Improvement — what's the chance this point beats the best so far?"""
    std = np.maximum(std, 1e-12)
    return norm.cdf((mean - y_best - xi) / std)


def variance(mean, std, **_):
    """Pure exploration — score is just the model's uncertainty at the point."""
    return std ** 2


def acq_values(model, U, beta=2.0, xi=0.01):
    """Run all four "standard" scoring rules at the same set of candidate points.

    Used in the reflection so I can see, e.g., "the rule I chose said 1.7, but EI
    only said 0.01 — that means I'm probing, not exploiting".
    Thompson and MES are missing on purpose — they don't score points one-by-one,
    they need a joint random draw or pre-sampled max values.
    """
    mean, std = model.predict(U)
    return {
        "ei": ei(mean, std, model.y_best, xi=xi),
        "ucb": ucb(mean, std, beta=beta),
        "pi": pi(mean, std, model.y_best, xi=xi),
        "var": variance(mean, std),
    }


def _thompson_sample(model, U, rng):
    """Thompson sampling — imagine one whole 'maybe true' surface that's consistent
    with everything I've seen, then pick the candidate where it's highest.

    Different draws give different surfaces, so the chosen point shifts with the
    posterior's uncertainty — naturally balances exploring and exploiting without
    a tuning knob. Good for noisy functions.
    """
    mean, cov = model.gp.predict(U, return_cov=True)
    cov = cov + 1e-6 * np.eye(len(mean))
    L = np.linalg.cholesky(cov)
    return mean + L @ rng.standard_normal(len(mean))


def _y_star_gumbel(mean_grid, std_grid, K, rng):
    """Take K guesses at what the function's true maximum value might be.

    Why: MES (below) needs candidate maxima to score against. Cheap trick — fit
    a Gumbel distribution (the standard "extreme-value" shape) to the model's
    own guess at what the max could be, then draw K samples from it.
    """
    std_grid = np.maximum(std_grid, 1e-9)

    def log_F(y):
        return float(norm.logcdf((y - mean_grid) / std_grid).sum())

    lo = float(mean_grid.min() - 5 * std_grid.max())
    hi = float(mean_grid.max() + 5 * std_grid.max())

    def quantile(q):
        target = float(np.log(q))
        a, b = lo, hi
        for _ in range(60):
            m = 0.5 * (a + b)
            if log_F(m) < target:
                a = m
            else:
                b = m
        return 0.5 * (a + b)

    q25, q50, q75 = quantile(0.25), quantile(0.5), quantile(0.75)
    b_param = (q75 - q25) / (np.log(-np.log(0.25)) - np.log(-np.log(0.75)))
    if b_param < 1e-9:                        # everything's certain — just return a flat guess
        return np.full(K, q50)
    a_param = q50 + b_param * np.log(-np.log(0.5))
    u = rng.uniform(1e-6, 1 - 1e-6, size=K)
    return a_param - b_param * np.log(-np.log(u))


def mes(mean, std, y_stars, **_):
    """Max-value Entropy Search — score each candidate by how much querying it
    would shrink my uncertainty about the *value* of the true maximum.

    Tends to pick informative interior points instead of the corner-snapping you
    see with plain UCB in high dimensions.
    """
    std = np.maximum(std, 1e-9)
    alpha = np.zeros_like(mean)
    for y_star in y_stars:
        gamma = (y_star - mean) / std
        log_Phi = norm.logcdf(gamma)
        Phi = np.maximum(np.exp(log_Phi), 1e-12)
        alpha += gamma * norm.pdf(gamma) / (2 * Phi) - log_Phi
    return alpha / len(y_stars)


def aei(mean, std, y_best, noise_std, xi=0.01, **_):
    """Augmented EI (Huang et al., 2006) — EI scaled by a noise-aware discount.

    Standard EI multiplied by (1 - σ_n / sqrt(σ² + σ_n²)). The factor shrinks the
    score at candidates where measurement noise dominates the posterior uncertainty —
    so the rule prefers spots where querying would actually reduce uncertainty,
    not just sample the noise floor. Drop-in replacement for plain EI on noisy
    functions (e.g. f2).
    """
    std = np.maximum(std, 1e-12)
    imp = mean - y_best - xi
    z = imp / std
    base = imp * norm.cdf(z) + std * norm.pdf(z)
    base[std < 1e-9] = 0.0
    discount = 1.0 - noise_std / np.sqrt(std ** 2 + noise_std ** 2)
    return base * discount


def _noise_std(model):
    """Pull σ_n (the WhiteKernel noise std) out of a fitted matern GP.

    Returns 0.0 for the rbf kernel (no noise term) so callers can treat it as
    "noise-free" without special-casing.
    """
    if model.kind != "matern":
        return 0.0
    try:
        return float(np.sqrt(model.gp.kernel_.k2.noise_level))
    except AttributeError:
        return 0.0


def far(mean, dist, **_):
    """Empty-region probe — favours candidates with high predicted value AND
    high distance from training data.

    Both inputs are rank-normalised across the candidate set before being
    multiplied, so the rule works the same whether the function's y range is
    positive (f5: 1 000s) or negative (f6: −0.7 to −2). Defends against
    locking onto a local maximum: candidates near known points are penalised
    even if the surrogate predicts they are high.

    `mean` can come from any surrogate — GP or NN — that exposes a predict()
    on the same Sobol grid. NN-driven `nn_far` is where this earns its keep
    because NN extrapolation gives non-trivial values in regions the GP
    would just revert to its prior mean.
    """
    m_norm = mean - mean.min()
    m_norm = m_norm / m_norm.max() if m_norm.max() > 0 else m_norm
    d_norm = dist / dist.max() if dist.max() > 0 else dist
    return m_norm * d_norm


# --------------------------------------------------------------------------- optimisation
def _n_base2(d):
    """How many candidate inputs to scatter across the search box, as a power of two.

    Used by `propose_next` — Sobol's `random_base2(n)` returns exactly 2**n points,
    so this picks `n` based on how many inputs the function has. Higher-D boxes are
    much emptier per-point, so they need more candidates to cover well:
      - up to 4D  → 2**12 = 4 096 candidates
      - 5D-6D    → 2**13 = 8 192 candidates
      - 7D-8D    → 2**14 = 16 384 candidates
    """
    return 12 if d <= 4 else 13 if d <= 6 else 14


def propose_next(model, acq="ei", beta=2.0, xi=0.01, n_restarts=10, seed=0, mes_K=10):
    """Pick the next input to query — the single most important step each round.

    1. Scatter a few thousand candidate inputs evenly across the search box (Sobol).
    2. Score every candidate with the chosen rule.
    3. Take the top few and "polish" each one to find the very best score nearby.
    4. Return the winner: its coordinates, the model's guess and uncertainty there,
       and the rule's score.

    Supported rules: `ei`, `ucb`, `pi`, `var`, `thompson`, `mes`.
    Thompson just picks the argmax of one random posterior draw (no polishing).
    MES samples K guesses at the true maximum first, then polishes against them.
    """
    d = model.d
    sob = qmc.Sobol(d=d, scramble=True, seed=seed)
    U = sob.random_base2(_n_base2(d))
    rng = np.random.default_rng(seed)

    if acq == "thompson":
        # Cap the candidate set — Thompson needs the joint covariance, whose memory and
        # compute cost balloon quickly with the number of points.
        if len(U) > 1024:
            U_t = qmc.Sobol(d=d, scramble=True, seed=seed).random_base2(10)
        else:
            U_t = U
        sample = _thompson_sample(model, U_t, rng)
        i = int(np.argmax(sample))
        best_u, best_val = U_t[i], float(sample[i])
        mean, std = model.predict(best_u.reshape(1, -1))
        x = from_unit(best_u, model.b)
        return dict(x=x, u=best_u, mean=float(mean[0]), std=float(std[0]),
                    acq=acq, acq_value=best_val)

    if acq == "mes":
        mean_g, std_g = model.predict(U)
        y_stars = _y_star_gumbel(mean_g, std_g, mes_K, rng)
        vals = mes(mean_g, std_g, y_stars)
        order = np.argsort(vals)[::-1][:n_restarts]

        def neg(u):
            m, s = model.predict(u.reshape(1, -1))
            return -mes(m, s, y_stars)[0]

        best_u, best_val = U[order[0]], vals[order[0]]
        for idx in order:
            res = minimize(neg, U[idx], method="L-BFGS-B", bounds=[(0.0, 1.0)] * d)
            if -res.fun > best_val:
                best_val, best_u = -res.fun, res.x
        best_u = np.clip(best_u, 0.0, 1.0)
        mean, std = model.predict(best_u.reshape(1, -1))
        x = from_unit(best_u, model.b)
        return dict(x=x, u=best_u, mean=float(mean[0]), std=float(std[0]),
                    acq=acq, acq_value=float(best_val))

    if acq == "aei":
        noise_std = _noise_std(model)
        mean_g, std_g = model.predict(U)
        vals = aei(mean_g, std_g, model.y_best, noise_std, xi=xi)
        order = np.argsort(vals)[::-1][:n_restarts]

        def neg(u):
            m, s = model.predict(u.reshape(1, -1))
            return -aei(m, s, model.y_best, noise_std, xi=xi)[0]

        best_u, best_val = U[order[0]], vals[order[0]]
        for idx in order:
            res = minimize(neg, U[idx], method="L-BFGS-B", bounds=[(0.0, 1.0)] * d)
            if -res.fun > best_val:
                best_val, best_u = -res.fun, res.x
        best_u = np.clip(best_u, 0.0, 1.0)
        mean, std = model.predict(best_u.reshape(1, -1))
        x = from_unit(best_u, model.b)
        return dict(x=x, u=best_u, mean=float(mean[0]), std=float(std[0]),
                    acq=acq, acq_value=float(best_val))

    if acq == "space_fill":
        # Pure max-distance probe — ignores the GP entirely. Use when LOO R² is
        # negative (the surrogate is fitting noise) and any acquisition built on
        # its mean or std would be picking arbitrarily. The honest move is to
        # spread queries as evenly as possible across the box and hope to land
        # on signal by accident.
        dist = cdist(U, model.U).min(axis=1)
        i = int(np.argmax(dist))
        best_u = U[i]
        mean, std = model.predict(best_u.reshape(1, -1))
        x = from_unit(best_u, model.b)
        return dict(x=x, u=best_u, mean=float(mean[0]), std=float(std[0]),
                    acq=acq, acq_value=float(dist[i]),
                    dist_to_nearest=float(dist[i]))

    if acq in ("far", "nn_far"):
        # Distance from each Sobol candidate to its nearest known training point.
        # (Not smoothly differentiable, so no L-BFGS-B polish — best-of-Sobol only.)
        dist = cdist(U, model.U).min(axis=1)
        if acq == "nn_far":
            nn = NNSurrogate()
            nn.fit(model.U, model.y)
            mean_g = nn.predict(U)
        else:
            mean_g, _ = model.predict(U)
        vals = far(mean_g, dist)
        i = int(np.argmax(vals))
        best_u = U[i]
        mean, std = model.predict(best_u.reshape(1, -1))
        x = from_unit(best_u, model.b)
        out = dict(x=x, u=best_u, mean=float(mean[0]), std=float(std[0]),
                   acq=acq, acq_value=float(vals[i]),
                   dist_to_nearest=float(dist[i]))
        if acq == "nn_far":
            out["nn_mean"] = float(nn.predict(best_u.reshape(1, -1))[0])
        return out

    vals = acq_values(model, U, beta=beta, xi=xi)[acq]
    order = np.argsort(vals)[::-1][:n_restarts]

    def neg(u):
        return -acq_values(model, u.reshape(1, -1), beta=beta, xi=xi)[acq][0]

    best_u, best_val = U[order[0]], vals[order[0]]
    for idx in order:
        res = minimize(neg, U[idx], method="L-BFGS-B", bounds=[(0.0, 1.0)] * d)
        if -res.fun > best_val:
            best_val, best_u = -res.fun, res.x
    best_u = np.clip(best_u, 0.0, 1.0)
    mean, std = model.predict(best_u.reshape(1, -1))
    x = from_unit(best_u, model.b)
    return dict(x=x, u=best_u, mean=float(mean[0]), std=float(std[0]),
               acq=acq, acq_value=float(best_val))


# --------------------------------------------------------------------------- submission
def format_submission(x):
    """Turn the chosen input into the exact string the portal asks for: each value
    to six decimal places, joined with hyphens, never quite reaching 1.0.
    """
    x = np.clip(np.asarray(x, dtype=float).reshape(-1), 0.0, 0.999999)
    return "-".join(f"{xi:.6f}" for xi in x)


def validate_submission(s, d):
    """Sanity-check a submission string before I paste it into the portal."""
    parts = s.split("-")
    assert len(parts) == d, f"expected {d} values, got {len(parts)}"
    for p in parts:
        assert p.startswith("0.") and len(p.split(".")[1]) == 6, f"bad value: {p}"
    return True


# --------------------------------------------------------------------------- plots
def plot_2d(model, beta=2.0, xi=0.01, proposed=None, grid=80, save=None):
    """For 2D functions only — paint six heatmaps showing what the model believes
    across the entire search box.

    Panels, top-to-bottom, left-to-right:
      1. **GP mean**   — model's best guess for the score at each point.
      2. **GP std**    — how unsure the model is at each point (bright = blind spot).
      3. **EI**        — Expected Improvement: expected size of beating the current best.
      4. **UCB**       — guess + β × uncertainty (the "explore" rule).
      5. **PI**        — chance of beating the current best (the "exploit" rule).
      6. **Variance**  — pure uncertainty (the "probe" rule).

    Every panel is overlaid with the same three markers:
      - white dots     = points we've already observed
      - cyan diamond   = current best (the "incumbent" the rules must beat)
      - red star       = next input the chosen rule wants to query

    Reading it: comparing panels 1 + 2 tells me where the model is confident vs blind.
    Comparing panels 3-6 shows how each scoring rule reacts to that — useful for spotting
    when a rule is chasing uncertainty (corners light up in UCB/Variance) vs exploiting
    a hot interior spot (EI/PI light up around the cyan diamond).
    """
    # Build an 80x80 grid of evenly spaced points covering the [0,1]x[0,1] search box.
    # `meshgrid` + `column_stack` flattens it into a list of (x1, x2) coordinates so
    # we can score every grid point in one batched call to the model.
    g = np.linspace(0, 1, grid)
    A, B = np.meshgrid(g, g)
    U = np.column_stack([A.ravel(), B.ravel()])

    # Ask the model for its guess and uncertainty at every grid point, then score the
    # same grid with all four standard scoring rules. These become the six heatmaps.
    mean, std = model.predict(U)
    acqs = acq_values(model, U, beta=beta, xi=xi)
    panels = [("GP mean", mean), ("GP std", std), ("EI", acqs["ei"]),
              ("UCB", acqs["ucb"]), ("PI", acqs["pi"]), ("Variance", acqs["var"])]

    # Lay out the six panels in a 2x3 grid, and set the heatmap axes to the function's
    # original input range (in case `bounds` ever overrides the unit cube).
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    Xg = from_unit(U, model.b)
    extent = [model.b[0, 0], model.b[0, 1], model.b[1, 0], model.b[1, 1]]

    for ax, (title, z) in zip(axes.ravel(), panels):
        # Reshape the flat 6 400-length score vector back into an 80x80 image and draw it.
        # `viridis` colour map: dark = low, bright yellow = high.
        im = ax.imshow(z.reshape(grid, grid), origin="lower", extent=extent,
                       aspect="auto", cmap="viridis")
        # Overlay the three reference markers on every panel.
        ax.scatter(model.X[:, 0], model.X[:, 1], c="white", edgecolors="k", s=30, label="observed")
        ax.scatter(*model.x_best, c="cyan", edgecolors="k", marker="D", s=60, label="incumbent")
        if proposed is not None:
            ax.scatter(*proposed, c="red", marker="*", s=180, edgecolors="k", label="proposed")
        ax.set_title(title)
        ax.set_xlabel("x1"); ax.set_ylabel("x2")
        fig.colorbar(im, ax=ax, fraction=0.046)   # colour scale next to each panel

    axes[0, 0].legend(loc="upper right", fontsize=8)
    fig.suptitle(f"Function {model.func_id} ({model.kind} GP) — posterior & acquisitions")
    fig.tight_layout()
    if save:
        fig.savefig(save, dpi=110, bbox_inches="tight")
    return fig


def plot_slices(model, beta=2.0, xi=0.01, proposed_u=None, n=120, save=None):
    """For higher-D functions: slice the model along each input axis through the
    current best point. Shows the guess (line), uncertainty band, and where I'm
    about to query, one panel per input.
    """
    d = model.d
    ncols = min(4, d)
    nrows = int(np.ceil(d / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.2 * ncols, 3.4 * nrows), squeeze=False)
    line = np.linspace(0, 1, n)
    for j in range(d):
        ax = axes[j // ncols][j % ncols]
        U = np.tile(model.u_best, (n, 1))
        U[:, j] = line
        mean, std = model.predict(U)
        xs = from_unit(U, model.b)[:, j]
        ax.plot(xs, mean, color="C0", label="GP mean")
        ax.fill_between(xs, mean - 1.96 * std, mean + 1.96 * std, alpha=0.2, color="C0")
        ax.axvline(model.x_best[j], color="cyan", ls="--", label="incumbent")
        if proposed_u is not None:
            ax.axvline(from_unit(proposed_u, model.b)[j], color="red", ls="-", label="proposed")
        ax.set_title(f"x{j + 1} (others at incumbent)")
        ax.set_xlabel(f"x{j + 1}")
    for k in range(d, nrows * ncols):
        axes[k // ncols][k % ncols].axis("off")
    axes[0][0].legend(fontsize=8)
    fig.suptitle(f"Function {model.func_id} ({model.kind} GP) — 1D slices through the incumbent")
    fig.tight_layout()
    if save:
        fig.savefig(save, dpi=110, bbox_inches="tight")
    return fig


def plot_diagnostics(model, save=None):
    """Two health-check charts per function:
      - "best observed so far" climbing curve — am I making progress round-on-round?
      - leave-one-out: hide each known point in turn, ask the model to guess it,
        plot predicted vs actual. If the cloud hugs the diagonal, the model is
        trustworthy on what it's already seen.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    running = np.maximum.accumulate(model.y)
    ax1.plot(np.arange(1, len(model.y) + 1), running, marker="o", ms=3)
    ax1.set_title(f"Function {model.func_id} — best observed so far")
    ax1.set_xlabel("observation #"); ax1.set_ylabel("max y")

    loo = _loo_predict(model)
    ax2.scatter(model.y, loo, s=25)
    lims = [min(model.y.min(), loo.min()), max(model.y.max(), loo.max())]
    ax2.plot(lims, lims, "k--", lw=1)
    ax2.set_title(f"Leave-one-out predicted vs observed ({model.kind})")
    ax2.set_xlabel("observed y"); ax2.set_ylabel("LOO predicted y")
    fig.tight_layout()
    if save:
        fig.savefig(save, dpi=110, bbox_inches="tight")
    return fig


def loo_r2(model):
    """Leave-one-out R² for the GP — how well does the surrogate predict held-out points?

    Acts as a hard *trust gate* for everything downstream. Acquisition values are only
    meaningful when the GP's predictions on data it hasn't seen are calibrated.

    - **R² > 0.7** — reliable surrogate. EI / PI / UCB scores can be trusted as exploit signals.
    - **0 < R² ≤ 0.7** — partial signal. Use balanced acquisitions (EI with conservative xi);
      don't commit hard to model predictions.
    - **R² < 0** — model is worse than predicting the mean. The GP is fitting noise.
      Don't trust *any* acquisition built on its mean or std; fall back to pure space-filling.

    Inspired by Omkar Joshi's reflection in week 5 — he reported negative R² on F1, F2, F3, F7,
    explaining why those functions had stalled. Worth computing every round before strategy.
    """
    y_pred = _loo_predict(model)
    ss_res = float(np.sum((model.y - y_pred) ** 2))
    ss_tot = float(np.sum((model.y - model.y.mean()) ** 2))
    if ss_tot < 1e-12:
        return 0.0
    return 1.0 - ss_res / ss_tot


def compute_r2_history(weeks=None, save=True):
    """Re-fit the GP at each historical week's data state and compute LOO R².

    The CSVs preserve submission order (one row appended per round, after the seed
    block), so truncating to the first N points reconstructs the state of the data
    at the start of each round. This gives us a per-function R² history we never
    bothered to record at the time — useful for spotting trends and avoiding noise
    from any single week's leave-one-out split.

    Returns a long-format DataFrame: week, fid, n, r2.
    """
    if weeks is None:
        weeks = list(range(1, 7))                  # W1 through W6 covered by default
    seed_sizes = {fid: FUNCTION_INFO[fid - 1]["n_seed"] for fid in FUNC_IDS}
    rows = []
    for week in weeks:
        for fid in FUNC_IDS:
            X, y, d = load(fid)
            n_at_start = seed_sizes[fid] + (week - 1)   # state going into that week
            if n_at_start > len(y):
                continue
            X_w, y_w = X[:n_at_start], y[:n_at_start]
            b = bounds(fid, d)
            gp = build_gp("matern", d)
            gp.fit(to_unit(X_w, b), y_w)
            m = Model(fid, "matern", gp, X_w, y_w, b)
            rows.append(dict(week=week, fid=fid, n=n_at_start, r2=loo_r2(m)))
    df = pd.DataFrame(rows)
    if save:
        df.to_csv(os.path.join(DATA_DIR, "r2_history.csv"), index=False)
    return df


def r2_trend(fid, last_k=3, path=None):
    """Trend classification of recent R² for a function — 'IMPROVING', 'STABLE',
    'DECLINING' or 'INSUFFICIENT' if fewer than 2 data points.

    Used in combination with the latest R² to decide whether to trust the
    surrogate this week. A function whose R² is bouncing around zero is a different
    creature from one steadily climbing toward reliability.
    """
    if path is None:
        path = os.path.join(DATA_DIR, "r2_history.csv")
    df = pd.read_csv(path)
    series = df[df.fid == fid].sort_values("week").tail(last_k)["r2"].to_numpy()
    if len(series) < 2:
        return "INSUFFICIENT"
    diffs = np.diff(series)
    if all(d > 0.05 for d in diffs):
        return "IMPROVING"
    if all(d < -0.05 for d in diffs):
        return "DECLINING"
    return "STABLE"


def gate(r2, trend):
    """Combined R² + trend → strategy recommendation.

    Refines the simpler R²-only gate from week 5. A reliable model that's declining
    deserves caution; a barely-positive model that's improving deserves a chance to
    earn promotion; a broken model that's recovering can stay on space_fill but
    isn't a write-off.
    """
    if r2 > 0.7:
        return "CAUTION" if trend == "DECLINING" else "RELIABLE"
    if r2 > 0:
        return "PROMOTE" if trend == "IMPROVING" else "PARTIAL"
    return "RECOVERING" if trend == "IMPROVING" else "BROKEN"


def rf_importance(func_id, n_estimators=200, seed=0):
    """Random Forest feature importance per input — a third opinion alongside ARD
    lengthscales (GP) and gradient sensitivities (NN).

    Useful as a tie-breaker when the GP and NN disagree on which dimensions matter,
    or as confirmation when they agree. The forest is non-parametric and partitions
    the input space differently to both — so it catches categorical-like jumps that
    smooth-kernel methods miss.

    Returns a numpy array of length d; higher value = more influential input.
    """
    from sklearn.ensemble import RandomForestRegressor
    X, y, d = load(func_id)
    b = bounds(func_id, d)
    rf = RandomForestRegressor(n_estimators=n_estimators, random_state=seed)
    rf.fit(to_unit(X, b), y)
    return rf.feature_importances_


def _loo_predict(model):
    """Leave-One-Out predictions — a self-honesty check for the model.

    For each known point in turn: hide it, retrain a fresh model on the other n-1
    points, then ask the retrained model to guess the hidden point's score. If the
    guesses end up close to the real scores, the model generalises well — it's
    learning the shape of the function, not just memorising the data.

    Used by `plot_diagnostics` to draw the "predicted vs observed" scatter. A tight
    cloud along the diagonal means the model is trustworthy; a wide scatter means
    its predictions (and therefore the next-query suggestions built on top of them)
    should be taken with a pinch of salt.

    Cost note: this trains `n` separate models, so it scales as O(n × fit-cost) —
    fine for the 10-40 points per function we have here, would be too slow at
    thousands of points.
    """
    n = len(model.y)
    pred = np.empty(n)
    for i in range(n):
        # Build a boolean mask that's True for every point *except* point i —
        # so model.U[mask] and model.y[mask] are the remaining n-1 input/output pairs.
        mask = np.arange(n) != i
        # Train a fresh model of the same kind on those n-1 points.
        # (Has to be fresh: scikit-learn GPs hold onto their training data internally.)
        gp = build_gp(model.kind, model.d)
        gp.fit(model.U[mask], model.y[mask])
        # Ask the retrained model to predict the held-out point we hid above.
        pred[i] = gp.predict(model.U[i:i + 1])[0]
    return pred


# --------------------------------------------------------------------------- driver
def run_function(func_id, kind="matern", acq="ei", beta=2.0, xi=0.01, seed=0, **kw):
    """One round, one function: train the model, pick the next query, package up
    everything the notebook needs to display (proposed input, model's guess + std,
    all four scoring rules at that input, and the portal-ready submission string).
    """
    model = fit(func_id, kind=kind, **kw)
    prop = propose_next(model, acq=acq, beta=beta, xi=xi, seed=seed)
    all_acq = acq_values(model, prop["u"].reshape(1, -1), beta=beta, xi=xi)
    prop["acq_all"] = {k: float(v[0]) for k, v in all_acq.items()}
    prop["submission"] = format_submission(prop["x"])
    validate_submission(prop["submission"], model.d)
    prop["incumbent_x"] = model.x_best
    prop["incumbent_y"] = model.y_best
    prop["n_data"] = len(model.y)
    prop["model"] = model
    return prop


def run_all(kind="matern", acq="ei", beta=2.0, xi=0.01, seed=0, **kw):
    """Run all eight functions with the same settings — handy for quick sanity checks."""
    return {fid: run_function(fid, kind=kind, acq=acq, beta=beta, xi=xi, seed=seed, **kw)
            for fid in FUNC_IDS}


# --------------------------------------------------------------------------- reflection
def render_reflection(week, results, path=None, overwrite=False):
    """Drop a starter weekly reflection on disk: standard intro, the three
    Part-2 prompts (left blank for me to fill in), and an auto-generated numbers
    table summarising what each function did this round.

    Refuses to overwrite an already-written reflection unless `overwrite=True`.
    """
    os.makedirs(REFLECT_DIR, exist_ok=True)
    if path is None:
        path = os.path.join(REFLECT_DIR, f"week{week:02d}.md")
    if os.path.exists(path) and not overwrite:
        return path
    rows = []
    for fid in FUNC_IDS:
        r = results[fid]
        info = FUNCTION_INFO[fid - 1]
        rows.append(
            f"| f{fid} | {info['dims']} | {r['n_data']} | {r['incumbent_y']:.4g} | "
            f"{r['mean']:.4g} | {r['std']:.4g} | {r['acq']} | "
            f"ei={r['acq_all']['ei']:.3g}, ucb={r['acq_all']['ucb']:.3g}, "
            f"pi={r['acq_all']['pi']:.3g}, var={r['acq_all']['var']:.3g} | `{r['submission']}` |")
    table = "\n".join(rows)
    text = f"""# Week {week:02d} reflection — BBO capstone

> Keep the posted reflection under 700 words. The appendix below is reference, not part of the word count.

## How I approached this

Each function is a black box — I can't see its formula, only the handful of input → output points I've gathered so far. The process is the same for all eight: fit a **Gaussian Process (GP)** to the known points (it predicts the output everywhere, plus how *unsure* it is), then use an **acquisition function** to score every candidate input and query the one that scores highest.

I built three acquisition modes and pick one per function depending on the stage:
- **Explore** — UCB with a high β: chase the most uncertain regions to map the space.
- **Balanced** — Expected Improvement (EI): trade off "might be high" against "unsure".
- **Optimise** — Probability of Improvement (PI): squeeze the area around the current best.

Early rounds lean Explore; later rounds shift toward Optimise as the picture firms up.

## 1. Main principle / heuristic per query point
_What guided each choice — exploitation of high outputs, exploration of uncertain regions, diversity of samples?_



## 2. Most challenging function(s) and why
_Which were hardest to query and why? What additional information would have helped?_



## 3. Strategy adjustment for next round
_How will you adapt given current performance and uncertainty levels?_



---

## Appendix — this round's numbers (auto-generated)

| func | d | n_data | incumbent y | pred mean@x | pred std@x | acq used | acq values @proposed | submission |
|------|---|--------|-------------|-------------|------------|----------|----------------------|------------|
{table}
"""
    with open(path, "w") as f:
        f.write(text)
    return path
