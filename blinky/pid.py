import time


class PID:
    def __init__(
        self,
        kp=1.0,
        ki=0.0,
        kd=0.0,
        sample_time=0.05,
        deadband=0.01,
        out_min=0.0,
        out_max=1.0,
    ):
        """
        Simple PID controller with derivative filtering.
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.sample_time = sample_time
        self.deadband = deadband
        self.out_min = out_min
        self.out_max = out_max

        self.leak_rate = 0.1

        # Internal state
        self._last_time = None
        self._last_output = 0.0
        self._integral = 0.0
        self._previous_error = 0.0

    def reset(self):
        """
        Reset the PID controller state.
        """
        self._last_time = None
        self.last_output = 0.0

    def compute(self, sp, pv):
        """
        Compute the PID output value for given process variable (pv) and current time.
        """
        now = time.ticks_ms()

        if self._last_time is None:
            self._last_time = now

        dt_ms = time.ticks_diff(now, self._last_time)
        dt = dt_ms / 1000.0

        if dt < self.sample_time:
            return self._last_output

        error = sp - pv

        p = self.kp * error

        if abs(error) < self.deadband:
            self._integral *= max(0.0, (1.0 - self.leak_rate) * dt)
            d = 0.0
        else:
            self._integral += max(-0.1, min(0.1, self.ki * error * dt))
            d = self.kd * ((error - self._previous_error) / dt)

        # Compute total output
        u = pv + p + self._integral + d

        # Clamp output to bounds
        u = max(self.out_min, min(self.out_max, u))
        if u < self.deadband:
            u = 0.0

        # Update state
        self._last_output = u
        self._last_time = now
        self._previous_error = error

        return u
