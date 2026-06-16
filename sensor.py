"""Config flow for PeakSense."""

from homeassistant import config_entries
from .const import DOMAIN


class PeakSenseConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle user initiated flow."""
        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="PeakSense", data={})

        return self.async_show_form(step_id="user")
