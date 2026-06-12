from .core import PeakSenseCore
from .detector import PeakDetector
from .coordinator import PeakSenseCoordinator

DOMAIN = "peaksense"

async def async_setup_entry(hass, entry):
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

    return True
