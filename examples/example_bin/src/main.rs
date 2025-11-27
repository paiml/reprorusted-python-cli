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
#[derive(Debug, Clone)]
pub struct ValueError {
    message: String,
}
impl std::fmt::Display for ValueError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "value error: {}", self.message)
    }
}
impl std::error::Error for ValueError {}
impl ValueError {
    pub fn new(message: impl Into<String>) -> Self {
        Self {
            message: message.into(),
        }
    }
}
#[derive(clap::Subcommand)]
enum Commands {
    Frombin { binstr: String },
    Tobin { num: i32 },
    Bits { num: i32 },
}
#[derive(clap::Parser)]
#[command(about = "Binary operations tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: proven to terminate"]
pub fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Tobin { .. });
    match &args.command {
        Commands::Tobin { ref num } => {
            let num = *num;
            println!("{}", format(num, "b"));
        }
        Commands::Frombin { ref binstr } => {
            println!("{}", i64::from_str_radix(binstr, 2).unwrap());
        }
        Commands::Bits { ref num } => {
            let num = *num;
            let mut count = 0;
            let mut n = num;
            while n > 0 {
                count = count + 1;
                n = {
                    let a = n;
                    let b = 2;
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
                };
            }
            println!("{}", count);
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
    Ok(())
}
