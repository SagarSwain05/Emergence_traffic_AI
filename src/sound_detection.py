# sound_detection.py
import sounddevice as sd
import numpy as np
import threading
import time
from scipy.signal import find_peaks
from utils import shared_state

SAMPLE_RATE = 22050
CHUNK = int(0.8 * SAMPLE_RATE)  # 0.8 sec

def detect_siren_chunk(chunk, sample_rate=SAMPLE_RATE):
    # chunk: 1D numpy array of float32
    # compute FFT
    windowed = chunk * np.hanning(len(chunk))
    fft = np.abs(np.fft.rfft(windowed))
    freqs = np.fft.rfftfreq(len(windowed), 1.0 / sample_rate)

    # energy in siren band
    band_mask = (freqs > 500) & (freqs < 2000)
    band_energy = np.sum(fft[band_mask])
    total_energy = np.sum(fft) + 1e-8
    ratio = band_energy / total_energy

    # heuristic thresholds
    if total_energy < 1e4:
        return False  # too quiet
    if ratio > 0.15 and band_energy > 1e4:
        return True

    # fallback: detect strong periodic peaks in band (siren often has harmonics)
    peaks, _ = find_peaks(fft[band_mask], height=np.max(fft[band_mask]) * 0.3)
    if len(peaks) >= 2 and ratio > 0.07:
        return True

    return False

def audio_loop():
    # moving window detection to stabilize
    recent = [False]*6
    while True:
        try:
            audio = sd.rec(CHUNK, samplerate=SAMPLE_RATE, channels=1, dtype='float32')
            sd.wait()
            audio = audio.flatten()
            is_siren = detect_siren_chunk(audio)
            recent.pop(0)
            recent.append(is_siren)
            # majority vote
            siren_flag = sum(recent) >= 2

            with shared_state.lock:
                shared_state.siren_detected = siren_flag
                if siren_flag:
                    shared_state.last_emergency_time = time.time()
            # small sleep to avoid tight loop
            time.sleep(0.15)
        except Exception as e:
            print("Audio error:", e)
            time.sleep(0.5)

def start_audio_thread():
    t = threading.Thread(target=audio_loop, daemon=True)
    t.start()
    return t

if __name__ == "__main__":
    start_audio_thread()
    while True:
        with shared_state.lock:
            print("Siren:", shared_state.siren_detected)
        time.sleep(0.5)
