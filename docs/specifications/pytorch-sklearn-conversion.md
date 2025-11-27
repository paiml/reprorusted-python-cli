# PyTorch & Scikit-Learn to Aprender Conversion Specification

> **Aprender** is a production-grade ML library for Rust providing scikit-learn-compatible estimators and PyTorch-style neural networks with reverse-mode automatic differentiation.

## Overview

This specification maps PyTorch and scikit-learn operations to Aprender equivalents for Python-to-Rust transpilation via **depyler**. Each mapping includes:
- Python (PyTorch/sklearn) syntax
- Rust (Aprender) equivalent
- Academic reference
- Example CLI implementations

---

## Academic References

The following peer-reviewed publications inform the algorithm implementations:

| # | Citation | Algorithm | DOI/Link |
|---|----------|-----------|----------|
| **[1]** | Pedregosa, F. et al. (2011). "Scikit-learn: Machine Learning in Python." *Journal of Machine Learning Research*, 12, 2825-2830. | sklearn API design | [JMLR](https://jmlr.org/papers/v12/pedregosa11a.html) |
| **[2]** | Paszke, A. et al. (2019). "PyTorch: An Imperative Style, High-Performance Deep Learning Library." *NeurIPS 2019*. | PyTorch autograd | [arXiv:1912.01703](https://arxiv.org/abs/1912.01703) |
| **[3]** | Baydin, A.G. et al. (2018). "Automatic Differentiation in Machine Learning: A Survey." *JMLR*, 18(153), 1-43. | Reverse-mode AD | [JMLR](https://jmlr.org/papers/v18/17-468.html) |
| **[4]** | Kingma, D.P. & Ba, J. (2015). "Adam: A Method for Stochastic Optimization." *ICLR 2015*. | Adam optimizer | [arXiv:1412.6980](https://arxiv.org/abs/1412.6980) |
| **[5]** | He, K. et al. (2015). "Delving Deep into Rectifiers: Surpassing Human-Level Performance on ImageNet Classification." *ICCV 2015*. | Weight initialization | [arXiv:1502.01852](https://arxiv.org/abs/1502.01852) |
| **[6]** | Ioffe, S. & Szegedy, C. (2015). "Batch Normalization: Accelerating Deep Network Training." *ICML 2015*. | BatchNorm | [arXiv:1502.03167](https://arxiv.org/abs/1502.03167) |
| **[7]** | Vaswani, A. et al. (2017). "Attention Is All You Need." *NeurIPS 2017*. | Transformer/Attention | [arXiv:1706.03762](https://arxiv.org/abs/1706.03762) |
| **[8]** | Breiman, L. (2001). "Random Forests." *Machine Learning*, 45(1), 5-32. | Random Forest | [Springer](https://doi.org/10.1023/A:1010933404324) |
| **[9]** | Lloyd, S. (1982). "Least Squares Quantization in PCM." *IEEE Transactions on Information Theory*, 28(2), 129-137. | K-Means | [IEEE](https://doi.org/10.1109/TIT.1982.1056489) |
| **[10]** | van der Maaten, L. & Hinton, G. (2008). "Visualizing Data using t-SNE." *JMLR*, 9, 2579-2605. | t-SNE | [JMLR](https://jmlr.org/papers/v9/vandermaaten08a.html) |

---

## Part 1: Scikit-Learn to Aprender

### Supervised Learning - Estimator Pattern

All sklearn estimators follow the `fit/predict/score` pattern **[1]**:

| sklearn | Aprender | Notes |
|---------|----------|-------|
| `model.fit(X, y)` | `model.fit(&x, &y)?` | Returns `Result<()>` |
| `model.predict(X)` | `model.predict(&x)` | Returns `Vector<f32>` |
| `model.score(X, y)` | `model.score(&x, &y)` | R² or accuracy |

### Linear Models

| sklearn | Aprender | Academic Ref |
|---------|----------|--------------|
| `LinearRegression()` | `LinearRegression::new()` | OLS via Cholesky |
| `Ridge(alpha=1.0)` | `Ridge::new(1.0)` | L2 regularization |
| `Lasso(alpha=1.0)` | `Lasso::new(1.0)` | L1 regularization |
| `ElasticNet(alpha=1.0, l1_ratio=0.5)` | `ElasticNet::new(1.0, 0.5)` | Combined L1/L2 |
| `LogisticRegression()` | `LogisticRegression::new()` | Gradient descent |

### Tree-Based Models **[8]**

| sklearn | Aprender | Notes |
|---------|----------|-------|
| `DecisionTreeClassifier(max_depth=5)` | `DecisionTreeClassifier::new().with_max_depth(5)` | GINI criterion |
| `DecisionTreeRegressor(max_depth=5)` | `DecisionTreeRegressor::new().with_max_depth(5)` | MSE criterion |
| `RandomForestClassifier(n_estimators=100)` | `RandomForestClassifier::new(100)` | Bootstrap aggregation |
| `RandomForestRegressor(n_estimators=100)` | `RandomForestRegressor::new(100)` | Mean prediction |
| `GradientBoostingClassifier()` | `GradientBoostingClassifier::new()` | Residual learning |

### Clustering **[9]**

| sklearn | Aprender | Notes |
|---------|----------|-------|
| `KMeans(n_clusters=3)` | `KMeans::new(3)` | Lloyd's algorithm |
| `KMeans(n_clusters=3, max_iter=300)` | `KMeans::new(3).with_max_iter(300)` | Builder pattern |
| `DBSCAN(eps=0.5, min_samples=5)` | `DBSCAN::new(0.5, 5)` | Density-based |
| `GaussianMixture(n_components=3)` | `GaussianMixture::new(3)` | EM algorithm |
| `kmeans.labels_` | `kmeans.labels()` | Cluster assignments |
| `kmeans.cluster_centers_` | `kmeans.centroids()` | Centroid locations |

### Preprocessing

| sklearn | Aprender | Notes |
|---------|----------|-------|
| `StandardScaler()` | `StandardScaler::new()` | Zero mean, unit variance |
| `scaler.fit_transform(X)` | `scaler.fit_transform(&x)?` | Combined fit+transform |
| `scaler.transform(X)` | `scaler.transform(&x)?` | Transform only |
| `MinMaxScaler()` | `MinMaxScaler::new()` | Scale to [0, 1] |

### Dimensionality Reduction **[10]**

| sklearn | Aprender | Notes |
|---------|----------|-------|
| `PCA(n_components=2)` | `PCA::new(2)` | Eigendecomposition |
| `pca.fit_transform(X)` | `pca.fit_transform(&x)?` | Project to subspace |
| `pca.explained_variance_ratio_` | `pca.explained_variance_ratio()` | Variance explained |
| `TSNE(n_components=2)` | `TSNE::new(2)` | Non-linear embedding |

### Model Selection **[1]**

| sklearn | Aprender | Notes |
|---------|----------|-------|
| `train_test_split(X, y, test_size=0.2)` | `train_test_split(n, 0.8, seed)` | Returns indices |
| `KFold(n_splits=5)` | `KFold::new(5)` | K-fold CV |
| `cross_val_score(model, X, y, cv=5)` | `cross_validate(&model, &x, &y, &kfold)?` | CV scores |

### Metrics

| sklearn | Aprender | Notes |
|---------|----------|-------|
| `accuracy_score(y_true, y_pred)` | `accuracy(&y_pred, &y_true)` | Classification |
| `precision_score(y_true, y_pred)` | `precision(&y_pred, &y_true, class)` | Per-class |
| `recall_score(y_true, y_pred)` | `recall(&y_pred, &y_true, class)` | Per-class |
| `f1_score(y_true, y_pred)` | `f1_score(&y_pred, &y_true, class)` | Harmonic mean |
| `confusion_matrix(y_true, y_pred)` | `confusion_matrix(&y_pred, &y_true)` | NxN matrix |
| `r2_score(y_true, y_pred)` | `r_squared(&y_pred, &y_true)` | Regression |
| `mean_squared_error(y_true, y_pred)` | `mse(&y_pred, &y_true)` | Regression |
| `silhouette_score(X, labels)` | `silhouette_score(&x, &labels)` | Clustering |

---

## Part 2: PyTorch to Aprender

### Tensor Operations **[2]**

| PyTorch | Aprender | Notes |
|---------|----------|-------|
| `torch.tensor([1, 2, 3])` | `Tensor::from_slice(&[1.0, 2.0, 3.0])` | Create tensor |
| `x.requires_grad_(True)` | `x.requires_grad()` | Enable gradients |
| `torch.zeros(3, 4)` | `Tensor::zeros(&[3, 4])` | Zero tensor |
| `torch.randn(3, 4)` | `Tensor::randn(&[3, 4])` | Normal random |
| `x + y` | `x.add(&y)` | Element-wise add |
| `x * y` | `x.mul(&y)` | Element-wise mul |
| `x @ y` | `x.matmul(&y)` | Matrix multiply |
| `x.sum()` | `x.sum()` | Reduce sum |
| `x.mean()` | `x.mean()` | Reduce mean |

### Automatic Differentiation **[3]**

| PyTorch | Aprender | Notes |
|---------|----------|-------|
| `loss.backward()` | `loss.backward()` | Compute gradients |
| `x.grad` | `x.grad()` | Access gradient |
| `with torch.no_grad():` | `no_grad(closure)` | Disable gradient tracking |
| `optimizer.zero_grad()` | `model.zero_grad()` | Clear gradients |

### Neural Network Layers **[5]** **[6]**

| PyTorch | Aprender | Notes |
|---------|----------|-------|
| `nn.Linear(in, out)` | `Linear::new(in_features, out_features)` | Dense layer |
| `nn.Conv2d(in, out, kernel)` | `Conv2d::new(in_ch, out_ch, kernel)` | 2D convolution |
| `nn.ReLU()` | `ReLU::new()` | ReLU activation |
| `nn.Sigmoid()` | `Sigmoid::new()` | Sigmoid activation |
| `nn.Tanh()` | `Tanh::new()` | Tanh activation |
| `nn.GELU()` | `GELU::new()` | GELU activation |
| `nn.Softmax(dim=1)` | `Softmax::new(1)` | Softmax |
| `nn.BatchNorm1d(features)` | `BatchNorm1d::new(features)` | Batch normalization |
| `nn.LayerNorm(shape)` | `LayerNorm::new(shape)` | Layer normalization |
| `nn.Dropout(p=0.5)` | `Dropout::new(0.5)` | Dropout regularization |

### Container Modules

| PyTorch | Aprender | Notes |
|---------|----------|-------|
| `nn.Sequential(layer1, layer2)` | `Sequential::new().add(layer1).add(layer2)` | Chain layers |
| `nn.ModuleList([...])` | `ModuleList::new(vec![...])` | List of modules |
| `model.parameters()` | `model.parameters()` | Get all params |
| `model(x)` / `model.forward(x)` | `model.forward(&x)` | Forward pass |

### Transformer Architecture **[7]**

| PyTorch | Aprender | Notes |
|---------|----------|-------|
| `nn.MultiheadAttention(d, nhead)` | `MultiHeadAttention::new(d_model, n_heads)` | Multi-head attention |
| `nn.TransformerEncoderLayer(d, nhead)` | `TransformerEncoderLayer::new(d, nhead)` | Encoder layer |
| `nn.TransformerDecoderLayer(d, nhead)` | `TransformerDecoderLayer::new(d, nhead)` | Decoder layer |
| `PositionalEncoding(d, max_len)` | `PositionalEncoding::new(d_model, max_len)` | Position embeddings |

### Loss Functions

| PyTorch | Aprender | Notes |
|---------|----------|-------|
| `nn.MSELoss()` | `MSELoss::new()` | Mean squared error |
| `nn.CrossEntropyLoss()` | `CrossEntropyLoss::new()` | Multi-class CE |
| `nn.BCEWithLogitsLoss()` | `BCEWithLogitsLoss::new()` | Binary CE with logits |
| `nn.L1Loss()` | `L1Loss::new()` | Mean absolute error |
| `nn.SmoothL1Loss()` | `SmoothL1Loss::new()` | Huber loss |
| `loss(pred, target)` | `loss.forward(&pred, &target)` | Compute loss |

### Optimizers **[4]**

| PyTorch | Aprender | Notes |
|---------|----------|-------|
| `optim.SGD(params, lr=0.01)` | `SGD::new(0.01)` | Stochastic GD |
| `optim.SGD(params, lr, momentum=0.9)` | `SGD::new(lr).with_momentum(0.9)` | With momentum |
| `optim.Adam(params, lr=0.001)` | `Adam::new(0.001)` | Adam optimizer |
| `optim.AdamW(params, lr, wd)` | `AdamW::new(lr).with_weight_decay(wd)` | Adam with decoupled WD |
| `optim.RMSprop(params, lr)` | `RMSprop::new(lr)` | RMSprop |
| `optimizer.step()` | `optimizer.step(&mut params, &grads)` | Update weights |

### Learning Rate Schedulers

| PyTorch | Aprender | Notes |
|---------|----------|-------|
| `StepLR(optimizer, step_size, gamma)` | `StepLR::new(step_size, gamma)` | Step decay |
| `ExponentialLR(optimizer, gamma)` | `ExponentialLR::new(gamma)` | Exponential decay |
| `CosineAnnealingLR(optimizer, T_max)` | `CosineAnnealingLR::new(t_max)` | Cosine annealing |
| `ReduceLROnPlateau(optimizer)` | `ReduceLROnPlateau::new()` | Adaptive reduction |

### Pooling Layers

| PyTorch | Aprender | Notes |
|---------|----------|-------|
| `nn.MaxPool2d(kernel)` | `MaxPool2d::new(kernel)` | Max pooling |
| `nn.AvgPool2d(kernel)` | `AvgPool2d::new(kernel)` | Average pooling |
| `nn.AdaptiveAvgPool2d((1,1))` | `GlobalAvgPool2d::new()` | Global average pool |

---

## Part 3: Planned CLI Examples

### sklearn Examples (10)

| # | Example | sklearn Feature | Aprender Equivalent |
|---|---------|-----------------|---------------------|
| 1 | `example_sklearn_linreg` | `LinearRegression` | `LinearRegression::new()` |
| 2 | `example_sklearn_logreg` | `LogisticRegression` | `LogisticRegression::new()` |
| 3 | `example_sklearn_kmeans` | `KMeans` | `KMeans::new(k)` |
| 4 | `example_sklearn_pca` | `PCA` | `PCA::new(n)` |
| 5 | `example_sklearn_dtree` | `DecisionTreeClassifier` | `DecisionTreeClassifier::new()` |
| 6 | `example_sklearn_rf` | `RandomForestClassifier` | `RandomForestClassifier::new(n)` |
| 7 | `example_sklearn_scaler` | `StandardScaler` | `StandardScaler::new()` |
| 8 | `example_sklearn_kfold` | `cross_val_score` | `cross_validate()` |
| 9 | `example_sklearn_metrics` | `accuracy_score`, `f1_score` | `accuracy()`, `f1_score()` |
| 10 | `example_sklearn_tsne` | `TSNE` | `TSNE::new(n)` |

### PyTorch Examples (10)

| # | Example | PyTorch Feature | Aprender Equivalent |
|---|---------|-----------------|---------------------|
| 1 | `example_pytorch_tensor` | `torch.tensor`, ops | `Tensor::from_slice()` |
| 2 | `example_pytorch_autograd` | `backward()`, gradients | `backward()`, `grad()` |
| 3 | `example_pytorch_linear` | `nn.Linear` | `Linear::new()` |
| 4 | `example_pytorch_sequential` | `nn.Sequential` | `Sequential::new()` |
| 5 | `example_pytorch_relu` | `nn.ReLU`, activations | `ReLU::new()` |
| 6 | `example_pytorch_conv` | `nn.Conv2d` | `Conv2d::new()` |
| 7 | `example_pytorch_batchnorm` | `nn.BatchNorm1d` | `BatchNorm1d::new()` |
| 8 | `example_pytorch_dropout` | `nn.Dropout` | `Dropout::new()` |
| 9 | `example_pytorch_adam` | `optim.Adam` | `Adam::new()` |
| 10 | `example_pytorch_mseloss` | `nn.MSELoss` | `MSELoss::new()` |

---

## Example Patterns

### sklearn Pattern: Linear Regression

```python
# Python (sklearn)
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = LinearRegression()
model.fit(X_train, y_train)
predictions = model.predict(X_test)
score = r2_score(y_test, predictions)
```

```rust
// Rust (Aprender)
use aprender::linear_model::LinearRegression;
use aprender::model_selection::train_test_split;
use aprender::metrics::r_squared;

let (train_idx, test_idx) = train_test_split(x.shape().0, 0.8, 42);
let mut model = LinearRegression::new();
model.fit(&x_train, &y_train)?;
let predictions = model.predict(&x_test);
let score = r_squared(&predictions, &y_test);
```

### PyTorch Pattern: MLP with Autograd

```python
# Python (PyTorch)
import torch
import torch.nn as nn
import torch.optim as optim

model = nn.Sequential(
    nn.Linear(784, 256),
    nn.ReLU(),
    nn.Linear(256, 10)
)
optimizer = optim.Adam(model.parameters(), lr=0.001)
loss_fn = nn.CrossEntropyLoss()

for epoch in range(100):
    optimizer.zero_grad()
    output = model(x)
    loss = loss_fn(output, y)
    loss.backward()
    optimizer.step()
```

```rust
// Rust (Aprender)
use aprender::nn::{Sequential, Linear, ReLU};
use aprender::nn::loss::CrossEntropyLoss;
use aprender::nn::optim::Adam;

let model = Sequential::new()
    .add(Linear::new(784, 256))
    .add(ReLU::new())
    .add(Linear::new(256, 10));

let mut optimizer = Adam::new(0.001);
let loss_fn = CrossEntropyLoss::new();

for _epoch in 0..100 {
    let output = model.forward(&x);
    let loss = loss_fn.forward(&output, &y);
    loss.backward();
    let grads = model.gradients();
    optimizer.step(&mut model.parameters(), &grads);
    model.zero_grad();
}
```

---

## Error Handling

Aprender uses Result-based error handling (no panics):

```rust
use aprender::{AprenderError, Result};

// All fallible operations return Result<T>
match model.fit(&x, &y) {
    Ok(()) => { /* success */ }
    Err(AprenderError::ShapeMismatch { expected, actual }) => { /* handle */ }
    Err(AprenderError::EmptyInput) => { /* handle */ }
    Err(e) => { /* other errors */ }
}
```

---

## Model Serialization

```rust
use aprender::format::{save, load, ModelType, SaveOptions};

// Save model
save(&model, ModelType::LinearRegression, "model.apr",
    SaveOptions::default().with_compression())?;

// Load model
let loaded: LinearRegression = load("model.apr", ModelType::LinearRegression)?;

// Interop with HuggingFace ecosystem
model.save_safetensors("model.safetensors")?;
```

---

## Testing & Validation

### Run All Tests
```bash
# Test all sklearn/pytorch examples
make compile-status-fast

# Benchmark Python vs Rust
make bench-scientific
```

### Current Status
- **sklearn examples**: 10/10 (Python tests passing)
- **pytorch examples**: 10/10 (Python tests passing)
- **Total tests**: 194 passing
- **depyler transpilation**: BLOCKED - depyler v3.21.0 has limitations:
  - JSON Value to primitive type coercion not working
  - Complex error handling traits missing
  - Tuple unpacking not supported
  - See depyler issue backlog for fixes needed

---

## Scientific Code Review & Validation
**Review Date:** 2025-11-27  
**Review Framework:** Toyota Way (Lean Principles) & Scientific Method

### 1. Genchi Genbutsu (Go and See) - Empirical Verification
*   **Hypothesis:** The proposed mapping 1:1 preserves algorithmic intent between Python and Rust.
*   **Observation:** The mapping correctly identifies core constructs. However, strict type adherence in Rust (e.g., `&x` borrowing) introduces cognitive overhead compared to Python's dynamic dispatch.
*   **Kaizen Opportunity:** Consider implementing `Into<Tensor>` traits for API inputs to reduce "Muda" (waste) in user code, allowing `model.fit(x, y)` instead of `model.fit(&x, &y)` where ownership transfer is acceptable **[11]**.

### 2. Poka-Yoke (Mistake Proofing) - Type Safety
*   **Analysis:** The use of `Result<T>` instead of exceptions is a strong Poka-Yoke mechanism, preventing runtime crashes common in Python (e.g., shape mismatches).
*   **Validation:** This adheres to Type Theory principles ensuring total functions where possible **[13]**.
*   **Action:** Ensure `depyler` transpiler explicitly handles Python's `None` types by mapping them to `Option<T>` to prevent null pointer exceptions, termed the "Billion Dollar Mistake" **[17]**.

### 3. Muda (Waste) - Technical Debt & Redundancy
*   **Observation:** The dual maintenance of `example_sklearn_*` and `example_pytorch_*` suites may lead to documentation drift.
*   **Proposal:** Standardize on a single "Golden Trace" verification system where one specification generates tests for both languages, reducing duplicate effort **[20]**.

### 4. Jidoka (Automation with Human Intelligence)
*   **Status:** `depyler` automates the translation.
*   **Gap:** No mention of handling dynamic Python features (e.g., list comprehensions inside model definitions).
*   **Constraint:** The system must detect and halt compilation on ambiguous dynamic typing, rather than guessing, to preserve scientific rigor **[12]**.

---

## Added Peer-Reviewed Annotations

The following references support the architectural decisions in this specification:

| # | Citation | Context | DOI/Link |
|---|----------|---------|----------|
| **[11]** | Matsakis, N. & Klock, F. (2014). "The Rust Language." *ACM SIGAda Ada Letters*, 34(3), 103-104. | Ownership & Borrowing model justifying API design. | [ACM](https://dl.acm.org/doi/10.1145/2692956.2663188) |
| **[12]** | Lattner, C. & Adve, V. (2004). "LLVM: A Compilation Framework for Lifelong Program Analysis & Transformation." *CGO 2004*. | Backend optimization principles for transpiled code. | [IEEE](https://ieeexplore.ieee.org/document/1281665) |
| **[13]** | Pierce, B. C. (2002). "Types and Programming Languages." *MIT Press*. | Theoretical foundation for type safety guarantees. | [MIT Press](https://mitpress.mit.edu/9780262162098/) |
| **[14]** | Ohno, T. (1988). "Toyota Production System: Beyond Large-Scale Production." *Productivity Press*. | Lean principles applied to API surface reduction. | [Google Books](https://books.google.com/books?id=7omgAAAAMAAJ) |
| **[15]** | Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). "Design Patterns: Elements of Reusable Object-Oriented Software." *Addison-Wesley*. | Justification for Builder Pattern in configuration. | [Pearson](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009483) |
| **[16]** | Wirth, N. (1971). "Program Development by Stepwise Refinement." *Communications of the ACM*, 14(4), 221-227. | Methodology for iterative implementation of estimators. | [ACM](https://dl.acm.org/doi/10.1145/362575.362577) |
| **[17]** | Hoare, C.A.R. (2009). "Null References: The Billion Dollar Mistake." *QCon London*. | Supporting strict `Option`/`Result` usage over nulls. | [InfoQ](https://www.infoq.com/presentations/Null-References-The-Billion-Dollar-Mistake-Tony-Hoare/) |
| **[18]** | IEEE Computer Society (2019). "IEEE Standard for Floating-Point Arithmetic." *IEEE Std 754-2019*. | Ensuring numerical consistency between Python/Rust. | [IEEE](https://ieeexplore.ieee.org/document/8766229) |
| **[19]** | Sculley, D. et al. (2015). "Hidden Technical Debt in Machine Learning Systems." *NeurIPS 2015*. | Identifying "glue code" risks in transpilation. | [NeurIPS](https://proceedings.neurips.cc/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html) |
| **[20]** | Fowler, M. (1999). "Refactoring: Improving the Design of Existing Code." *Addison-Wesley*. | Continuous improvement (Kaizen) of the codebase. | [MartinFowler](https://martinfowler.com/books/refactoring.html) |

---

## References

1. Pedregosa et al. (2011). Scikit-learn: Machine Learning in Python. JMLR 12:2825-2830.
2. Paszke et al. (2019). PyTorch: An Imperative Style, High-Performance Deep Learning Library. NeurIPS.
3. Baydin et al. (2018). Automatic Differentiation in Machine Learning: A Survey. JMLR 18(153):1-43.
4. Kingma & Ba (2015). Adam: A Method for Stochastic Optimization. ICLR.
5. He et al. (2015). Delving Deep into Rectifiers. ICCV.
6. Ioffe & Szegedy (2015). Batch Normalization. ICML.
7. Vaswani et al. (2017). Attention Is All You Need. NeurIPS.
8. Breiman (2001). Random Forests. Machine Learning 45(1):5-32.
9. Lloyd (1982). Least Squares Quantization in PCM. IEEE Trans. Info. Theory.
10. van der Maaten & Hinton (2008). Visualizing Data using t-SNE. JMLR 9:2579-2605.