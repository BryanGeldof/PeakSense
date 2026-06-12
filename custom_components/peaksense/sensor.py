from homeassistant.helpers.entity import Entity

class PeakSenseLastEventSensor(Entity):
    def __init__(self, core):
        self._core = core

    @property
    def name(self):
        return "PeakSense Last Event"

    @property
    def state(self):
        if not self._core.last_event:
            return None
        return self._core.last_event["peak"]

    @property
    def extra_state_attributes(self):
        return self._core.last_event or {}


class PeakSensePredictionSensor(Entity):
    def __init__(self, core):
        self._core = core

    @property
    def name(self):
        return "PeakSense Prediction"

    @property
    def state(self):
        if not self._core.last_event:
            return "idle"
        return self._core.last_event.get("device_guess", "unknown")


class PeakSenseStatusSensor(Entity):
    def __init__(self, core):
        self._core = core

    @property
    def name(self):
        return "PeakSense Status"

    @property
    def state(self):
        return "active" if self._core.detector.active else "idle"
