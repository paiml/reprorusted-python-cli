use clap::Parser;
const STR_FALSE: &'static str = "false";
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
    Starts { text: String, prefix: String },
    Ends { text: String, suffix: String },
}
#[derive(clap::Parser)]
#[command(about = "String prefix/suffix tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: proven to terminate"]
pub fn main() -> Result<(), IndexError> {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Starts { .. });
    match &args.command {
        Commands::Starts {
            ref prefix,
            ref text,
        } => {
            let _cse_temp_1 = prefix.len() as i32;
            let _cse_temp_2 = _cse_temp_1 > _cse_temp_1;
            if _cse_temp_2 {
                println!("{}", STR_FALSE);
            } else {
                let mut r#match = true;
                let mut i = 0;
                while i < prefix.len() as i32 {
                    if text.get(i as usize).cloned().unwrap_or_default()
                        != prefix.get(i as usize).cloned().unwrap_or_default()
                    {
                        r#match = false;
                    }
                    i = i + 1;
                }
                if r#match {
                    println!("{}", "true");
                } else {
                    println!("{}", STR_FALSE);
                }
            }
        }
        Commands::Ends {
            ref suffix,
            ref text,
        } => {
            let _cse_temp_4 = suffix.len() as i32;
            let _cse_temp_5 = _cse_temp_4 > _cse_temp_4;
            if _cse_temp_5 {
                println!("{}", STR_FALSE);
            } else {
                let mut r#match = true;
                let offset = _cse_temp_4 - _cse_temp_4;
                let mut i = 0;
                while i < suffix.len() as i32 {
                    if {
                        let base = &text;
                        let idx: i32 = offset + i;
                        let actual_idx = if idx < 0 {
                            base.len().saturating_sub(idx.abs() as usize)
                        } else {
                            idx as usize
                        };
                        base.get(actual_idx).cloned().unwrap_or_default()
                    } != suffix.get(i as usize).cloned().unwrap_or_default()
                    {
                        r#match = false;
                    }
                    i = i + 1;
                }
                if r#match {
                    println!("{}", "true");
                } else {
                    println!("{}", STR_FALSE);
                }
            }
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
    Ok(())
}
