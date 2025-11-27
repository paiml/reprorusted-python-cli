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
    Consonants { text: String },
    Vowels { text: String },
    Char { text: String, target: String },
}
#[derive(clap::Parser)]
#[command(about = "String count tool")]
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
            ref target,
            ref text,
        } => {
            let mut count = 0;
            let mut i = 0;
            while i < text.len() as i32 {
                if text.get(i as usize).cloned().unwrap_or_default() == target {
                    count = count + 1;
                }
                i = i + 1;
            }
            println!("{}", count);
        }
        Commands::Vowels { ref text } => {
            let mut count = 0;
            let mut i = 0;
            while i < text.len() as i32 {
                let mut c = text.get(i as usize).cloned().unwrap_or_default();
                if ((((c == "a") || (c == "e")) || (c == "i")) || (c == "o")) || (c == "u") {
                    count = count + 1;
                }
                i = i + 1;
            }
            println!("{}", count);
        }
        Commands::Consonants { ref text } => {
            let mut count = 0;
            let mut i = 0;
            while i < text.len() as i32 {
                let mut c = text.get(i as usize).cloned().unwrap_or_default();
                let is_vowel =
                    ((((c == "a") || (c == "e")) || (c == "i")) || (c == "o")) || (c == "u");
                let is_alpha = (c >= "a") && (c <= "z");
                if (is_alpha) && (!is_vowel) {
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
