use rust::{generator, simulation};
use std::fs::File;
use std::io::{BufWriter, Write};
use std::env;
use std::path::Path;
use std::time::Instant;

fn main() -> std::io::Result<()> {
    let args: Vec<String> = env::args().collect();
    let n: usize = args.get(1).and_then(|s| s.parse().ok()).unwrap_or(500);
    let steps: usize = args.get(2).and_then(|s| s.parse().ok()).unwrap_or(100);
    let dt: f64 = args.get(3).and_then(|s| s.parse().ok()).unwrap_or(0.01);
    let write_trajectory = args.get(4).map(|s| s == "write_trajectory").unwrap_or(false);

    let trajectory_path = if write_trajectory {
        let path_string = format!("../data/rust_{}_{}.csv", n, steps);
        let path = Path::new(&path_string);
        std::fs::create_dir_all(path.parent().unwrap())?;
        Some(path.to_path_buf())
    } else {
        None
    };

    let mut bodies = generator::generate_bodies(n, 42);
    let mut writer: Option<BufWriter<File>> = None;

    if let Some(path) = trajectory_path {
        let file = File::create(path)?;
        let mut buf_writer = BufWriter::new(file);
        writeln!(buf_writer, "step,body_id,x,y,vx,vy")?;
        writer = Some(buf_writer);
    }

    let start = Instant::now();
    simulation::simulate(&mut bodies, steps, dt, writer.as_mut())?;
    let duration = start.elapsed();

    println!("[RUST SEQ] N={}, steps={}", n, steps);
    println!("Execution time: {:.6?}", duration);

    Ok(())
}