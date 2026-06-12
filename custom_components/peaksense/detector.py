import time

class PeakDetector:
    def __init__(self, core, threshold_factor=1.5):
        self.core = core
        self.active = False
        self.threshold_factor = threshold_factor

        self._start = None
        self._values = []

    def process(self, value):
        self.core.update_baseline(value)

        threshold = max(50, self.core.baseline * self.threshold_factor)

        if value > threshold and not self.active:
            self.active = True
            self._start = time.time()
            self._values = []

        if self.active:
            self._values.append(value)

            if value < threshold * 0.8:
                self._finish()

    def _finish(self):
        if not self._values:
            return

        peak = max(self._values)
        avg = sum(self._values) / len(self._values)
        duration = int(time.time() - self._start)

        device = self.core.match_device(peak, duration)

        self.core.last_event = {
            "peak": peak,
            "avg": avg,
            "duration": duration,
            "start": self._start,
            "end": time.time(),
            "device_guess": device,
        }

        self.active = False
        self._values = []
