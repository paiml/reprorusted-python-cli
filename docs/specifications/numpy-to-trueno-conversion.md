# NumPy to Trueno Conversion Specification

> **Trueno** ("Thunder" in Spanish) is a high-performance SIMD-accelerated compute library for Rust that provides NumPy-like operations with automatic backend dispatch (SSE2/AVX/AVX2/AVX-512/NEON/WASM/GPU).

## Overview

This specification maps NumPy operations to Trueno equivalents for Python-to-Rust transpilation via **depyler**. Each mapping includes:
- Python (NumPy) syntax
- Rust (Trueno) equivalent
- Performance characteristics
- Example CLI implementations

---

## Vector Operations

### Construction

| NumPy | Trueno | Notes |
|-------|--------|-------|
| `np.array([1, 2, 3])` | `Vector::from_slice(&[1.0, 2.0, 3.0])` | Auto-selects best SIMD backend |
| `np.array(list)` | `Vector::from_vec(data)` | Zero-copy ownership transfer |
| `np.zeros(n)` | `Vector::from_vec(vec![0.0; n])` | Zero-initialized |
| `np.ones(n)` | `Vector::from_vec(vec![1.0; n])` | One-initialized |
| `len(arr)` | `v.len()` | Vector length |
| `arr.tolist()` | `v.as_slice().to_vec()` | Convert to Vec |

### Element-Wise Binary Operations

| NumPy | Trueno | Speedup | Notes |
|-------|--------|---------|-------|
| `a + b` | `a.add(&b)?` | 1.0-1.2x | Memory-bound |
| `a - b` | `a.sub(&b)?` | 1.0-1.2x | Memory-bound |
| `a * b` | `a.mul(&b)?` | 1.0-1.2x | Hadamard product |
| `a / b` | `a.div(&b)?` | 1.0-1.2x | Element-wise division |
| `np.minimum(a, b)` | `a.minimum(&b)?` | 1.0-1.2x | Element-wise min |
| `np.maximum(a, b)` | `a.maximum(&b)?` | 1.0-1.2x | Element-wise max |

### Scalar Operations

| NumPy | Trueno | Notes |
|-------|--------|-------|
| `a * 5.0` | `a.scale(5.0)?` | Scalar multiplication |
| `np.clip(a, lo, hi)` | `a.clamp(lo, hi)?` | Constrain to range |
| `a * t + b * (1-t)` | `a.lerp(&b, t)?` | Linear interpolation |
| `a * b + c` | `a.fma(&b, &c)?` | Fused multiply-add (hardware FMA) |

### Reductions (Compute-Bound - Massive Speedups!)

| NumPy | Trueno | Speedup | Notes |
|-------|--------|---------|-------|
| `np.sum(a)` | `a.sum()?` | **315%** | Basic sum |
| `np.sum(a)` (stable) | `a.sum_kahan()?` | **315%** | Numerically stable |
| `np.max(a)` | `a.max()?` | **348%** | Maximum value |
| `np.min(a)` | `a.min()?` | **340%** | Minimum value |
| `np.argmax(a)` | `a.argmax()?` | - | Index of max |
| `np.argmin(a)` | `a.argmin()?` | - | Index of min |
| `np.sum(a**2)` | `a.sum_of_squares()?` | - | Sum of squares |
| `np.dot(a, b)` | `a.dot(&b)?` | **17x** (AVX-512) | Dot product |

### Vector Norms

| NumPy | Trueno | Formula | Use Case |
|-------|--------|---------|----------|
| `np.linalg.norm(a)` | `a.norm_l2()?` | √(Σaᵢ²) | Euclidean distance |
| `np.linalg.norm(a, ord=1)` | `a.norm_l1()?` | Σ\|aᵢ\| | L1 regularization |
| `np.linalg.norm(a, ord=np.inf)` | `a.norm_linf()?` | max(\|aᵢ\|) | Optimization |
| `a / np.linalg.norm(a)` | `a.normalize()?` | Unit vector | Feature normalization |

### Statistical Operations

| NumPy | Trueno | Notes |
|-------|--------|-------|
| `np.mean(a)` | `a.mean()?` | Arithmetic average |
| `np.var(a)` | `a.variance()?` | Population variance |
| `np.std(a)` | `a.stddev()?` | Standard deviation |
| `np.cov(a, b)` | `a.covariance(&b)?` | Covariance |
| `np.corrcoef(a, b)[0,1]` | `a.correlation(&b)?` | Pearson correlation |

### Preprocessing & Normalization

| NumPy | Trueno | Formula | Use Case |
|-------|--------|---------|----------|
| `(a - mean) / std` | `a.zscore()?` | Z-score | Standardization |
| `(a - min) / (max - min)` | `a.minmax_normalize()?` | Min-max | Scale to [0,1] |

