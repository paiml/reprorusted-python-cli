use clap::Parser;
#[derive(clap::Subcommand)]
enum Commands {
    And { x: i32, y: i32 },
    Or { x: i32, y: i32 },
    Not { x: i32 },
}
#[derive(clap::Parser)]
#[command(about = "Boolean operations tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: verified panic-free"]
#[doc = " Depyler: proven to terminate"]
pub fn main() {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::And { .. });
    match &args.command {
        Commands::And { ref x } => {
            let x = *x;
            let _cse_temp_1 = x != 0;
            let _cse_temp_2 = (_cse_temp_1) && (_cse_temp_1);
            if _cse_temp_2 {
                println!("{}", "true");
            } else {
                println!("{}", "false");
            }
        }
        Commands::Or { ref x } => {
            let x = *x;
            let _cse_temp_4 = x != 0;
            let _cse_temp_5 = (_cse_temp_4) || (_cse_temp_4);
            if _cse_temp_5 {
                println!("{}", "true");
            } else {
                println!("{}", "false");
            }
        }
        Commands::Not { ref x } => {
            let x = *x;
            let _cse_temp_7 = x == 0;
            if _cse_temp_7 {
                println!("{}", "true");
            } else {
                println!("{}", "false");
            }
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
}
