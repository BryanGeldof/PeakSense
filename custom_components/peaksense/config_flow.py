from homeassistant import config_entries
from .const import DOMAIN


class PeakSenseConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the UI setup flow for PeakSense."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Single step: user clicks Submit, integration is created."""
        if user_input is not None:
            # Prevent adding the integration twice
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="PeakSense", data={})

        return self.async_show_form(step_id="user")
