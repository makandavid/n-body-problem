import numpy as np
from typing import List
from .body import Body

def generate_bodies(n: int, seed: int = 42) -> List[Body]:
    rng = np.random.default_rng(seed)

    bodies = []
    for _ in range(n):
        body = Body(
            mass=1.0,
            position=rng.random(2),
            velocity=rng.random(2) * 0.1
        )
        bodies.append(body)

    return bodies