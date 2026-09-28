"""Sensor platform for SU Eletricidade."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.util import dt as dt_util

from .const import (
    CONF_CYCLE,
    CONF_PRICE_CHEIAS,
    CONF_PRICE_PONTA,
    CONF_PRICE_VAZIO,
    CYCLE_DIARIO,
    CYCLE_OPTIONS,
    CYCLE_SEMANAL,
    DEFAULT_PRICE_CHEIAS,
    DEFAULT_PRICE_PONTA,
    DEFAULT_PRICE_VAZIO,
    DOMAIN,
    IVA_6_MULTIPLIER,
    IVA_23_MULTIPLIER,
    PERIOD_CHEIAS,
    PERIOD_LABELS,
    PERIOD_PONTA,
    PERIOD_VAZIO,
)

# Official BTN tri-horário daily cycle for Portugal Continental.
_TRI_DAILY_SCHEDULE = {
    "winter": (
        (8 * 60, 9 * 60, PERIOD_CHEIAS),
        (9 * 60, 10 * 60 + 30, PERIOD_PONTA),
        (10 * 60 + 30, 18 * 60, PERIOD_CHEIAS),
        (18 * 60, 20 * 60 + 30, PERIOD_PONTA),
        (20 * 60 + 30, 22 * 60, PERIOD_CHEIAS),
    ),
    "summer": (
        (8 * 60, 10 * 60 + 30, PERIOD_CHEIAS),
        (10 * 60 + 30, 13 * 60, PERIOD_PONTA),
        (13 * 60, 19 * 60 + 30, PERIOD_CHEIAS),
        (19 * 60 + 30, 21 * 60, PERIOD_PONTA),
        (21 * 60, 22 * 60, PERIOD_CHEIAS),
    ),
}

# Official BTN tri-horário weekly cycle for Portugal Continental.
_TRI_WEEKLY_SCHEDULE = {
    "winter": {
        "weekday": (
            (7 * 60, 9 * 60 + 30, PERIOD_CHEIAS),
            (9 * 60 + 30, 12 * 60, PERIOD_PONTA),
            (12 * 60, 18 * 60 + 30, PERIOD_CHEIAS),
            (18 * 60 + 30, 21 * 60, PERIOD_PONTA),
            (21 * 60, 24 * 60, PERIOD_CHEIAS),
        ),
        "saturday": (
            (9 * 60 + 30, 13 * 60, PERIOD_CHEIAS),
            (18 * 60 + 30, 22 * 60, PERIOD_CHEIAS),
        ),
        "sunday": (),
    },
    "summer": {
        "weekday": (
            (7 * 60, 9 * 60 + 15, PERIOD_CHEIAS),
            (9 * 60 + 15, 12 * 60 + 15, PERIOD_PONTA),
            (12 * 60 + 15, 24 * 60, PERIOD_CHEIAS),
        ),
        "saturday": (
            (9 * 60, 14 * 60, PERIOD_CHEIAS),
            (20 * 60, 22 * 60, PERIOD_CHEIAS),
        ),
        "sunday": (),
    },
}


def _now() -> datetime:
    """Return Home Assistant local time."""
    return dt_util.now()


def _is_summer(dt: datetime) -> bool:
    """Check if datetime is in Portugal legal summer time."""
    return bool(dt.dst())


def _tri_periodo_diario(dt: datetime) -> str:
    """Return current tri-horário period for Ciclo Diário."""
    t = dt.hour * 60 + dt.minute
    schedule_key = "summer" if _is_summer(dt) else "winter"
    for start, end, period in _TRI_DAILY_SCHEDULE[schedule_key]:
        if start <= t < end:
            return period
    return PERIOD_VAZIO


def _tri_periodo_semanal(dt: datetime) -> str:
    """Return current tri-horário period for Ciclo Semanal."""
    weekday = dt.weekday()
    season = "summer" if _is_summer(dt) else "winter"

    if weekday < 5:
        day_key = "weekday"
    elif weekday == 5:
        day_key = "saturday"
    else:
        day_key = "sunday"

    schedule = _TRI_WEEKLY_SCHEDULE[season][day_key]
    t = dt.hour * 60 + dt.minute
    for start, end, period in schedule:
        if start <= t < end:
            return period
    return PERIOD_VAZIO


def get_current_period(cycle: str, dt: datetime) -> str:
    """Get current period based on cycle and datetime."""
    if cycle == CYCLE_SEMANAL:
        return _tri_periodo_semanal(dt)
    return _tri_periodo_diario(dt)


def _get_entry_value(entry: ConfigEntry, key: str, default: Any) -> Any:
    """Get value from options with fallback to data and default."""
    return entry.options.get(key, entry.data.get(key, default))


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SU Eletricidade sensors from a config entry."""
    cycle = _get_entry_value(entry, CONF_CYCLE, CYCLE_DIARIO)
    cycle_label = CYCLE_OPTIONS.get(cycle, "Ciclo Diário")

    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=f"SU Eletricidade {cycle_label}",
        manufacturer="SU Eletricidade",
        model="BTN Tri-Horário",
        entry_type=DeviceEntryType.SERVICE,
    )

    entities: list[SensorEntity] = [
        SuEletricidadePeriodSensor(entry, device_info),
        SuEletricidadeTotalSensor(entry, device_info),
        SuEletricidadeIva6Sensor(entry, device_info),
        SuEletricidadeIva23Sensor(entry, device_info),
    ]

    async_add_entities(entities, True)


