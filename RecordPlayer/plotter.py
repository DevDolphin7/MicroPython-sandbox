import serial, struct, sys, sounddevice
import numpy as np
from collections import deque
from pyqtgraph.Qt import QtWidgets, QtCore
import pyqtgraph as pg

PORT = "/dev/ttyACM0"
BAUD = 115200
MAGIC = b"\xaa\x55"
FRAME_SAMPLES = 512
FS = 44100  # Hz
PLOT_SECONDS = 5.0

stream = sounddevice.OutputStream(samplerate=FS, channels=1, dtype="float32")
stream.start()


def read_exact(ser: serial.Serial, n: int) -> bytes:
    """Read exactly n bytes or raise"""
    data = ser.read(n)
    while len(data) < n:
        more = ser.read(n - len(data))
        if not more:
            raise RuntimeError("Serial read timeout")
        data += more
    return data


def sync_to_magic(ser: serial.Serial) -> bool | None:
    """Find MAGIC sequence in the incoming byte stream"""
    state = 0
    while True:
        b = ser.read(1)
        if not b:
            raise RuntimeError("Serial read timeout during sync")
        if state == 0 and b == MAGIC[0:1]:
            state = 1
        elif state == 1:
            if b == MAGIC[1:2]:
                return True
            else:
                state = 0


def read_frame(ser: serial.Serial) -> np.ndarray:
    """Read one frame: header (MAGIC + sample count) + samples"""
    sync_to_magic(ser)
    count_bytes = read_exact(ser, 2)
    (count,) = struct.unpack("<H", count_bytes)
    payload = read_exact(ser, count * 2)
    samples = np.frombuffer(payload, dtype=np.int16)
    # print(samples + 32768)
    return samples


def play_audio(data: np.ndarray):
    """Play audio streamed from a microcontroller"""
    stream.write(data)


def main():
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"Connected to serial port {PORT}")

    app = QtWidgets.QApplication([])
    win = pg.GraphicsLayoutWidget(show=True, title="Live Audio from Record Player")
    win.resize(1800, 1200)

    pg.setConfigOptions(antialias=True)

    p1 = win.addPlot(row=0, col=0, title="Vinyl Output Waveform")
    p1.setLabel("bottom", "Time", units="s")
    p1.setLabel("left", "Amplitude", units="normalised")
    curve = p1.plot(pen=pg.mkPen(color="c", width=1))

    max_samples = int(FS * PLOT_SECONDS)
    ring = deque(maxlen=max_samples)

    def update():
        try:
            samples = read_frame(ser)
        except Exception as e:
            print(f"Error reading frame: {e}")
            return

        y = samples.astype(np.float32) / 32768.0

        ring.extend(y.tolist())

        if len(ring) > 1:
            data = np.array(ring, dtype=np.float32)
            t = np.arange(data.size) / FS
            curve.setData(t, data)
            p1.setXRange(max(0, t[-1] - PLOT_SECONDS), t[-1], padding=0)

        play_audio(y)

    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(0)

    if sys.flags.interactive != 1:
        QtWidgets.QApplication.instance().exec_()

    try:
        stream.stop()
        stream.close()
    except Exception:
        pass
    ser.close()


if __name__ == "__main__":
    main()
