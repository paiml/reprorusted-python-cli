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
    Reverse { text: String },
    Index { text: String },
    Start { text: String, offset: i32 },
}
#[derive(clap::Parser)]
#[command(about = "Enumerate operations tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: proven to terminate"]
pub fn main() -> Result<(), IndexError> {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Index { .. });
    match &args.command {
        Commands::Index { ref text } => {
            let mut result = "";
            let mut idx = 0;
            while idx < text.len() as i32 {
                if idx > 0 {
                    result = format!("{}{}", result, " ");
                }
                result = format!("{}{}", result + idx.to_string(), ":")
                    + text.get(idx as usize).cloned().unwrap_or_default();
                idx = idx + 1;
            }
            println!("{}", result);
        }
        Commands::Start {
            ref offset,
            ref text,
        } => {
            let offset = *offset;
            let mut result = "";
            let mut idx = 0;
            while idx < text.len() as i32 {
                if idx > 0 {
                    result = format!("{}{}", result, " ");
                }
                result = format!("{}{}", result + offset + idx.to_string(), ":")
                    + text.get(idx as usize).cloned().unwrap_or_default();
                idx = idx + 1;
            }
            println!("{}", result);
        }
        Commands::Reverse { ref text } => {
            let mut result = "";
            let _cse_temp_3 = text.len() as i32;
            let mut idx = _cse_temp_3 - 1;
            let mut first = true;
            while idx >= 0 {
                if !first {
                    result = format!("{}{}", result, " ");
                }
                first = false;
                result = format!("{}{}", result + idx.to_string(), ":")
                    + text.get(idx as usize).cloned().unwrap_or_default();
                idx = idx - 1;
            }
            println!("{}", result);
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
    Ok(())
}
