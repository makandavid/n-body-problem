from __future__ import annotations

from multiprocessing import cpu_count
import time
import csv
from pathlib import Path
from typing import Optional
import argparse

from python.nbody.generator import generate_bodies
from python.nbody.parallel_simulation import simulate_parallel

RESULTS_FILE = Path("experiments/results/python_benchmarks.csv")
HEADER = ["language", "mode", "n_bodies", "steps", "dt", "workers", "time_s"]


def ensure_header(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.stat().st_size == 0:
        with path.open("w", newline="") as f:
            csv.writer(f).writerow(HEADER)

def run_simulation(n_bodies: int, n_steps: int, dt: float, num_workers: int, write_trajectory: bool = True) -> float:
    bodies = generate_bodies(n_bodies)

    trajectory_file: Optional[Path] = Path(f"data/python_par_{n_bodies}_{n_steps}.csv") if write_trajectory else None
    writer: Optional[csv.writer] = None
    output_file = None

    if trajectory_file:
        trajectory_file.parent.mkdir(parents=True, exist_ok=True)
        output_file = trajectory_file.open("w", newline="")
        writer = csv.writer(output_file)
        writer.writerow(["step", "body_id", "x", "y", "vx", "vy"])

    start = time.perf_counter()
    simulate_parallel(bodies, n_steps, dt, num_workers, writer)
    elapsed = time.perf_counter() - start

    if output_file is not None:
        output_file.close()

    return elapsed

def main() -> None:
    parser = argparse.ArgumentParser(description="Run Python parallel N-body simulation.")
    parser.add_argument("--n", type=int, default=500)
    parser.add_argument("--steps", type=int, default=100)
    parser.add_argument("--dt", type=float, default=0.001)
    parser.add_argument("--workers", type=int, default=cpu_count())
    parser.add_argument("--write_trajectory", action="store_true")

    args = parser.parse_args()

    elapsed = run_simulation(args.n, args.steps, args.dt, args.workers, args.write_trajectory)

    print(f"[PYTHON PAR] N={args.n}, steps={args.steps}, dt={args.dt}, workers={args.workers}")
    print(f"Execution time: {elapsed:.6f} s")

    ensure_header(RESULTS_FILE)
    with RESULTS_FILE.open("a", newline="") as f:
        csv.writer(f).writerow(["python", "parallel", args.n, args.steps, args.dt, args.workers, elapsed])


if __name__ == "__main__":
    main()