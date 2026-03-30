use rust::visualization::parser::parse_file;
use rust::visualization::trajectory::plot_trajectories;
use rust::visualization::snapshot::plot_snapshot;
use rust::visualization::animation::generate_frames;

use std::env;

fn main() {
    let args: Vec<String> = env::args().collect();
    let path = args.get(1).map(|s| s.as_str()).unwrap_or("output.csv");

    let (trajectories, snapshots) = parse_file(path);

    plot_trajectories(&trajectories).unwrap();

    if let Some(last_step) = snapshots.keys().max() {
        plot_snapshot(&snapshots[last_step], "snapshot.png").unwrap();
    }

    generate_frames(&snapshots);
}