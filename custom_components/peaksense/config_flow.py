"""Config flow for PeakSense - NO CODE setup."""

import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.entity_registry import async_get

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class PeakSenseConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """PeakSense config flow."""

    VERSION = 1
    
    def __init__(self):
        self.power_meter = None
        self.devices = []

    async def async_step_user(self, user_input=None):
        """Step 1: Select power meter (can be sensor or helper)."""
        
        if user_input is not None:
            self.power_meter = user_input["power_meter"]
            return await self.async_step_devices()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("power_meter"): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["sensor", "input_number"],
                    )
                ),
            }),
            description_placeholders={
                "info": "Select your total power consumption sensor or helper (can be a calculation like grid - solar + battery)"
            },
        )

    async def async_step_devices(self, user_input=None):
        """Step 2: Add devices (optional, up to 5)."""
        
        if user_input is not None:
            # Collect devices from input
            devices = []
            for i in range(1, 6):
                name_key = f"device_{i}_name"
                if name_key in user_input and user_input[name_key]:
                    devices.append({
                        "name": user_input[name_key],
                        "standby_power": user_input.get(f"device_{i}_standby", 0)
                    })
            
            self.devices = devices
            
            # Create entry
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            
            return self.async_create_entry(
                title="PeakSense",
                data={
                    "power_meter": self.power_meter,
                    "devices": devices,
                }
            )

        # Build form with device slots
        schema_dict = {}
        for i in range(1, 6):
            schema_dict[vol.Optional(f"device_{i}_name")] = str
            schema_dict[vol.Optional(f"device_{i}_standby", default=0)] = vol.All(
                vol.Coerce(float), vol.Range(min=0, max=100)
            )

        return self.async_show_form(
            step_id="devices",
            data_schema=vol.Schema(schema_dict),
            description_placeholders={
                "info": "Add devices to monitor (optional, can be added later). Leave blank to skip."
            },
        )


class PeakSenseOptionsFlow(config_entries.OptionsFlow):
    """Options for PeakSense - manage devices after initial setup."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Init step."""
        return await self.async_step_manage_devices()

    async def async_step_manage_devices(self, user_input=None):
        """Manage devices."""
        
        if user_input is not None:
            # Collect devices
            devices = []
            for i in range(1, 6):
                name_key = f"device_{i}_name"
                if name_key in user_input and user_input[name_key]:
                    devices.append({
                        "name": user_input[name_key],
                        "standby_power": user_input.get(f"device_{i}_standby", 0)
                    })
            
            return self.async_create_entry(
                title="",
                data={
                    "power_meter": user_input.get("power_meter", self.config_entry.data.get("power_meter")),
                    "devices": devices,
                }
            )

        current_power_meter = self.config_entry.data.get("power_meter")
        current_devices = self.config_entry.data.get("devices", [])
        
        schema_dict = {
            vol.Optional("power_meter", default=current_power_meter): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain=["sensor", "input_number"],
                )
            ),
        }
        
        # Show existing devices for editing
        for i, device in enumerate(current_devices, 1):
            schema_dict[vol.Optional(f"device_{i}_name")] = str
            schema_dict[vol.Optional(f"device_{i}_standby", default=device.get("standby_power", 0))] = vol.All(
                vol.Coerce(float), vol.Range(min=0, max=100)
            )
        
        # Allow adding new devices (up to 5 total)
        for i in range(len(current_devices) + 1, 6):
            schema_dict[vol.Optional(f"device_{i}_name")] = str
            schema_dict[vol.Optional(f"device_{i}_standby", default=0)] = vol.All(
                vol.Coerce(float), vol.Range(min=0, max=100)
            )

        return self.async_show_form(
            step_id="manage_devices",
            data_schema=vol.Schema(schema_dict),
            description_placeholders={
                "info": f"Currently monitoring {len(current_devices)} device(s). Edit or add more."
            },
        )
