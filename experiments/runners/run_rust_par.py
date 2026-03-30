from __future__ import annotations
from multiprocessing import cpu_count
import subprocess
import time
from pathlib import Path
import argparse

RESULTS_FILE = Path("experiments/results/rust_benchmarks.csv")
RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Rust N-body parallel simulation and log benchmark.")
    parser.add_argument("--n", type=int, default=500, help="Number of bodies")
    parser.add_argument("--steps", type=int, default=100, help="Number of simulation steps")
    parser.add_argument("--dt", type=float, default=0.01, help="Time delta per step")
    parser.add_argument("--workers", type=int, default=cpu_count(), help="Number of threads")
    parser.add_argument("--write_trajectory", action="store_true", help="Write trajectory CSV for visualization")
    args = parser.parse_args()

    cmd = [
        "cargo", "run", "--release", "--bin", "run_par", "--quiet", "--",
        str(args.n), str(args.steps), str(args.dt), str(args.workers)
    ]
    if args.write_trajectory:
        cmd.append("write_trajectory")

    start = time.perf_counter()

    subprocess.run(cmd, cwd="rust", check=True)

    end = time.perf_counter()
    elapsed = end - start
    print(f"[ORCH] Rust parallel run finished in {elapsed:.3f} s")

    with RESULTS_FILE.open("a", newline="") as f:
        f.write(f"rust,parallel,{args.n},{args.steps},{args.dt},{args.workers},{elapsed:.6f}\n")


if __name__ == "__main__":
    main()