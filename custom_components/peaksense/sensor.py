"""PeakSense sensors."""

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
    """Set up sensors."""
    core = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        PeakSenseLastEventSensor(core),
        PeakSenseStatusSensor(core),
        PeakSenseCurrentDeviceSensor(core),
        PeakSenseConfidenceSensor(core),
    ]
    
    async_add_entities(entities, update_before_add=True)


class PeakSenseLastEventSensor(Entity):
    """Last event peak."""

    _attr_has_entity_name = True

    def __init__(self, core):
        self._core = core
        self._state = 0
        self._attributes = {}

    @property
    def name(self):
        return "Last Event"

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
        """Update state."""
        event = self._core.last_event
        if event:
            self._state = event.get("peak", 0)
            self._attributes = {
                "id": event.get("id"),
                "start": event.get("start"),
                "end": event.get("end"),
                "average_w": event.get("avg"),
                "duration_samples": event.get("duration"),
                "label": event.get("label", "unknown"),
                "device": self._core.current_device or "unknown",
                "confidence": self._core.current_confidence,
            }
        else:
            self._state = 0
            self._attributes = {}


class PeakSenseStatusSensor(Entity):
    """Spike detection status."""

    _attr_has_entity_name = True

    def __init__(self, core):
        self._core = core

    @property
    def name(self):
        return "Status"

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
        """State is live."""
        pass


class PeakSenseCurrentDeviceSensor(Entity):
    """Detected device."""

    _attr_has_entity_name = True

    def __init__(self, core):
        self._core = core

    @property
    def name(self):
        return "Current Device"

    @property
    def unique_id(self):
        return "peaksense_current_device"

    @property
    def state(self):
        return self._core.current_device or "unknown"

    @property
    def icon(self):
        return "mdi:devices"

    def update(self):
        """State is live."""
        pass


class PeakSenseConfidenceSensor(Entity):
    """Detection confidence."""

    _attr_has_entity_name = True

    def __init__(self, core):
        self._core = core

    @property
    def name(self):
        return "Detection Confidence"

    @property
    def unique_id(self):
        return "peaksense_confidence"

    @property
    def state(self):
        return round(self._core.current_confidence * 100, 0)

    @property
    def unit_of_measurement(self):
        return "%"

    @property
    def icon(self):
        confidence = self._core.current_confidence
        if confidence >= 0.8:
            return "mdi:check-circle"
        elif confidence >= 0.5:
            return "mdi:alert-circle"
        else:
            return "mdi:help-circle"

    def update(self):
        """State is live."""
        pass
