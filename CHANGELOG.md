from .const import SPIKE_START_THRESHOLD, SPIKE_END_THRESHOLD


class SpikeDetector:
    def __init__(self, start_threshold=SPIKE_START_THRESHOLD, end_threshold=SPIKE_END_THRESHOLD):
        self.start_threshold = start_threshold
        self.end_threshold = end_threshold
        self.active = False
        self.current_event = None

    def process(self, value, timestamp):
        event = None

        # START SPIKE
        if not self.active and value > self.start_threshold:
            self.active = True
            self.current_event = {
                "start": timestamp,
                "values": [value],
                "peak": value,
                "min": value,
            }

        # ACTIVE SPIKE
        elif self.active:
            self.current_event["values"].append(value)
            self.current_event["peak"] = max(self.current_event["peak"], value)
            self.current_event["min"] = min(self.current_event["min"], value)

            # END SPIKE
            if value < self.end_threshold:
                self.active = False
                self.current_event["end"] = timestamp
                event = self._finalize(self.current_event)
                self.current_event = None

        return event

    def _finalize(self, event):
        values = event["values"]
        event["avg"] = round(sum(values) / len(values), 1)
        event["duration"] = len(values)
        event["variance"] = self._calculate_variance(values)
        event["peak"] = round(event["peak"], 1)
        event["min"] = round(event["min"], 1)
        
        # Clean up internal fields
        del event["values"]
        
        return event

    @staticmethod
    def _calculate_variance(values):
        """Calculate variance of the spike pattern."""
        if len(values) < 2:
            return 0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return round(variance, 1)
