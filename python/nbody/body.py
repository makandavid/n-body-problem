import numpy as np
from numpy.typing import NDArray

class Body:
    def __init__(self, mass: float, position: NDArray[np.float64], velocity: NDArray[np.float64]) -> None:
        self.mass = mass
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.force = np.zeros(2, dtype=float)

    def reset_force(self) -> None:
        self.force[:] = 0.0