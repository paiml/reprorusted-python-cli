use clap::Parser;
#[derive(clap::Subcommand)]
enum Commands {
    Min {
        a: i32,
        b: i32,
        c: i32,
        d: i32,
        e: i32,
    },
    Max {
        a: i32,
        b: i32,
        c: i32,
        d: i32,
        e: i32,
    },
    Clamp {
        val: i32,
        lo: i32,
        hi: i32,
    },
}
#[derive(clap::Parser)]
#[command(about = "Min/max tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: verified panic-free"]
#[doc = " Depyler: proven to terminate"]
pub fn main() {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Min { .. });
    match &args.command {
        Commands::Min {
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
            let mut result = a;
            let _cse_temp_1 = b < result;
            if _cse_temp_1 {
                result = b;
            }
            if _cse_temp_1 {
                result = c;
            }
            if _cse_temp_1 {
                result = d;
            }
            if _cse_temp_1 {
                result = e;
            }
            println!("{}", result);
        }
        Commands::Max {
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
            let mut result = a;
            let _cse_temp_3 = b > result;
            if _cse_temp_3 {
                result = b;
            }
            if _cse_temp_3 {
                result = c;
            }
            if _cse_temp_3 {
                result = d;
            }
            if _cse_temp_3 {
                result = e;
            }
            println!("{}", result);
        }
        Commands::Clamp {
            ref hi,
            ref lo,
            ref val,
        } => {
            let hi = *hi;
            let lo = *lo;
            let val = *val;
            let mut result = val;
            let _cse_temp_5 = result < lo;
            if _cse_temp_5 {
                result = lo;
            }
            let _cse_temp_6 = result > hi;
            if _cse_temp_6 {
                result = hi;
            }
            println!("{}", result);
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
}
