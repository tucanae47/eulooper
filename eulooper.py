import numpy as np
from scipy.io import wavfile
import scipy.signal as sig 
from scipy.signal import firwin, filtfilt, hamming
from pcm_audio import AudioMan
from euler_utils import read_wav, stft, resynthesize, amplify_pyramid,stft_laplacian_pyramid 
WAVE_OUTPUT_FILENAME = "output.wav"




def audio_mag(path):
    (nyq,signal) = read_wav(path)
    print(signal)
    length = signal.size
    window = int(np.log2(length)) 
    step = window / 2
    sp = stft(signal,window)
    print "constructing Laplacian pyramid"
    pyr = stft_laplacian_pyramid(sp)
    print "amplifying components of Laplacian pyramid"
    passband = [0.6, 1.0]
    fs = length / step
    gain = 3.0
    amplified_pyr = amplify_pyramid(pyr, passband=passband, fs=fs, gain=gain)
    print "resynthesizing spectrogram from amplified Laplacian pyramid"
    pyramid_resynth = resynthesize(amplified_pyr.sum(axis=-1),window)
    path_out = "out" + path
    wavfile.write(path_out, int(2 * nyq), pyramid_resynth)
    return path_out



def main():
    path = "hi.wav"
    #audio = AudioMan()
    path_out = audio_mag(path)

if __name__ == "__main__":
    main()
