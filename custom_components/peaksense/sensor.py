from homeassistant.helpers.entity import Entity

DOMAIN = "peaksense"

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    core = hass.data.get(DOMAIN)
    if core is None:
        return False
    sensor = PeakSenseLastEventSensor(hass, core)
    async_add_entities([sensor])
    return True

class PeakSenseLastEventSensor(Entity):
    def __init__(self, hass, core):
        self.hass = hass
        self._core = core
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        return "PeakSense Last Event"

    @property
    def unique_id(self):
        return "peaksense_last_event"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    def update(self):
        event = self._core.last_event
        if event:
            self._state = event.get("peak")
            self._attributes = {
                "start": event.get("start"),
                "end": event.get("end"),
                "avg": event.get("avg"),
                "duration": event.get("duration"),
                "label": event.get("label", "unknown"),
            }
