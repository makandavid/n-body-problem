use crate::visualization::snapshot::plot_snapshot;
use std::collections::HashMap;

pub fn generate_frames(
    snapshots: &HashMap<usize, Vec<(f64, f64)>>
) {
    let mut steps: Vec<_> = snapshots.keys().cloned().collect();
    steps.sort();

    for step in steps {
        let positions = &snapshots[&step];
        let filename = format!("../frames/frame_{:04}.png", step);
        plot_snapshot(positions, &filename).unwrap();
    }
}