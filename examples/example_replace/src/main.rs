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
    First {
        text: String,
        new: String,
    },
    Char {
        text: String,
        old: String,
        new: String,
    },
    All {
        text: String,
        new: String,
    },
}
#[derive(clap::Parser)]
#[command(about = "String replace tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: proven to terminate"]
pub fn main() -> Result<(), IndexError> {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Char { .. });
    match &args.command {
        Commands::Char {
            ref new,
            ref old,
            ref text,
        } => {
            println!("{}", text.replace(old, new));
        }
        Commands::First { ref new, ref text } => {
            let mut result = "";
            let mut found = false;
            let mut i = 0;
            while i < text.len() as i32 {
                if (!found)
                    && (text.get(i as usize).cloned().unwrap_or_default()
                        == text.get(0usize).cloned().unwrap_or_default())
                {
                    result = result + new;
                    found = true;
                } else {
                    result = result + text.get(i as usize).cloned().unwrap_or_default();
                }
                i = i + 1;
            }
            println!("{}", result);
        }
        Commands::All { ref new } => {
            let mut result = "";
            let mut i = 0;
            while i < text.len() as i32 {
                result = result + new;
                i = i + 1;
            }
            println!("{}", result);
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
    Ok(())
}
