from __future__ import annotations
import subprocess
import time
from pathlib import Path
import argparse

RESULTS_FILE = Path("experiments/results/rust_seq.csv")
RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Rust N-body sequential simulation and log benchmark.")
    parser.add_argument("--n", type=int, default=500, help="Number of bodies")
    parser.add_argument("--steps", type=int, default=100, help="Number of simulation steps")
    parser.add_argument("--dt", type=float, default=0.01, help="Time delta per step")
    parser.add_argument("--write_trajectory", action="store_true", help="Write trajectory CSV for visualization")
    args = parser.parse_args()

    cmd = [
        "cargo", "run", "--bin", "run_seq", "--quiet", "--",
        str(args.n), str(args.steps), str(args.dt)
    ]
    if args.write_trajectory:
        cmd.append("write_trajectory")

    start = time.perf_counter()

    subprocess.run(cmd, cwd="rust", check=True)

    end = time.perf_counter()
    elapsed = end - start
    print(f"[ORCH] Rust sequential run finished in {elapsed:.3f} s")

    with RESULTS_FILE.open("a", newline="") as f:
        f.write(f"rust,sequential,{args.n},{args.steps},{args.dt},1,{elapsed:.6f}\n")


if __name__ == "__main__":
    main()