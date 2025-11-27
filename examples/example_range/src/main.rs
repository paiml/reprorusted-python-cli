use clap::Parser;
#[derive(clap::Subcommand)]
enum Commands {
    Between { start: i32, end: i32 },
    Upto { n: i32 },
    Step { start: i32, end: i32, step: i32 },
}
#[derive(clap::Parser)]
#[command(about = "Range tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: verified panic-free"]
#[doc = " Depyler: proven to terminate"]
pub fn main() {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Upto { .. });
    match &args.command {
        Commands::Upto { .. } => {
            let mut result = "";
            let mut i = 0;
            while i < n {
                if i > 0 {
                    result = format!("{}{}", result, " ");
                }
                result = result + i.to_string();
                i = i + 1;
            }
            println!("{}", result);
        }
        Commands::Between { ref start } => {
            let start = *start;
            let mut result = "";
            let mut i = start;
            while i < end {
                if i > start {
                    result = format!("{}{}", result, " ");
                }
                result = result + i.to_string();
                i = i + 1;
            }
            println!("{}", result);
        }
        Commands::Step {
            ref start,
            ref step,
        } => {
            let start = *start;
            let step = *step;
            let mut result = "";
            let mut i = start;
            let mut first = true;
            while i < end {
                if !first {
                    result = format!("{}{}", result, " ");
                }
                first = false;
                result = result + i.to_string();
                i = i + step;
            }
            println!("{}", result);
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
}
