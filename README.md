# N-Body-Problem - Advanced Programming Techniques Project

## Project Overview
This project focuses on the implementation, parallelization, and performance analysis of the N-body problem, a classical computational problem in physics and numerical simulation. The N-body problem models the motion of N interacting bodies under pairwise forces, most commonly gravitational interaction.
Due to its quadratic computational complexity O(N^2) per iteration, the N-body problem is well suited for studying parallel programming techniques, scalability, and performance limits.
The project includes:
- sequential and parallel implementations in Python and Rust,
- strong and weak scaling experiments,
- theoretical analysis using Amdahl’s and Gustafson’s laws,
- visualization of simulation results.

## Problem Description
Each body in the system is defined by its:
- mass,
- position (2D or 3D),
- velocity.

The solution simulates the system iteratively over a fixed number of time steps. In each iteration, the following steps are performed:
1. Compute pairwise forces between bodies
2. Accumulate net force per body
3. Update velocities based on acceleration
4. Update positions based on velocity
5. Store the system state for later analysis and visualization

Because force computation dominates runtime and is independent per body, it represents the main parallelizable part of the algorithm.

## Implementation Plan
### Python Implementation (25 points)
#### Sequential Version
- Bodies are stored in simple data structures (lists or arrays).
- Nested loops are used to compute all pairwise interactions.
- After each iteration, position and velocities are written to an output file.
- Execution time is measured for performance comparison.

#### Parallel Version
- Implemented using the ```multiprocessing``` library.
- Bodies are divided among processes.
- Each process computes force contributions for its assigned subset.
- Partial results are combined to update the global system state.
- Output format matches the sequential version.

### Rust Implementation (26 points)
#### Sequential Version
- Bodies are stored in vectors for cache-friendly access.
- Emphasis on explicit memory management and minimal overhead.
- System state is saved after each iteration in CSV format.

#### Parallel Version
- Implemented using native Rust threads.
- Work is distributed by splitting the set of bodies across threads.
- Shared data structures are protected using ```Arc``` and synchronization primitives when required.
- The implementation avoids unnecessary locking by minimizing shared mutable state.

## Scaling Experiments (9 + 10 points)
### Strong Scaling (Amdahl's Law)
- Fixed number of bodies and iterations
- Increasing number of CPU cores
- Measurement of execution time and speedup
- Comparison with theoretical speedup limits

### Weak Scaling (Gustafson's Law)
- Number of bodies increases proportionally with the number of cores
- Work per core remains approximately constant
- Evaluation of scalability as the problem size grows

## Visualization (10 points)
Visualization is implemented in Rust, based on the previously generated output files.
Planned visualizations include:
- 2D plots of body trajectories,
- Snapshots of body positions per iteration,
- Optimal animation of system evolution.

The ```plotters``` library is used for rendering graphs and spatial distributions.

## Architecture
The project architecture is guided by the following principles:
- Modularity – clear separation between simulation, parallelism, and visualization
- Comparability – identical logic across languages and execution modes
- Reproducibility – deterministic outputs with controlled randomness
- Minimal coupling – visualization and analysis are decoupled from computation

## Technologies
#### Python
- ```multiprocessing```
- ```numpy```
#### Rust
- ```std::thread```
- ```Arc```, ```Mutex```
- ```plotters```

## Expected Outcomes
The project will demonstrate:
- Differences in performance between Python and Rust
- Benefits and limits of parallelization for O(N²) problems
- Empirical validation of Amdahl’s and Gustafson’s laws
- Clear visualization of complex dynamical systems
___

David Makan, SV33/2022
