"""Constants for the Téléinfo integration."""
from datetime import timedelta
import logging

LOGGER = logging.getLogger(__package__)

DOMAIN = "tic"

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=5)

CONF_ATTRIBUTION = "EDF Teleinfo."
