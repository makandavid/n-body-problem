from __future__ import annotations
import subprocess
import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Visualization for N-body simulation.")
    parser.add_argument("--path", type=str, help="Path to data")
    args = parser.parse_args()

    cmd = [
        "cargo", "run", "--release", "--bin", "visualize", args.path
    ]

    subprocess.run(cmd, cwd="rust", check=True)


if __name__ == "__main__":
    main()