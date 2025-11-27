use clap::Parser;
#[derive(clap::Subcommand)]
enum Commands {
    Sum {
        a1: i32,
        a2: i32,
        a3: i32,
        b1: i32,
        b2: i32,
        b3: i32,
    },
    Pair {
        a1: String,
        a2: String,
        a3: String,
        b1: String,
        b2: String,
        b3: String,
    },
    Diff {
        a1: i32,
        a2: i32,
        a3: i32,
        b1: i32,
        b2: i32,
        b3: i32,
    },
}
#[derive(clap::Parser)]
#[command(about = "Zip operations tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: verified panic-free"]
#[doc = " Depyler: proven to terminate"]
pub fn main() {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Pair { .. });
    match &args.command {
        Commands::Pair { .. } => {
            println!("{}", format!("{}:{} {}:{} {}:{}", a1, b1, a2, b2, a3, b3));
        }
        Commands::Sum { ref a1, ref b1 } => {
            let a1 = *a1;
            let b1 = *b1;
            let _cse_temp_2 = a1 + b1;
            let mut r1 = _cse_temp_2.clone();
            let mut r2 = _cse_temp_2.clone();
            let mut r3 = _cse_temp_2.clone();
            println!("{}", format!("{:?} {:?} {:?}", r1, r2, r3));
        }
        Commands::Diff { ref a1, ref b1 } => {
            let a1 = *a1;
            let b1 = *b1;
            let _cse_temp_4 = a1 - b1;
            let mut r1 = _cse_temp_4.clone();
            let mut r2 = _cse_temp_4.clone();
            let mut r3 = _cse_temp_4.clone();
            println!("{}", format!("{:?} {:?} {:?}", r1, r2, r3));
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
}
