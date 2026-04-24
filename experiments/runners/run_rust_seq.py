from __future__ import annotations
import csv
import re
import subprocess
from pathlib import Path
import argparse

RESULTS_FILE = Path("experiments/results/rust_benchmarks.csv")
HEADER = ["language", "mode", "n_bodies", "steps", "dt", "workers", "time_s"]

TIME_RE = re.compile(r"Execution time:\s+([\d.]+)(µs|ms|s|ns)")

MULTIPLIERS = {"ns": 1e-9, "µs": 1e-6, "ms": 1e-3, "s": 1.0}

def parse_rust_time(output: str) -> float:
    m = TIME_RE.search(output)
    if not m:
        raise ValueError(f"Could not parse execution time from Rust output:\n{output}")
    value, unit = float(m.group(1)), m.group(2)
    return value * MULTIPLIERS[unit]


def ensure_header(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.stat().st_size == 0:
        with path.open("w", newline="") as f:
            csv.writer(f).writerow(HEADER)

def main() -> None:
    parser = argparse.ArgumentParser(description="Run Rust N-body sequential simulation and log benchmark.")
    parser.add_argument("--n", type=int, default=500, help="Number of bodies")
    parser.add_argument("--steps", type=int, default=100, help="Number of simulation steps")
    parser.add_argument("--dt", type=float, default=0.001, help="Time delta per step")
    parser.add_argument("--write_trajectory", action="store_true", help="Write trajectory CSV for visualization")
    parser.add_argument("--runs", type=int, default=1)
    args = parser.parse_args()

    cmd = [
        "cargo", "run", "--release", "--bin", "run_seq", "--quiet", "--",
        str(args.n), str(args.steps), str(args.dt)
    ]
    if args.write_trajectory:
        cmd.append("write_trajectory")

    ensure_header(RESULTS_FILE)

    for run_id in range(args.runs):
        result = subprocess.run(cmd, cwd="rust", check=True, capture_output=True, text=True)
        print(result.stdout)
        elapsed = parse_rust_time(result.stdout)
        print(f"[ORCH] Parsed Rust sequential time {run_id+1}/{args.runs} -> {elapsed:.6f}s")
        with RESULTS_FILE.open("a", newline="") as f:
            csv.writer(f).writerow(["rust", "sequential", args.n, args.steps, args.dt, 1, f"{elapsed:.6f}"])


if __name__ == "__main__":
    main()