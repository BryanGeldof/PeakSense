import json
import logging

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.http import HomeAssistantView

from .coordinator import PeakSenseCore
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PeakSense — no configuration.yaml needed."""

    core = PeakSenseCore()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = core

    # ------------------------------------------------------------------ #
    # Service: peaksense.update                                            #
    # Push a power reading in. Call this from an automation every ~5s.    #
    # Example: service: peaksense.update  data: {value: 1200}             #
    # ------------------------------------------------------------------ #
    async def handle_update(call: ServiceCall):
        value = float(call.data.get("value", 0))
        event = await hass.async_add_executor_job(core.process_value, value)
        if event:
            _LOGGER.info("PeakSense spike detected: %s W", event.get("peak"))
            # Refresh sensors immediately when a spike is completed
            await hass.helpers.entity_component.async_update_entity(
                "sensor.peaksense_last_event"
            )

    hass.services.async_register(DOMAIN, "update", handle_update)

    # ------------------------------------------------------------------ #
    # Service: peaksense.label_event                                       #
    # Label an event by its database ID.                                  #
    # Example: service: peaksense.label_event                             #
    #          data: {event_id: 3, label: "Wasmachine"}                   #
    # ------------------------------------------------------------------ #
    async def handle_label(call: ServiceCall):
        event_id = int(call.data.get("event_id"))
        label = str(call.data.get("label", "unknown"))
        await hass.async_add_executor_job(
            core.storage.label_event, event_id, label
        )
        _LOGGER.info("PeakSense event %s labeled as '%s'", event_id, label)

    hass.services.async_register(DOMAIN, "label_event", handle_label)

    # ------------------------------------------------------------------ #
    # REST endpoint: GET /api/peaksense/events                            #
    # Returns the last 50 events as JSON — used by the dashboard.        #
    # ------------------------------------------------------------------ #
    hass.http.register_view(PeakSenseEventsView(core))

    # Load sensors
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
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
        events = await request.app["hass"].async_add_executor_job(
            self._core.storage.get_recent_events, 50
        )
        return Response(
            text=json.dumps(events),
            content_type="application/json",
        )
