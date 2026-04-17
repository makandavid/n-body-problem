use std::fs::File;
use std::io::BufWriter;

use crate::body::Body;
use crate::generator::G;

pub const EPSILON: f64 = 0.5;

pub fn compute_forces(bodies: &mut [Body]) {
    let n = bodies.len();

    for b in bodies.iter_mut() {
        b.reset_force();
    }

    for i in 0..n {
        for j in (i + 1)..n {
            let dx = bodies[j].position[0] - bodies[i].position[0];
            let dy = bodies[j].position[1] - bodies[i].position[1];

            let dist_sq = dx * dx + dy * dy + EPSILON * EPSILON;
            let dist = dist_sq.sqrt();

            let force_mag = G * bodies[i].mass * bodies[j].mass / dist_sq;

            let fx = force_mag * dx / dist;
            let fy = force_mag * dy / dist;

            bodies[i].force[0] += fx;
            bodies[i].force[1] += fy;

            bodies[j].force[0] -= fx;
            bodies[j].force[1] -= fy;
        }
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

pub fn simulate(
    bodies: &mut [Body],
    steps: usize,
    dt: f64,
    mut writer: Option<&mut BufWriter<File>>,
) -> std::io::Result<()> {
    for step in 0..steps {
        compute_forces(bodies);
        update_bodies(bodies, dt);

        if let Some(w) = writer.as_deref_mut() {
            crate::io_utils::write_state(w, step, bodies)?;
        }
    }
    Ok(())
}
