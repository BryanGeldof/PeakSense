from .devices import DEVICE_PROFILES

class PeakSenseCore:
    def __init__(self):
        self.last_event = None
        self.history = []
        self.baseline = 0

    def update_baseline(self, value):
        self.history.append(value)

        if len(self.history) > 300:
            self.history.pop(0)

        self.baseline = sum(self.history) / len(self.history)

    def match_device(self, peak, duration):
        best = "unknown"
        best_score = 0

        for name, p in DEVICE_PROFILES.items():
            pmin, pmax = p["peak"]
            dmin, dmax = p["duration"]

            if pmin <= peak <= pmax and dmin <= duration <= dmax:
                score = 1
                if score > best_score:
                    best = name
                    best_score = score

        return best
