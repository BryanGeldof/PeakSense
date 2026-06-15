import json
import logging

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.http import HomeAssistantView

from .coordinator import PeakSenseCore
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PeakSense from a config entry."""
    _LOGGER.debug("PeakSense: async_setup_entry starting")

    core = PeakSenseCore()
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = core
    _LOGGER.debug("PeakSense: Core initialized")

    # Service: peaksense.update
    async def handle_update(call: ServiceCall):
        value = float(call.data.get("value", 0))
        _LOGGER.debug(f"PeakSense: update service called with value={value}")
        event = core.process_value(value)
        if event:
            _LOGGER.info(f"PeakSense: spike detected! Peak={event.get('peak')}W")

    hass.services.async_register(DOMAIN, "update", handle_update)
    _LOGGER.debug("PeakSense: update service registered")

    # Service: peaksense.label_event
    async def handle_label(call: ServiceCall):
        event_id = int(call.data.get("event_id"))
        label = str(call.data.get("label", "unknown"))
        _LOGGER.debug(f"PeakSense: label_event called for id={event_id}, label={label}")
        core.storage.label_event(event_id, label)
        _LOGGER.info(f"PeakSense: event {event_id} labeled as '{label}'")

    hass.services.async_register(DOMAIN, "label_event", handle_label)
    _LOGGER.debug("PeakSense: label_event service registered")

    # REST endpoint
    hass.http.register_view(PeakSenseEventsView(core))
    _LOGGER.debug("PeakSense: REST API endpoint registered")

    # Load sensors
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    _LOGGER.debug("PeakSense: sensors loaded")

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class PeakSenseEventsView(HomeAssistantView):
    """REST endpoint that returns recent events as JSON."""

    url = "/api/peaksense/events"
    name = "api:peaksense:events"
    requires_auth = True

    def __init__(self, core: PeakSenseCore):
        self._core = core

    async def get(self, request):
        from aiohttp.web import Response
        try:
            events = self._core.storage.get_recent_events(100)
            return Response(
                text=json.dumps(events),
                content_type="application/json",
            )
        except Exception as e:
            _LOGGER.error(f"PeakSense API error: {e}", exc_info=True)
            return Response(
                text=json.dumps({"error": str(e)}),
                status=500,
                content_type="application/json",
            )
