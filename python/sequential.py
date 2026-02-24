import time
import csv
from pathlib import Path
from nbody.generator import generate_bodies
from nbody.simulation import simulate

OUTPUT_PATH = Path("../data/python_sequential.csv")

def main():
    N = 500
    STEPS = 100
    DT = 0.01

    bodies = generate_bodies(N)

    start = time.perf_counter()

    with OUTPUT_PATH.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["step", "body_id", "x", "y", "vx", "vy"])

        simulate(bodies, STEPS, DT, writer)

    end = time.perf_counter()

    print(f"N={N}, steps={STEPS}")
    print(f"Execution time: {end - start:.4f} s")


if __name__ == "__main__":
    main()