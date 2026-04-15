use plotters::prelude::*;
use std::collections::HashMap;

pub fn plot_trajectories(
    trajectories: &HashMap<usize, Vec<(usize, f64, f64)>>,
) -> Result<(), Box<dyn std::error::Error>> {
    let root = BitMapBackend::new("../visualizations/trajectories.png", (800, 800)).into_drawing_area();
    root.fill(&WHITE)?;

    let mut all_points = vec![];

    for (_, points) in trajectories {
        for (_, x, y) in points {
            all_points.push((*x, *y));
        }
    }

    let min_x = all_points
        .iter()
        .map(|(x, _)| *x)
        .fold(f64::INFINITY, f64::min);
    let max_x = all_points
        .iter()
        .map(|(x, _)| *x)
        .fold(f64::NEG_INFINITY, f64::max);
    let min_y = all_points
        .iter()
        .map(|(_, y)| *y)
        .fold(f64::INFINITY, f64::min);
    let max_y = all_points
        .iter()
        .map(|(_, y)| *y)
        .fold(f64::NEG_INFINITY, f64::max);

    let padding = 10.0;

    let mut chart = ChartBuilder::on(&root)
        .margin(10)
        .caption("Trajectories", ("sans-serif", 20))
        .build_cartesian_2d(
            (min_x - padding)..(max_x + padding),
            (min_y - padding)..(max_y + padding),
        )?;

    chart.configure_mesh().draw()?;

    let colors = [&RED, &BLUE, &GREEN, &CYAN, &MAGENTA];

    let max_radius = 200.0;

    for (i, (_id, points)) in trajectories.iter().take(50).enumerate() {
        let color = colors[i % colors.len()];

        let ordered: Vec<(f64, f64)> = points
            .iter()
            .filter(|(_, x, y)| {
                let r = (x * x + y * y).sqrt();
                r < max_radius // filter exploding bodies
            })
            .map(|(_, x, y)| (*x, *y))
            .collect();

        chart.draw_series(LineSeries::new(ordered, color.stroke_width(2)))?;
    }

    Ok(())
}
