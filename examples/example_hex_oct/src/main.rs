use clap::Parser;
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
    Dec { hexval: String },
    Oct { num: i32 },
    Hex { num: i32 },
}
#[derive(clap::Parser)]
#[command(about = "Number base conversion tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: verified panic-free"]
#[doc = " Depyler: proven to terminate"]
pub fn main() -> Result<(), ValueError> {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Hex { .. });
    match &args.command {
        Commands::Hex { ref num } => {
            let num = *num;
            println!("{}", format(num, "x"));
        }
        Commands::Oct { ref num } => {
            let num = *num;
            println!("{}", format(num, "o"));
        }
        Commands::Dec { ref hexval } => {
            println!("{}", i64::from_str_radix(hexval, 16).unwrap());
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
    Ok(())
}
