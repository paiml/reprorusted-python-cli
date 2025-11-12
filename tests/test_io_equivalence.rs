// test_io_equivalence.rs
//
// Comprehensive I/O equivalence testing for Python vs Rust binaries
//
// This test suite validates that transpiled Rust binaries produce identical
// output to their Python source counterparts for all examples.
//
// Test methodology:
// 1. Run Python script with test arguments
// 2. Run Rust binary with same arguments
// 3. Compare exit codes
// 4. Compare stdout output (exact match)
// 5. Compare stderr output patterns
//
// Tested examples:
// - example_simple/trivial_cli
// - example_flags/flag_parser
// - example_positional/positional_args
// - example_subcommands/git_clone
// - example_complex/complex_cli
// - example_stdlib/stdlib_integration

use assert_cmd::Command;
use std::path::{Path, PathBuf};
use tempfile::TempDir;

/// Helper struct to represent an example with its paths
struct Example {
    name: &'static str,
    python_script: PathBuf,
    rust_binary: PathBuf,
}

impl Example {
    fn new(name: &'static str, dir: &'static str, script: &'static str) -> Self {
        let base = PathBuf::from("examples").join(dir);
        Self {
            name,
            python_script: base.join(script),
            rust_binary: base.join(script.trim_end_matches(".py")),
        }
    }

    /// Run Python script with given arguments
    fn run_python(&self, args: &[&str]) -> (i32, String, String) {
        let output = Command::new("python3")
            .arg(&self.python_script)
            .args(args)
            .output()
            .expect("Failed to execute Python script");

        let exit_code = output.status.code().unwrap_or(-1);
        let stdout = String::from_utf8_lossy(&output.stdout).to_string();
        let stderr = String::from_utf8_lossy(&output.stderr).to_string();

        (exit_code, stdout, stderr)
    }

    /// Run Rust binary with given arguments
    fn run_rust(&self, args: &[&str]) -> (i32, String, String) {
        // Check if binary exists
        if !self.rust_binary.exists() {
            panic!(
                "Rust binary not found: {}. Run 'make compile' in examples/{}/",
                self.rust_binary.display(),
                self.name
            );
        }

        let output = Command::new(&self.rust_binary)
            .args(args)
            .output()
            .expect("Failed to execute Rust binary");

        let exit_code = output.status.code().unwrap_or(-1);
        let stdout = String::from_utf8_lossy(&output.stdout).to_string();
        let stderr = String::from_utf8_lossy(&output.stderr).to_string();

        (exit_code, stdout, stderr)
    }

    /// Assert that Python and Rust produce identical output
    fn assert_equivalence(&self, args: &[&str]) {
        let (py_exit, py_stdout, py_stderr) = self.run_python(args);
        let (rs_exit, rs_stdout, rs_stderr) = self.run_rust(args);

        // Compare exit codes
        assert_eq!(
            py_exit, rs_exit,
            "{}: Exit codes differ for args {:?}\n  Python: {}\n  Rust: {}",
            self.name, args, py_exit, rs_exit
        );

        // Compare stdout (exact match)
        assert_eq!(
            py_stdout, rs_stdout,
            "{}: Stdout differs for args {:?}\n  Python: {}\n  Rust: {}",
            self.name, args, py_stdout, rs_stdout
        );

        // For stderr, we only compare if both are non-empty
        // (some implementations may have different error formatting)
        if !py_stderr.is_empty() && !rs_stderr.is_empty() {
            // Both should indicate an error occurred
            assert!(
                rs_stderr.contains("error") || rs_stderr.contains("Error"),
                "{}: Rust stderr should contain error for args {:?}\n  Rust stderr: {}",
                self.name,
                args,
                rs_stderr
            );
        }
    }
}

// ============================================================================
// Example: trivial_cli (example_simple)
// ============================================================================

#[test]
fn test_trivial_cli_help() {
    let example = Example::new("trivial_cli", "example_simple", "trivial_cli.py");
    example.assert_equivalence(&["--help"]);
}

#[test]
fn test_trivial_cli_version() {
    let example = Example::new("trivial_cli", "example_simple", "trivial_cli.py");
    example.assert_equivalence(&["--version"]);
}

#[test]
fn test_trivial_cli_valid_name() {
    let example = Example::new("trivial_cli", "example_simple", "trivial_cli.py");
    example.assert_equivalence(&["--name", "Alice"]);
}

#[test]
fn test_trivial_cli_name_with_spaces() {
    let example = Example::new("trivial_cli", "example_simple", "trivial_cli.py");
    example.assert_equivalence(&["--name", "Dr. Smith"]);
}

// ============================================================================
// Example: flag_parser (example_flags)
// ============================================================================

#[test]
fn test_flag_parser_help() {
    let example = Example::new("flag_parser", "example_flags", "flag_parser.py");
    example.assert_equivalence(&["--help"]);
}

