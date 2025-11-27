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
    Calc { a: i32, b: i32 },
    Rem { a: i32, b: i32 },
    Quot { a: i32, b: i32 },
}
#[derive(clap::Parser)]
#[command(about = "Divmod tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: proven to terminate"]
pub fn main() -> Result<(), ZeroDivisionError> {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Calc { .. });
    match &args.command {
        Commands::Calc { .. } => {
            println!(
                "{}",
                format!(
                    "{} {}",
                    {
                        let a = a;
                        let b = b;
                        let q = a / b;
                        let r = a % b;
                        let r_negative = r < 0;
                        let b_negative = b < 0;
                        let r_nonzero = r != 0;
                        let signs_differ = r_negative != b_negative;
                        let needs_adjustment = r_nonzero && signs_differ;
                        if needs_adjustment {
                            q - 1
                        } else {
                            q
                        }
                    },
                    a % b
                )
            );
        }
        Commands::Quot { ref a, ref b } => {
            let a = *a;
            let b = *b;
            println!("{}", {
                let a = a;
                let b = b;
                let q = a / b;
                let r = a % b;
                let r_negative = r < 0;
                let b_negative = b < 0;
                let r_nonzero = r != 0;
                let signs_differ = r_negative != b_negative;
                let needs_adjustment = r_nonzero && signs_differ;
                if needs_adjustment {
                    q - 1
                } else {
                    q
                }
            });
        }
        Commands::Rem { ref a, ref b } => {
            let a = *a;
            let b = *b;
            println!("{}", a % b);
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
    Ok(())
}
