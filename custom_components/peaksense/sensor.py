"""PeakSense sensors - including dynamic per-device power sensors."""

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
    """Setup sensors."""
    core = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        PeakSenseLastEventSensor(core),
        PeakSenseStatusSensor(core),
        PeakSenseCurrentDeviceSensor(core),
        PeakSenseConfidenceSensor(core),
    ]
    
    # Add per-device power sensors
    devices = core.get_all_devices()
    for device in devices:
        entities.append(DevicePowerSensor(core, device['id'], device['name']))
    
    async_add_entities(entities, update_before_add=True)


class PeakSenseLastEventSensor(Entity):
    """Last event peak (W)."""
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
        event = self._core.last_event
        if event:
            self._state = event.get("peak", 0)
            self._attributes = {
                "id": event.get("id"),
                "start": event.get("start"),
                "end": event.get("end"),
                "average_w": event.get("avg"),
                "duration_samples": event.get("duration"),
            }


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
        pass


class PeakSenseCurrentDeviceSensor(Entity):
    """Currently detected device."""
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
        pass


class PeakSenseConfidenceSensor(Entity):
    """Detection confidence (%)."""
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
        conf = self._core.current_confidence
        return "mdi:check-circle" if conf >= 0.8 else "mdi:alert-circle" if conf >= 0.5 else "mdi:help-circle"

    def update(self):
        pass


class DevicePowerSensor(Entity):
    """Per-device power consumption (last detected peak)."""

    def __init__(self, core, device_id, device_name):
        self._core = core
        self._device_id = device_id
        self._device_name = device_name
        self._state = 0

    @property
    def name(self):
        return f"{self._device_name} Power"

    @property
    def unique_id(self):
        return f"peaksense_{self._device_name.lower().replace(' ', '_')}_power"

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return "W"

    @property
    def icon(self):
        return "mdi:power-socket"

    @property
    def device_class(self):
        return "power"

    def update(self):
        """Update with last known power for this device."""
        if self._device_name in self._core.device_powers:
            self._state = self._core.device_powers[self._device_name]
        else:
            self._state = 0
