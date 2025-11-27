use clap::Parser;
#[derive(clap::Subcommand)]
enum Commands {
    Parse { text: String },
    Toint { x: f64 },
    Tofloat { x: i32 },
}
#[derive(clap::Parser)]
#[command(about = "Type conversion tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: verified panic-free"]
#[doc = " Depyler: proven to terminate"]
pub fn main() {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Toint { .. });
    match &args.command {
        Commands::Toint { ref x } => {
            let x = *x;
            println!("{}", (x) as i32);
        }
        Commands::Tofloat { ref x } => {
            let x = *x;
            println!("{}", (x) as f64);
        }
        Commands::Parse { ref text } => {
            println!("{}", (text) as i32);
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
}
