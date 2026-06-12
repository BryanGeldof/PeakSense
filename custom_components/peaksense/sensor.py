import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    core = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        PeakSenseLastEventSensor(core),
        PeakSenseStatusSensor(core),
    ], update_before_add=True)


class PeakSenseLastEventSensor(Entity):
    """Peak wattage + details of the last completed spike."""

    _attr_has_entity_name = True

    def __init__(self, core):
        self._core = core
        self._state = 0
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
    def unit_of_measurement(self):
        return "W"

    @property
    def icon(self):
        return "mdi:lightning-bolt"

    @property
    def extra_state_attributes(self):
        return self._attributes

    def update(self):
        event = self._core.last_event
        if event:
            self._state = event.get("peak", 0)
            self._attributes = {
                "start": event.get("start"),
                "end": event.get("end"),
                "average_w": event.get("avg"),
                "duration_samples": event.get("duration"),
                "label": event.get("label", "unknown"),
            }


class PeakSenseStatusSensor(Entity):
    """Active while a spike is being recorded, idle otherwise."""

    _attr_has_entity_name = True

    def __init__(self, core):
        self._core = core

    @property
    def name(self):
        return "PeakSense Status"

    @property
    def unique_id(self):
        return "peaksense_status"

    @property
    def state(self):
        return "active" if self._core.detector.active else "idle"

    @property
    def icon(self):
        return "mdi:pulse" if self._core.detector.active else "mdi:sleep"

    def update(self):
        pass
