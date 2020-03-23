"""Support for Cozytouch switches."""
from homeassistant.components.cozytouch.device import DeviceInfo
from homeassistant.components.switch import SwitchDevice

from .const import DOMAIN, LOGGER


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Old way of setting up deCONZ platforms."""


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up switches for Cozytouch component.

    Switches are based same device class as heater in Cozytouch.
    """
    setup = hass.data[DOMAIN][config_entry.unique_id]
    entities = []

    for heater in setup.heaters:
        entities.append(CozytouchSwitch(heater))

    async_add_entities(entities, True)


class CozytouchSwitch(DeviceInfo, SwitchDevice):
    """Header switch (on/off)."""

    def __init__(self, heater):
        """Initialize switch."""
        super(CozytouchSwitch, self).__init__(heater)
        self.heater = heater

    @property
    def unique_id(self):
        """Return the unique id of this switch."""
        return self.heater.id + "_switch"

    @property
    def name(self):
        """Return the display name of this switch."""
        return self.heater.name

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self.heater.is_on

    @property
    def device_class(self):
        """Return the device class."""
        return "heat"

    def turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        self.heater.turn_on()

    def turn_off(self, **kwargs):
        """Turn the entity off."""
        self.heater.turn_off()

    async def async_device_update(self, warning=True):
        """Fetch new state data for this heater."""
        LOGGER.info("Update switch {name}".format(name=self.name))
        await self.heater.async_update()
