use crate::visualization::snapshot::plot_snapshot;
use std::{collections::HashMap, fs};

pub fn generate_frames(
    snapshots: &HashMap<usize, Vec<(f64, f64)>>
) {
    let frames_dir = "../frames";

    if fs::metadata(frames_dir).is_ok() {
        if let Err(e) = fs::remove_dir_all(frames_dir) {
            eprintln!("Could not delete frames folder: {}", e);
            eprintln!("Trying to continue...");
        }
    }

    fs::create_dir_all(frames_dir).unwrap();

    let mut steps: Vec<_> = snapshots.keys().cloned().collect();
    steps.sort();

    for step in steps {
        let positions = &snapshots[&step];
        let filename = format!("{}/frame_{:04}.png", frames_dir, step);
        plot_snapshot(positions, &filename).unwrap();
    }
}
