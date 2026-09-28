"""Config flow for SU Eletricidade."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_CYCLE,
    CONF_PRICE_CHEIAS,
    CONF_PRICE_PONTA,
    CONF_PRICE_VAZIO,
    CYCLE_DIARIO,
    CYCLE_OPTIONS,
    DEFAULT_NAME,
    DEFAULT_PRICE_CHEIAS,
    DEFAULT_PRICE_PONTA,
    DEFAULT_PRICE_VAZIO,
    DOMAIN,
)


def _build_schema(
    cycle: str = CYCLE_DIARIO,
    price_ponta: float = DEFAULT_PRICE_PONTA,
    price_cheias: float = DEFAULT_PRICE_CHEIAS,
    price_vazio: float = DEFAULT_PRICE_VAZIO,
) -> vol.Schema:
    """Build the configuration schema."""
    cycle_options = [
        selector.SelectOptionDict(value=k, label=v)
        for k, v in CYCLE_OPTIONS.items()
    ]

    return vol.Schema(
        {
            vol.Required(CONF_CYCLE, default=cycle): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=cycle_options,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                ),
            ),
            vol.Required(
                CONF_PRICE_PONTA, default=price_ponta
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0.0,
                    max=2.0,
                    step=0.0001,
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="€/kWh",
                ),
            ),
            vol.Required(
                CONF_PRICE_CHEIAS, default=price_cheias
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0.0,
                    max=2.0,
                    step=0.0001,
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="€/kWh",
                ),
            ),
            vol.Required(
                CONF_PRICE_VAZIO, default=price_vazio
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0.0,
                    max=2.0,
                    step=0.0001,
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="€/kWh",
                ),
            ),
        }
    )


class SuEletricidadeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SU Eletricidade."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get options flow handler."""
        return SuEletricidadeOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            cycle = user_input[CONF_CYCLE]
            cycle_label = CYCLE_OPTIONS[cycle]

            await self.async_set_unique_id(f"su_eletricidade_{cycle}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"{DEFAULT_NAME} {cycle_label}",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(),
            errors=errors,
        )


class SuEletricidadeOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for SU Eletricidade."""

    def __init__(self, config_entry: config_entries.ConfigEntry | None = None) -> None:
        """Initialize options flow."""
        if config_entry is not None:
            self._config_entry = config_entry

    @property
    def config_entry(self) -> config_entries.ConfigEntry:
        """Return the config entry."""
        return getattr(self, "_config_entry", None) or super().config_entry


    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        cycle = self.config_entry.options.get(
            CONF_CYCLE,
            self.config_entry.data.get(CONF_CYCLE, CYCLE_DIARIO),
        )
        price_ponta = self.config_entry.options.get(
            CONF_PRICE_PONTA,
            self.config_entry.data.get(CONF_PRICE_PONTA, DEFAULT_PRICE_PONTA),
        )
        price_cheias = self.config_entry.options.get(
            CONF_PRICE_CHEIAS,
            self.config_entry.data.get(CONF_PRICE_CHEIAS, DEFAULT_PRICE_CHEIAS),
        )
        price_vazio = self.config_entry.options.get(
            CONF_PRICE_VAZIO,
            self.config_entry.data.get(CONF_PRICE_VAZIO, DEFAULT_PRICE_VAZIO),
        )

        return self.async_show_form(
            step_id="init",
            data_schema=_build_schema(
                cycle=cycle,
                price_ponta=price_ponta,
                price_cheias=price_cheias,
                price_vazio=price_vazio,
            ),
        )
