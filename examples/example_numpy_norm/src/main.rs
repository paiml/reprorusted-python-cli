#[doc = "// NOTE: Map Python module 'numpy'(tracked in DEPYLER-0424)"]
use clap::Parser;
#[derive(clap::Subcommand)]
enum Commands {
    Linf { a: f64, b: f64, c: f64 },
    L1 { a: f64, b: f64, c: f64 },
    L2 { a: f64, b: f64 },
}
#[derive(clap::Parser)]
#[command(about = "Vector norm tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: verified panic-free"]
#[doc = " Depyler: proven to terminate"]
pub fn main() {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::L2 { .. });
    match &args.command {
        Commands::L2 { ref a, ref b } => {
            let a = *a;
            let b = *b;
            let mut arr = np.array(vec![a, b]);
            println!("{}", np.linalg.norm(arr));
        }
        Commands::L1 {
            ref a,
            ref b,
            ref c,
        } => {
            let a = *a;
            let b = *b;
            let c = *c;
            let mut arr = np.array(vec![a, b, c]);
            println!("{}", np.linalg.norm(arr));
        }
        Commands::Linf {
            ref a,
            ref b,
            ref c,
        } => {
            let a = *a;
            let b = *b;
            let c = *c;
            let mut arr = np.array(vec![a, b, c]);
            println!("{}", np.linalg.norm(arr));
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
}
