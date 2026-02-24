use std::fs::File;
use std::io::{BufWriter, Write};

use crate::body::Body;

pub fn write_state(
    writer: &mut BufWriter<File>,
    step: usize,
    bodies: &[Body],
) -> std::io::Result<()> {
    for (i, b) in bodies.iter().enumerate() {
        writeln!(
            writer,
            "{},{},{},{},{},{}",
            step,
            i,
            b.position[0],
            b.position[1],
            b.velocity[0],
            b.velocity[1]
        )?;
    }
    Ok(())
}