use std::fs::File;
use std::io::BufWriter;
use std::sync::Arc;
use std::thread;

use crate::body::Body;

pub const G: f64 = 1.0;
pub const EPSILON: f64 = 1e-5;

pub fn compute_forces_parallel(bodies: &mut [Body], num_threads: usize) {
    let n = bodies.len();

    // Reset forces
    for b in bodies.iter_mut() {
        b.reset_force();
    }

    // Shared read-only snapshot
    let bodies_arc = Arc::new(bodies.to_vec());

    let chunk_size = (n + num_threads - 1) / num_threads;

    let mut handles = vec![];

    for t in 0..num_threads {
        let bodies_clone = Arc::clone(&bodies_arc);

        let start = t * chunk_size;
        let end = ((t + 1) * chunk_size).min(n);

        let handle = thread::spawn(move || {
            // Each thread keeps FULL force array (important!)
            let mut local_forces = vec![[0.0; 2]; bodies_clone.len()];

            for i in start..end {
                for j in (i + 1)..bodies_clone.len() {
                    let dx = bodies_clone[j].position[0] - bodies_clone[i].position[0];
                    let dy = bodies_clone[j].position[1] - bodies_clone[i].position[1];

                    let dist_sq = dx * dx + dy * dy + EPSILON;
                    let dist = dist_sq.sqrt();

                    let force_mag =
                        G * bodies_clone[i].mass * bodies_clone[j].mass / dist_sq;

                    let fx = force_mag * dx / dist;
                    let fy = force_mag * dy / dist;

                    // Apply to both i and j (symmetry)
                    local_forces[i][0] += fx;
                    local_forces[i][1] += fy;

                    local_forces[j][0] -= fx;
                    local_forces[j][1] -= fy;
                }
            }

            local_forces
        });

        handles.push(handle);
    }

    // Merge all thread results
    let mut total_forces = vec![[0.0; 2]; n];

    for handle in handles {
        let local = handle.join().unwrap();

        for i in 0..n {
            total_forces[i][0] += local[i][0];
            total_forces[i][1] += local[i][1];
        }
    }

    // Write back to bodies
    for i in 0..n {
        bodies[i].force = total_forces[i];
    }
}

pub fn update_bodies(bodies: &mut [Body], dt: f64) {
    for b in bodies.iter_mut() {
        let ax = b.force[0] / b.mass;
        let ay = b.force[1] / b.mass;

        b.velocity[0] += ax * dt;
        b.velocity[1] += ay * dt;

        b.position[0] += b.velocity[0] * dt;
        b.position[1] += b.velocity[1] * dt;
    }
}

pub fn simulate_parallel(
    bodies: &mut [Body],
    steps: usize,
    dt: f64,
    num_threads: usize,
    mut writer: Option<&mut BufWriter<File>>,
) -> std::io::Result<()> {
    for step in 0..steps {
        compute_forces_parallel(bodies, num_threads);
        update_bodies(bodies, dt);

        if let Some(w) = writer.as_deref_mut() {
            crate::io_utils::write_state(w, step, bodies)?;
        }
    }
    Ok(())
}