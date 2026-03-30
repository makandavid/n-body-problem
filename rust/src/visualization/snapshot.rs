use plotters::prelude::*;

pub fn plot_snapshot(
    positions: &Vec<(f64, f64)>,
    filename: &str,
) -> Result<(), Box<dyn std::error::Error>> {

    let root = BitMapBackend::new(filename, (800, 800))
        .into_drawing_area();
    root.fill(&WHITE)?;

    let mut chart = ChartBuilder::on(&root)
        .build_cartesian_2d(-100.0..100.0, -100.0..100.0)?;

    chart.configure_mesh().draw()?;

    chart.draw_series(
        positions.iter().map(|(x, y)| {
            Circle::new((*x, *y), 3, RED.filled())
        })
    )?;

    Ok(())
}