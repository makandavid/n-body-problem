mod body;
mod generator;
mod simulation;
mod io_utils;

use std::fs::File;
use std::io::{BufWriter, Write};
use std::time::Instant;

fn main() -> std::io::Result<()> {
    let n = 500;
    let steps = 100;
    let dt = 0.01;

    let mut bodies = generator::generate_bodies(n, 42);

    let file = File::create("../data/rust_sequential.csv")?;
    let mut writer = BufWriter::new(file);

    writeln!(writer, "step,body_id,x,y,vx,vy")?;

    let start = Instant::now();
    simulation::simulate(&mut bodies, steps, dt, Some(&mut writer))?;
    let duration = start.elapsed();

    println!("N={}, steps={}", n, steps);
    println!("Execution time: {:.4?}", duration);

    Ok(())
}