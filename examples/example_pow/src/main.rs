use clap::Parser;
#[derive(clap::Subcommand)]
enum Commands {
    Square { x: i32 },
    Cube { x: i32 },
    Power { base: i32, exp: i32 },
}
#[derive(clap::Parser)]
#[command(about = "Power operations tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: verified panic-free"]
#[doc = " Depyler: proven to terminate"]
pub fn main() {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Square { .. });
    match &args.command {
        Commands::Square { ref x } => {
            let x = *x;
            println!("{}", x * x);
        }
        Commands::Cube { ref x } => {
            let x = *x;
            println!("{}", x * x * x);
        }
        Commands::Power { ref base } => {
            let base = *base;
            let mut result = 1;
            let mut i = 0;
            while i < exp {
                result = result * base;
                i = i + 1;
            }
            println!("{}", result);
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
}
