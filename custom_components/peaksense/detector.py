class SpikeDetector:
    def __init__(self, start_threshold=800, end_threshold=300):
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
                "values": [value]
            }

        # ACTIVE SPIKE
        elif self.active:
            self.current_event["values"].append(value)

            # END SPIKE
            if value < self.end_threshold:
                self.active = False
                self.current_event["end"] = timestamp
                event = self._finalize(self.current_event)
                self.current_event = None

        return event

    def _finalize(self, event):
        values = event["values"]
        event["peak"] = max(values)
        event["avg"] = round(sum(values) / len(values), 1)
        event["duration"] = len(values)
        return event
