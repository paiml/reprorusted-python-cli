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
pub struct IndexError {
    message: String,
}
impl std::fmt::Display for IndexError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "index out of range: {}", self.message)
    }
}
impl std::error::Error for IndexError {}
impl IndexError {
    pub fn new(message: impl Into<String>) -> Self {
        Self {
            message: message.into(),
        }
    }
}
#[derive(clap::Subcommand)]
enum Commands {
    Digits { num: i32 },
    Words { text: String },
    String { text: String },
}
#[derive(clap::Parser)]
#[command(about = "Length tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: proven to terminate"]
pub fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::String { .. });
    match &args.command {
        Commands::String { ref text } => {
            println!("{}", text.len() as i32);
        }
        Commands::Digits { ref num } => {
            let num = *num;
            let mut count = 0;
            let mut n = num;
            let _cse_temp_2 = n < 0;
            if _cse_temp_2 {
                n = -n;
            }
            let _cse_temp_3 = n == 0;
            if _cse_temp_3 {
                count = 1;
            } else {
                while n > 0 {
                    count = count + 1;
                    n = {
                        let a = n;
                        let b = 10;
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
            }
            println!("{}", count);
        }
        Commands::Words { ref text } => {
            let mut count = 1;
            let mut i = 0;
            while i < text.len() as i32 {
                if text.get(i as usize).cloned().unwrap_or_default() == "_" {
                    count = count + 1;
                }
                i = i + 1;
            }
            println!("{}", count);
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
    Ok(())
}
