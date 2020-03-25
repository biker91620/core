"""The CozyTouch integration."""
import asyncio

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

from .const import DOMAIN

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

PLATFORMS = ["switch", "sensor", "climate", "binary_sensor"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the CozyTouch component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up CozyTouch from a config entry."""
    from cozypy import CozytouchClient

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    client = CozytouchClient(entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD])
    hass.data[DOMAIN][entry.unique_id] = await client.async_get_setup()

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

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
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
