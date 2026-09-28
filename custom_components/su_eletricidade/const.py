"""Constants for SU Eletricidade integration."""

from typing import Final

DOMAIN: Final = "su_eletricidade"
DEFAULT_NAME: Final = "SU Eletricidade"

# Default BTN Tri-Horário tariff prices (EUR/kWh before VAT)
DEFAULT_PRICE_PONTA: Final = 0.2495
DEFAULT_PRICE_CHEIAS: Final = 0.1690
DEFAULT_PRICE_VAZIO: Final = 0.1087

# VAT rates in Portugal
IVA_6_MULTIPLIER: Final = 1.06
IVA_23_MULTIPLIER: Final = 1.23

# Configuration keys
CONF_CYCLE: Final = "cycle"
CONF_PRICE_PONTA: Final = "price_ponta"
CONF_PRICE_CHEIAS: Final = "price_cheias"
CONF_PRICE_VAZIO: Final = "price_vazio"

# Cycle types
CYCLE_DIARIO: Final = "diario"
CYCLE_SEMANAL: Final = "semanal"

CYCLE_OPTIONS: Final = {
    CYCLE_DIARIO: "Ciclo Diário",
    CYCLE_SEMANAL: "Ciclo Semanal",
}

# Period definitions
PERIOD_PONTA: Final = "ponta"
PERIOD_CHEIAS: Final = "cheias"
PERIOD_VAZIO: Final = "vazio"

PERIOD_LABELS: Final = {
    PERIOD_PONTA: "Ponta",
    PERIOD_CHEIAS: "Cheias",
    PERIOD_VAZIO: "Vazio",
}
