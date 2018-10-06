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
    print "constructing Laplacian pyramid"
    pyr = stft_laplacian_pyramid(sp)
    print "amplifying components of Laplacian pyramid"
    passband = [0.5, 1.0]
    fs = 44100 / step
    gain = 10.0
    amplified_pyr = amplify_pyramid(pyr, passband=passband, fs=fs, gain=gain)
    print "resynthesizing spectrogram from amplified Laplacian pyramid"
    pyramid_resynth = resynthesize(amplified_pyr.sum(axis=-1))
    path_out = path + "_aug.wav"
    wavfile.write(path_out, int(2 * nyq), pyramid_resynth)
    return path_out



def main():
    path = "hi.wav"
    audio = AudioMan()
    audio.record_audio(path)
    path_out = audio_mag(path)
    audio.play_audio(path_out)

