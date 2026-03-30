use plotters::prelude::*;
use std::collections::HashMap;

pub fn plot_trajectories(
    trajectories: &HashMap<usize, Vec<(f64, f64)>>
) -> Result<(), Box<dyn std::error::Error>> {

    let root = BitMapBackend::new("trajectories.png", (800, 800))
        .into_drawing_area();
    root.fill(&WHITE)?;

    let mut chart = ChartBuilder::on(&root)
        .margin(10)
        .caption("Trajectories", ("sans-serif", 20))
        .build_cartesian_2d(-100.0..100.0, -100.0..100.0)?;

    chart.configure_mesh().draw()?;

    for (_id, points) in trajectories {
        chart.draw_series(LineSeries::new(points.clone(), &BLUE))?;
    }

    Ok(())
}