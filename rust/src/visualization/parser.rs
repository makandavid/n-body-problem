use std::collections::HashMap;
use std::fs::File;
use std::io::{BufRead, BufReader};

pub type Trajectories = HashMap<usize, Vec<(f64, f64)>>;
pub type Snapshots = HashMap<usize, Vec<(f64, f64)>>;

pub fn parse_file(path: &str) -> (Trajectories, Snapshots) {
    let file = File::open(path).expect("Cannot open file");
    let reader = BufReader::new(file);

    let mut trajectories: Trajectories = HashMap::new();
    let mut snapshots: Snapshots = HashMap::new();

    for line in reader.lines() {
        let line = line.unwrap();

        // Adjust depending on your CSV format!
        let parts: Vec<&str> = line.split(',').collect();

        if parts[0].parse::<usize>().is_err() {
            continue;
        }

        let step: usize = parts[0].parse().unwrap();
        let body_id: usize = parts[1].parse().unwrap();
        let x: f64 = parts[2].parse().unwrap();
        let y: f64 = parts[3].parse().unwrap();

        trajectories.entry(body_id).or_default().push((x, y));
        snapshots.entry(step).or_default().push((x, y));
    }

    (trajectories, snapshots)
}
