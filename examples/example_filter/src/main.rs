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
    Positive {
        a: i32,
        b: i32,
        c: i32,
        d: i32,
        e: i32,
    },
    Even {
        a: i32,
        b: i32,
        c: i32,
        d: i32,
        e: i32,
    },
    Odd {
        a: i32,
        b: i32,
        c: i32,
        d: i32,
        e: i32,
    },
}
#[derive(clap::Parser)]
#[command(about = "Filter operations tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: proven to terminate"]
pub fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Positive { .. });
    match &args.command {
        Commands::Positive {
            ref a,
            ref b,
            ref c,
            ref d,
            ref e,
        } => {
            let a = *a;
            let b = *b;
            let c = *c;
            let d = *d;
            let e = *e;
            let mut result = "";
            let mut nums = vec![a, b, c, d, e];
            let mut i = 0;
            while i < 5 {
                if nums.get(i as usize).cloned().unwrap_or_default() > 0 {
                    if result.len() as i32 > 0 {
                        result = format!("{}{}", result, " ");
                    }
                    result = result
                        + nums
                            .get(i as usize)
                            .cloned()
                            .unwrap_or_default()
                            .to_string();
                }
                i = i + 1;
            }
            println!("{}", result);
        }
        Commands::Even {
            ref a,
            ref b,
            ref c,
            ref d,
            ref e,
        } => {
            let a = *a;
            let b = *b;
            let c = *c;
            let d = *d;
            let e = *e;
            let mut result = "";
            let mut nums = vec![a, b, c, d, e];
            let mut i = 0;
            while i < 5 {
                if nums.get(i as usize).cloned().unwrap_or_default() % 2 == 0 {
                    if result.len() as i32 > 0 {
                        result = format!("{}{}", result, " ");
                    }
                    result = result
                        + nums
                            .get(i as usize)
                            .cloned()
                            .unwrap_or_default()
                            .to_string();
                }
                i = i + 1;
            }
            println!("{}", result);
        }
        Commands::Odd {
            ref a,
            ref b,
            ref c,
            ref d,
            ref e,
        } => {
            let a = *a;
            let b = *b;
            let c = *c;
            let d = *d;
            let e = *e;
            let mut result = "";
            let mut nums = vec![a, b, c, d, e];
            let mut i = 0;
            while i < 5 {
                if nums.get(i as usize).cloned().unwrap_or_default() % 2 != 0 {
                    if result.len() as i32 > 0 {
                        result = format!("{}{}", result, " ");
                    }
                    result = result
                        + nums
                            .get(i as usize)
                            .cloned()
                            .unwrap_or_default()
                            .to_string();
                }
                i = i + 1;
            }
            println!("{}", result);
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
    Ok(())
}
