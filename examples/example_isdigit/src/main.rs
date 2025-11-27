use clap::Parser;
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
    Digit { text: String },
    Alpha { text: String },
}
#[derive(clap::Parser)]
#[command(about = "String type check tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: proven to terminate"]
pub fn main() -> Result<(), IndexError> {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Digit { .. });
    match &args.command {
        Commands::Digit { ref text } => {
            let mut result = true;
            let mut i = 0;
            while i < text.len() as i32 {
                let mut c = text.get(i as usize).cloned().unwrap_or_default();
                if (c < "0") || (c > "9") {
                    result = false;
                }
                i = i + 1;
            }
            if !result.is_empty() {
                println!("{}", "true");
            } else {
                println!("{}", "false");
            }
        }
        Commands::Alpha { ref text } => {
            let mut result = true;
            let mut i = 0;
            while i < text.len() as i32 {
                let mut c = text.get(i as usize).cloned().unwrap_or_default();
                let is_lower = (c >= "a") && (c <= "z");
                let is_upper = (c >= "A") && (c <= "Z");
                if (!is_lower) && (!is_upper) {
                    result = false;
                }
                i = i + 1;
            }
            if !result.is_empty() {
                println!("{}", "true");
            } else {
                println!("{}", "false");
            }
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
    Ok(())
}
