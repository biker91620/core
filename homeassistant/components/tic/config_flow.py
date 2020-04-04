"""Config flow for Téléinfo integration."""
import voluptuous as vol

from homeassistant import config_entries, core, exceptions
from homeassistant.const import CONF_DEVICE

from .const import DOMAIN, LOGGER

DATA_SCHEMA = vol.Schema({CONF_DEVICE: str})


async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to read teleinfo frame."""

    from ticpy import Teleinfo

    try:
        with Teleinfo(data[CONF_DEVICE]) as tic:
            tic.read_frame()
    except Exception as e:
        raise BadDevice(str(e))

    return True


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Téléinfo."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_UNKNOWN

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""

        errors = {}
        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)

                return self.async_create_entry(title="Teleinfo", data=user_input)
            except Exception:
                LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class BadDevice(exceptions.HomeAssistantError):
    """Error to indicate we cannot read teleinfo from device."""
