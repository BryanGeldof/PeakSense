"""Spike detection algorithm."""

from .const import SPIKE_START_THRESHOLD, SPIKE_END_THRESHOLD


class SpikeDetector:
    """Detects power spikes above threshold."""

    def __init__(self, start_threshold=SPIKE_START_THRESHOLD, end_threshold=SPIKE_END_THRESHOLD):
        self.start_threshold = start_threshold
        self.end_threshold = end_threshold
        self.active = False
        self.current_event = None

    def process(self, value, timestamp):
        """Process a power value and detect spikes."""
        event = None

        if not self.active and value > self.start_threshold:
            self.active = True
            self.current_event = {
                "start": timestamp,
                "values": [value],
                "peak": value,
                "min": value,
            }

        elif self.active:
            self.current_event["values"].append(value)
            self.current_event["peak"] = max(self.current_event["peak"], value)
            self.current_event["min"] = min(self.current_event["min"], value)

            if value < self.end_threshold:
                self.active = False
                self.current_event["end"] = timestamp
                event = self._finalize(self.current_event)
                self.current_event = None

        return event

    def _finalize(self, event):
        """Calculate spike statistics."""
        values = event["values"]
        event["avg"] = round(sum(values) / len(values), 1)
        event["duration"] = len(values)
        event["variance"] = self._calculate_variance(values)
        event["peak"] = round(event["peak"], 1)
        event["min"] = round(event["min"], 1)
        del event["values"]
        return event

    @staticmethod
    def _calculate_variance(values):
        """Calculate variance of spike pattern."""
        if len(values) < 2:
            return 0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return round(variance, 1)
