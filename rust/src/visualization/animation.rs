use crate::visualization::snapshot::plot_snapshot;
use std::collections::HashMap;

pub fn generate_frames(
    snapshots: &HashMap<usize, Vec<(f64, f64)>>
) {
    for (step, positions) in snapshots {
        let filename = format!("frames/frame_{:04}.png", step);
        plot_snapshot(positions, &filename).unwrap();
    }
}