#[test]
fn test_flag_parser_version() {
    let example = Example::new("flag_parser", "example_flags", "flag_parser.py");
    example.assert_equivalence(&["--version"]);
}

#[test]
fn test_flag_parser_no_flags() {
    let example = Example::new("flag_parser", "example_flags", "flag_parser.py");
    example.assert_equivalence(&[]);
}

#[test]
fn test_flag_parser_verbose() {
    let example = Example::new("flag_parser", "example_flags", "flag_parser.py");
    example.assert_equivalence(&["--verbose"]);
}

#[test]
fn test_flag_parser_debug() {
    let example = Example::new("flag_parser", "example_flags", "flag_parser.py");
    example.assert_equivalence(&["--debug"]);
}

#[test]
fn test_flag_parser_quiet() {
    let example = Example::new("flag_parser", "example_flags", "flag_parser.py");
    example.assert_equivalence(&["--quiet"]);
}

#[test]
fn test_flag_parser_combined() {
    let example = Example::new("flag_parser", "example_flags", "flag_parser.py");
    example.assert_equivalence(&["-vdq"]);
}

// ============================================================================
// Example: positional_args (example_positional)
// ============================================================================

#[test]
fn test_positional_help() {
    let example = Example::new("positional_args", "example_positional", "positional_args.py");
    example.assert_equivalence(&["--help"]);
}

#[test]
fn test_positional_version() {
    let example = Example::new("positional_args", "example_positional", "positional_args.py");
    example.assert_equivalence(&["--version"]);
}

#[test]
fn test_positional_start_no_targets() {
    let example = Example::new("positional_args", "example_positional", "positional_args.py");
    example.assert_equivalence(&["start"]);
}

#[test]
fn test_positional_start_single_target() {
    let example = Example::new("positional_args", "example_positional", "positional_args.py");
    example.assert_equivalence(&["start", "web"]);
}

#[test]
fn test_positional_start_multiple_targets() {
    let example = Example::new("positional_args", "example_positional", "positional_args.py");
    example.assert_equivalence(&["start", "web", "db", "cache"]);
}

#[test]
fn test_positional_stop() {
    let example = Example::new("positional_args", "example_positional", "positional_args.py");
    example.assert_equivalence(&["stop", "db"]);
}

#[test]
fn test_positional_restart() {
    let example = Example::new("positional_args", "example_positional", "positional_args.py");
    example.assert_equivalence(&["restart", "web", "api"]);
}

// ============================================================================
// Example: git_clone (example_subcommands)
// ============================================================================

#[test]
fn test_git_clone_help() {
    let example = Example::new("git_clone", "example_subcommands", "git_clone.py");
    example.assert_equivalence(&["--help"]);
}

#[test]
fn test_git_clone_version() {
    let example = Example::new("git_clone", "example_subcommands", "git_clone.py");
    example.assert_equivalence(&["--version"]);
}

#[test]
fn test_git_clone_clone() {
    let example = Example::new("git_clone", "example_subcommands", "git_clone.py");
    example.assert_equivalence(&["clone", "https://example.com/repo.git"]);
}

#[test]
fn test_git_clone_clone_ssh() {
    let example = Example::new("git_clone", "example_subcommands", "git_clone.py");
    example.assert_equivalence(&["clone", "git@github.com:user/repo.git"]);
}

#[test]
fn test_git_clone_push() {
    let example = Example::new("git_clone", "example_subcommands", "git_clone.py");
    example.assert_equivalence(&["push", "origin"]);
}

#[test]
fn test_git_clone_pull() {
    let example = Example::new("git_clone", "example_subcommands", "git_clone.py");
    example.assert_equivalence(&["pull", "origin"]);
}

#[test]
fn test_git_clone_verbose() {
    let example = Example::new("git_clone", "example_subcommands", "git_clone.py");
    example.assert_equivalence(&["--verbose", "clone", "https://example.com/repo.git"]);
}

// ============================================================================
// Example: complex_cli (example_complex)
// ============================================================================

#[test]
fn test_complex_cli_help() {
    let example = Example::new("complex_cli", "example_complex", "complex_cli.py");
    example.assert_equivalence(&["--help"]);
}

#[test]
fn test_complex_cli_version() {
    let example = Example::new("complex_cli", "example_complex", "complex_cli.py");
    example.assert_equivalence(&["--version"]);
}

#[test]
fn test_complex_cli_basic() {
    let example = Example::new("complex_cli", "example_complex", "complex_cli.py");
    example.assert_equivalence(&["--input", "data.txt"]);
}

#[test]
fn test_complex_cli_json() {
    let example = Example::new("complex_cli", "example_complex", "complex_cli.py");
    example.assert_equivalence(&["--input", "data.txt", "--json"]);
}

#[test]
fn test_complex_cli_with_port() {
    let example = Example::new("complex_cli", "example_complex", "complex_cli.py");
    example.assert_equivalence(&["--input", "data.txt", "--port", "8080"]);
}

