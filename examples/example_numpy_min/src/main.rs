#[doc = "// NOTE: Map Python module 'numpy'(tracked in DEPYLER-0424)"]
use clap::Parser;
#[derive(clap::Subcommand)]
enum Commands {
    Min5 {
        a: f64,
        b: f64,
        c: f64,
        d: f64,
        e: f64,
    },
    Min3 {
        a: f64,
        b: f64,
        c: f64,
    },
    Min4 {
        a: f64,
        b: f64,
        c: f64,
        d: f64,
    },
}
#[derive(clap::Parser)]
#[command(about = "Min reduction tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: verified panic-free"]
#[doc = " Depyler: proven to terminate"]
pub fn main() {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Min3 { .. });
    match &args.command {
        Commands::Min3 {
            ref a,
            ref b,
            ref c,
        } => {
            let a = *a;
            let b = *b;
            let c = *c;
            let mut arr = np.array(vec![a, b, c]);
            println!("{}", np.min(arr));
        }
        Commands::Min4 {
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
            println!("{}", np.min(arr));
        }
        Commands::Min5 {
            ref a,
            ref b,
            ref c,
            ref d,
            ref e,
        } => {
            let a = *a;
            let b = *b;
            let c = *c;
            let d = *d;
            let e = *e;
            let mut arr = np.array(vec![a, b, c, d, e]);
            println!("{}", np.min(arr));
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
}
