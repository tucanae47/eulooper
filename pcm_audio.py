import pyaudio
import wave

CHUNK = 2048
FORMAT = pyaudio.paInt16
CHANNELS = 8
RATE = 96000
RECORD_SECONDS = 2


class AudioMan:
    def __init__(self):
        self.p = pyaudio.PyAudio()

    def play_audio(self,path):
        def callback(in_data, frame_count, time_info, status):
            data = wf.readframes(frame_count)
            return (data, pyaudio.paContinue)

        wf = wave.open(path, 'rb')
        stream = self.p.open(format=self.p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True,
                        stream_callback=callback)
        stream.start_stream()
        while stream.is_active():
            time.sleep(0.1)

        stream.stop_stream()
        stream.close()
        wf.close()
        self.p.terminate()


    def record_audio(self, path, secs= RECORD_SECONDS):
        stream = self.p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        print("* recording")
        frames = []
        for i in range(0, int(RATE / CHUNK * secs)):
            data = stream.read(CHUNK)
            frames.append(data)
        print("* done recording")
        stream.stop_stream()
        stream.close()
        self.p.terminate()
        wf = wave.open(path, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
