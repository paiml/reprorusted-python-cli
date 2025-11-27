use clap::Parser;
#[derive(clap::Subcommand)]
enum Commands {
    Underscore { a: String, b: String, c: String },
    Dash { a: String, b: String, c: String },
    Dot { a: String, b: String, c: String },
}
#[derive(clap::Parser)]
#[command(about = "String join tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: verified panic-free"]
#[doc = " Depyler: proven to terminate"]
pub fn main() {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Underscore { .. });
    match &args.command {
        Commands::Underscore {
            ref a,
            ref b,
            ref c,
        } => {
            println!("{}", format!("{}{}", format!("{}{}", a, "_") + b, "_") + c);
        }
        Commands::Dash {
            ref a,
            ref b,
            ref c,
        } => {
            println!("{}", format!("{}{}", format!("{}{}", a, "-") + b, "-") + c);
        }
        Commands::Dot {
            ref a,
            ref b,
            ref c,
        } => {
            println!("{}", format!("{}{}", format!("{}{}", a, ".") + b, ".") + c);
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
}
