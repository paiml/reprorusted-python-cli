use clap::Parser;
#[derive(clap::Subcommand)]
enum Commands {
    Lower { code: i32 },
    Digit { n: i32 },
    Upper { code: i32 },
}
#[derive(clap::Parser)]
#[command(about = "ASCII operations tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: verified panic-free"]
#[doc = " Depyler: proven to terminate"]
pub fn main() {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Upper { .. });
    match &args.command {
        Commands::Upper { ref code } => {
            let code = *code;
            println!("{}", char::from_u32(code as u32).unwrap().to_string());
        }
        Commands::Lower { ref code } => {
            let code = *code;
            println!("{}", char::from_u32(code as u32).unwrap().to_string());
        }
        Commands::Digit { ref n } => {
            let n = *n;
            println!("{}", "0".chars().next().unwrap() as i32 + n);
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
}
