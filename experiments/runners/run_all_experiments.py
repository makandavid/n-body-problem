"""
Runs the full strong and weak scaling experiment matrix for both Python and Rust,
sequential and parallel. Results are appended to the existing benchmark CSVs.

Usage:
    python experiments/run_all_experiments.py [--max_cores N] [--skip_python]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from multiprocessing import cpu_count
from pathlib import Path

# ── Experiment parameters ────────────────────────────────────────────────────

STEPS = 200          # Fixed step count throughout — long enough to be meaningful
DT = 0.001           # Small enough for stable integration

# Strong scaling: fixed N, vary cores
STRONG_N = 1000      # Large enough that parallelism pays off

# Weak scaling: N per core stays constant, total N = N_PER_CORE * cores
# This keeps each core's O(N²) share roughly constant
N_PER_CORE_WEAK = 200

# Thread/worker counts to sweep (only counts ≤ available cores are actually run)
THREAD_COUNTS = [1, 2, 4, 8, 12]

# ── Helpers ──────────────────────────────────────────────────────────────────

def run(cmd: list[str], label: str) -> None:
    print(f"\n{'─'*60}")
    print(f"  {label}")
    print(f"  {' '.join(cmd)}")
    print(f"{'─'*60}")
    subprocess.run(cmd, check=True)


def python_seq(n: int, steps: int) -> list[str]:
    return ["uv", "run", "python", "-m", "experiments.runners.run_python_seq",
            "--n", str(n), "--steps", str(steps), "--dt", str(DT), "--write_trajectory"]


def python_par(n: int, steps: int, workers: int) -> list[str]:
    return ["uv", "run", "python", "-m", "experiments.runners.run_python_par",
            "--n", str(n), "--steps", str(steps), "--dt", str(DT),
            "--workers", str(workers), "--write_trajectory"]


def rust_seq(n: int, steps: int) -> list[str]:
    return ["uv", "run", "python", "-m", "experiments.runners.run_rust_seq",
            "--n", str(n), "--steps", str(steps), "--dt", str(DT), "--write_trajectory"]


def rust_par(n: int, steps: int, workers: int) -> list[str]:
    return ["uv", "run", "python", "-m", "experiments.runners.run_rust_par",
            "--n", str(n), "--steps", str(steps), "--dt", str(DT),
            "--workers", str(workers), "--write_trajectory"]


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max_cores", type=int, default=cpu_count(),
                        help="Cap the thread sweep at this many cores")
    parser.add_argument("--skip_python", action="store_true",
                        help="Skip Python runs (they are slow for large N)")
    args = parser.parse_args()

    max_cores = min(args.max_cores, cpu_count())
    thread_counts = [t for t in THREAD_COUNTS if t <= max_cores]

    print(f"\n{'='*60}")
    print(f"  N-Body Scaling Experiments")
    print(f"  Available cores : {cpu_count()}")
    print(f"  Core sweep      : {thread_counts}")
    print(f"  Strong N        : {STRONG_N}")
    print(f"  N/core (weak)   : {N_PER_CORE_WEAK}")
    print(f"  Steps           : {STEPS},  dt={DT}")
    print(f"{'='*60}")

    # ── 1. Baselines: sequential at fixed N ──────────────────────────────────
    print("\n### SEQUENTIAL BASELINES (strong N) ###")

    if not args.skip_python:
        run(python_seq(STRONG_N, STEPS), f"Python SEQ  N={STRONG_N}")

    run(rust_seq(STRONG_N, STEPS), f"Rust   SEQ  N={STRONG_N}")

    # ── 2. Strong scaling: fixed N, sweep cores ───────────────────────────────
    # Amdahl's law: T(p) = T_serial * (s + (1-s)/p)
    # Speedup S(p) = T(1) / T(p)
    print("\n### STRONG SCALING (fixed N, sweep cores) ###")

    for t in thread_counts:
        if not args.skip_python:
            run(python_par(STRONG_N, STEPS, t),
                f"Python PAR  N={STRONG_N}, workers={t}")

        run(rust_par(STRONG_N, STEPS, t),
            f"Rust   PAR  N={STRONG_N}, threads={t}")

    # ── 3. Weak scaling: N grows with cores ───────────────────────────────────
    # Gustafson's law: S(p) = p - α(p-1)  where α is the serial fraction
    # Ideal: runtime stays constant as N and p grow together
    print("\n### WEAK SCALING (N = N_per_core × cores) ###")

    for t in thread_counts:
        n_weak = N_PER_CORE_WEAK * t

        if not args.skip_python:
            run(python_par(n_weak, STEPS, t),
                f"Python PAR  N={n_weak} ({N_PER_CORE_WEAK}×{t}), workers={t}")

        run(rust_par(n_weak, STEPS, t),
            f"Rust   PAR  N={n_weak} ({N_PER_CORE_WEAK}×{t}), threads={t}")

    print(f"\n{'='*60}")
    print("  All experiments complete.")
    print("  Results written to:")
    print("    experiments/results/python_benchmarks.csv")
    print("    experiments/results/rust_benchmarks.csv")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()