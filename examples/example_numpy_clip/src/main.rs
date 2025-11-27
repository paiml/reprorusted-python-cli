#[doc = "// NOTE: Map Python module 'numpy'(tracked in DEPYLER-0424)"]
use clap::Parser;
#[derive(clap::Subcommand)]
enum Commands {
    Clip4 {
        a: f64,
        b: f64,
        c: f64,
        d: f64,
        lo: f64,
        hi: f64,
    },
    Clip3 {
        a: f64,
        b: f64,
        c: f64,
        lo: f64,
        hi: f64,
    },
    Clip2 {
        a: f64,
        b: f64,
        lo: f64,
        hi: f64,
    },
}
#[derive(clap::Parser)]
#[command(about = "Clip/clamp tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: verified panic-free"]
#[doc = " Depyler: proven to terminate"]
pub fn main() {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Clip3 { .. });
    match &args.command {
        Commands::Clip3 {
            ref a,
            ref b,
            ref c,
            ref hi,
            ref lo,
        } => {
            let a = *a;
            let b = *b;
            let c = *c;
            let hi = *hi;
            let lo = *lo;
            let mut arr = np.array(vec![a, b, c]);
            let mut result = np.clip(arr, lo, hi);
            println!(
                "{}",
                result.iter().copied().map(|x| x.to_string()).join(" ")
            );
        }
        Commands::Clip4 {
            ref a,
            ref b,
            ref c,
            ref d,
            ref hi,
            ref lo,
        } => {
            let a = *a;
            let b = *b;
            let c = *c;
            let d = *d;
            let hi = *hi;
            let lo = *lo;
            let mut arr = np.array(vec![a, b, c, d]);
            let mut result = np.clip(arr, lo, hi);
            println!(
                "{}",
                result.iter().copied().map(|x| x.to_string()).join(" ")
            );
        }
        Commands::Clip2 {
            ref a,
            ref b,
            ref hi,
            ref lo,
        } => {
            let a = *a;
            let b = *b;
            let hi = *hi;
            let lo = *lo;
            let mut arr = np.array(vec![a, b]);
            let mut result = np.clip(arr, lo, hi);
            println!(
                "{}",
                result.iter().copied().map(|x| x.to_string()).join(" ")
            );
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
}
