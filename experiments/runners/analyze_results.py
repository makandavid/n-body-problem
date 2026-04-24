"""
Reads benchmark CSVs, computes mean/std/outliers per configuration,
generates the 4 required scaling graphs with theory lines,
and prints supporting tables.
"""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RESULTS = {
    "python": Path("experiments/results/python_benchmarks.csv"),
    "rust":   Path("experiments/results/rust_benchmarks.csv"),
}
OUT = Path("experiments/results/figures")
OUT.mkdir(parents=True, exist_ok=True)

# ── Load data ────────────────────────────────────────────────────────────────

def load(path: Path) -> list[dict]:
    rows = []
    with path.open() as f:
        for r in csv.DictReader(f):
            rows.append({
                "language": r["language"],
                "mode":     r["mode"],
                "n":        int(r["n_bodies"]),
                "steps":    int(r["steps"]),
                "workers":  int(r["workers"]),
                "time":     float(r["time_s"]),
            })
    return rows

def group(rows, **filters):
    """Return list of times matching all filter key=value pairs."""
    out = []
    for r in rows:
        if all(r[k] == v for k, v in filters.items()):
            out.append(r["time"])
    return out

# ── Statistics ───────────────────────────────────────────────────────────────

def stats(times: list[float]) -> dict:
    a = np.array(times)
    mean = float(np.mean(a))
    std  = float(np.std(a, ddof=1)) if len(a) > 1 else 0.0
    q1, q3 = np.percentile(a, [25, 75])
    iqr = q3 - q1
    outliers = [t for t in times if t < q1 - 1.5*iqr or t > q3 + 1.5*iqr]
    return {"mean": mean, "std": std, "n": len(a), "outliers": outliers}

# ── Serial fraction estimation ────────────────────────────────────────────────

def estimate_alpha(speedups: list[float], cores: list[int]) -> float:
    """Least-squares fit of Amdahl's law: S = 1/(α + (1-α)/p)."""
    best_alpha, best_err = 0.5, float("inf")
    for alpha in np.linspace(0.001, 0.999, 5000):
        pred = [1.0 / (alpha + (1 - alpha) / p) for p in cores]
        err  = sum((s - p)**2 for s, p in zip(speedups, pred))
        if err < best_err:
            best_err, best_alpha = err, alpha
    return best_alpha

# ── Plotting helpers ──────────────────────────────────────────────────────────

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                      "axes.titlesize": 13, "figure.dpi": 150})

def plot_strong(cores, speedups, errs, alpha, lang, ax):
    p = np.linspace(1, max(cores), 200)
    ideal        = p
    amdahl_curve = 1.0 / (alpha + (1 - alpha) / p)

    ax.plot(p, ideal,          "k--", lw=1.2, label="Ideal linear", alpha=0.5)
    ax.plot(p, amdahl_curve,   "r:",  lw=1.8,
            label=f"Amdahl limit (α={alpha:.3f})")
    ax.errorbar(cores, speedups, yerr=errs, fmt="bo-", lw=2, ms=7,
                capsize=4, label=f"{lang} measured")
    ax.set_xlabel("Number of cores")
    ax.set_ylabel("Speedup  S(p) = T_seq / T(p)")
    ax.set_xticks(cores)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

def plot_weak(cores, efficiencies, errs, alpha_g, lang, ax):
    p     = np.linspace(1, max(cores), 200)
    ideal = np.ones_like(p)
    # Gustafson scaled speedup efficiency: (p - alpha_g*(p-1)) / p
    gust  = (p - alpha_g * (p - 1)) / p

    ax.plot(p, ideal,  "k--", lw=1.2, label="Ideal (efficiency=1)", alpha=0.5)
    ax.plot(p, gust,   "r:",  lw=1.8,
            label=f"Gustafson limit (α={alpha_g:.3f})")
    ax.errorbar(cores, efficiencies, yerr=errs, fmt="bs-", lw=2, ms=7,
                capsize=4, label=f"{lang} measured")
    ax.set_xlabel("Number of cores")
    ax.set_ylabel("Weak scaling efficiency  E(p) = T(1) / T(p)")
    ax.set_xticks(cores)
    ax.set_ylim(0, 1.2)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

# ── Supporting table printer ──────────────────────────────────────────────────

def print_table(title, headers, rows):
    col_w = [max(len(h), max(len(str(r[i])) for r in rows))
             for i, h in enumerate(headers)]
    sep = "+" + "+".join("-" * (w + 2) for w in col_w) + "+"
    fmt = "|" + "|".join(f" {{:<{w}}} " for w in col_w) + "|"
    print(f"\n{title}")
    print(sep)
    print(fmt.format(*headers))
    print(sep)
    for r in rows:
        print(fmt.format(*[str(x) for x in r]))
    print(sep)

# ── Main analysis ─────────────────────────────────────────────────────────────

