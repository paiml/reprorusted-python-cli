"""Tests for num_fft_cli.py"""

import math

from num_fft_cli import (
    Complex,
    convolution_fft,
    dft,
    exp_j,
    fft,
    find_dominant_frequency,
    frequency_bins,
    generate_signal,
    ifft,
    magnitude_spectrum,
    power_spectrum,
    simulate_fft,
)


class TestComplex:
    def test_create(self):
        c = Complex(3, 4)
        assert c.real == 3
        assert c.imag == 4

    def test_add(self):
        c1 = Complex(1, 2)
        c2 = Complex(3, 4)
        result = c1 + c2
        assert result.real == 4
        assert result.imag == 6

    def test_sub(self):
        c1 = Complex(5, 6)
        c2 = Complex(1, 2)
        result = c1 - c2
        assert result.real == 4
        assert result.imag == 4

    def test_mul(self):
        c1 = Complex(1, 2)
        c2 = Complex(3, 4)
        result = c1 * c2
        assert result.real == -5  # 1*3 - 2*4
        assert result.imag == 10  # 1*4 + 2*3

    def test_div(self):
        c = Complex(4, 6)
        result = c / 2
        assert result.real == 2
        assert result.imag == 3

    def test_magnitude(self):
        c = Complex(3, 4)
        assert c.magnitude() == 5

    def test_phase(self):
        c = Complex(1, 1)
        assert abs(c.phase() - math.pi / 4) < 1e-10

    def test_conjugate(self):
        c = Complex(3, 4)
        conj = c.conjugate()
        assert conj.real == 3
        assert conj.imag == -4


class TestExpJ:
    def test_zero(self):
        c = exp_j(0)
        assert abs(c.real - 1) < 1e-10
        assert abs(c.imag) < 1e-10

    def test_pi_over_2(self):
        c = exp_j(math.pi / 2)
        assert abs(c.real) < 1e-10
        assert abs(c.imag - 1) < 1e-10

    def test_pi(self):
        c = exp_j(math.pi)
        assert abs(c.real - (-1)) < 1e-10
        assert abs(c.imag) < 1e-10


class TestFFT:
    def test_single_element(self):
        result = fft([Complex(5)])
        assert len(result) == 1
        assert result[0].real == 5

    def test_two_elements(self):
        result = fft([Complex(1), Complex(2)])
        assert len(result) == 2
        assert abs(result[0].real - 3) < 1e-10  # DC component
        assert abs(result[1].real - (-1)) < 1e-10

    def test_power_of_two(self):
        signal = [Complex(i) for i in range(8)]
        result = fft(signal)
        assert len(result) == 8

    def test_dc_component(self):
        signal = [Complex(1)] * 4
        result = fft(signal)
        assert abs(result[0].real - 4) < 1e-10
        for i in range(1, 4):
            assert result[i].magnitude() < 1e-10


class TestIFFT:
    def test_round_trip(self):
        original = [Complex(1), Complex(2), Complex(3), Complex(4)]
        spectrum = fft(original)
        recovered = ifft(spectrum)
        for orig, rec in zip(original, recovered, strict=False):
            assert abs(orig.real - rec.real) < 1e-10
            assert abs(orig.imag - rec.imag) < 1e-10

    def test_round_trip_8(self):
        original = [Complex(i * 0.5) for i in range(8)]
        spectrum = fft(original)
        recovered = ifft(spectrum)
        for orig, rec in zip(original, recovered, strict=False):
            assert abs(orig.real - rec.real) < 1e-10


class TestDFT:
    def test_matches_fft(self):
        signal = [Complex(1), Complex(2), Complex(3), Complex(4)]
        fft_result = fft(signal)
        dft_result = dft(signal)
        for f, d in zip(fft_result, dft_result, strict=False):
            assert abs(f.real - d.real) < 1e-10
            assert abs(f.imag - d.imag) < 1e-10


class TestMagnitudeSpectrum:
    def test_basic(self):
        signal = [Complex(1), Complex(0), Complex(0), Complex(0)]
        spectrum = fft(signal)
        mags = magnitude_spectrum(spectrum)
        assert all(abs(m - 1) < 1e-10 for m in mags)


class TestPowerSpectrum:
    def test_basic(self):
        signal = [Complex(1), Complex(0), Complex(0), Complex(0)]
        spectrum = fft(signal)
        power = power_spectrum(spectrum)
        assert all(abs(p - 1) < 1e-10 for p in power)


class TestFrequencyBins:
    def test_basic(self):
        bins = frequency_bins(8, 100.0)
        assert len(bins) == 8
        assert bins[0] == 0.0
        assert bins[1] == 12.5


class TestGenerateSignal:
    def test_single_frequency(self):
        signal = generate_signal([10.0], [1.0], [0.0], 100, 100.0)
        assert len(signal) == 100
        assert abs(signal[0].real - 1.0) < 1e-10  # cos(0) = 1

    def test_dc_signal(self):
        signal = generate_signal([0.0], [5.0], [0.0], 10, 100.0)
        for s in signal:
            assert abs(s.real - 5.0) < 1e-10


class TestFindDominantFrequency:
    def test_single_tone(self):
        signal = generate_signal([25.0], [1.0], [0.0], 128, 128.0)
        spectrum = fft(signal)
        freq, mag = find_dominant_frequency(spectrum, 128.0)
        assert abs(freq - 25.0) < 1.0


class TestConvolutionFFT:
    def test_basic(self):
        a = [Complex(1), Complex(2), Complex(3)]
        b = [Complex(1), Complex(1)]
        result = convolution_fft(a, b)
        expected = [1, 3, 5, 3]  # [1, 2, 3] * [1, 1]
        for r, e in zip(result, expected, strict=False):
            assert abs(r.real - e) < 1e-10


class TestSimulateFFT:
    def test_fft(self):
        result = simulate_fft(["fft:1,0,0,0"])
        assert "1.00" in result[0]

    def test_ifft(self):
        result = simulate_fft(["ifft:1,2,3,4"])
        # Should recover original values
        assert "1.00" in result[0]

    def test_dominant(self):
        result = simulate_fft(["dominant:"])
        assert "freq=" in result[0]
