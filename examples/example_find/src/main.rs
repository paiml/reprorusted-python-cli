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
    Last { text: String, char: String },
    First { text: String, char: String },
}
#[derive(clap::Parser)]
#[command(about = "String find tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: proven to terminate"]
pub fn main() -> Result<(), IndexError> {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::First { .. });
    match &args.command {
        Commands::First { ref char, ref text } => {
            let mut result = -1;
            let mut i = 0;
            while i < text.len() as i32 {
                if text.get(i as usize).cloned().unwrap_or_default() == char {
                    result = i;
                    break;
                }
                i = i + 1;
            }
            println!("{}", result);
        }
        Commands::Last { ref char, ref text } => {
            let mut result = -1;
            let mut i = 0;
            while i < text.len() as i32 {
                if text.get(i as usize).cloned().unwrap_or_default() == char {
                    result = i;
                }
                i = i + 1;
            }
            println!("{}", result);
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
    Ok(())
}
