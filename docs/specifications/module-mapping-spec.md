# Module Mapping Specification

**Version:** 1.0.0
**Status:** Active
**Related Issues:** #4, #5
**Last Updated:** 2025-11-28

## Executive Summary

This document specifies the Python-to-Rust module mappings required for depyler to successfully transpile the examples in this repository. It serves as both documentation and a roadmap for improving depyler's module support.

## 1. Current Module Usage Analysis

Based on analysis of all examples (excluding test files), the following modules are used:

### 1.1 Standard Library (Priority 1)

| Module | Usage Count | Rust Equivalent | Status |
|--------|-------------|-----------------|--------|
| `argparse` | 271 | `clap` | ✅ Working |
| `sys` | 185 | `std::env`, `std::process` | ⚠️ Partial |
| `json` | 36 | `serde_json` | ⚠️ Partial |
| `math` | 28 | `std::f64`, `libm` | ⚠️ Partial |
| `re` | 14 | `regex` | ⚠️ Partial |
| `os` | 14 | `std::env`, `std::fs` | ⚠️ Partial |
| `random` | 9 | `rand` | ⚠️ Partial |
| `time` | 5 | `std::time` | ⚠️ Partial |
| `threading` | 5 | `std::thread` | ❌ Not supported |
| `struct` | 5 | `byteorder` | ❌ Not supported |
| `hashlib` | 5 | `sha2`, `md5` | ❌ Not supported |
| `asyncio` | 5 | `tokio` | ❌ Not supported |
| `tempfile` | 3 | `tempfile` | ❌ Not supported |
| `shutil` | 3 | `fs_extra` | ❌ Not supported |
| `base64` | 3 | `base64` | ❌ Not supported |
| `csv` | 2 | `csv` | ⚠️ Partial |
| `statistics` | 2 | Manual impl | ❌ Not supported |
| `calendar` | 2 | `chrono` | ❌ Not supported |
| `datetime` | 4+ | `chrono` | ⚠️ Partial |
| `pathlib` | 6 | `std::path` | ⚠️ Partial |

### 1.2 Typing Module

| Type | Usage Count | Rust Equivalent | Status |
|------|-------------|-----------------|--------|
| `Dict[K, V]` | 50+ | `HashMap<K, V>` | ⚠️ Partial |
| `List[T]` | 30+ | `Vec<T>` | ✅ Working |
| `Any` | 15 | `dyn Any` or generics | ⚠️ Partial |
| `Generic[T]` | 10 | `struct<T>` | ⚠️ Partial |
| `TypeVar` | 10 | Generic parameter | ⚠️ Partial |
| `Callable` | 28 | `Fn` traits | ❌ Not supported |

### 1.3 Data Structures

| Type | Usage Count | Rust Equivalent | Status |
|------|-------------|-----------------|--------|
| `dataclass` | 60+ | `struct` with derives | ✅ Working |
| `Enum` | 19 | `enum` | ⚠️ Partial |
| `deque` | 3 | `VecDeque` | ❌ Not supported |
| `namedtuple` | varies | `struct` | ⚠️ Partial |

### 1.4 Third-Party Libraries

| Library | Usage Count | Rust Equivalent | Status |
|---------|-------------|-----------------|--------|
| `numpy` | 25 | `ndarray` or Vec | ⚠️ Partial |
| `abc` | 8 | `trait` | ⚠️ Partial |

## 2. Proposed Module Mappings

### 2.1 Top 10 Stdlib Modules (Priority)

#### 2.1.1 `sys` Module

```python
# Python
import sys
sys.argv
sys.exit(code)
sys.stdin
sys.stdout
sys.stderr
```

```rust
// Rust
use std::env;
use std::process;
use std::io::{stdin, stdout, stderr};

env::args()
process::exit(code)
stdin()
stdout()
stderr()
```

#### 2.1.2 `json` Module

```python
# Python
import json
data = json.loads(text)
text = json.dumps(obj)
```

```rust
// Rust
use serde_json;
let data: serde_json::Value = serde_json::from_str(&text)?;
let text = serde_json::to_string(&obj)?;
```

#### 2.1.3 `math` Module

```python
# Python
import math
math.sqrt(x)
math.pow(x, y)
math.floor(x)
math.ceil(x)
math.sin(x)
math.cos(x)
math.pi
math.e
```

```rust
// Rust
// No import needed for f64 methods
x.sqrt()
x.powf(y)
x.floor()
x.ceil()
x.sin()
x.cos()
std::f64::consts::PI
std::f64::consts::E
```

#### 2.1.4 `os` Module

```python
# Python
import os
os.environ.get("VAR")
os.getcwd()
os.path.exists(path)
os.listdir(path)
```

```rust
// Rust
use std::env;
use std::fs;
use std::path::Path;

env::var("VAR").ok()
env::current_dir()?
Path::new(path).exists()
fs::read_dir(path)?
```

#### 2.1.5 `re` Module

```python
# Python
import re
match = re.match(pattern, text)
matches = re.findall(pattern, text)
result = re.sub(pattern, repl, text)
```

