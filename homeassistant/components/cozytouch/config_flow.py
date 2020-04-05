"""Config flow for CozyTouch integration."""
import logging

import voluptuous as vol

from homeassistant import config_entries, core, exceptions
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({CONF_USERNAME: str, CONF_PASSWORD: str})


async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect."""
    from cozypy import CozytouchClient
    from cozypy.exception import CozytouchException

    try:
        client = CozytouchClient(data[CONF_USERNAME], data[CONF_PASSWORD])
        return await client.async_get_setup()
    except CozytouchException:
        raise InvalidAuth


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CozyTouch."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_UNKNOWN

    def __init__(self):
        """Initialize the Cozytouch config flow."""
        self.gateway_id = None

    async def _create_entry(self, setup, data):
        """Create entry for gateway."""
        if not self.gateway_id:
            if setup is None or len(setup.gateways) == 0:
                return self.async_abort(reason="no_gateways")
            self.gateway_id = setup.gateways[0].id
            await self.async_set_unique_id(self.gateway_id)

            self._abort_if_unique_id_configured()

        return self.async_create_entry(title=self.gateway_id, data=data)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                setup = await validate_input(self.hass, user_input)
                return await self._create_entry(setup=setup, data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""
