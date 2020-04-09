"""The Téléinfo integration."""
import asyncio
import atexit
from datetime import timedelta

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Téléinfo component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Téléinfo from a config entry."""
    from pyticcom import UNIT_NONE

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    updater = DataUpdater(device=entry.data[CONF_DEVICE])
    updater.open()

    coordinator = DataUpdateCoordinator(
        hass,
        LOGGER,
        name="teleinformation sensor",
        update_method=updater.async_update_data,
        update_interval=timedelta(seconds=3),
    )

    hass.data[DOMAIN][entry.unique_id] = coordinator

    await coordinator.async_refresh()

    if coordinator.data is None:
        raise IOError("Unable to load coordinator")
    for group in coordinator.data.groups:
        if group.info.unit == UNIT_NONE:
            hass.states.async_set(DOMAIN + "." + group.info.name, group.value)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.unique_id)

    return unload_ok


class DataUpdater:
    """This class is responsible to update teleinfo data."""

    def __init__(self, device):
        """Initialize data updater."""
        from pyticcom import Teleinfo

        self.teleinfo = Teleinfo(port=device)

        def shutdown():
            LOGGER.debug("Shutting down teleinfo")
            self.teleinfo.close()

        atexit.register(shutdown)

    def open(self):
        """Open serial port."""
        LOGGER.debug("Opening serial port")
        self.teleinfo.open()

    def close(self):
        """Close serial port."""
        LOGGER.debug("Closing serial port")
        self.teleinfo.close()

    async def async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            LOGGER.debug("Reading tic frame")
            return await self.teleinfo.read_frame()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with device: {err}")
