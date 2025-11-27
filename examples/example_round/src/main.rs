use clap::Parser;
use std::f64 as math;
#[derive(clap::Subcommand)]
enum Commands {
    Floor { x: f64 },
    Ceil { x: f64 },
    Nearest { x: f64 },
}
#[derive(clap::Parser)]
#[command(about = "Rounding tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: verified panic-free"]
#[doc = " Depyler: proven to terminate"]
pub fn main() {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Nearest { .. });
    match &args.command {
        Commands::Nearest { ref x } => {
            let x = *x;
            println!("{}", x.round() as i32);
        }
        Commands::Floor { ref x } => {
            let x = *x;
            println!("{}", (x as f64).floor() as i32);
        }
        Commands::Ceil { ref x } => {
            let x = *x;
            println!("{}", (x as f64).ceil() as i32);
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
}
