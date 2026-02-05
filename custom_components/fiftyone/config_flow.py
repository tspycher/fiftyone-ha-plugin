"""Config flow for FiftyOne integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import FiftyOneApiClient
from .const import API_BASE_URL, CONF_API_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_API_URL, default=API_BASE_URL): str,
    }
)


class FiftyOneConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for FiftyOne."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Check if already configured
            await self.async_set_unique_id(user_input[CONF_API_URL])
            self._abort_if_unique_id_configured()

            # Test the connection
            session = async_get_clientsession(self.hass)
            client = FiftyOneApiClient(
                session=session,
                api_url=user_input[CONF_API_URL],
            )

            if await client.async_test_connection():
                return self.async_create_entry(
                    title="FiftyOne",
                    data=user_input,
                )
            else:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
