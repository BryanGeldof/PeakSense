from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from .coordinator import PeakSenseCore
from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PeakSense from a config entry (UI-based, no configuration.yaml needed)."""

    core = PeakSenseCore()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = core

    # Register the service so automations can push power values into PeakSense
    async def handle_update(call: ServiceCall):
        value = float(call.data.get("value", 0))
        core.process_value(value)

    hass.services.async_register(DOMAIN, "update", handle_update)

    # Load the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
