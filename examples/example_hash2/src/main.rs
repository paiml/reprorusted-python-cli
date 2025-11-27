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
    Simple { text: String },
    Djb2 { text: String },
    Fnv { text: String },
}
#[derive(clap::Parser)]
#[command(about = "Hash operations tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: proven to terminate"]
pub fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Djb2 { .. });
    match &args.command {
        Commands::Djb2 { ref text } => {
            let mut h = 5381;
            let mut i = 0;
            while i < text.len() as i32 {
                h = (h * 33
                    + text
                        .get(i as usize)
                        .cloned()
                        .unwrap_or_default()
                        .chars()
                        .next()
                        .unwrap() as i32)
                    % (2 as i32)
                        .checked_pow(32 as u32)
                        .expect("Power operation overflowed");
                i = i + 1;
            }
            println!("{}", h);
        }
        Commands::Fnv { ref text } => {
            let mut h = 2166136261;
            let mut i = 0;
            while i < text.len() as i32 {
                h = h * 16777619
                    % (2 as i32)
                        .checked_pow(32 as u32)
                        .expect("Power operation overflowed");
                h = h ^ text
                    .get(i as usize)
                    .cloned()
                    .unwrap_or_default()
                    .chars()
                    .next()
                    .unwrap() as i32;
                i = i + 1;
            }
            println!("{}", h);
        }
        Commands::Simple { ref text } => {
            let mut h = 0;
            let mut i = 0;
            while i < text.len() as i32 {
                h = h + text
                    .get(i as usize)
                    .cloned()
                    .unwrap_or_default()
                    .chars()
                    .next()
                    .unwrap() as i32;
                i = i + 1;
            }
            println!("{}", h);
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
    Ok(())
}
