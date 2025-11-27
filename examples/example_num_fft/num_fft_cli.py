"""Fast Fourier Transform CLI.

Demonstrates FFT for signal processing.
"""

import math
import sys
from dataclasses import dataclass


@dataclass
class Complex:
    """Complex number."""

    real: float
    imag: float = 0.0

    def __add__(self, other: "Complex") -> "Complex":
        return Complex(self.real + other.real, self.imag + other.imag)

    def __sub__(self, other: "Complex") -> "Complex":
        return Complex(self.real - other.real, self.imag - other.imag)

    def __mul__(self, other: "Complex") -> "Complex":
        return Complex(
            self.real * other.real - self.imag * other.imag,
            self.real * other.imag + self.imag * other.real,
        )

    def __truediv__(self, other: float) -> "Complex":
        return Complex(self.real / other, self.imag / other)

    def magnitude(self) -> float:
        return math.sqrt(self.real**2 + self.imag**2)

    def phase(self) -> float:
        return math.atan2(self.imag, self.real)

    def conjugate(self) -> "Complex":
        return Complex(self.real, -self.imag)

    def __repr__(self) -> str:
        if self.imag >= 0:
            return f"{self.real:.4f}+{self.imag:.4f}j"
        return f"{self.real:.4f}{self.imag:.4f}j"


def exp_j(theta: float) -> Complex:
    """e^(j*theta) = cos(theta) + j*sin(theta)."""
    return Complex(math.cos(theta), math.sin(theta))


def fft(x: list[Complex]) -> list[Complex]:
    """Cooley-Tukey FFT (radix-2)."""
    n = len(x)
    if n <= 1:
        return x[:]

    # Pad to power of 2
    if n & (n - 1) != 0:
        next_pow2 = 1 << (n - 1).bit_length()
        x = x + [Complex(0, 0)] * (next_pow2 - n)
        n = next_pow2

    # Bit-reversal permutation
    bits = (n - 1).bit_length()
    result = [Complex(0, 0)] * n
    for i in range(n):
        rev = int(bin(i)[2:].zfill(bits)[::-1], 2)
        result[rev] = x[i]

    # Iterative FFT
    length = 2
    while length <= n:
        half = length // 2
        w_n = exp_j(-2 * math.pi / length)
        for i in range(0, n, length):
            w = Complex(1, 0)
            for j in range(half):
                u = result[i + j]
                t = w * result[i + j + half]
                result[i + j] = u + t
                result[i + j + half] = u - t
                w = w * w_n
        length *= 2

    return result


def ifft(x: list[Complex]) -> list[Complex]:
    """Inverse FFT."""
    n = len(x)
    # Conjugate input
    conj = [c.conjugate() for c in x]
    # Forward FFT
    result = fft(conj)
    # Conjugate and scale
    return [c.conjugate() / n for c in result]


def dft(x: list[Complex]) -> list[Complex]:
    """Direct DFT (O(n^2), for reference)."""
    n = len(x)
    result = []
    for k in range(n):
        total = Complex(0, 0)
        for j in range(n):
            angle = -2 * math.pi * k * j / n
            total = total + x[j] * exp_j(angle)
        result.append(total)
    return result


def magnitude_spectrum(x: list[Complex]) -> list[float]:
    """Get magnitude spectrum from FFT result."""
    return [c.magnitude() for c in x]


def phase_spectrum(x: list[Complex]) -> list[float]:
    """Get phase spectrum from FFT result."""
    return [c.phase() for c in x]


def power_spectrum(x: list[Complex]) -> list[float]:
    """Get power spectrum (magnitude squared)."""
    return [c.magnitude() ** 2 for c in x]


def frequency_bins(n: int, sample_rate: float) -> list[float]:
    """Get frequency bin centers."""
    return [k * sample_rate / n for k in range(n)]


def generate_signal(
    frequencies: list[float],
    amplitudes: list[float],
    phases: list[float],
    n_samples: int,
    sample_rate: float,
) -> list[Complex]:
    """Generate signal from frequency components."""
    signal = [Complex(0, 0)] * n_samples
    for i in range(n_samples):
        t = i / sample_rate
        val = 0.0
        for freq, amp, phase in zip(frequencies, amplitudes, phases, strict=False):
            val += amp * math.cos(2 * math.pi * freq * t + phase)
        signal[i] = Complex(val)
    return signal


def find_dominant_frequency(spectrum: list[Complex], sample_rate: float) -> tuple[float, float]:
    """Find dominant frequency and its magnitude."""
    n = len(spectrum)
    magnitudes = magnitude_spectrum(spectrum[: n // 2])  # Only positive frequencies
    max_idx = max(range(len(magnitudes)), key=lambda i: magnitudes[i])
    freq = max_idx * sample_rate / n
    return freq, magnitudes[max_idx]


def convolution_fft(a: list[Complex], b: list[Complex]) -> list[Complex]:
    """Convolution using FFT."""
    n = len(a) + len(b) - 1
    next_pow2 = 1 << (n - 1).bit_length()

    a_padded = a + [Complex(0)] * (next_pow2 - len(a))
    b_padded = b + [Complex(0)] * (next_pow2 - len(b))

    fft_a = fft(a_padded)
    fft_b = fft(b_padded)

    product = [fa * fb for fa, fb in zip(fft_a, fft_b, strict=False)]
    result = ifft(product)

    return result[:n]


def simulate_fft(operations: list[str]) -> list[str]:
    """Simulate FFT operations."""
    results: list[str] = []

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "fft":
            values = [float(x) for x in parts[1].split(",")]
            signal = [Complex(v) for v in values]
            spectrum = fft(signal)
            mags = [f"{c.magnitude():.2f}" for c in spectrum]
            results.append(str(mags))
        elif cmd == "ifft":
            values = [float(x) for x in parts[1].split(",")]
            signal = [Complex(v) for v in values]
            spectrum = fft(signal)
            recovered = ifft(spectrum)
            reals = [f"{c.real:.2f}" for c in recovered]
            results.append(str(reals))
        elif cmd == "dominant":
            signal = generate_signal([10.0], [1.0], [0.0], 64, 100.0)
            spectrum = fft(signal)
            freq, mag = find_dominant_frequency(spectrum, 100.0)
            results.append(f"freq={freq:.1f}")

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: num_fft_cli.py <command>")
        return 1

    cmd = sys.argv[1]

    if cmd == "demo":
        # Generate signal with 10 Hz and 25 Hz components
        signal = generate_signal([10.0, 25.0], [1.0, 0.5], [0.0, 0.0], 128, 100.0)
        spectrum = fft(signal)
        freq, mag = find_dominant_frequency(spectrum, 100.0)
        print(f"Dominant frequency: {freq} Hz (magnitude: {mag:.2f})")

        # Round-trip test
        recovered = ifft(spectrum)
        print(f"First 5 original: {[f'{s.real:.3f}' for s in signal[:5]]}")
        print(f"First 5 recovered: {[f'{r.real:.3f}' for r in recovered[:5]]}")
    else:
        print("Unknown command")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