def analyze(lang: str, rows: list[dict],
            strong_n: int, weak_n_per_core: int, steps: int):

    cores_all = sorted(set(r["workers"] for r in rows if r["mode"] == "parallel"))

    # ── Sequential baseline ───────────────────────────────────────────────
    seq_times = group(rows, mode="sequential", n=strong_n, steps=steps)
    if not seq_times:
        print(f"[{lang}] No sequential data found for N={strong_n}. Skipping.")
        return
    seq_stat  = stats(seq_times)
    T_seq     = seq_stat["mean"]

    print(f"\n{'='*60}")
    print(f"  {lang.upper()}  —  Sequential baseline  N={strong_n}")
    print(f"  mean={T_seq:.4f}s  std={seq_stat['std']:.4f}s  n={seq_stat['n']}")
    print(f"  outliers: {seq_stat['outliers'] or 'none'}")

    # ── Strong scaling ────────────────────────────────────────────────────
    strong_cores, strong_speedups, strong_errs = [], [], []
    strong_table_rows = []

    for p in cores_all:
        t_list = group(rows, mode="parallel", n=strong_n, steps=steps, workers=p)
        if not t_list:
            continue
        s = stats(t_list)
        speedup      = T_seq / s["mean"]
        speedup_err  = speedup * (s["std"] / s["mean"])  # error propagation
        strong_cores.append(p)
        strong_speedups.append(speedup)
        strong_errs.append(speedup_err)
        strong_table_rows.append([
            p, s["n"], f"{s['mean']:.4f}", f"{s['std']:.4f}",
            f"{speedup:.3f}", f"{speedup_err:.3f}",
            len(s["outliers"]) or "—"
        ])

    if not strong_cores:
        print(f"[{lang}] No parallel strong scaling data found.")
        return

    alpha = estimate_alpha(strong_speedups, strong_cores)

    print_table(
        f"\n[{lang.upper()}] Strong Scaling — N={strong_n}, steps={steps}",
        ["Cores", "Runs", "Mean (s)", "Std (s)", "Speedup", "Speedup err", "Outliers"],
        strong_table_rows
    )
    print(f"  Fitted serial fraction α = {alpha:.4f}  "
          f"(parallel fraction = {1-alpha:.4f})")
    print(f"  Amdahl theoretical max speedup (p=∞) = {1/alpha:.2f}×")

    fig, ax = plt.subplots(figsize=(7, 5))
    plot_strong(strong_cores, strong_speedups, strong_errs, alpha, lang.capitalize(), ax)
    ax.set_title(f"Strong Scaling — {lang.capitalize()}\nN={strong_n}, {steps} steps  (α={alpha:.3f})")
    fig.tight_layout()
    out_path = OUT / f"strong_{lang}.png"
    fig.savefig(out_path)
    plt.close()
    print(f"  Saved: {out_path}")

    # ── Weak scaling ──────────────────────────────────────────────────────
    # p=1 baseline: par run with 1 worker at N = weak_n_per_core * 1
    weak_cores, weak_effs, weak_errs = [], [], []
    weak_table_rows = []

    baseline_weak_times = group(rows, mode="parallel",
                                n=weak_n_per_core * 1, steps=steps, workers=1)
    if not baseline_weak_times:
        print(f"[{lang}] No weak scaling p=1 baseline found.")
        return
    T_weak_base = stats(baseline_weak_times)["mean"]

    for p in cores_all:
        n_weak = weak_n_per_core * p
        t_list = group(rows, mode="parallel", n=n_weak, steps=steps, workers=p)
        if not t_list:
            continue
        s   = stats(t_list)
        eff = T_weak_base / s["mean"]
        eff_err = eff * (s["std"] / s["mean"])
        weak_cores.append(p)
        weak_effs.append(eff)
        weak_errs.append(eff_err)
        weak_table_rows.append([
            p, n_weak, s["n"], f"{s['mean']:.4f}", f"{s['std']:.4f}",
            f"{eff:.3f}", f"{eff_err:.3f}",
            len(s["outliers"]) or "—"
        ])

    # Gustafson serial fraction from efficiency: E(p) = (p - α(p-1))/p → α
    # fit by least squares on α
    if len(weak_cores) > 1:
        best_ag, best_err = 0.5, float("inf")
        for ag in np.linspace(0.001, 0.999, 5000):
            pred = [(p - ag * (p - 1)) / p for p in weak_cores]
            err  = sum((e - pe)**2 for e, pe in zip(weak_effs, pred))
            if err < best_err:
                best_err, best_ag = err, ag
    else:
        best_ag = 1 - weak_effs[0] if weak_effs else 0.5

    print_table(
        f"\n[{lang.upper()}] Weak Scaling — N per core={weak_n_per_core}, steps={steps}",
        ["Cores", "N", "Runs", "Mean (s)", "Std (s)", "Efficiency", "Eff err", "Outliers"],
        weak_table_rows
    )
    print(f"  Fitted Gustafson serial fraction α = {best_ag:.4f}")
    print(f"  Gustafson scaled speedup at p=12: "
          f"{12 - best_ag*(12-1):.2f}×")

    fig, ax = plt.subplots(figsize=(7, 5))
    plot_weak(weak_cores, weak_effs, weak_errs, best_ag, lang.capitalize(), ax)
    ax.set_title(f"Weak Scaling — {lang.capitalize()}\n"
                 f"N={weak_n_per_core}×p, {steps} steps  (α={best_ag:.3f})")
    fig.tight_layout()
    out_path = OUT / f"weak_{lang}.png"
    fig.savefig(out_path)
    plt.close()
    print(f"  Saved: {out_path}")


if __name__ == "__main__":
    all_rows = {}
    for lang, path in RESULTS.items():
        if path.exists():
            all_rows[lang] = load(path)
        else:
            print(f"WARNING: {path} not found, skipping {lang}")

    if "python" in all_rows:
        analyze("python", all_rows["python"],
                strong_n=150, weak_n_per_core=50, steps=200)

    if "rust" in all_rows:
        analyze("rust", all_rows["rust"],
                strong_n=1000, weak_n_per_core=200, steps=200)