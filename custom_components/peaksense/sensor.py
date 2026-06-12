from homeassistant.helpers.entity import Entity
from datetime import datetime

DOMAIN = "peaksense"

class PeakSenseSensor(Entity):
    def __init__(self, core):
        self._core = core
        self._state = None
        self._last_event = None

    @property
    def name(self):
        return "PeakSense Last Event"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._last_event or {}

    def update_from_power(self, value):
        event = self._core.process_value(value)

        if event:
            self._state = event["peak"]
            self._last_event = event