class SuEletricidadeBaseSensor(SensorEntity):
    """Base class for SU Eletricidade sensors."""

    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry, device_info: DeviceInfo) -> None:
        """Initialize the base sensor."""
        self._entry = entry
        self._attr_device_info = device_info

    @property
    def cycle(self) -> str:
        """Return configured cycle."""
        return _get_entry_value(self._entry, CONF_CYCLE, CYCLE_DIARIO)

    @property
    def price_ponta(self) -> float:
        """Return configured Ponta price."""
        return float(
            _get_entry_value(self._entry, CONF_PRICE_PONTA, DEFAULT_PRICE_PONTA)
        )

    @property
    def price_cheias(self) -> float:
        """Return configured Cheias price."""
        return float(
            _get_entry_value(
                self._entry, CONF_PRICE_CHEIAS, DEFAULT_PRICE_CHEIAS
            )
        )

    @property
    def price_vazio(self) -> float:
        """Return configured Vazio price."""
        return float(
            _get_entry_value(self._entry, CONF_PRICE_VAZIO, DEFAULT_PRICE_VAZIO)
        )

    def get_price_for_period(self, period: str) -> float:
        """Return base price for given period."""
        if period == PERIOD_PONTA:
            return self.price_ponta
        if period == PERIOD_CHEIAS:
            return self.price_cheias
        return self.price_vazio

    async def async_added_to_hass(self) -> None:
        """Track periodic clock updates."""
        self.async_on_remove(
            async_track_time_change(
                self.hass,
                self._handle_time_update,
                minute=[0, 15, 30, 45],
                second=0,
            )
        )
        self._update_state()

    @callback
    def _handle_time_update(self, now: datetime) -> None:
        """Handle time-driven tariff changes."""
        self._update_state()
        self.async_write_ha_state()

    def _update_state(self) -> None:
        """Override in subclasses to update state."""


class SuEletricidadePeriodSensor(SuEletricidadeBaseSensor):
    """Sensor that shows current tariff period."""

    _attr_icon = "mdi:clock-outline"
    _attr_name = "Period"

    def __init__(self, entry: ConfigEntry, device_info: DeviceInfo) -> None:
        """Initialize the period sensor."""
        super().__init__(entry, device_info)
        self._attr_unique_id = f"{entry.entry_id}_period"

    def _update_state(self) -> None:
        dt = _now()
        period = get_current_period(self.cycle, dt)
        self._attr_native_value = PERIOD_LABELS.get(period, period)
        self._attr_extra_state_attributes = {
            "period": period,
            "cycle": self.cycle,
            "season": "summer" if _is_summer(dt) else "winter",
        }


class SuEletricidadePriceSensor(SuEletricidadeBaseSensor):
    """Base class for price sensors (€/kWh)."""

    _attr_native_unit_of_measurement = "€/kWh"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 4
    _attr_icon = "mdi:currency-eur"


class SuEletricidadeTotalSensor(SuEletricidadePriceSensor):
    """Current electricity price before VAT."""

    _attr_name = "Total"

    def __init__(self, entry: ConfigEntry, device_info: DeviceInfo) -> None:
        """Initialize the total sensor."""
        super().__init__(entry, device_info)
        self._attr_unique_id = f"{entry.entry_id}_total"

    def _update_state(self) -> None:
        dt = _now()
        period = get_current_period(self.cycle, dt)
        price = self.get_price_for_period(period)
        self._attr_native_value = round(price, 4)
        self._attr_extra_state_attributes = {
            "period": period,
            "price_ponta": self.price_ponta,
            "price_cheias": self.price_cheias,
            "price_vazio": self.price_vazio,
        }


class SuEletricidadeIva6Sensor(SuEletricidadePriceSensor):
    """Total price with 6% VAT (first 200 kWh/month, <= 6.9 kVA)."""

    _attr_name = "Total c/ IVA 6%"

    def __init__(self, entry: ConfigEntry, device_info: DeviceInfo) -> None:
        """Initialize the 6% VAT sensor."""
        super().__init__(entry, device_info)
        self._attr_unique_id = f"{entry.entry_id}_iva6"

    def _update_state(self) -> None:
        dt = _now()
        period = get_current_period(self.cycle, dt)
        price = self.get_price_for_period(period)
        self._attr_native_value = round(price * IVA_6_MULTIPLIER, 4)
        self._attr_extra_state_attributes = {
            "period": period,
            "description": "First 200 kWh/month (contracts \u2264 6.9 kVA)",
            "vat_rate": 0.06,
        }


class SuEletricidadeIva23Sensor(SuEletricidadePriceSensor):
    """Total price with 23% VAT (beyond 200 kWh/month)."""

    _attr_name = "Total c/ IVA 23%"

    def __init__(self, entry: ConfigEntry, device_info: DeviceInfo) -> None:
        """Initialize the 23% VAT sensor."""
        super().__init__(entry, device_info)
        self._attr_unique_id = f"{entry.entry_id}_iva23"

    def _update_state(self) -> None:
        dt = _now()
        period = get_current_period(self.cycle, dt)
        price = self.get_price_for_period(period)
        self._attr_native_value = round(price * IVA_23_MULTIPLIER, 4)
        self._attr_extra_state_attributes = {
            "period": period,
            "description": "Beyond 200 kWh/month",
            "vat_rate": 0.23,
        }
