use rand::{Rng, SeedableRng};
use rand::rngs::StdRng;

use crate::body::Body;

pub fn generate_bodies(n: usize, seed: u64) -> Vec<Body> {
    let mut rng = StdRng::seed_from_u64(seed);

    let mut bodies = Vec::with_capacity(n);

    for _ in 0..n {
        let position = [rng.gen::<f64>(), rng.gen::<f64>()];
        let velocity = [rng.gen::<f64>() * 0.1, rng.gen::<f64>() * 0.1];

        bodies.push(Body::new(1.0, position, velocity));
    }

    bodies
}