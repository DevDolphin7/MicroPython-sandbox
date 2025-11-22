from machine import Pin, ADC, PWM
from utime import sleep
from pid import PID

onboard_led = Pin("LED", Pin.OUT)
adc = ADC(Pin(26))
pwm = PWM(Pin(15))
pwm.freq(1000)

pins = [onboard_led]

sample_time = 0.05  # seconds


def read_normalized_adc() -> float:
    return adc.read_u16() / 65535.0


def write_pwm(value: float) -> None:
    duty = int(max(0.0, min(1.0, value)) * 65535)
    pwm.duty_u16(duty)


pid_controller = PID(
    kp=0.02,
    ki=0.008,
    kd=0.008,
    sample_time=sample_time,
    deadband=0.005,
    out_min=0.0,
    out_max=1.0,
)

while True:
    try:
        # onboard_led.toggle()

        sp = read_normalized_adc()
        print(f"Desired output: {sp:.2f}")

        u = pid_controller.compute(sp, u if "u" in locals() else 0.0)
        print(f"PID Output: {u:.2f}")
        write_pwm(u)

        sleep(sample_time)

    except KeyboardInterrupt:
        break

for pin in pins:
    pin.off()
print("Finished.")
