from homeassistant.helpers.entity import Entity

DOMAIN = "peaksense"

class PeakSenseLastEventSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        return "PeakSense Last Event"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    def update_from_core(self):
        core = self.hass.data["peaksense"]["core"]

        event = core.last_event

        if event:
            self._state = event.get("peak")
            self._attributes = {
                "start": event.get("start"),
                "end": event.get("end"),
                "avg": event.get("avg"),
                "duration": event.get("duration"),
                "values": event.get("values"),
            }
