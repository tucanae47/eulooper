import numpy as np
from scipy.io import wavfile
import scipy.signal as sig 
from scipy.signal import firwin, filtfilt, hamming
from pcm_audio import AudioMan
from euler_utils import read_wav, stft,normalize_total_power,resynthesize, amplify_pyramid,stft_laplacian_pyramid 
WAVE_OUTPUT_FILENAME = "output.wav"



window = 1024
step = window / 4


def audio_mag(path):
    (nyq,signal) = read_wav(path)
    sp = stft(signal)
    print("whitening spectrum")
    whitened = sp / np.sqrt(power)
    whitened = normalize_total_power(whitened, utils.total_power(sp))

    print("unwhitening spectrum")
    unwhitened = whitened * np.sqrt(power)
    unwhitened = normalize_total_power(unwhitened, utils.total_power(sp))

    print "resynthesizing from whitened-unwhitened spectrogram"
    resynth = resynthesize(unwhitened)
    wavfile.write("resynth.wav", int(2 * nyq), resynth)

    print "constructing Laplacian pyramid"
    pyr = stft_laplacian_pyramid(sp)

    print "amplifying components of Laplacian pyramid"
    passband = [0.5, 1.0]
    fs = 44100 / step
    gain = 10.0
    amplified_pyr = amplify_pyramid(pyr, passband=passband, fs=fs, gain=gain)
    print "resynthesizing spectrogram from amplified Laplacian pyramid"
    pyramid_resynth = resynthesize(amplified_pyr.sum(axis=-1))
    wavfile.write("hi_new.wav", int(2 * nyq), pyramid_resynth)



def main():
    path = "hi.wav"
    audio = AudioMan()
    audio.record_audio(path)
    audio_mag(path)
    audio.play_audio(path)

