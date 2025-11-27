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
    String { text: String },
    Words { text: String },
    Digits { num: i32 },
}
#[derive(clap::Parser)]
#[command(about = "Reverse tool")]
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
            let mut result = "";
            let _cse_temp_1 = text.len() as i32;
            let mut i = _cse_temp_1 - 1;
            while i >= 0 {
                result = result + text.get(i as usize).cloned().unwrap_or_default();
                i = i - 1;
            }
            println!("{}", result);
        }
        Commands::Digits { ref num } => {
            let num = *num;
            let mut n = num;
            let mut result = 0;
            while n > 0 {
                result = result * 10 + n % 10;
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
            println!("{}", result);
        }
        Commands::Words { ref text } => {
            let parts = text
                .split("_")
                .map(|s| s.to_string())
                .collect::<Vec<String>>();
            let _cse_temp_4 = format!("{}{}", parts.get(2usize).cloned().unwrap_or_default(), "_");
            let _cse_temp_5 = _cse_temp_4 + parts.get(1usize).cloned().unwrap_or_default();
            let _cse_temp_6 =
                format!("{}{}", _cse_temp_5, "_") + parts.get(0usize).cloned().unwrap_or_default();
            let mut result = _cse_temp_6.clone();
            println!("{}", result);
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
    Ok(())
}