#[test]
fn test_complex_cli_with_email() {
    let example = Example::new("complex_cli", "example_complex", "complex_cli.py");
    example.assert_equivalence(&["--input", "data.txt", "--email", "user@example.com"]);
}

// ============================================================================
// Example: stdlib_integration (example_stdlib)
// ============================================================================

#[test]
fn test_stdlib_help() {
    let example = Example::new("stdlib_integration", "example_stdlib", "stdlib_integration.py");
    example.assert_equivalence(&["--help"]);
}

#[test]
fn test_stdlib_version() {
    let example = Example::new("stdlib_integration", "example_stdlib", "stdlib_integration.py");
    example.assert_equivalence(&["--version"]);
}

#[test]
fn test_stdlib_text_format() {
    // Create a temporary test file
    let temp_dir = TempDir::new().unwrap();
    let test_file = temp_dir.path().join("test.txt");
    std::fs::write(&test_file, "Hello World").unwrap();

    let example = Example::new("stdlib_integration", "example_stdlib", "stdlib_integration.py");
    example.assert_equivalence(&["--file", test_file.to_str().unwrap()]);
}

#[test]
fn test_stdlib_json_format() {
    // Create a temporary test file
    let temp_dir = TempDir::new().unwrap();
    let test_file = temp_dir.path().join("test.txt");
    std::fs::write(&test_file, "Test content").unwrap();

    let example = Example::new("stdlib_integration", "example_stdlib", "stdlib_integration.py");
    example.assert_equivalence(&["--file", test_file.to_str().unwrap(), "--format", "json"]);
}

#[test]
fn test_stdlib_with_hash() {
    // Create a temporary test file
    let temp_dir = TempDir::new().unwrap();
    let test_file = temp_dir.path().join("test.txt");
    std::fs::write(&test_file, "Hello").unwrap();

    let example = Example::new("stdlib_integration", "example_stdlib", "stdlib_integration.py");
    example.assert_equivalence(&[
        "--file",
        test_file.to_str().unwrap(),
        "--hash",
        "md5",
    ]);
}

#[test]
fn test_stdlib_compact_format() {
    // Create a temporary test file
    let temp_dir = TempDir::new().unwrap();
    let test_file = temp_dir.path().join("test.txt");
    std::fs::write(&test_file, "Data").unwrap();

    let example = Example::new("stdlib_integration", "example_stdlib", "stdlib_integration.py");
    example.assert_equivalence(&[
        "--file",
        test_file.to_str().unwrap(),
        "--format",
        "compact",
    ]);
}

// ============================================================================
// Integration Tests: Cross-Example Validation
// ============================================================================

#[test]
fn test_all_examples_have_help() {
    let examples = vec![
        Example::new("trivial_cli", "example_simple", "trivial_cli.py"),
        Example::new("flag_parser", "example_flags", "flag_parser.py"),
        Example::new("positional_args", "example_positional", "positional_args.py"),
        Example::new("git_clone", "example_subcommands", "git_clone.py"),
        Example::new("complex_cli", "example_complex", "complex_cli.py"),
        Example::new("stdlib_integration", "example_stdlib", "stdlib_integration.py"),
    ];

    for example in examples {
        println!("Testing --help for {}", example.name);
        example.assert_equivalence(&["--help"]);
    }
}

#[test]
fn test_all_examples_have_version() {
    let examples = vec![
        Example::new("trivial_cli", "example_simple", "trivial_cli.py"),
        Example::new("flag_parser", "example_flags", "flag_parser.py"),
        Example::new("positional_args", "example_positional", "positional_args.py"),
        Example::new("git_clone", "example_subcommands", "git_clone.py"),
        Example::new("complex_cli", "example_complex", "complex_cli.py"),
        Example::new("stdlib_integration", "example_stdlib", "stdlib_integration.py"),
    ];

    for example in examples {
        println!("Testing --version for {}", example.name);
        example.assert_equivalence(&["--version"]);
    }
}

// ============================================================================
// Performance Comparison Tests (informational, not assertions)
// ============================================================================

#[cfg(feature = "benchmark")]
#[test]
fn test_performance_comparison() {
    use std::time::Instant;

    let examples = vec![
        Example::new("trivial_cli", "example_simple", "trivial_cli.py"),
        Example::new("flag_parser", "example_flags", "flag_parser.py"),
    ];

    for example in examples {
        println!("\nPerformance comparison for {}", example.name);

        // Python timing
        let start = Instant::now();
        for _ in 0..100 {
            example.run_python(&["--version"]);
        }
        let py_duration = start.elapsed();

        // Rust timing
        let start = Instant::now();
        for _ in 0..100 {
            example.run_rust(&["--version"]);
        }
        let rs_duration = start.elapsed();

        println!("  Python: {:?}", py_duration);
        println!("  Rust: {:?}", rs_duration);
        println!(
            "  Speedup: {:.2}x",
            py_duration.as_secs_f64() / rs_duration.as_secs_f64()
        );
    }
}