---

## Mathematical Functions

### Element-Wise Math

| NumPy | Trueno | Notes |
|-------|--------|-------|
| `np.abs(a)` | `a.abs()?` | Absolute value |
| `np.sqrt(a)` | `a.sqrt()?` | Square root |
| `1 / a` | `a.recip()?` | Reciprocal |
| `a ** n` | `a.pow(n)?` | Power |
| `np.exp(a)` | `a.exp()?` | Exponential |
| `np.log(a)` | `a.ln()?` | Natural log |
| `np.log2(a)` | `a.log2()?` | Log base 2 |
| `np.log10(a)` | `a.log10()?` | Log base 10 |

### Trigonometric Functions

| NumPy | Trueno | Use Case |
|-------|--------|----------|
| `np.sin(a)` | `a.sin()?` | Signal processing |
| `np.cos(a)` | `a.cos()?` | Phase calculation |
| `np.tan(a)` | `a.tan()?` | Tangent |
| `np.arcsin(a)` | `a.asin()?` | Inverse sine |
| `np.arccos(a)` | `a.acos()?` | Inverse cosine |
| `np.arctan(a)` | `a.atan()?` | Angle calculation |

### Hyperbolic Functions

| NumPy | Trueno |
|-------|--------|
| `np.sinh(a)` | `a.sinh()?` |
| `np.cosh(a)` | `a.cosh()?` |
| `np.tanh(a)` | `a.tanh()?` |
| `np.arcsinh(a)` | `a.asinh()?` |
| `np.arccosh(a)` | `a.acosh()?` |
| `np.arctanh(a)` | `a.atanh()?` |

### Rounding Functions

| NumPy | Trueno |
|-------|--------|
| `np.floor(a)` | `a.floor()?` |
| `np.ceil(a)` | `a.ceil()?` |
| `np.round(a)` | `a.round()?` |
| `np.trunc(a)` | `a.trunc()?` |
| `a % 1.0` | `a.fract()?` |
| `np.sign(a)` | `a.signum()?` |
| `-a` | `a.neg()?` |

---

## Activation Functions (Neural Networks)

| NumPy/PyTorch | Trueno | Formula | Use Case |
|---------------|--------|---------|----------|
| `np.maximum(0, a)` | `a.relu()?` | max(0, x) | CNN, ResNet |
| `torch.nn.LeakyReLU(0.01)` | `a.leaky_relu(0.01)?` | x if x>0, αx else | GANs |
| `torch.nn.ELU()` | `a.elu(1.0)?` | x if x>0, α(eˣ-1) else | Deep networks |
| `scipy.special.expit()` | `a.sigmoid()?` | 1/(1+e⁻ˣ) | Binary classification |
| `np.tanh(a)` | `a.tanh()?` | (eˣ-e⁻ˣ)/(eˣ+e⁻ˣ) | LSTM/GRU |
| `torch.nn.GELU()` | `a.gelu()?` | GELU formula | **Transformers (BERT, GPT)** |
| `torch.nn.SiLU()` | `a.swish()?` | x·σ(x) | EfficientNet |
| `torch.nn.Softmax()` | `a.softmax()?` | eˣⁱ/Σeˣ | Classification |
| `torch.nn.LogSoftmax()` | `a.log_softmax()?` | Numerically stable | Cross-entropy |
| `torch.nn.Hardswish()` | `a.hardswish()?` | MobileNet v2 | Mobile inference |
| `torch.nn.Mish()` | `a.mish()?` | Self-regularizing | Advanced networks |
| `torch.nn.SELU()` | `a.selu()?` | Self-normalizing | SNN |

---

## Matrix Operations

### Construction

| NumPy | Trueno | Notes |
|-------|--------|-------|
| `np.zeros((m, n))` | `Matrix::zeros(m, n)` | Zero matrix |
| `np.eye(n)` | `Matrix::identity(n)` | Identity matrix |
| `np.array([[...]])` | `Matrix::from_vec(m, n, data)?` | Row-major |
| `A.shape` | `m.shape()` → `(rows, cols)` | Dimensions |
| `A[i, j]` | `m.get(i, j)` | Element access |

### Matrix Operations

| NumPy | Trueno | Performance | Notes |
|-------|--------|-------------|-------|
| `A @ B` | `A.matmul(&B)?` | 2-10x vs NumPy | Matrix multiply |
| `A.T` | `A.transpose()?` | Cache-optimized | Transpose |
| `A @ v` | `A.matvec(&v)?` | SIMD dot products | Matrix-vector |
| `v @ A` | `Matrix::vecmat(&v, &A)?` | SIMD optimized | Vector-matrix |

