# Performance Regression Detection

Automated performance regression detection for reprorusted-python-cli benchmarks.

## Overview

The regression detection system compares current benchmark results against baseline measurements to identify performance degradations. This ensures that code changes don't introduce unexpected performance regressions.

## Thresholds

### Time Regression
- **Default**: 5% increase in execution time is considered a regression
- **Rationale**: Allows for minor fluctuations due to system load while catching significant slowdowns
- **Configurable**: Use `--time-threshold` flag to adjust

### Memory Regression
- **Default**: 10% increase in memory usage is considered a regression
- **Rationale**: Memory measurements have higher variance than execution time
- **Configurable**: Use `--memory-threshold` flag to adjust

## Usage

### Command Line

```bash
# Check for regressions (uses default thresholds)
python3 benchmarks/framework/regression_check.py

# Check with custom thresholds
python3 benchmarks/framework/regression_check.py \
  --time-threshold 3.0 \
  --memory-threshold 15.0

# Specify custom directories
python3 benchmarks/framework/regression_check.py \
  --baseline-dir benchmarks/baseline \
  --results-dir benchmarks/reports
```

### Make Target

```bash
# Run regression check
make bench-regression
```

### Exit Codes

- **0**: No regressions detected (success)
- **1**: Regressions detected (failure)
- **2**: Error (missing files, parse errors)

## Baseline Management

### Creating Baseline

After running benchmarks, establish a baseline:

```bash
# Run benchmarks
make bench-all

# Copy results as baseline
cp benchmarks/reports/*.json benchmarks/baseline/
git add benchmarks/baseline/
git commit -m "chore: Update benchmark baseline"
```

### Updating Baseline

Update the baseline when:
- Intentional performance improvements are made
- Architecture changes are expected to affect performance
- New optimizations are added

```bash
# After validating new performance characteristics
cp benchmarks/reports/*.json benchmarks/baseline/
git add benchmarks/baseline/
git commit -m "chore: Update benchmark baseline after optimization"
```

### Baseline Files

Baseline files are version-controlled in `benchmarks/baseline/`:
- `example_simple-bench.json`
- `example_flags-bench.json`
- `example_positional-bench.json`
- `example_complex-bench.json`
- `example_stdlib-bench.json`
- `example_subcommands-bench.json`

**Note**: `.gitignore` is configured to:
- Ignore `benchmarks/reports/*.json` (current results)
- **Include** `benchmarks/baseline/*.json` (version-controlled baselines)

## CI/CD Integration

### GitHub Actions

The regression check runs automatically in the `benchmarks` workflow:

```yaml
- name: Check for regressions
  id: regression_check
  continue-on-error: true
  run: make bench-regression

- name: Comment regression status on PR
  if: github.event_name == 'pull_request' && steps.regression_check.outcome == 'failure'
  uses: actions/github-script@v7
  with:
    script: |
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: '⚠️ **Performance Regression Detected**...'
      })
```

### Pull Request Workflow

1. PR is created
2. CI runs benchmarks on PR branch
3. Regression check compares against baseline
4. If regressions detected:
   - Job fails
   - Comment is added to PR
   - Developer reviews and addresses

## Example Output

### No Regressions
```
✅ No performance regressions detected!
```

### Regressions Detected
```
❌ Performance regressions detected:

📊 example_simple:
  - rust Execution Time: 2.45ms → 2.72ms (+11.0%)

📊 example_flags:
  - python Memory: 10982.40KB → 12280.50KB (+11.8%)
```

## Methodology

### Statistical Approach

1. **Multiple iterations**: Each benchmark runs 10 times with 3 warmup iterations
2. **Mean comparison**: Compares mean execution time/memory usage
3. **Percentage change**: Calculates relative change to detect regressions
4. **Threshold-based**: Only reports changes exceeding configured thresholds

### What's Measured

- **Execution Time**: Mean time in milliseconds from bashrs bench
- **Memory Usage**: Peak memory in KB from `/usr/bin/time`
- **Binary Size**: File size in bytes (informational, not checked for regression)

### Limitations

- System load can affect measurements (use dedicated CI runners for consistency)
- First run may be slower due to cold cache
- Memory measurements may have higher variance on different systems

## Troubleshooting

### Missing Baseline Files

```bash
Error: Baseline directory not found: benchmarks/baseline
Run benchmarks first and create baseline with: cp benchmarks/reports/*.json benchmarks/baseline/
```

**Solution**: Create baseline files as described above.

### Parse Errors

If JSON files are corrupted:
```bash
# Re-run benchmarks
make bench-all

# Verify JSON is valid
cat benchmarks/reports/example_simple-bench.json | jq '.'
```

### False Positives

If you're seeing false positives due to system variance:

1. Increase thresholds:
   ```bash
   python3 benchmarks/framework/regression_check.py --time-threshold 10.0
   ```

2. Run benchmarks multiple times and average
3. Use dedicated CI environment with consistent resources

## Roadmap

Part of **RC-017**: Implement performance regression detection

- ✅ Write regression_check.py
- ✅ Integrate with CI/CD
- ✅ Setup baseline results
- ✅ Document regression thresholds
