import time

from nbody.generator import generate_bodies
from nbody.simulation import simulate

def main():
    N = 500
    STEPS = 100
    DT = 0.01

    bodies = generate_bodies(N)

    start = time.perf_counter()
    simulate(bodies, STEPS, DT)
    end = time.perf_counter()

    print(f"N={N}, steps={STEPS}")
    print(f"Execution time: {end - start:.4f} s")


if __name__ == "__main__":
    main()