#[doc = "// NOTE: Map Python module 'numpy'(tracked in DEPYLER-0424)"]
use clap::Parser;
#[derive(clap::Subcommand)]
enum Commands {
    Scale2 {
        a: f64,
        b: f64,
        scalar: f64,
    },
    Scale3 {
        a: f64,
        b: f64,
        c: f64,
        scalar: f64,
    },
    Scale4 {
        a: f64,
        b: f64,
        c: f64,
        d: f64,
        scalar: f64,
    },
}
#[derive(clap::Parser)]
#[command(about = "Scalar multiplication tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: verified panic-free"]
#[doc = " Depyler: proven to terminate"]
pub fn main() {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Scale3 { .. });
    match &args.command {
        Commands::Scale3 {
            ref a,
            ref b,
            ref c,
            ref scalar,
        } => {
            let a = *a;
            let b = *b;
            let c = *c;
            let scalar = *scalar;
            let mut arr = np.array(vec![a, b, c]);
            let _cse_temp_1 = arr * scalar;
            let mut result = _cse_temp_1.clone();
            println!(
                "{}",
                result.iter().copied().map(|x| x.to_string()).join(" ")
            );
        }
        Commands::Scale4 {
            ref a,
            ref b,
            ref c,
            ref d,
            ref scalar,
        } => {
            let a = *a;
            let b = *b;
            let c = *c;
            let d = *d;
            let scalar = *scalar;
            let mut arr = np.array(vec![a, b, c, d]);
            let _cse_temp_3 = arr * scalar;
            let mut result = _cse_temp_3.clone();
            println!(
                "{}",
                result.iter().copied().map(|x| x.to_string()).join(" ")
            );
        }
        Commands::Scale2 {
            ref a,
            ref b,
            ref scalar,
        } => {
            let a = *a;
            let b = *b;
            let scalar = *scalar;
            let mut arr = np.array(vec![a, b]);
            let _cse_temp_5 = arr * scalar;
            let mut result = _cse_temp_5.clone();
            println!(
                "{}",
                result.iter().copied().map(|x| x.to_string()).join(" ")
            );
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
}
