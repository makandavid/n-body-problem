"""
Full scaling experiment suite — 30 runs per configuration.
Python uses N=150 (feasible in ~10s/run). Rust uses N=1000 and N=5000.
"""
from __future__ import annotations
import argparse
import subprocess
from multiprocessing import cpu_count

STEPS       = 200
DT          = 0.001
RUNS        = 30

# Python uses smaller N so 30 runs are feasible
PYTHON_STRONG_N   = 150
N_PER_CORE_PYTHON = 50   # weak: N = 50 * p

# Rust can handle larger N
RUST_STRONG_N     = 1000
N_PER_CORE_RUST   = 200  # weak: N = 200 * p

THREAD_COUNTS = [1, 2, 4, 8, 12]

# ── Helpers ──────────────────────────────────────────────────────────────────

def run(cmd, label):
    print(f"\n{'─'*60}\n  {label}\n  {' '.join(cmd)}\n{'─'*60}")
    subprocess.run(cmd, check=True)

def py_seq(n, runs=RUNS):
    return ["uv", "run", "python", "-m", "experiments.runners.run_python_seq",
            "--n", str(n), "--steps", str(STEPS), "--dt", str(DT), "--write_trajectory", "--runs", str(runs)]

def py_par(n, workers, runs=RUNS):
    return ["uv", "run", "python", "-m", "experiments.runners.run_python_par",
            "--n", str(n), "--steps", str(STEPS), "--dt", str(DT),
            "--workers", str(workers), "--write_trajectory", "--runs", str(runs)]

def rs_seq(n, runs=RUNS):
    return ["uv", "run", "python", "-m", "experiments.runners.run_rust_seq",
            "--n", str(n), "--steps", str(STEPS), "--dt", str(DT), "--write_trajectory", "--runs", str(runs)]

def rs_par(n, workers, runs=RUNS):
    return ["uv", "run", "python", "-m", "experiments.runners.run_rust_par",
            "--n", str(n), "--steps", str(STEPS), "--dt", str(DT),
            "--workers", str(workers), "--write_trajectory", "--runs", str(runs)]


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max_cores", type=int, default=cpu_count())
    parser.add_argument("--runs", type=int, default=RUNS)
    parser.add_argument("--skip_python", action="store_true")
    args = parser.parse_args()

    cores = [t for t in THREAD_COUNTS if t <= min(args.max_cores, cpu_count())]
    R = args.runs

    print(f"\nCores to test : {cores}")
    print(f"Runs per config: {R}")

    # ── Python sequential baseline (30 runs) ──────────────────────────────
    if not args.skip_python:
        run(py_seq(PYTHON_STRONG_N, R),
            f"Python SEQ baseline N={PYTHON_STRONG_N} × {R} runs")

    # ── Rust sequential baseline (30 runs) ────────────────────────────────
    run(rs_seq(RUST_STRONG_N, R),
        f"Rust SEQ baseline N={RUST_STRONG_N} × {R} runs")

    # ── Strong scaling ────────────────────────────────────────────────────
    print("\n### STRONG SCALING ###")
    for t in cores:
        if not args.skip_python:
            run(py_par(PYTHON_STRONG_N, t, R),
                f"Python PAR strong N={PYTHON_STRONG_N} workers={t} × {R} runs")
        run(rs_par(RUST_STRONG_N, t, R),
            f"Rust PAR strong N={RUST_STRONG_N} threads={t} × {R} runs")

    # ── Weak scaling ──────────────────────────────────────────────────────
    print("\n### WEAK SCALING ###")
    for t in cores:
        if not args.skip_python:
            n_py = N_PER_CORE_PYTHON * t
            run(py_par(n_py, t, R),
                f"Python PAR weak N={n_py} ({N_PER_CORE_PYTHON}×{t}) workers={t} × {R} runs")

        n_rs = N_PER_CORE_RUST * t
        run(rs_par(n_rs, t, R),
            f"Rust PAR weak N={n_rs} ({N_PER_CORE_RUST}×{t}) threads={t} × {R} runs")

    print("\nAll done. Results in experiments/results/")


if __name__ == "__main__":
    main()