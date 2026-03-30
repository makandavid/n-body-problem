import csv
import numpy as np
from typing import List, Optional
from multiprocessing import Pool, cpu_count
from .body import Body
from .simulation import update_bodies
from .io_utils import write_state

G = 1.0
EPSILON = 1e-5

def compute_forces_chunk(args):
    bodies, start, end = args

    local_forces = np.zeros((end - start, 2))

    for local_i, i in enumerate(range(start, end)):
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

        local_forces[local_i] = force

    return start, local_forces

def compute_forces_parallel(bodies: List[Body], pool, num_workers: int) -> None:
    n = len(bodies)
    num_proc = num_workers

    chunk_size = (n + num_proc - 1) // num_proc

    tasks = []
    for p in range(num_proc):
        start = p * chunk_size
        end = min((p + 1) * chunk_size, n)

        if start < end:
            tasks.append((bodies, start, end))

    results = pool.map(compute_forces_chunk, tasks)

    for start, local_forces in results:
        for offset, f in enumerate(local_forces):
            bodies[start + offset].force = f

# def compute_forces_on_body(args: tuple[int, List[Body]]) -> np.ndarray:
#     i, bodies = args
#     bi = bodies[i]

#     force = np.zeros(2)

#     for j, bj in enumerate(bodies):
#         if i == j:
#             continue
        
#         diff = bj.position - bi.position
#         dist_sq = np.dot(diff, diff) + EPSILON
#         dist = np.sqrt(dist_sq)

#         force_mag = G * bi.mass * bj.mass / dist_sq
#         force_vec = force_mag * diff / dist

#         force += force_vec

#     return force

# def compute_forces_parallel(bodies: List[Body]) -> None:
#     n = len(bodies)

#     with Pool(cpu_count()) as pool:
#         forces = pool.map(compute_forces_on_body, [(i, bodies) for i in range(n)])
    
#     for i, f in enumerate(forces):
#         bodies[i].force = f

def simulate_parallel(bodies: List[Body], steps: int, dt: float, num_workers: int, writer: Optional[csv.writer] = None) -> None:
    with Pool(cpu_count()) as pool:
        for step in range(steps):
            for b in bodies:
                b.reset_force()

            compute_forces_parallel(bodies, pool, num_workers)

            update_bodies(bodies, dt)

            if writer is not None:
                write_state(writer, step, bodies)