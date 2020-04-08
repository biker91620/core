"""The Téléinfo integration."""
import asyncio

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER, MIN_TIME_BETWEEN_UPDATES

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Téléinfo component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Téléinfo from a config entry."""
    from pyticcom import Teleinfo
    from pyticcom import UNIT_NONE

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    async def async_update_data():
        """Fetch data from API endpoint."""
        try:
            with Teleinfo(port=entry.data[CONF_DEVICE]) as teleinfo:
                return teleinfo.read_frame()

        except Exception as err:
            raise UpdateFailed(f"Error communicating with device: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        LOGGER,
        name="teleinformation sensor",
        update_method=async_update_data,
        update_interval=MIN_TIME_BETWEEN_UPDATES,
    )
    await coordinator.async_refresh()
    hass.data[DOMAIN][entry.unique_id] = coordinator

    frame = coordinator.data
    for group in frame.groups:
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