```rust
// Rust
use regex::Regex;
let re = Regex::new(pattern)?;
let caps = re.captures(text);
let matches: Vec<_> = re.find_iter(text).collect();
let result = re.replace_all(text, repl);
```

#### 2.1.6 `random` Module

```python
# Python
import random
random.randint(a, b)
random.random()
random.choice(seq)
random.shuffle(seq)
```

```rust
// Rust
use rand::Rng;
let mut rng = rand::thread_rng();
rng.gen_range(a..=b)
rng.gen::<f64>()
seq.choose(&mut rng)
seq.shuffle(&mut rng)
```

#### 2.1.7 `datetime` Module

```python
# Python
from datetime import datetime, timedelta
now = datetime.now()
dt = datetime.fromisoformat(s)
delta = timedelta(days=1)
```

```rust
// Rust
use chrono::{DateTime, Local, Duration};
let now = Local::now();
let dt = DateTime::parse_from_rfc3339(s)?;
let delta = Duration::days(1);
```

#### 2.1.8 `pathlib` Module

```python
# Python
from pathlib import Path
p = Path("dir/file.txt")
p.exists()
p.is_file()
p.read_text()
p.parent
p.name
```

```rust
// Rust
use std::path::PathBuf;
use std::fs;
let p = PathBuf::from("dir/file.txt");
p.exists()
p.is_file()
fs::read_to_string(&p)?
p.parent()
p.file_name()
```

#### 2.1.9 `hashlib` Module

```python
# Python
import hashlib
h = hashlib.sha256()
h.update(data)
digest = h.hexdigest()
```

```rust
// Rust
use sha2::{Sha256, Digest};
let mut h = Sha256::new();
h.update(data);
let digest = format!("{:x}", h.finalize());
```

#### 2.1.10 `collections` Module

```python
# Python
from collections import deque, Counter, defaultdict
q = deque()
q.append(item)
q.popleft()
c = Counter(items)
d = defaultdict(list)
```

```rust
// Rust
use std::collections::{VecDeque, HashMap};
let mut q = VecDeque::new();
q.push_back(item);
q.pop_front()
// Counter: manual implementation with HashMap
// defaultdict: use entry API
```

## 3. NumPy Array Basics

### 3.1 Core Operations

```python
# Python
import numpy as np
arr = np.array([1, 2, 3])
zeros = np.zeros(10)
ones = np.ones(10)
s = np.sum(arr)
m = np.mean(arr)
```

```rust
// Rust (using Vec for simplicity)
let arr = vec![1.0, 2.0, 3.0];
let zeros = vec![0.0; 10];
let ones = vec![1.0; 10];
let s: f64 = arr.iter().sum();
let m = s / arr.len() as f64;

// Or with ndarray crate:
use ndarray::Array1;
let arr = Array1::from_vec(vec![1.0, 2.0, 3.0]);
let zeros = Array1::zeros(10);
let ones = Array1::ones(10);
let s = arr.sum();
let m = arr.mean().unwrap();
```

## 4. Sklearn train_test_split

```python
# Python
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
```

```rust
// Rust (manual implementation)
fn train_test_split<T: Clone>(
    data: &[T],
    test_size: f64,
) -> (Vec<T>, Vec<T>) {
    let split_idx = ((1.0 - test_size) * data.len() as f64) as usize;
    let train = data[..split_idx].to_vec();
    let test = data[split_idx..].to_vec();
    (train, test)
}
```

## 5. Error Handling for Unmapped Modules

When depyler encounters an unmapped module, it should emit a helpful error:

```
error[DEPYLER-0501]: Unsupported module 'zipfile'
  --> script.py:3:1
   |
3  | import zipfile
   | ^^^^^^^^^^^^^^
   |
   = help: The 'zipfile' module is not yet supported for transpilation.
   = hint: Consider using the 'zip' crate in Rust directly.
   = see: https://docs.rs/zip/latest/zip/
```

## 6. Configuration

### 6.1 Proposed depyler.toml

```toml
[module_mappings]
# Override default mappings
"custom_module" = { crate = "custom-crate", features = ["feature1"] }

[unsupported_modules]
# Modules to skip (stub generation)
skip = ["unittest", "doctest", "pdb"]

[feature_flags]
numpy = true      # Enable numpy->ndarray mapping
sklearn = false   # Disable sklearn mapping
pytorch = false   # Disable pytorch mapping
```

## 7. Acceptance Criteria

1. ✅ Document all stdlib modules used in examples (this document)
2. ⬜ Implement top 10 stdlib modules (depyler enhancement)
3. ⬜ Add numpy array basics (depyler enhancement)
4. ⬜ Add sklearn train_test_split (depyler enhancement)
5. ⬜ Emit helpful error for unmapped modules (depyler enhancement)

## 8. Related Issues

- Issue #4: Examples needed to reach 100% depyler compilation rate
- Issue #5: Module mapping coverage (this specification addresses)
- DEPYLER-0424: zipfile module tracking
- DEPYLER-0606, DEPYLER-0607: Type inference improvements
