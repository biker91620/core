"""Config flow for Téléinfo integration."""
import voluptuous as vol

from homeassistant import config_entries, core, exceptions
from homeassistant.const import CONF_DEVICE, CONF_SCAN_INTERVAL

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, LOGGER

DATA_SCHEMA = vol.Schema({CONF_DEVICE: str})


async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to read teleinfo frame."""
    from pyticcom import Teleinfo

    try:
        with Teleinfo(data[CONF_DEVICE]) as tic:
            await tic.read_frame()
    except Exception as e:
        raise InvalidSerialDevice(str(e))

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
                option = serial.device
                if serial.product is not None:
                    option = "{device} ({product})".format(
                        device=serial.device, product=serial.product
                    )
                self._options[serial.device] = option

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_DEVICE): vol.In(self._options),
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                    ): int,
                }
            ),
            errors=errors,
        )


class InvalidSerialDevice(exceptions.HomeAssistantError):
    """Error to indicate we cannot read teleinfo from device."""
