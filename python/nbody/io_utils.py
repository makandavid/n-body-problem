import csv
from typing import List
from .body import Body

def write_state(writer: csv.writer, step: int, bodies: List[Body]) -> None:
    for i, b in enumerate(bodies):
        writer.writerow([
            step,
            i,
            b.position[0],
            b.position[1],
            b.velocity[0],
            b.velocity[1]
        ])