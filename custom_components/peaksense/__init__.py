from homeassistant.core import HomeAssistant, ServiceCall
from .coordinator import PeakSenseCore
from homeassistant.helpers import discovery

DOMAIN = "peaksense"

print("PEAKSENSE LOADED")

async def async_setup(hass: HomeAssistant, config: dict):

    core = PeakSenseCore()

    hass.data[DOMAIN] = core

    discovery.load_platform(hass, "sensor", DOMAIN, {}, config)

    async def handle_update(call: ServiceCall):
        value = float(call.data.get("value", 0))

        event = core.process_value(value)

        if event:
            hass.states.async_set(
                "sensor.peaksense_last_event",
                event["peak"],
                {
                    "start": event["start"],
                    "end": event["end"],
                    "avg": event["avg"],
                    "duration": event["duration"],
                    "values": event["values"],
                }
            )

    hass.services.async_register(
        DOMAIN,
        "update",
        handle_update
    )

    return True
