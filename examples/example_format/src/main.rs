use clap::Parser;
const STR__: &'static str = " ";
#[derive(clap::Subcommand)]
enum Commands {
    Padleft { text: String, width: i32 },
    Padright { text: String, width: i32 },
    Center { text: String, width: i32 },
}
#[derive(clap::Parser)]
#[command(about = "String formatting tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: verified panic-free"]
#[doc = " Depyler: proven to terminate"]
pub fn main() {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::Padleft { .. });
    match &args.command {
        Commands::Padleft { ref text } => {
            let mut result = text;
            while (result.len() as i32) < width {
                result = format!("{}{}", STR__, result);
            }
            println!("{}", result);
        }
        Commands::Padright { ref text } => {
            let mut result = text;
            while (result.len() as i32) < width {
                result = format!("{}{}", result, STR__);
            }
            println!("{}", result);
        }
        Commands::Center { ref text } => {
            let mut result = text;
            let mut left = true;
            while (result.len() as i32) < width {
                if left {
                    result = format!("{}{}", STR__, result);
                } else {
                    result = format!("{}{}", result, STR__);
                }
                left = !left;
            }
            println!("{}", result);
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
}
