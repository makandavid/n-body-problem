use rust::visualization::parser::parse_file;
use rust::visualization::trajectory::plot_trajectories;
use rust::visualization::snapshot::plot_snapshot;
use rust::visualization::animation::generate_frames;

use std::env;
use std::process::Command;

fn main() {
    let args: Vec<String> = env::args().collect();
    let path = args.get(1).map(|s| s.as_str()).unwrap_or("output.csv");

    let (trajectories, snapshots) = parse_file(path);

    plot_trajectories(&trajectories).unwrap();

    if let Some(last_step) = snapshots.keys().max() {
        plot_snapshot(&snapshots[last_step], "../visualizations/snapshot.png").unwrap();
    }

    generate_frames(&snapshots);

    let status = Command::new("ffmpeg")
        .args([
            "-y",
            "-framerate", "30",
            "-i", "../frames/frame_%04d.png",
            "-pix_fmt", "yuv420p",
            "../visualizations/animation.mp4",
        ])
        .status();

    match status {
        Ok(s) if s.success() => {
            println!("Animation created: animation.mp4");
        }
        Ok(_) => {
            eprintln!("FFmpeg failed to create animation");
        }
        Err(e) => {
            eprintln!("Failed to run FFmpeg: {}", e);
        }
    }
}