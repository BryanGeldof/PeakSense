from .coordinator import PeakSenseCore
from .sensor import PeakSenseSensor

async def async_setup(hass, config):
    core = PeakSenseCore()

    sensor = PeakSenseSensor(core)

    hass.data["peaksense"] = {
        "core": core,
        "sensor": sensor
    }

    return True
