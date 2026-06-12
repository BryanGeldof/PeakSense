from .detector import SpikeDetector
from .storage import Storage
from datetime import datetime

class PeakSenseCore:
    def __init__(self):
        self.detector = SpikeDetector()
        self.storage = Storage()
        self.last_event = None

    def process_value(self, value):
        event = self.detector.process(value, datetime.now().isoformat())

        if event:
            self.storage.save_event(event)
            self.last_event = event
            return event

        return None
