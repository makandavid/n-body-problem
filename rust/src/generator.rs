use rand::rngs::StdRng;
use rand::{Rng, SeedableRng};

use crate::body::Body;

pub const G: f64 = 1.0;

pub fn generate_bodies(n: usize, seed: u64) -> Vec<Body> {
    let mut rng = StdRng::seed_from_u64(seed);

    let mut bodies = Vec::with_capacity(n);

    let radius = 50.0;
    let center_mass = 1000.0;

    // Central massive body
    bodies.push(Body::new(center_mass, [0.0, 0.0], [0.0, 0.0]));

    for _ in 1..n {
        let angle = rng.gen::<f64>() * std::f64::consts::TAU;
        let r = (rng.gen::<f64>() * radius).max(1.0);

        let x = r * angle.cos();
        let y = r * angle.sin();

        // Circular orbit velocity
        let speed = (G * center_mass / r).sqrt();

        let vx = -speed * angle.sin();
        let vy = speed * angle.cos();

        // Small random perturbation
        let perturb = 0.05;
        let dvx = (rng.gen::<f64>() - 0.5) * perturb * speed;
        let dvy = (rng.gen::<f64>() - 0.5) * perturb * speed;

        // Vary body masses slightly so interactions are non-trivial
        let mass = 0.5 + rng.gen::<f64>() * 1.5; // 0.5 to 2.0

        bodies.push(Body::new(mass, [x, y], [vx + dvx, vy + dvy]));
    }

    bodies
}
