import struct

import matplotlib.pyplot as plt
import numpy as np

from collections import namedtuple

WavFormatChunk = namedtuple('WavFormatChunk', [
    'FormatBlockID',   # 4 bytes: "fmt "
    'BlockSize',       # 4 bytes: Chunk size (usually 16)
    'AudioFormat',    # 2 bytes: 1 for PCM, 3 for Float
    'NbrChannels',    # 2 bytes: Number of channels
    'Frequency',      # 4 bytes: Sample rate (Hz)
    'BytePerSec',     # 4 bytes: (Frequency * BytePerBlock)
    'BytePerBlock',    # 2 bytes: (NbrChannels * BitsPerSample / 8)
    'BitsPerSample'   # 2 bytes: Bits per sample (e.g., 16, 24)
])

def plotter():
    fig = plt.figure(figsize=(10, 6), facecolor="#ffffff", dpi=100)
    ax = fig.add_subplot()

    ax.set_facecolor('white') # Inside plot color

    # Removing the top and right borders for a cleaner look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Changing spine color and thickness
    ax.spines['bottom'].set_linewidth(2)
    ax.spines['left'].set_linewidth(2)

    ax.grid(True, linestyle='-', alpha=0.6, color='grey')

    return fig, ax

def extact_wav_audio_mono(filename):
    f = open(filename, 'rb')

    master_riff_chunk = f.read(12)
    data_format_chunk = f.read(24)
    data_identifier_chunk = f.read(8)
    raw_data = f.read()

    f.close()

    # Mater RIFF chunk unpacking
    riff_label, file_size, file_format_id = struct.unpack('<4si4s', master_riff_chunk)

    assert riff_label == b'RIFF'
    assert file_format_id == b'WAVE'

    # Data format unpacking
    format = WavFormatChunk(*struct.unpack('<4sihhiihh', data_format_chunk))

    assert format.FormatBlockID == b'fmt '

    # Data identifier block unpacking
    data_label, data_size = struct.unpack('4si', data_identifier_chunk)

    assert data_label == b'data'

    print('Audio format:', format.AudioFormat, '(PCM)' if format.AudioFormat == 1 else '')
    print('Chanels:', format.NbrChannels)
    print('Frequency:', format.Frequency)
    print('Bit depth:', format.BitsPerSample)

    bps = format.BitsPerSample // 8

    # We just skip R chanel if it exists
    data = [int.from_bytes(raw_data[i : i + bps], byteorder='little', signed=True) for i in range(0, len(raw_data), bps * format.NbrChannels)]

    return data
        

# data = extact_wav_audio_mono('/home/filipp/Documents/testSound.wav')

fig, ax = plotter()

x = np.linspace(0, 10 * np.pi, 200)
y1 = np.sin(0.5 * x)
y2 = 0.7 * np.sin(2 * x)

# ax.plot(x, y1, color='red', alpha=0.3, label='y1 = sin(0.5 * t)')
# ax.plot(x, y2, color='blue', alpha=0.3, label='y2 = 0.7 * sin(2 * t)')
# ax.plot(x, y1 + y2, color='green', label='y3 = y1 + y2')
# ax.legend()

bits = 3
levels = 2**bits 

x = np.linspace(0, 2 * np.pi, 1000)
y_analog = np.sin(x)


# 3. The Math: Normalize -> Round -> De-normalize
# We scale the -1 to 1 range to the number of steps, round them, and scale back.
y_quantized = np.floor(y_analog * (levels / 2))

# Plot the smooth wave for comparison
ax.plot(x, y_analog * (levels / 2), label='Analog (Continuous)', alpha=0.9, linestyle='--')

# Plot the stepped version
ax.step(x, y_quantized, where='post', label='Digital (Sampled)', color='red', linewidth=2)

ax.set_title("Quantization (3 bits per sample)", pad=10)
ax.set_xlabel("Time", fontsize=12, labelpad=5)
ax.set_ylabel("Value", fontsize=12, labelpad=5)

plt.show()

