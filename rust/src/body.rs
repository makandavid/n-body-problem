#[derive(Clone, Debug)]
pub struct Body {
    pub mass: f64,
    pub position: [f64; 2],
    pub velocity: [f64; 2],
    pub force: [f64; 2]
}

impl Body {
    pub fn new(mass: f64, position: [f64; 2], velocity: [f64; 2]) -> Self {
        Self {
            mass,
            position,
            velocity,
            force: [0.0; 2]
        }
    }

    pub fn reset_force(&mut self) {
        self.force = [0.0; 2];
    }
}