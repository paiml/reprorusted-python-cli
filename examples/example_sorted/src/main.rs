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
    Asc {
        a: i32,
        b: i32,
        c: i32,
        d: i32,
        e: i32,
    },
    Desc {
        a: i32,
        b: i32,
        c: i32,
        d: i32,
        e: i32,
    },
    Alpha {
        a: String,
        b: String,
        c: String,
    },
}
#[derive(clap::Parser)]
#[command(about = "Sorting tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: proven to terminate"]
pub fn main() -> Result<(), IndexError> {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Asc { .. });
    match &args.command {
        Commands::Asc {
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
            let mut nums = vec![a, b, c, d, e];
            let mut i = 0;
            while i < 5 {
                let mut j = i + 1;
                while j < 5 {
                    if nums.get(j as usize).cloned().unwrap_or_default()
                        < nums.get(i as usize).cloned().unwrap_or_default()
                    {
                        let mut tmp = nums.get(i as usize).cloned().unwrap_or_default();
                        nums.insert(
                            (i) as usize,
                            nums.get(j as usize).cloned().unwrap_or_default(),
                        );
                        nums.insert((j) as usize, tmp);
                    }
                    j = j + 1;
                }
                i = i + 1;
            }
            println!(
                "{}",
                format!(
                    "{} {} {} {} {}",
                    nums.get(0usize).cloned().unwrap_or_default(),
                    nums.get(1usize).cloned().unwrap_or_default(),
                    nums.get(2usize).cloned().unwrap_or_default(),
                    nums.get(3usize).cloned().unwrap_or_default(),
                    nums.get(4usize).cloned().unwrap_or_default()
                )
            );
        }
        Commands::Desc {
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
            let mut nums = vec![a, b, c, d, e];
            let mut i = 0;
            while i < 5 {
                let mut j = i + 1;
                while j < 5 {
                    if nums.get(j as usize).cloned().unwrap_or_default()
                        > nums.get(i as usize).cloned().unwrap_or_default()
                    {
                        let mut tmp = nums.get(i as usize).cloned().unwrap_or_default();
                        nums.insert(
                            (i) as usize,
                            nums.get(j as usize).cloned().unwrap_or_default(),
                        );
                        nums.insert((j) as usize, tmp);
                    }
                    j = j + 1;
                }
                i = i + 1;
            }
            println!(
                "{}",
                format!(
                    "{} {} {} {} {}",
                    nums.get(0usize).cloned().unwrap_or_default(),
                    nums.get(1usize).cloned().unwrap_or_default(),
                    nums.get(2usize).cloned().unwrap_or_default(),
                    nums.get(3usize).cloned().unwrap_or_default(),
                    nums.get(4usize).cloned().unwrap_or_default()
                )
            );
        }
        Commands::Alpha {
            ref a,
            ref b,
            ref c,
        } => {
            let mut words = vec![a, b, c];
            let mut i = 0;
            while i < 3 {
                let mut j = i + 1;
                while j < 3 {
                    if words.get(j as usize).cloned().unwrap_or_default()
                        < words.get(i as usize).cloned().unwrap_or_default()
                    {
                        let mut tmp = words.get(i as usize).cloned().unwrap_or_default();
                        words.insert(
                            (i) as usize,
                            words.get(j as usize).cloned().unwrap_or_default(),
                        );
                        words.insert((j) as usize, tmp);
                    }
                    j = j + 1;
                }
                i = i + 1;
            }
            println!(
                "{}",
                format!(
                    "{} {} {}",
                    words.get(0usize).cloned().unwrap_or_default(),
                    words.get(1usize).cloned().unwrap_or_default(),
                    words.get(2usize).cloned().unwrap_or_default()
                )
            );
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
    Ok(())
}
