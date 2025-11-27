use clap::Parser;
#[derive(clap::Subcommand)]
enum Commands {
    Left { text: String },
    Right { text: String },
    Both { text: String },
}
#[derive(clap::Parser)]
#[command(about = "String strip tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: verified panic-free"]
#[doc = " Depyler: proven to terminate"]
pub fn main() {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Both { .. });
    match &args.command {
        Commands::Both { ref text } => {}
        Commands::Left { ref text } => {}
        Commands::Right { ref text } => {}
        _ => unreachable!("Other command variants handled elsewhere"),
    }
}
