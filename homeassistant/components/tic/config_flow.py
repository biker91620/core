"""Config flow for Téléinfo integration."""
import voluptuous as vol

from homeassistant import config_entries, core, exceptions
from homeassistant.const import CONF_DEVICE

from .const import DOMAIN, LOGGER

DATA_SCHEMA = vol.Schema({CONF_DEVICE: str})


async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to read teleinfo frame."""
    from pyticcom import Teleinfo

    try:
        with Teleinfo(data[CONF_DEVICE]) as tic:
            tic.read_frame()
    except Exception as e:
        raise BadDevice(str(e))

    return True


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Téléinfo."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    _options = None

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

        if self._options is None:
            from pyticcom.scanner import ComScanner

            scanner = ComScanner()
            serials = scanner.scan()
            self._options = {}
            for idx, serial in enumerate(serials):
                name = serial.device
                if serial.name is not None:
                    name = "{device} ({name})".format(
                        device=serial.device, name=serial.name
                    )
                self._options[serial.device] = name

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_DEVICE): vol.In(self._options)}),
            errors=errors,
        )


class BadDevice(exceptions.HomeAssistantError):
    """Error to indicate we cannot read teleinfo from device."""
