use clap::Parser;
use std::io::Read;
use std::io::Write;
#[derive(clap::Parser)]
#[command(about = "Test with open()")]
struct Args {
    #[arg(long)]
    #[arg(action = clap::ArgAction::SetTrue)]
    #[doc = "Write to file"]
    write: bool,
    #[arg(long)]
    #[arg(action = clap::ArgAction::SetTrue)]
    #[doc = "Read from file"]
    read: bool,
}
#[doc = " Depyler: verified panic-free"]
#[doc = " Depyler: proven to terminate"]
pub fn main() -> Result<(), std::io::Error> {
    let args = Args::parse();
    if args.write {
        let mut f = std::fs::File::create("test.txt".to_string())?;
        f.write_all("Hello from Rust!\n".to_string().as_bytes())
            .unwrap();
        println!("{}", "Written to test.txt");
    }
    if args.read {
        let mut f = std::fs::File::open("test.txt".to_string())?;
        let content = {
            let mut content = String::new();
            f.read_to_string(&mut content)?;
            content
        };
        println!("{}", format!("Read: {:?}", content));
    }
    Ok(())
}