### Convolution (Image Processing)

| NumPy/SciPy | Trueno | GPU Threshold |
|-------------|--------|---------------|
| `scipy.signal.convolve2d()` | `image.convolve2d(&kernel)?` | >10K output elements |

---

## Error Handling

```rust
use trueno::{Vector, TruenoError};

match a.add(&b) {
    Ok(result) => { /* use result */ }
    Err(TruenoError::SizeMismatch { expected, actual }) => { /* handle */ }
    Err(TruenoError::DivisionByZero) => { /* handle */ }
    Err(TruenoError::EmptyVector) => { /* handle */ }
    Err(e) => { /* other errors */ }
}
```

---

## Backend System

### Available Backends

| Backend | Platform | Width | Best For |
|---------|----------|-------|----------|
| `Scalar` | All | 1 | Fallback |
| `SSE2` | x86_64 | 128-bit | Baseline |
| `AVX` | x86_64 | 256-bit | Modern Intel/AMD |
| `AVX2` | x86_64 | 256-bit + FMA | **Memory-bound ops** |
| `AVX512` | x86_64 | 512-bit | **Compute-bound ops (17x!)** |
| `NEON` | ARM | 128-bit | Mobile/M1 |
| `WasmSIMD` | Browser | 128-bit | WebAssembly |
| `GPU` | All (wgpu) | Massive | Large matrices (≥500×500) |

### Auto-Dispatch

```rust
// Default: Auto-selects best backend
let v = Vector::from_slice(&data);

// Explicit (for testing)
let v = Vector::from_slice_with_backend(&data, Backend::AVX2);
```

---

## Performance Guidelines

### Memory-Bound Operations (Modest SIMD gains: 1-1.2x)
- `add`, `sub`, `mul`, `div`, `scale`, `abs`, `clamp`, `relu`, `sigmoid`
- **Use AVX2** (avoid AVX-512 which causes 10-33% slowdown)

### Compute-Bound Operations (Massive SIMD gains: 7-17x)
- `dot`, `max`, `min`, `argmax`, `argmin`, `norm_l1`, `norm_l2`, `matmul`
- **Use AVX-512** for maximum performance

### GPU Operations (Only for large data)
- Matrix multiply ≥500×500: **2-10x speedup**
- Convolution ≥256×256: **10-50x speedup**
- **DO NOT use GPU for vector element-wise ops** (2-65,000x SLOWER)

---

## Example Patterns

### Cosine Similarity
```python
# NumPy
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```
```rust
// Trueno
fn cosine_similarity(a: &Vector<f32>, b: &Vector<f32>) -> f32 {
    let dot = a.dot(b).unwrap();
    let mag_a = a.norm_l2().unwrap();
    let mag_b = b.norm_l2().unwrap();
    dot / (mag_a * mag_b)
}
```

### Euclidean Distance
```python
# NumPy
def euclidean_distance(a, b):
    return np.linalg.norm(a - b)
```
```rust
// Trueno
fn euclidean_distance(a: &Vector<f32>, b: &Vector<f32>) -> f32 {
    a.sub(b).unwrap().norm_l2().unwrap()
}
```

### Z-Score Normalization
```python
# NumPy
normalized = (data - np.mean(data)) / np.std(data)
```
```rust
// Trueno
let normalized = data.zscore()?;
```

### Neural Network Layer
```python
# NumPy/PyTorch
z = W @ x + b
output = gelu(z)
```
```rust
// Trueno
let z = w.matvec(&x)?;
let z_plus_b = z.add(&b)?;
let output = z_plus_b.gelu()?;
```

---

## CLI Example Template

```python
#!/usr/bin/env python3
"""NumPy Example - Vector operations CLI."""

import argparse
import numpy as np


def main():
    parser = argparse.ArgumentParser(description="Vector operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    d = subs.add_parser("dot")
    d.add_argument("a1", type=float)
    d.add_argument("a2", type=float)
    d.add_argument("a3", type=float)
    d.add_argument("b1", type=float)
    d.add_argument("b2", type=float)
    d.add_argument("b3", type=float)

    args = parser.parse_args()
    if args.cmd == "dot":
        a = np.array([args.a1, args.a2, args.a3])
        b = np.array([args.b1, args.b2, args.b3])
        print(np.dot(a, b))


if __name__ == "__main__":
    main()
```

---

## References

- [Trueno Repository](https://github.com/paiml/trueno)
- [Depyler Transpiler](https://github.com/paiml/depyler)
- [NumPy Documentation](https://numpy.org/doc/)
- [PyTorch Documentation](https://pytorch.org/docs/)
