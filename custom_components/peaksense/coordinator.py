import logging
from datetime import datetime
from .detector import SpikeDetector
from .storage import Storage
from .pattern_matcher import PatternMatcher

_LOGGER = logging.getLogger(__name__)

class PeakSenseCore:
    def __init__(self):
        self.detector = SpikeDetector()
        self.storage = Storage()
        self.matcher = PatternMatcher()
        self.matcher.storage = self.storage
        self.last_event = None
        self.current_device = None
        self.current_confidence = 0
        self.device_powers = {}

    def process_value(self, value: float):
        event = self.detector.process(value, datetime.now().isoformat())
        if event:
            eid = self.storage.save_event(event)
            event['id'] = eid
            devices = self.storage.get_all_devices()
            detection = self.matcher.match_event(event, devices)
            
            if detection['device_id']:
                self.storage.update_event_device(eid, detection['device_id'], detection['confidence'])
                self.device_powers[detection['device_name']] = event['peak']
                _LOGGER.info(f"Detected: {detection['device_name']} ({detection['confidence']*100:.0f}%)")
            
            self.last_event = event
            self.current_device = detection['device_name']
            self.current_confidence = detection['confidence']
            return event
        return None

    def register_device(self, name: str, standby_power: float = 0):
        did = self.storage.create_device(name, standby_power)
        _LOGGER.info(f"Registered: {name}")
        return did

    def record_signature(self, device_id: int, event: dict):
        self.storage.record_signature(device_id, event)
        _LOGGER.info(f"Signature recorded for device {device_id}: {event['peak']}W")

    def get_all_devices(self):
        return self.storage.get_all_devices()

    def delete_device(self, device_id: int):
        self.storage.delete_device(device_id)
        _LOGGER.info(f"Deleted device {device_id}")
