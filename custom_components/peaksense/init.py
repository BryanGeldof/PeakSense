from .service import process_power

async def async_setup(hass, config):
    hass.data["peaksense"] = {}

    return True
