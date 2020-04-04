"""Support for Cozytouch binary sensors."""
from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.components.cozytouch.device import DeviceInfo

from .const import DOMAIN, LOGGER


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Old way of setting up Cozytouch platforms."""


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up binary sensors for Cozytouch component."""
    from cozypy.constant import DeviceType

    setup = hass.data[DOMAIN][config_entry.unique_id]
    entities = []

    for sensor in setup.sensors:
        if sensor.widget == DeviceType.OCCUPANCY:
            entities.append(CozytouchOccupancySensor(sensor))
        elif sensor.widget == DeviceType.CONTACT:
            entities.append(CozytouchContactSensor(sensor))

    LOGGER.debug("Found {count} binary sensors".format(count=len(entities)))

    async_add_entities(entities, True)


class CozytouchOccupancySensor(DeviceInfo, BinarySensorDevice):
    """Occupancy sensor (present/not present)."""

    device_class = "motion"

    def __init__(self, sensor):
        """Initialize occupancy sensor."""
        super(CozytouchOccupancySensor, self).__init__(sensor)
        self.sensor = sensor

    @property
    def unique_id(self):
        """Return the unique id of this binary sensor."""
        return self.sensor.id

    @property
    def name(self):
        """Return the display name of this binary sensor."""
        return self.sensor.name

    @property
    def is_on(self):
        """Return true if area is occupied."""
        return self.sensor.is_occupied

    async def async_device_update(self, warning=True):
        """Fetch new state data for this sensor."""
        LOGGER.debug("Update binary sensor {name}".format(name=self.name))
        await self.sensor.async_update()


class CozytouchContactSensor(DeviceInfo, BinarySensorDevice):
    """Contact sensor (window open/close)."""

    device_class = "window"

    def __init__(self, sensor):
        """Initialize window sensor."""
        super(CozytouchContactSensor, self).__init__(sensor)
        self.sensor = sensor

    @property
    def unique_id(self):
        """Return the unique id of this binary sensor."""
        return self.sensor.id

    @property
    def name(self):
        """Return the display name of this binary sensor."""
        return self.sensor.name

    @property
    def is_on(self):
        """Return true if window is opened."""
        return self.sensor.is_opened

    async def async_device_update(self, warning=True):
        """Fetch new state data for this sensor."""
        LOGGER.debug("Update binary sensor {name}".format(name=self.name))
        await self.sensor.async_update()
