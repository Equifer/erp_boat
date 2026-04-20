"""Config flow for ERP Boat integration."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    CONF_ENABLE_MAINTENANCE,
    CONF_ENABLE_INVENTORY,
    CONF_ENABLE_TANKS,
    CONF_ENABLE_DOCUMENTS,
    DEFAULT_ENABLE_MAINTENANCE,
    DEFAULT_ENABLE_INVENTORY,
    DEFAULT_ENABLE_TANKS,
    DEFAULT_ENABLE_DOCUMENTS,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ENABLE_MAINTENANCE, default=DEFAULT_ENABLE_MAINTENANCE): bool,
        vol.Required(CONF_ENABLE_INVENTORY, default=DEFAULT_ENABLE_INVENTORY): bool,
        vol.Required(CONF_ENABLE_TANKS, default=DEFAULT_ENABLE_TANKS): bool,
        vol.Required(CONF_ENABLE_DOCUMENTS, default=DEFAULT_ENABLE_DOCUMENTS): bool,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ERP Boat."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ):
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        return self.async_create_entry(title="ERP Boat", data=user_input)
