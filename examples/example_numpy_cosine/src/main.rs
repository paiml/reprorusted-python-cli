#[doc = "// NOTE: Map Python module 'numpy'(tracked in DEPYLER-0424)"]
use clap::Parser;
#[derive(clap::Subcommand)]
enum Commands {
    Cosine4 {
        a1: f64,
        a2: f64,
        a3: f64,
        a4: f64,
        b1: f64,
        b2: f64,
        b3: f64,
        b4: f64,
    },
    Cosine2 {
        a1: f64,
        a2: f64,
        b1: f64,
        b2: f64,
    },
    Cosine3 {
        a1: f64,
        a2: f64,
        a3: f64,
        b1: f64,
        b2: f64,
        b3: f64,
    },
}
#[derive(clap::Parser)]
#[command(about = "Cosine similarity tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: verified panic-free"]
#[doc = " Depyler: proven to terminate"]
pub fn main() {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Cosine3 { .. });
    match &args.command {
        Commands::Cosine3 {
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
            let mut dot = np.dot(a, b);
            let mut norm_a = np.linalg.norm(a);
            let mut norm_b = np.linalg.norm(b);
            let mut result = if (norm_a > 0) && (norm_b > 0) {
                dot / (norm_a * norm_b)
            } else {
                0
            };
            println!("{}", (result as f64).round() as i32);
        }
        Commands::Cosine2 {
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
            let mut dot = np.dot(a, b);
            let mut norm_a = np.linalg.norm(a);
            let mut norm_b = np.linalg.norm(b);
            let mut result = if (norm_a > 0) && (norm_b > 0) {
                dot / (norm_a * norm_b)
            } else {
                0
            };
            println!("{}", (result as f64).round() as i32);
        }
        Commands::Cosine4 {
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
            let mut dot = np.dot(a, b);
            let mut norm_a = np.linalg.norm(a);
            let mut norm_b = np.linalg.norm(b);
            let mut result = if (norm_a > 0) && (norm_b > 0) {
                dot / (norm_a * norm_b)
            } else {
                0
            };
            println!("{}", (result as f64).round() as i32);
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
}
