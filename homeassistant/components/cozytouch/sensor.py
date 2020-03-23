"""Support for Cozytouch sensors."""
from homeassistant.components.cozytouch.device import DeviceInfo
from homeassistant.const import DEVICE_CLASS_POWER, TEMP_CELSIUS
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, KW_UNIT, LOGGER


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Old way of setting up deCONZ platforms."""


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensors for Cozytouch component."""
    from cozypy.constant import DeviceType

    setup = hass.data[DOMAIN][config_entry.unique_id]
    entities = []

    for heater in setup.heaters:
        for sensor in heater.sensors:
            if sensor.widget == DeviceType.TEMPERATURE:
                entities.append(CozyTouchTemperatureSensor(sensor))
            elif sensor.widget == DeviceType.ELECTRICITY:
                entities.append(CozyTouchElectricitySensor(sensor))

    LOGGER.info("Found {count} sensors".format(count=len(entities)))

    async_add_entities(entities, True)


class CozyTouchTemperatureSensor(DeviceInfo, Entity):
    """Representation of a temperature sensor."""

    def __init__(self, sensor):
        """Initialize temperature sensor."""
        super(CozyTouchTemperatureSensor, self).__init__(sensor)
        self.sensor = sensor

    @property
    def unique_id(self):
        """Return the unique id of this sensor."""
        return self.sensor.id

    @property
    def name(self):
        """Return the display name of this sensor."""
        return self.sensor.name

    @property
    def state(self):
        """Return the temperature."""
        return self.sensor.temperature

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    async def async_device_update(self, warning=True):
        """Fetch new state data for this sensor."""
        LOGGER.info("Update sensor {name}".format(name=self.name))
        await self.sensor.async_update()


class CozyTouchElectricitySensor(DeviceInfo, Entity):
    """Representation of an electricity Sensor."""

    def __init__(self, sensor):
        """Initialize the sensor."""
        super(CozyTouchElectricitySensor, self).__init__(sensor)
        self.sensor = sensor

    @property
    def unique_id(self):
        """Return the unique id of this sensor."""
        return self.sensor.id

    @property
    def name(self):
        """Return the display name of this sensor."""
        return self.sensor.name

    @property
    def device_class(self):
        """Return the device class."""
        return DEVICE_CLASS_POWER

    @property
    def state(self):
        """Return the electricity consumption."""
        return self.sensor.consumption / 1000

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return KW_UNIT

    async def async_device_update(self, warning=True):
        """Fetch new state data for this sensor."""
        LOGGER.info("Update sensor {name}".format(name=self.name))
        await self.sensor.async_update()
