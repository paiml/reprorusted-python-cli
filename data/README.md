---
license: mit
task_categories:
  - translation
language:
  - en
tags:
  - code
  - python
  - rust
  - transpilation
  - compiler
pretty_name: Depyler CITL Corpus
size_categories:
  - n<1K
---

# Depyler CITL Corpus

Python→Rust transpilation pairs for Compiler-in-the-Loop training.

## Dataset Description

606 Python CLI examples with corresponding Rust translations (where available), designed for training transpiler ML models.

| Split | Examples | With Rust | Size |
|-------|----------|-----------|------|
| train | 606 | 436 (72%) | 1.1 MB |

## Schema

```
- example_name: str      # Directory name (e.g., "example_fibonacci")
- python_file: str       # Python filename
- python_code: str       # Full Python source
- rust_code: str         # Corresponding Rust (empty if not transpiled)
- has_rust: bool         # Whether Rust translation exists
- category: str          # Extracted category
- python_lines: int      # Line count
- rust_lines: int        # Line count
```

## Usage

```python
from datasets import load_dataset

ds = load_dataset("paiml/depyler-citl")

# Filter to pairs with Rust translations
pairs = ds["train"].filter(lambda x: x["has_rust"])

for row in pairs:
    print(f"Python: {row['python_lines']} lines → Rust: {row['rust_lines']} lines")
```

## Related Projects

- [depyler](https://github.com/paiml/depyler) - Python→Rust transpiler
- [alimentar](https://github.com/paiml/alimentar) - Dataset loading library
- [entrenar](https://github.com/paiml/entrenar) - ML training with CITL

## License

MIT
