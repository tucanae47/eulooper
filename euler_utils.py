#@title
import numpy as np
from scipy.io import wavfile
from scipy.signal import firwin, filtfilt, hamming, resample

default_nyquist = 22050.0


def read_wav(path):
    """Read samples from the 0th channel of a WAV file specified by
    *path*."""
    (fs, signal) = wavfile.read(path)
    nyq = fs / 2.0
    # For expediency, just pull one channel
    if signal.ndim > 1:
        signal = signal[:, 0]
    return (nyq, signal)


def _num_windows(length, window, step):
    return max(0, int((length - window + step) / step))


def window_slice_iterator(length, window, step):
    """Generate slices into a 1-dimensional array of specified *length*
    with the specified *window* size and *step* size.

    Yields slice objects of length *window*. Any remainder at the end is
    unceremoniously truncated.
    """
    num_windows = _num_windows(length, window, step)
    for i in xrange(num_windows):
        start = step * i
        end = start + window
        yield slice(start, end)


def stft(signal, window=1024, step=None, n=None):
    """Compute the short-time Fourier transform on a 1-dimensional array
    *signal*, with the specified *window* size, *step* size, and
    *n*-resolution FFT.

    This function returns a 2-dimensional array of complex floats. The
    0th dimension is time (window steps) and the 1th dimension is
    frequency.
    """
    length = signal.size
    if step is None:
        step = window / 2
    if n is None:
        n = window
    if signal.ndim != 1:
        raise ValueError("signal must be a 1-dimensional array")
    
    num_windows = _num_windows(length, window, step)
    print num_windows
    out = np.zeros((num_windows, n), dtype=np.complex64)
    taper = hamming(window)
    for (i, s) in enumerate(window_slice_iterator(length, window, step)):
        out[i, :] = np.fft.fft(signal[s] * taper, n)
    return out

def stft_laplacian_pyramid(spectrogram, levels=None):
    """For each window of the spectrogram, construct laplacian pyramid
    on the real and imaginary components of the FFT.
    """
    (num_windows, num_freqs) = spectrogram.shape
    if levels is None:
        levels = int(np.log2(num_freqs))
    # (num_windows, num_frequencies, levels)
    pyr = np.zeros(spectrogram.shape + (levels,), dtype=np.complex)
    for i in xrange(num_windows):
        real_pyr = list(laplacian_pyramid(np.real(spectrogram[i, :]), levels=levels))
        imag_pyr = list(laplacian_pyramid(np.imag(spectrogram[i, :]), levels=levels))
        for j in xrange(levels):
            pyr[i, :, j] = real_pyr[j] + 1.0j * imag_pyr[j]
    return pyr

def laplacian_pyramid(arr, levels=None):
    if arr.ndim != 1:
        raise ValueError("arr must be 1-dimensional")
    if levels is None:
        levels = int(np.log2(arr.size))
    tap = np.array([1.0, 4.0, 6.0, 4.0, 1.0]) / 16.0
    tap_fft = np.fft.fft(tap, arr.size)
    for i in xrange(levels):
        smoothed = np.real(np.fft.ifft(np.fft.fft(arr) * tap_fft))
        band = arr - smoothed
        yield band
        arr = smoothed

def amplify_pyramid(pyr, passband, fs, gain=5.0):
    tap = firwin(100, passband, nyq=(fs / 2.0), pass_zero=False)
    (_, num_freqs, levels) = pyr.shape
    amplified_pyr = np.copy(pyr)
    for i in xrange(num_freqs):
        for j in xrange(levels):
            amplitude = gain * filtfilt(tap, [1.0], np.abs(pyr[:, i, j]))
            theta = np.angle(pyr[:, i, j])
            amplified_pyr[:, i, j] += amplitude * np.exp(1.0j * theta)
    return amplified_pyr

def resynthesize(spectrogram, window=1024, step=None, n=None):
    """Compute the short-time Fourier transform on a 1-dimensional array
    *signal*, with the specified *window* size, *step* size, and
    *n*-resolution FFT.

    This function returns a 2-dimensional array of complex floats. The
    0th dimension is time (window steps) and the 1th dimension is
    frequency.
    """
    if step is None:
        step = window / 2
    if n is None:
        n = window
    if spectrogram.ndim != 2:
        raise ValueError("spectrogram must be a 2-dimensional array")
    (num_windows, num_freqs) = spectrogram.shape
    length = step * (num_windows - 1) + window
    signal = np.zeros((length,))
    for i in xrange(num_windows):
        snippet = np.real(np.fft.ifft(spectrogram[i, :], window))
        signal[(step * i):(step * i + window)] += snippet
    signal = signal[window:]
    ceiling = np.max(np.abs(signal))
    signal = signal / ceiling * 0.9 * 0x8000
    signal = signal.astype(np.int16)
    return signal

