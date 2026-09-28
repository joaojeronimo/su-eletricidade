# SU Eletricidade - Home Assistant Integration

Custom integration for Home Assistant providing real-time electricity price and tariff period sensors for **SU Eletricidade** (Portugal regulated market) in **Baixa Tensão Normal (BTN) Tri-Horário**.

## Features

- **Real-time Price Sensors**:
  - `sensor.su_eletricidade_<cycle>_period`: Current tariff period (`Ponta`, `Cheias`, or `Vazio`)
  - `sensor.su_eletricidade_<cycle>_total`: Current base price before IVA (€/kWh)
  - `sensor.su_eletricidade_<cycle>_total_c_iva_6`: Total price with 6% IVA (for first 200 kWh/month, contracts ≤ 6.9 kVA)
  - `sensor.su_eletricidade_<cycle>_total_c_iva_23`: Total price with 23% IVA (standard rate)
- **Official ERSE Schedules**:
  - **Ciclo Diário** (Default): Same schedule every day of the week.
  - **Ciclo Semanal**: Differentiated schedules for weekdays, Saturdays, and Sundays.
- **Automatic Seasonal Adjustments**:
  - Automatic daylight saving time (DST) detection for official summer and winter legal schedules in Portugal Continental.
- **Configurable Prices**:
  - Pre-filled with default 2026 BTN tri-horário rates:
    - **Ponta**: `0.2495 €/kWh`
    - **Cheias**: `0.1690 €/kWh`
    - **Vazio**: `0.1087 €/kWh`
  - Prices can be customized during setup or changed at any time via **Configure** (Options Flow) in Home Assistant.
- **Translations**: Full UI support in English and Portuguese.

---

## Installation via HACS

1. Open **HACS** in your Home Assistant.
2. Click the three dots in the top right corner > **Custom repositories**.
3. Add the repository URL:
   ```
   https://github.com/joaojeronimo/su-eletricidade
   ```
   - **Type**: `Integration`
4. Click **Add**, then search for **SU Eletricidade** and click **Download**.
5. Restart Home Assistant.
6. Go to **Settings** > **Devices & Services** > **+ Add Integration**.
7. Search for **SU Eletricidade** and follow the on-screen configuration.

---

## Manual Installation

1. Copy `custom_components/su_eletricidade` into your Home Assistant `<config_dir>/custom_components/` directory.
2. Restart Home Assistant.
3. Go to **Settings** > **Devices & Services** > **+ Add Integration**.
4. Search for **SU Eletricidade** and click to set up.

---

## Tariff Schedule Overview (Portugal Continental)

### Ciclo Diário
- **Winter**:
  - `00:00 - 08:00`: Vazio
  - `08:00 - 09:00`: Cheias
  - `09:00 - 10:30`: Ponta
  - `10:30 - 18:00`: Cheias
  - `18:00 - 20:30`: Ponta
  - `20:30 - 22:00`: Cheias
  - `22:00 - 24:00`: Vazio
- **Summer**:
  - `00:00 - 08:00`: Vazio
  - `08:00 - 10:30`: Cheias
  - `10:30 - 13:00`: Ponta
  - `13:00 - 19:30`: Cheias
  - `19:30 - 21:00`: Ponta
  - `21:00 - 22:00`: Cheias
  - `22:00 - 24:00`: Vazio

### Ciclo Semanal
- **Weekdays**:
  - *Winter*: Vazio (`00:00-07:00`), Cheias (`07:00-09:30`, `12:00-18:30`, `21:00-24:00`), Ponta (`09:30-12:00`, `18:30-21:00`)
  - *Summer*: Vazio (`00:00-07:00`), Cheias (`07:00-09:15`, `12:15-24:00`), Ponta (`09:15-12:15`)
- **Saturdays**:
  - *Winter*: Cheias (`09:30-13:00`, `18:30-22:00`), Vazio (all other hours)
  - *Summer*: Cheias (`09:00-14:00`, `20:00-22:00`), Vazio (all other hours)
- **Sundays**:
  - Vazio all day (`00:00-24:00`)
