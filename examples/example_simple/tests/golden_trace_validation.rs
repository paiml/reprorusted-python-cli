//! Golden Trace Validation Tests
//!
//! These tests validate that the CLI binary produces expected syscall patterns
//! and meets performance budgets defined in renacer.toml.
//!
//! Run with: cargo test --test golden_trace_validation

use std::process::Command;
use std::fs;

#[test]
fn test_cli_execution_completes() {
    // Basic smoke test: CLI executes successfully
    // Use cargo run to ensure binary is built
    let output = Command::new("cargo")
        .args(&["run", "--quiet", "--", "--name", "TestUser"])
        .output()
        .expect("Failed to execute trivial_cli via cargo run");

    assert!(output.status.success(), "CLI should exit with success");

    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("Hello, TestUser!"), "Output should contain greeting");
}

#[test]
fn test_golden_trace_exists() {
    // Verify golden trace was captured
    let golden_trace_path = "../../golden_traces/trivial_cli_rust.json";
    assert!(
        std::path::Path::new(golden_trace_path).exists(),
        "Golden trace should exist. Run: ./scripts/capture_golden_traces.sh from project root"
    );
}

#[test]
fn test_golden_trace_format() {
    // Validate JSON structure of golden trace
    let golden_trace_path = "../../golden_traces/trivial_cli_rust.json";
    let contents = fs::read_to_string(golden_trace_path)
        .expect("Golden trace file should be readable");

    let json: serde_json::Value = serde_json::from_str(&contents)
        .expect("Golden trace should be valid JSON");

    // Check version
    assert_eq!(json["version"], "0.6.2", "Trace version should match");
    assert_eq!(json["format"], "renacer-json-v1", "Format should be renacer-json-v1");

    // Check syscalls array exists
    assert!(json["syscalls"].is_array(), "Should have syscalls array");

    let syscalls = json["syscalls"].as_array().unwrap();
    assert!(!syscalls.is_empty(), "Should have at least one syscall");

    // Verify syscall structure
    let first_syscall = &syscalls[0];
    assert!(first_syscall["name"].is_string(), "Syscall should have name");
    assert!(first_syscall["args"].is_array(), "Syscall should have args");
}

#[test]
fn test_performance_baseline() {
    // Verify CLI meets performance baseline from golden trace
    let summary_path = "../../golden_traces/trivial_cli_rust_summary.txt";
    let summary = fs::read_to_string(summary_path)
        .expect("Summary file should exist");

    // Parse total runtime from last line
    // Format: "100.00    0.000561           8        65         2 total"
    let last_line = summary.lines().last().unwrap();
    let parts: Vec<&str> = last_line.split_whitespace().collect();

    // Extract total time (column 2)
    let total_time_str = parts[1];
    let total_time_secs: f64 = total_time_str.parse().unwrap();
    let total_time_ms = total_time_secs * 1000.0;

    println!("Golden trace total runtime: {:.3}ms", total_time_ms);

    // Baseline: CLI should complete in <2ms (very generous for CI environments)
    assert!(
        total_time_ms < 2.0,
        "CLI should complete in <2ms (actual: {:.3}ms)",
        total_time_ms
    );
}

#[test]
fn test_syscall_count_budget() {
    // Verify CLI doesn't exceed syscall budget
    let summary_path = "../../golden_traces/trivial_cli_rust_summary.txt";
    let summary = fs::read_to_string(summary_path)
        .expect("Summary file should exist");

    // Parse total syscalls from last line
    let last_line = summary.lines().last().unwrap();
    let parts: Vec<&str> = last_line.split_whitespace().collect();

    // Extract total calls (column 4)
    let total_calls: usize = parts[3].parse().unwrap();

    println!("Golden trace total syscalls: {}", total_calls);

    // Budget: CLI should use <100 syscalls for simple operation
    assert!(
        total_calls < 100,
        "CLI should use <100 syscalls (actual: {})",
        total_calls
    );
}

#[test]
fn test_expected_syscall_patterns() {
    // Verify CLI makes expected syscalls (write for output)
    let golden_trace_path = "../../golden_traces/trivial_cli_rust.json";
    let contents = fs::read_to_string(golden_trace_path)
        .expect("Golden trace file should be readable");

    let json: serde_json::Value = serde_json::from_str(&contents)
        .expect("Golden trace should be valid JSON");

    let syscalls = json["syscalls"].as_array().unwrap();

    // Find write syscall (for "Hello, ..." output)
    let has_write = syscalls.iter().any(|sc| {
        sc["name"].as_str() == Some("write")
    });

    assert!(has_write, "CLI should perform write syscall for output");

    // Find brk/mmap syscalls (memory allocation)
    let has_memory_alloc = syscalls.iter().any(|sc| {
        matches!(sc["name"].as_str(), Some("brk") | Some("mmap"))
    });

    assert!(has_memory_alloc, "CLI should perform memory allocation");
}

#[test]
#[ignore] // Run manually: cargo test --test golden_trace_validation test_regression_check -- --ignored
fn test_regression_check() {
    // Compare current execution against golden trace
    // This test requires running the CLI and capturing a new trace

    use std::process::Command;

    // Run CLI with renacer to capture new trace
    let output = Command::new("renacer")
        .args(&["--format", "json", "--", "./trivial_cli", "--name", "RegressionTest"])
        .current_dir("..")
        .output()
        .expect("Failed to run renacer");

    assert!(output.status.success(), "Renacer should execute successfully");

    let new_trace = String::from_utf8_lossy(&output.stdout);

    // Filter out the "Hello" line (program output)
    let new_trace_json: String = new_trace
        .lines()
        .filter(|line| !line.starts_with("Hello"))
        .collect::<Vec<_>>()
        .join("\n");

    let new_json: serde_json::Value = serde_json::from_str(&new_trace_json)
        .expect("New trace should be valid JSON");

    // Load golden trace
    let golden_trace_path = "../../golden_traces/trivial_cli_rust.json";
    let golden_contents = fs::read_to_string(golden_trace_path)
        .expect("Golden trace should exist");
    let golden_json: serde_json::Value = serde_json::from_str(&golden_contents)
        .expect("Golden trace should be valid JSON");

    // Compare syscall counts
    let new_count = new_json["syscalls"].as_array().unwrap().len();
    let golden_count = golden_json["syscalls"].as_array().unwrap().len();

    // Allow some variance (±10 syscalls) due to environment differences
    let diff = (new_count as i32 - golden_count as i32).abs();

    assert!(
        diff <= 10,
        "Syscall count regression detected. Golden: {}, New: {}, Diff: {}",
        golden_count, new_count, diff
    );

    println!("✓ No significant regression detected");
    println!("  Golden syscalls: {}", golden_count);
    println!("  New syscalls: {}", new_count);
    println!("  Difference: {}", diff);
}
