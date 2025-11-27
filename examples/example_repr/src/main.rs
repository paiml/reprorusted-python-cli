use clap::Parser;
#[derive(clap::Subcommand)]
enum Commands {
    String { text: String },
    Escape { name: String },
    Number { num: i32 },
}
#[derive(clap::Parser)]
#[command(about = "Representation tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}
#[doc = " Depyler: verified panic-free"]
#[doc = " Depyler: proven to terminate"]
pub fn main() {
    let args = Args::parse();
    let _cse_temp_0 = matches!(args.command, Commands::String { .. });
    match &args.command {
        Commands::String { .. } => {
            println!("{}", format!("'{}'", text));
        }
        Commands::Number { ref num } => {
            let num = *num;
            println!("{}", num);
        }
        Commands::Escape { ref name } => {
            let _cse_temp_3 = name == "tab";
            if _cse_temp_3 {
                println!("{}", format!("{:?}", "\t"));
            } else {
                let _cse_temp_4 = name == "newline";
                if _cse_temp_4 {
                    println!("{}", format!("{:?}", "\n"));
                } else {
                    println!("{}", format!("{:?}", name));
                }
            }
        }
        _ => unreachable!("Other command variants handled elsewhere"),
    }
}
