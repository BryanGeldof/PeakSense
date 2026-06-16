"""Config flow for PeakSense with device setup."""

import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class PeakSenseConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the PeakSense config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Initial step - select power meter."""
        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            
            return await self.async_step_devices(user_input)

        # Get all power sensors in the system
        power_sensors = await self._get_power_sensors()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("power_meter", default=""): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        device_class="power",
                    )
                ),
            }),
            description_placeholders={
                "sensors_found": f"Found {len(power_sensors)} power sensors"
            },
        )

    async def async_step_devices(self, user_input=None):
        """Step 2: Add devices to monitor."""
        
        if user_input is not None:
            # Store config
            power_meter = user_input.get("power_meter_from_user")
            devices = user_input.get("devices", [])
            
            return self.async_create_entry(
                title="PeakSense",
                data={
                    "power_meter": power_meter,
                    "devices": devices,
                    "version": "0.5.0",
                }
            )

        return self.async_show_form(
            step_id="devices",
            data_schema=vol.Schema({
                vol.Optional("power_meter_from_user"): str,
                vol.Optional("device_1_name"): str,
                vol.Optional("device_1_standby", default=0): vol.All(
                    vol.Coerce(float), vol.Range(min=0, max=100)
                ),
                vol.Optional("device_2_name"): str,
                vol.Optional("device_2_standby", default=0): vol.All(
                    vol.Coerce(float), vol.Range(min=0, max=100)
                ),
                vol.Optional("device_3_name"): str,
                vol.Optional("device_3_standby", default=0): vol.All(
                    vol.Coerce(float), vol.Range(min=0, max=100)
                ),
            }),
            description_placeholders={
                "info": "Add devices you want to monitor (optional, can be added later)"
            },
        )

    @staticmethod
    async def _get_power_sensors():
        """Get all available power sensors."""
        # This will be populated during form display
        return []

    @callback
    def async_create_entry_from_devices(self, data):
        """Create entry from device data."""
        return self.async_create_entry(title="PeakSense", data=data)


class PeakSenseOptionsFlow(config_entries.OptionsFlow):
    """Handle options for PeakSense."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage options."""
        return await self.async_step_devices()

    async def async_step_devices(self, user_input=None):
        """Manage devices."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_devices = self.config_entry.data.get("devices", [])
        
        # Build schema for adding/editing devices
        schema_dict = {
            vol.Optional("power_meter"): str,
        }
        
        # Show existing devices
        for i, device in enumerate(current_devices, 1):
            schema_dict[vol.Optional(f"device_{i}_name")] = str
            schema_dict[vol.Optional(f"device_{i}_standby")] = vol.All(
                vol.Coerce(float), vol.Range(min=0, max=100)
            )
        
        # Allow adding new devices
        schema_dict[vol.Optional("new_device_name")] = str
        schema_dict[vol.Optional("new_device_standby", default=0)] = vol.All(
            vol.Coerce(float), vol.Range(min=0, max=100)
        )

        return self.async_show_form(
            step_id="devices",
            data_schema=vol.Schema(schema_dict),
            description_placeholders={
                "current": f"Currently monitoring {len(current_devices)} devices"
            },
        )
