from machine import Pin, ADC
import sys, ustruct, utime

SAMPLE_RATE = 5000  # 44100  # hz
FRAME_SAMPLES = 512  # samples per frame
MAGIC = b"\xaa\x55"  # frame header


onboard_led = Pin("LED", Pin.OUT)
left_channel_raw = ADC(Pin(26))
# right_channel_raw = ADC(Pin(28))

buffer = bytearray(FRAME_SAMPLES * 2)
out = sys.stdout.buffer

period_us = int(1_000_000 // SAMPLE_RATE)


def write_frame(fsamples: int):
    out.write(MAGIC)
    out.write(ustruct.pack("<H", fsamples))
    out.write(buffer[: fsamples * 2])


def main():
    print("Starting data acquisition...")
    onboard_led.value(1)
    utime.sleep(0.1)

    next_tick = utime.ticks_us()
    i = 0

    while True:
        now = utime.ticks_us()

        if utime.ticks_diff(now, next_tick) >= 0:
            raw = left_channel_raw.read_u16()
            # right_raw = right_channel_raw.read_u16()
            # print(raw, right_raw, sep=",  ")
            signed = int(raw)

            buffer[i * 2 : i * 2 + 2] = ustruct.pack("<h", signed)
            i += 1

            next_tick = utime.ticks_add(next_tick, period_us)

            if i >= FRAME_SAMPLES:
                write_frame(FRAME_SAMPLES)
                i = 0


try:
    main()
    print("Finished.")
except Exception as e:
    print("Error:", e)
