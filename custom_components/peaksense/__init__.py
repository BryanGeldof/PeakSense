from homeassistant.helpers import discovery
from .coordinator import PeakSenseCore
from .sensor import PeakSenseLastEventSensor

async def async_setup(hass, config):

    core = PeakSenseCore()

    sensor = PeakSenseLastEventSensor(hass)

    hass.data["peaksense"] = {
        "core": core,
        "sensor": sensor
    }

    async def handle_update(call):
        value = float(call.data.get("value", 0))
        event = core.process_value(value)

        sensor.update_from_core()

        hass.states.async_set(
            "sensor.peaksense_last_event",
            sensor.state,
            sensor.extra_state_attributes
        )

    hass.services.async_register(
        "peaksense",
        "update",
        handle_update
    )

    return True
