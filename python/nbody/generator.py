import numpy as np
from typing import List
from .body import Body

def generate_bodies(n: int, seed: int = 42) -> List[Body]:
    rng = np.random.default_rng(seed)

    bodies = []

    radius = 50.0
    center_mass = 1000.0
    G = 1.0

    # Central massive body
    bodies.append(Body(
        mass=center_mass,
        position=np.array([0.0, 0.0]),
        velocity=np.array([0.0, 0.0])
    ))

    for _ in range(1, n):
        angle = rng.random() * 2 * np.pi
        r = (rng.random() ** 0.5) * radius
        r = max(r, 1.0)

        x = r * np.cos(angle)
        y = r * np.sin(angle)

        speed = np.sqrt(G * center_mass / r)

        vx = -speed * np.sin(angle)
        vy =  speed * np.cos(angle)

        bodies.append(Body(
            mass=1.0,
            position=np.array([x, y]),
            velocity=np.array([vx, vy])
        ))

    return bodies