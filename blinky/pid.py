import time


class PID:
    def __init__(
        self,
        kp=1.0,
        ki=0.0,
        kd=0.0,
        sample_time=0.05,
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
        self.out_min = out_min
        self.out_max = out_max

        # Internal state
        self._last_time = None
        self._last_output = 0.0

    def reset(self):
        """
        Reset the PID controller state.
        """
        self._last_time = None
        self.last_output = 0.0

    def compute(self, pv, prev_u):
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

        error = pv - prev_u
        p = self.kp * error

        # Compute total output
        u = p

        # Clamp output to bounds
        u = max(self.out_min, min(self.out_max, u))

        # Update state
        self._last_output = u
        self._last_time = now

        return u
