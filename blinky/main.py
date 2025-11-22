from machine import Pin, ADC, PWM
from utime import sleep
from pid import PID

onboard_led = Pin("LED", Pin.OUT)
adc = ADC(Pin(26))
pwm = PWM(Pin(15))
pwm.freq(1000)

pins = [onboard_led]

sample_time = 0.5  # seconds
u = 0.0  # Initial control output


def read_normalized_adc() -> float:
    return adc.read_u16() / 65535.0


def write_pwm(value: float) -> None:
    duty = int(max(0.0, min(1.0, value)) * 65535)
    pwm.duty_u16(duty)


pid_controller = PID(
    kp=0.8,
    ki=0.0,
    kd=0.0,
    sample_time=sample_time,
    out_min=0.0,
    out_max=1.0,
)

while True:
    try:
        onboard_led.toggle()

        pv = read_normalized_adc()
        print(f"Voltage: {pv * 3.3:.2f} V")

        u = pid_controller.compute(pv, u)
        print(f"PID Output: {u:.2f}")
        write_pwm(u)

        sleep(sample_time)

    except KeyboardInterrupt:
        break

for pin in pins:
    pin.off()
print("Finished.")
