"""Config flow for FiftyOne integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import FiftyOneApiClient
from .const import API_BASE_URL, CONF_API_URL, CONF_IMAGE_SOURCES, DOMAIN

_LOGGER = logging.getLogger(__name__)


class FiftyOneConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for FiftyOne."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict[str, Any] = {}
        self._image_sources: list[dict[str, str]] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step - API configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Test the connection
            session = async_get_clientsession(self.hass)
            client = FiftyOneApiClient(
                session=session,
                api_url=user_input[CONF_API_URL],
            )

            if await client.async_test_connection():
                self._data[CONF_API_URL] = user_input[CONF_API_URL]
                return await self.async_step_image_sources()
            else:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_API_URL, default=API_BASE_URL): str,
                }
            ),
            errors=errors,
        )

    async def async_step_image_sources(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle adding image sources."""
        errors: dict[str, str] = {}

        if user_input is not None:
            if user_input.get("add_source"):
                # User wants to add a source
                code = user_input.get("code", "").strip()
                name = user_input.get("name", "").strip() or code

                if code:
                    # Check for duplicate codes
                    existing_codes = [s["code"] for s in self._image_sources]
                    if code in existing_codes:
                        errors["code"] = "duplicate_code"
                    else:
                        self._image_sources.append({"code": code, "name": name})

                if not errors:
                    return await self.async_step_image_sources()
            else:
                # User is done adding sources, finish setup
                self._data[CONF_IMAGE_SOURCES] = self._image_sources

                # Set unique ID based on API URL
                await self.async_set_unique_id(self._data[CONF_API_URL])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="FiftyOne",
                    data=self._data,
                )

        # Build description with current sources
        if self._image_sources:
            source_list = ", ".join([s["name"] for s in self._image_sources])
            sources_text = f"Current sources: {source_list}"
        else:
            sources_text = ""

        return self.async_show_form(
            step_id="image_sources",
            data_schema=vol.Schema(
                {
                    vol.Optional("code"): str,
                    vol.Optional("name"): str,
                    vol.Optional("add_source", default=False): bool,
                }
            ),
            errors=errors,
            description_placeholders={"sources": sources_text},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return FiftyOneOptionsFlow(config_entry)


class FiftyOneOptionsFlow(OptionsFlow):
    """Handle options flow for FiftyOne."""

    def __init__(self, config_entry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry
        self._image_sources: list[dict[str, str]] = list(
            config_entry.data.get(CONF_IMAGE_SOURCES, [])
        )

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        return await self.async_step_image_sources(user_input)

    async def async_step_image_sources(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle adding/removing image sources."""
        errors: dict[str, str] = {}

        if user_input is not None:
            action = user_input.get("action", "done")

            if action == "add":
                code = user_input.get("code", "").strip()
                name = user_input.get("name", "").strip() or code

                if code:
                    existing_codes = [s["code"] for s in self._image_sources]
                    if code in existing_codes:
                        errors["code"] = "duplicate_code"
                    else:
                        self._image_sources.append({"code": code, "name": name})

                if not errors:
                    return await self.async_step_image_sources()

            elif action == "remove":
                remove_code = user_input.get("remove_code")
                if remove_code:
                    self._image_sources = [
                        s for s in self._image_sources if s["code"] != remove_code
                    ]
                return await self.async_step_image_sources()

            else:  # done
                # Update the config entry with new data
                new_data = dict(self._config_entry.data)
                new_data[CONF_IMAGE_SOURCES] = self._image_sources

                self.hass.config_entries.async_update_entry(
                    self._config_entry,
                    data=new_data,
                )

                return self.async_create_entry(title="", data={})

        # Build schema with current sources for removal
        source_options = {s["code"]: s["name"] for s in self._image_sources}

        schema_dict: dict[Any, Any] = {
            vol.Optional("code"): str,
            vol.Optional("name"): str,
        }

        if source_options:
            schema_dict[vol.Optional("remove_code")] = vol.In(source_options)

        schema_dict[vol.Required("action", default="done")] = vol.In(
            {"add": "Add source", "remove": "Remove source", "done": "Finish"}
        )

        # Build description
        if self._image_sources:
            source_list = ", ".join([f"{s['name']} ({s['code']})" for s in self._image_sources])
            sources_text = f"Current sources: {source_list}"
        else:
            sources_text = "No sources configured."

        return self.async_show_form(
            step_id="image_sources",
            data_schema=vol.Schema(schema_dict),
            errors=errors,
            description_placeholders={"sources": sources_text},
        )
