use plotters::prelude::*;

pub fn plot_snapshot(
    positions: &Vec<(f64, f64)>,
    filename: &str,
) -> Result<(), Box<dyn std::error::Error>> {
    let root = BitMapBackend::new(filename, (800, 800)).into_drawing_area();
    root.fill(&WHITE)?;

    let min_x = positions
        .iter()
        .map(|(x, _)| *x)
        .fold(f64::INFINITY, f64::min);
    let max_x = positions
        .iter()
        .map(|(x, _)| *x)
        .fold(f64::NEG_INFINITY, f64::max);
    let min_y = positions
        .iter()
        .map(|(_, y)| *y)
        .fold(f64::INFINITY, f64::min);
    let max_y = positions
        .iter()
        .map(|(_, y)| *y)
        .fold(f64::NEG_INFINITY, f64::max);

    let padding = 10.0;

    let mut chart = ChartBuilder::on(&root).build_cartesian_2d(
        (min_x - padding)..(max_x + padding),
        (min_y - padding)..(max_y + padding),
    )?;

    chart.configure_mesh().draw()?;

    chart.draw_series(
        positions
            .iter()
            .map(|(x, y)| Circle::new((*x, *y), 3, RED.filled())),
    )?;

    Ok(())
}
