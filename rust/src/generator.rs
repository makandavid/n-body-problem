use rand::rngs::StdRng;
use rand::{Rng, SeedableRng};

use crate::body::Body;

pub fn generate_bodies(n: usize, seed: u64) -> Vec<Body> {
    let mut rng = StdRng::seed_from_u64(seed);

    let mut bodies = Vec::with_capacity(n);

    let radius = 50.0;
    let center_mass = 1000.0;

    // Central massive body
    bodies.push(Body::new(center_mass, [0.0, 0.0], [0.0, 0.0]));

    for _ in 1..n {
        let angle = rng.gen::<f64>() * std::f64::consts::TAU;
        let r = rng.gen::<f64>() * radius;

        let x = r * angle.cos();
        let y = r * angle.sin();

        // Circular orbit velocity
        let speed = (1.0 * center_mass / r.max(1.0)).sqrt();

        let vx = -speed * angle.sin();
        let vy = speed * angle.cos();

        bodies.push(Body::new(1.0, [x, y], [vx, vy]));
    }

    bodies
}
