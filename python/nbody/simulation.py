import numpy as np
from typing import List
from .body import Body

G = 1.0
EPSILON = 1e-5

def compute_forces(bodies: List[Body]) -> None:
    n = len(bodies)

    for b in bodies:
        b.reset_force()

    for i in range(n):
        for j in range(i + 1, n):
            diff = bodies[j].position - bodies[i].position
            dist_sq = np.dot(diff, diff) + EPSILON
            dist = np.sqrt(dist_sq)

            force_mag = G * bodies[i].mass * bodies[j].mass / dist_sq
            force_vec = force_mag * diff / dist

            bodies[i].force += force_vec
            bodies[j].force -= force_vec

def update_bodies(bodies: List[Body], dt: float) -> None:
    for b in bodies:
        acceleration = b.force / b.mass
        b.velocity += acceleration * dt
        b.position += b.velocity * dt

def simulate(bodies: List[Body], steps: int, dt: float) -> None:
    for _ in range(steps):
        compute_forces(bodies)
        update_bodies(bodies, dt)
        