use clap::Parser;
const STR__: &'static str = " ";
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
    Underscore { text: String },
    Dash { text: String },
    Dot { text: String },
}
#[derive(clap::Parser)]
#[command(about = "String split tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: proven to terminate"]
pub fn main() -> Result<(), IndexError> {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Underscore { .. });
    match &args.command {
        Commands::Underscore { ref text } => {
            let mut parts = text
                .split("_")
                .map(|s| s.to_string())
                .collect::<Vec<String>>();
            println!(
                "{}",
                format!(
                    "{}{}",
                    format!(
                        "{}{}",
                        parts.get(0usize).cloned().unwrap_or_default(),
                        STR__
                    ) + parts.get(1usize).cloned().unwrap_or_default(),
                    STR__
                ) + parts.get(2usize).cloned().unwrap_or_default()
            );
        }
        Commands::Dash { ref text } => {
            let mut parts = text
                .split("-")
                .map(|s| s.to_string())
                .collect::<Vec<String>>();
            println!(
                "{}",
                format!(
                    "{}{}",
                    format!(
                        "{}{}",
                        parts.get(0usize).cloned().unwrap_or_default(),
                        STR__
                    ) + parts.get(1usize).cloned().unwrap_or_default(),
                    STR__
                ) + parts.get(2usize).cloned().unwrap_or_default()
            );
        }
        Commands::Dot { ref text } => {
            let mut parts = text
                .split(".")
                .map(|s| s.to_string())
                .collect::<Vec<String>>();
            println!(
                "{}",
                format!(
                    "{}{}",
                    format!(
                        "{}{}",
                        parts.get(0usize).cloned().unwrap_or_default(),
                        STR__
                    ) + parts.get(1usize).cloned().unwrap_or_default(),
                    STR__
                ) + parts.get(2usize).cloned().unwrap_or_default()
            );
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
    Ok(())
}
