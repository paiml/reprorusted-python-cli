#[doc = "// NOTE: Map Python module 'numpy'(tracked in DEPYLER-0424)"]
use clap::Parser;
#[derive(clap::Subcommand)]
enum Commands {
    Sqrt3 { a: f64, b: f64, c: f64 },
    Sqrt4 { a: f64, b: f64, c: f64, d: f64 },
    Sqrt2 { a: f64, b: f64 },
}
#[derive(clap::Parser)]
#[command(about = "Element-wise sqrt tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: verified panic-free"]
#[doc = " Depyler: proven to terminate"]
pub fn main() {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Sqrt3 { .. });
    match &args.command {
        Commands::Sqrt3 {
            ref a,
            ref b,
            ref c,
        } => {
            let a = *a;
            let b = *b;
            let c = *c;
            let mut arr = np.array(vec![a, b, c]);
            let mut result = np.sqrt(arr);
            println!(
                "{}",
                result.iter().copied().map(|x| x.to_string()).join(" ")
            );
        }
        Commands::Sqrt4 {
            ref a,
            ref b,
            ref c,
            ref d,
        } => {
            let a = *a;
            let b = *b;
            let c = *c;
            let d = *d;
            let mut arr = np.array(vec![a, b, c, d]);
            let mut result = np.sqrt(arr);
            println!(
                "{}",
                result.iter().copied().map(|x| x.to_string()).join(" ")
            );
        }
        Commands::Sqrt2 { ref a, ref b } => {
            let a = *a;
            let b = *b;
            let mut arr = np.array(vec![a, b]);
            let mut result = np.sqrt(arr);
            println!(
                "{}",
                result.iter().copied().map(|x| x.to_string()).join(" ")
            );
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
}
