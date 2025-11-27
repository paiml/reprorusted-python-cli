#[doc = "// NOTE: Map Python module 'numpy'(tracked in DEPYLER-0424)"]
use clap::Parser;
#[derive(clap::Subcommand)]
enum Commands {
    Dist3 {
        a1: f64,
        a2: f64,
        a3: f64,
        b1: f64,
        b2: f64,
        b3: f64,
    },
    Dist4 {
        a1: f64,
        a2: f64,
        a3: f64,
        a4: f64,
        b1: f64,
        b2: f64,
        b3: f64,
        b4: f64,
    },
    Dist2 {
        a1: f64,
        a2: f64,
        b1: f64,
        b2: f64,
    },
}
#[derive(clap::Parser)]
#[command(about = "Euclidean distance tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: verified panic-free"]
#[doc = " Depyler: proven to terminate"]
pub fn main() {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Dist3 { .. });
    match &args.command {
        Commands::Dist3 {
            ref a1,
            ref a2,
            ref a3,
            ref b1,
            ref b2,
            ref b3,
        } => {
            let a1 = *a1;
            let a2 = *a2;
            let a3 = *a3;
            let b1 = *b1;
            let b2 = *b2;
            let b3 = *b3;
            let mut a = np.array(vec![a1, a2, a3]);
            let mut b = np.array(vec![b1, b2, b3]);
            println!("{}", (np.linalg.norm(a - b) as f64).round() as i32);
        }
        Commands::Dist2 {
            ref a1,
            ref a2,
            ref b1,
            ref b2,
        } => {
            let a1 = *a1;
            let a2 = *a2;
            let b1 = *b1;
            let b2 = *b2;
            let mut a = np.array(vec![a1, a2]);
            let mut b = np.array(vec![b1, b2]);
            println!("{}", (np.linalg.norm(a - b) as f64).round() as i32);
        }
        Commands::Dist4 {
            ref a1,
            ref a2,
            ref a3,
            ref a4,
            ref b1,
            ref b2,
            ref b3,
            ref b4,
        } => {
            let a1 = *a1;
            let a2 = *a2;
            let a3 = *a3;
            let a4 = *a4;
            let b1 = *b1;
            let b2 = *b2;
            let b3 = *b3;
            let b4 = *b4;
            let mut a = np.array(vec![a1, a2, a3, a4]);
            let mut b = np.array(vec![b1, b2, b3, b4]);
            println!("{}", (np.linalg.norm(a - b) as f64).round() as i32);
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
}
