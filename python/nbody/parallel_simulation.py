import csv
import numpy as np
from typing import List, Optional
from multiprocessing import Pool, cpu_count
from .body import Body
from .simulation import update_bodies
from .io_utils import write_state

G = 1.0
EPSILON = 1e-5

def compute_forces_on_body(args: tuple[int, List[Body]]) -> np.ndarray:
    i, bodies = args
    bi = bodies[i]

    force = np.zeros(2)

    for j, bj in enumerate(bodies):
        if i == j:
            continue
        
        diff = bj.position - bi.position
        dist_sq = np.dot(diff, diff) + EPSILON
        dist = np.sqrt(dist_sq)

        force_mag = G * bi.mass * bj.mass / dist_sq
        force_vec = force_mag * diff / dist

        force += force_vec

    return force

def compute_forces_parallel(bodies: List[Body]) -> None:
    n = len(bodies)

    with Pool(cpu_count()) as pool:
        forces = pool.map(compute_forces_on_body, [(i, bodies) for i in range(n)])
    
    for i, f in enumerate(forces):
        bodies[i].force = f

def simulate_parallel(bodies: List[Body], steps: int, dt: float, writer: Optional[csv.writer] = None) -> None:
    for step in range(steps):
        for b in bodies:
            b.reset_force()

        compute_forces_parallel(bodies)

        update_bodies(bodies, dt)

        if writer is not None:
            write_state(writer, step, bodies)