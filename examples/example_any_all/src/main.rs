use clap::Parser;
#[derive(clap::Subcommand)]
enum Commands {
    Any { a: i32, b: i32, c: i32, d: i32 },
    All { a: i32, b: i32, c: i32, d: i32 },
}
#[derive(clap::Parser)]
#[command(about = "Any/all operations tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: verified panic-free"]
#[doc = " Depyler: proven to terminate"]
pub fn main() {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Any { .. });
    match &args.command {
        Commands::Any { ref a } => {
            let a = *a;
            let _cse_temp_1 = a != 0;
            let _cse_temp_2 = (_cse_temp_1) || (_cse_temp_1);
            let _cse_temp_3 = (_cse_temp_2) || (_cse_temp_1);
            let _cse_temp_4 = (_cse_temp_3) || (_cse_temp_1);
            if _cse_temp_4 {
                println!("{}", "true");
            } else {
                println!("{}", "false");
            }
        }
        Commands::All { ref a } => {
            let a = *a;
            let _cse_temp_6 = a != 0;
            let _cse_temp_7 = (_cse_temp_6) && (_cse_temp_6);
            let _cse_temp_8 = (_cse_temp_7) && (_cse_temp_6);
            let _cse_temp_9 = (_cse_temp_8) && (_cse_temp_6);
            if _cse_temp_9 {
                println!("{}", "true");
            } else {
                println!("{}", "false");
            }
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
}
