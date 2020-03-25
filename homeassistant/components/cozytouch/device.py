"""Support for Device info."""
from .const import DOMAIN, LOGGER


class DeviceInfo:
    """Helper class for managing device info."""

    def __init__(self, device):
        """Initialize device info."""
        self.device = device

    @property
    def device_info(self):
        """Return a device description for device registry."""
        if self.device is None:
            return None

        dev = self.device.parent if self.device.parent is not None else self.device

        info = {
            "identifiers": {(DOMAIN, dev.id)},
            "manufacturer": dev.manufacturer,
            "model": dev.model,
            "name": dev.name,
            "sw_version": dev.version,
            "via_device": (
                DOMAIN,
                self.device.parent.id
                if self.device.parent is not None
                else self.device.gateway.id,
            ),
        }
        LOGGER.debug(info)
        return info
