"""Support for Teleinfo sensors."""
from homeassistant.const import CONF_DEVICE, DEVICE_CLASS_POWER, STATE_UNKNOWN
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, LOGGER


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Old way of setting up ticpy platforms."""


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensors for the teleinformation."""
    from pyticcom import UNIT_NONE
    from pyticcom.scanner import ComScanner

    device = config_entry.data.get(CONF_DEVICE)
    scanner = ComScanner()
    coordinator = hass.data[DOMAIN][config_entry.unique_id]
    frame = coordinator.data
    if frame is not None:
        entities = []
        for group in frame.groups:
            if group.info.unit != UNIT_NONE:
                entities.append(
                    TeleinfoSensor(
                        coordinator, device=device, info=group.info, scanner=scanner
                    )
                )

        async_add_entities(entities, True)


class TeleinfoSensor(Entity):
    """Representation of an electricity Sensor."""

    def __init__(self, coordinator, device, info, scanner):
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._device = device
        self._info = info
        self._scanner = scanner

    @property
    def unique_id(self):
        """Return the unique id of this sensor."""
        return self._device + "_" + self._info.name

    @property
    def name(self):
        """Return the display name of this sensor."""
        return self._info.description

    @property
    def device_class(self):
        """Return the device class."""
        return DEVICE_CLASS_POWER

    @property
    def state(self):
        """Return the electricity consumption."""
        group = self._coordinator.data.get(self._info)
        if group is None:
            return STATE_UNKNOWN
        state = int(group.value)
        return state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._info.unit

    @property
    def should_poll(self):
        """No need to poll. Coordinator notifies entity of updates."""
        return self._coordinator.last_update_success

    @property
    def available(self):
        """Return if entity is available."""
        return True  # self._coordinator.last_update_success

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self._coordinator.async_add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """When entity will be removed from hass."""
        self._coordinator.async_remove_listener(self.async_write_ha_state)

    async def async_update(self):
        """Update the entity.

        Only used by the generic entity update service.
        """
        await self._coordinator.async_request_refresh()

    @property
    def device_info(self):
        """Return a device description for device registry."""
        serial = self._scanner.find_serial(self._device)
        if serial is None:
            return {"identifiers": {(DOMAIN, self._device)}}
        info = {
            "identifiers": {(DOMAIN, self._device)},
            "manufacturer": serial.manufacturer,
            "model": serial.product,
            "name": serial.name,
            "sw_version": serial.vid,
        }
        LOGGER.debug(info)
        return info
