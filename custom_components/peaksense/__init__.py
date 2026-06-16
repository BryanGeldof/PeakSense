"""PeakSense integration."""

import json
import logging

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.http import HomeAssistantView

from .coordinator import PeakSenseCore
from .const import DOMAIN, CONF_POWER_METER, CONF_DEVICES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PeakSense."""
    _LOGGER.debug("PeakSense: setup_entry starting")

    core = PeakSenseCore()
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = core
    
    # Store config
    hass.data[DOMAIN]["config"] = entry.data
    
    # Register initial devices from config
    devices = entry.data.get(CONF_DEVICES, [])
    for device in devices:
        if isinstance(device, dict) and device.get("name"):
            core.register_device(
                device.get("name"),
                device.get("standby_power", 0),
                device.get("notes", "")
            )
    
    _LOGGER.debug("PeakSense: Core initialized")

    # Service: peaksense.update
    async def handle_update(call: ServiceCall):
        value = float(call.data.get("value", 0))
        core.process_value(value)

    hass.services.async_register(DOMAIN, "update", handle_update)

    # Service: peaksense.register_device
    async def handle_register_device(call: ServiceCall):
        name = str(call.data.get("name", "Unknown"))
        standby_power = float(call.data.get("standby_power", 0))
        notes = str(call.data.get("notes", ""))
        
        core.register_device(name, standby_power, notes)

    hass.services.async_register(DOMAIN, "register_device", handle_register_device)

    # Service: peaksense.record_signature
    async def handle_record_signature(call: ServiceCall):
        event_id = int(call.data.get("event_id"))
        device_id = int(call.data.get("device_id"))
        
        events = core.storage.get_recent_events(1)
        if events and events[0]['id'] == event_id:
            event = events[0]
            core.record_device_signature(device_id, event)

    hass.services.async_register(DOMAIN, "record_signature", handle_record_signature)

    # Service: peaksense.label_event
    async def handle_label_event(call: ServiceCall):
        event_id = int(call.data.get("event_id"))
        label = str(call.data.get("label", "unknown"))
        
        core.storage.label_event(event_id, label)

    hass.services.async_register(DOMAIN, "label_event", handle_label_event)

    # Service: peaksense.provide_feedback
    async def handle_provide_feedback(call: ServiceCall):
        event_id = int(call.data.get("event_id"))
        device_id = int(call.data.get("device_id"))
        is_correct = bool(call.data.get("is_correct", False))
        
        core.provide_feedback(event_id, device_id, is_correct)

    hass.services.async_register(DOMAIN, "provide_feedback", handle_provide_feedback)

    # Service: peaksense.update_device
    async def handle_update_device(call: ServiceCall):
        device_id = int(call.data.get("device_id"))
        kwargs = {}
        if "name" in call.data:
            kwargs['name'] = str(call.data.get("name"))
        if "standby_power" in call.data:
            kwargs['standby_power'] = float(call.data.get("standby_power"))
        if "notes" in call.data:
            kwargs['notes'] = str(call.data.get("notes"))
        
        core.update_device(device_id, **kwargs)

    hass.services.async_register(DOMAIN, "update_device", handle_update_device)

    # Service: peaksense.delete_device
    async def handle_delete_device(call: ServiceCall):
        device_id = int(call.data.get("device_id"))
        core.delete_device(device_id)

    hass.services.async_register(DOMAIN, "delete_device", handle_delete_device)

    # REST API
    hass.http.register_view(PeakSenseEventsView(core))
    hass.http.register_view(PeakSenseDevicesView(core))
    hass.http.register_view(PeakSenseStatsView(core))

    # Load sensors
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    
    # Setup options flow
    entry.async_on_unload(entry.add_update_listener(async_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Update listener."""
    await hass.config_entries.async_reload(entry.entry_id)


class PeakSenseEventsView(HomeAssistantView):
    """REST: GET /api/peaksense/events"""

    url = "/api/peaksense/events"
    name = "api:peaksense:events"
    requires_auth = True

    def __init__(self, core):
        self._core = core

    async def get(self, request):
        from aiohttp.web import Response
        try:
            events = self._core.storage.get_recent_events(100)
            return Response(text=json.dumps(events), content_type="application/json")
        except Exception as e:
            _LOGGER.error(f"API error: {e}", exc_info=True)
            return Response(text=json.dumps({"error": str(e)}), status=500, content_type="application/json")


class PeakSenseDevicesView(HomeAssistantView):
    """REST: GET /api/peaksense/devices"""

    url = "/api/peaksense/devices"
    name = "api:peaksense:devices"
    requires_auth = True

    def __init__(self, core):
        self._core = core

    async def get(self, request):
        from aiohttp.web import Response
        try:
            devices = self._core.get_all_devices()
            devices_with_stats = []
            for device in devices:
                stats = self._core.get_device_stats(device['id'])
                device['stats'] = stats
                devices_with_stats.append(device)
            
            return Response(text=json.dumps(devices_with_stats), content_type="application/json")
        except Exception as e:
            _LOGGER.error(f"API error: {e}", exc_info=True)
            return Response(text=json.dumps({"error": str(e)}), status=500, content_type="application/json")


class PeakSenseStatsView(HomeAssistantView):
    """REST: GET /api/peaksense/stats"""

    url = "/api/peaksense/stats"
    name = "api:peaksense:stats"
    requires_auth = True

    def __init__(self, core):
        self._core = core

    async def get(self, request):
        from aiohttp.web import Response
        try:
            accuracy = self._core.storage.get_accuracy_stats()
            return Response(text=json.dumps(accuracy), content_type="application/json")
        except Exception as e:
            _LOGGER.error(f"API error: {e}", exc_info=True)
            return Response(text=json.dumps({"error": str(e)}), status=500, content_type="application/json")
