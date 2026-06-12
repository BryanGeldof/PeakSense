from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
import asyncio

class PeakSenseCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, core, sensor_entity):
        super().__init__(
            hass,
            logger=None,
            name="peaksense",
            update_interval=None,
        )

        self.core = core
        self.sensor_entity = sensor_entity

    async def async_refresh(self):
        state = self.hass.states.get(self.sensor_entity)

        if state is None:
            return

        try:
            value = float(state.state)
        except:
            return

        self.core.detector.process(value)

        self.async_set_updated_data(self.core.last_event)
