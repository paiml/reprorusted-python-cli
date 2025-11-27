use clap::Parser;
#[derive(Debug, Clone)]
pub struct ZeroDivisionError {
    message: String,
}
impl std::fmt::Display for ZeroDivisionError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "division by zero: {}", self.message)
    }
}
impl std::error::Error for ZeroDivisionError {}
impl ZeroDivisionError {
    pub fn new(message: impl Into<String>) -> Self {
        Self {
            message: message.into(),
        }
    }
}
#[derive(clap::Subcommand)]
enum Commands {
    Average {
        a: i32,
        b: i32,
        c: i32,
    },
    Product {
        a: i32,
        b: i32,
        c: i32,
    },
    Add {
        a: i32,
        b: i32,
        c: i32,
        d: i32,
        e: i32,
    },
}
#[derive(clap::Parser)]
#[command(about = "Sum tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: proven to terminate"]
pub fn main() -> Result<(), ZeroDivisionError> {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Add { .. });
    match &args.command {
        Commands::Add {
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
            println!("{}", a + b + c + d + e);
        }
        Commands::Product {
            ref a,
            ref b,
            ref c,
        } => {
            let a = *a;
            let b = *b;
            let c = *c;
            println!("{}", a * b * c);
        }
        Commands::Average {
            ref a,
            ref b,
            ref c,
        } => {
            let a = *a;
            let b = *b;
            let c = *c;
            let _cse_temp_3 = a + b;
            let _cse_temp_4 = _cse_temp_3 + c;
            let total = _cse_temp_4;
            println!("{}", total / 3);
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
    Ok(())
}
