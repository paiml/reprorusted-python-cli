use clap::Parser;
#[derive(clap::Subcommand)]
enum Commands {
    Float { x: f64 },
    Int { x: i32 },
}
#[derive(clap::Parser)]
#[command(about = "Absolute value tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: verified panic-free"]
#[doc = " Depyler: proven to terminate"]
pub fn main() {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Int { .. });
    match &args.command {
        Commands::Int { ref x } => {
            let x = *x;
            let _cse_temp_1 = x < 0;
            if _cse_temp_1 {
                println!("{}", -x);
            } else {
                println!("{}", x);
            }
        }
        Commands::Float { ref x } => {
            let x = *x;
            let _cse_temp_3 = x < 0;
            if _cse_temp_3 {
                println!("{}", -x);
            } else {
                println!("{}", x);
            }
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
}
