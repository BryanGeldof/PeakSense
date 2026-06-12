from .core import PeakSenseCore
from .detector import PeakDetector
from .coordinator import PeakSenseCoordinator

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

DOMAIN = "peaksense"
PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up PeakSense from a config entry."""

    core = PeakSenseCore()
    core.detector = PeakDetector(core)

    sensor_entity = entry.data.get("sensor")

    coordinator = PeakSenseCoordinator(hass, core, sensor_entity)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "core": core,
        "coordinator": coordinator,
        "sensor": sensor_entity,
    }

    # start first refresh
    await coordinator.async_refresh()

    # forward entities to sensor.py
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload PeakSense."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok
