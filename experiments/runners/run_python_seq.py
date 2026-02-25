from __future__ import annotations

import time
import csv
from pathlib import Path
from typing import Optional
import argparse

from python.nbody.generator import generate_bodies
from python.nbody.simulation import simulate


def run_simulation(n_bodies: int, n_steps: int, dt: float, write_trajectory: bool = True) -> float:
    bodies = generate_bodies(n_bodies)

    trajectory_file: Optional[Path] = Path(f"data/python_{n_bodies}_{n_steps}.csv") if write_trajectory else None
    writer: Optional[csv.writer] = None
    output_file = None

    if trajectory_file:
        trajectory_file.parent.mkdir(parents=True, exist_ok=True)
        output_file = trajectory_file.open("w", newline="")
        writer = csv.writer(output_file)
        writer.writerow(["step", "body_id", "x", "y", "vx", "vy"])

    start = time.perf_counter()
    simulate(bodies, n_steps, dt, writer)
    end = time.perf_counter()
    elapsed = end - start

    if output_file is not None:
        output_file.close()

    return elapsed


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Python N-body simulation and log benchmark.")
    parser.add_argument("--n", type=int, default=500, help="Number of bodies")
    parser.add_argument("--steps", type=int, default=100, help="Number of simulation steps")
    parser.add_argument("--dt", type=float, default=0.01, help="Time delta per step")
    parser.add_argument("--write_trajectory", action="store_true", help="Write trajectory CSV for visualization")
    args = parser.parse_args()

    elapsed = run_simulation(args.n, args.steps, args.dt, args.write_trajectory)

    print(f"[PYTHON] N={args.n}, steps={args.steps}, dt={args.dt}")
    print(f"Execution time: {elapsed:.6f} s")

    results_file = Path("experiments/results/python_benchmarks.csv")
    results_file.parent.mkdir(parents=True, exist_ok=True)
    with results_file.open("a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["python", "sequential", args.n, args.steps, args.dt, 1, elapsed])


if __name__ == "__main__":
    main()