from .core import PeakSenseCore
from .detector import PeakDetector
from .coordinator import PeakSenseCoordinator

DOMAIN = "peaksense"

async def async_setup_entry(hass, entry):
    core = PeakSenseCore()
    core.detector = PeakDetector(core)

    sensor_entity = entry.data["sensor"]

    coordinator = PeakSenseCoordinator(hass, core, sensor_entity)

    hass.data[DOMAIN] = {
        "core": core,
        "coordinator": coordinator,
    }

    await coordinator.async_refresh()

    return True
