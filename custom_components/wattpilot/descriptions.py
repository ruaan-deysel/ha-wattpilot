"""Entity descriptions for the Fronius Wattpilot integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntityDescription,
)
from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.components.select import SelectEntityDescription
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.components.switch import SwitchEntityDescription
from homeassistant.components.update import (
    UpdateDeviceClass,
    UpdateEntityDescription,
)
from homeassistant.const import (
    EntityCategory,
)

# ---------------------------------------------------------------------------
# Source type constants
# ---------------------------------------------------------------------------
SOURCE_PROPERTY = "property"
SOURCE_ATTRIBUTE = "attribute"
SOURCE_NAMESPACELIST = "namespacelist"
SOURCE_NONE = "none"


# ---------------------------------------------------------------------------
# Base description mixin for Wattpilot-specific fields
# ---------------------------------------------------------------------------
@dataclass(frozen=True, kw_only=True)
class WattpilotDescriptionMixin:
    """Mixin for Wattpilot-specific entity description fields."""

    # Charger API key (go-eCharger API v2 key)
    charger_key: str
    # Data source: property, attribute, namespacelist, none
    source: str = SOURCE_PROPERTY
    # Unique ID suffix override (required when multiple entities share same charger_key)
    uid: str | None = None
    # Firmware version constraint (e.g., ">=38.5", "<40.7")
    firmware: str | None = None
    # Charger variant filter: "11" or "22" (kW)
    variant: str | None = None
    # Connection type filter: "local" or "cloud"
    connection: str | None = None
    # Default state for None/null charger properties
    default_state: Any = None
    # For namespace properties: which attribute to use as state value
    value_id: str | int | None = None
    # For namespace properties: which item from namespace list
    namespace_id: int = 0
    # For namespace properties: extra attributes to include
    attribute_ids: list[str] | None = None
    # Description text (stored as entity extra attribute)
    description_text: str | None = None
    # Type to use when setting value: "bool", "int", "float", "string"
    set_type: str | None = None


# ---------------------------------------------------------------------------
# Sensor descriptions
# ---------------------------------------------------------------------------
@dataclass(frozen=True, kw_only=True)
class WattpilotSensorEntityDescription(
    WattpilotDescriptionMixin, SensorEntityDescription
):
    """Describes a Wattpilot sensor entity."""

    # Enum mapping: {api_value: display_string}
    enum: dict[Any, str] | None = None
    # Whether to unescape HTML entities in state value
    html_unescape: bool = False


SENSOR_DESCRIPTIONS: list[WattpilotSensorEntityDescription] = [
    # --- Attribute-based sensors ---
    WattpilotSensorEntityDescription(
        key="access_state",
        charger_key="AccessState",
        source=SOURCE_ATTRIBUTE,
        translation_key="access_state",
        icon="mdi:lock-question",
        description_text="State of access for the charger - values are: 'open', 'locked', 'auto'",
    ),
    WattpilotSensorEntityDescription(
        key="car_connected",
        charger_key="carConnected",
        source=SOURCE_ATTRIBUTE,
        translation_key="car_connected",
        icon="mdi:ev-plug-type2",
        description_text="State of the car plug - values are: 'no car', 'charging', 'ready','complete'",
    ),
    # --- Namespace list sensors (ID chips/cards) ---
    *[
        WattpilotSensorEntityDescription(
            key=f"id_chip_{i}",
            charger_key=f"cards_{i}",
            source=SOURCE_NAMESPACELIST,
            translation_key="id_chip",
            icon="mdi:credit-card-chip",
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL,
            native_unit_of_measurement="Wh",
            default_state=-1,
            entity_registry_enabled_default=False,
            value_id="energy",
            namespace_id=i,
            attribute_ids=["name", "cardId"],
            description_text=f"charging ID chip/card {i} energy usage",
        )
        for i in range(10)
    ],
    # --- Property-based sensors ---
    WattpilotSensorEntityDescription(
        key="car_state",
        charger_key="car",
        translation_key="car_state",
        icon="mdi:state-machine",
        enum={
            0: "Unknown",
            1: "Idle",
            2: "Charging",
            3: "Wait Car",
            4: "Complete",
            5: "Error",
        },
        description_text="Charging state of the car - values are: 'Unknown', 'Idle', 'Charging', 'Wait Car', 'Complete', 'Error'",
    ),
    WattpilotSensorEntityDescription(
        key="inverter",
        charger_key="cci",
        translation_key="inverter",
        icon="mdi:solar-power",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_id="label",
        html_unescape=True,
        attribute_ids=[
            "paired",
            "model",
            "commonName",
            "ip",
            "connected",
            "status",
            "message",
        ],
        description_text="Connected solar inverter",
    ),
    WattpilotSensorEntityDescription(
        key="wifi_connection",
        charger_key="ccw",
        translation_key="wifi_connection",
        icon="mdi:wifi",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_id="ssid",
        attribute_ids=["ip", "netmask", "gw", "channel", "bssid"],
        description_text="WiFi connection information",
    ),
    WattpilotSensorEntityDescription(
        key="cable_unlock",
        charger_key="cus",
        translation_key="cable_unlock",
        icon="mdi:state-machine",
        entity_category=EntityCategory.DIAGNOSTIC,
        enum={
            0: "Unknown",
            1: "Unlocked",
            2: "Unlock Failed",
            3: "Locked",
            4: "Lock Failed",
            5: "Lock/Unlock Power Out",
        },
        description_text="Cable unlock status",
    ),
    WattpilotSensorEntityDescription(
        key="internal_error",
        charger_key="err",
        translation_key="internal_error",
        icon="mdi:alert-circle",
        entity_category=EntityCategory.DIAGNOSTIC,
        enum={
            0: "None",
            1: "FI AC",
            2: "FI DC",
            3: "Phase",
            4: "Overvolt",
            5: "Overamp",
            6: "Diode",
            7: "PP Invalid",
            8: "Gnd Invalid",
            9: "Contactor Stuck",
            10: "Contactor Missing",
            11: "FI Unknown",
            12: "Unknown",
            13: "Overtemp",
            14: "No Comm",
            15: "Status Lock Stuck Open",
            16: "Status Lock Stuck Locked",
            20: "Reserved 20",
            21: "Reserved 21",
            22: "Reserved 22",
            23: "Reserved 23",
            24: "Reserved 24",
        },
        description_text="Internal error state",
    ),
    WattpilotSensorEntityDescription(
        key="total_energy",
        charger_key="eto",
        translation_key="total_energy",
        icon="mdi:meter-electric",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="Wh",
        default_state=0,
        description_text="Total energy charged (lifetime). Use this sensor for Home Assistant Energy Dashboard device consumption tracking.",
    ),
    WattpilotSensorEntityDescription(
        key="lock_feedback",
        charger_key="ffb",
        translation_key="lock_feedback",
        icon="mdi:lock-reset",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
        enum={
            0: "Unknown",
            1: "Unlocked",
            2: "Unlock Failed",
            3: "Locked",
            4: "Lock Failed",
            5: "Lock/Unlock Power Out",
        },
        description_text="Actual lock feedback",
    ),
    WattpilotSensorEntityDescription(
        key="effective_lock_setting",
        charger_key="lck",
        translation_key="effective_lock_setting",
        icon="mdi:lock",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
        enum={
            0: "Normal",
            1: "AutoUnlock",
            2: "AlwaysLock",
            3: "ForceUnlock",
        },
        description_text="Lock setting, as sent to Charge Ctrl",
    ),
    WattpilotSensorEntityDescription(
        key="local_time",
        charger_key="loc",
        translation_key="local_time",
        icon="mdi:clock-outline",
        entity_registry_enabled_default=False,
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        connection="local",
        description_text="Local time on the charger",
    ),
    WattpilotSensorEntityDescription(
        key="charging_reason",
        charger_key="modelStatus",
        translation_key="charging_reason",
        icon="mdi:ev-station",
        entity_category=EntityCategory.DIAGNOSTIC,
        enum={
            0: "Not Charging - No Charge Control Data",
            1: "Not Charging - Overtemperature",
            2: "Not Charging - Access Control Wait",
            3: "Charging - Force State On",
            4: "Not Charging - Force State Off",
            5: "Not Charging - Scheduler",
            6: "Not Charging - Energy Limit",
            7: "Charging - aWattar Price Low",
            8: "Charging - Automatic Stop Test",
            9: "Charging - Automatic Stop Not Enough Time",
            10: "Charging - Automatic Stop",
            11: "Charging - Automatic Stop No Clock",
            12: "Charging - PV Surplus",
            13: "Charging - Fallback Go-e Default",
            14: "Charging - Fallback Go-e Scheduler",
            15: "Charging - Fallback Default",
            16: "Not Charging - Fallback Go-e aWattar",
            17: "Not Charging - Fallback aWattar",
            18: "Not Charging - Fallback Automatic Stop",
            19: "Charging - Car Compatibility Keep Alive",
            20: "Charging - Charge Pause Not Allowed",
            22: "Not Charging - Simulate Unplugging",
            23: "Not Charging - Phase Switch",
            24: "Not Charging - Min Pause Duration",
            26: "Not Charging - Error",
            27: "Not Charging - Load Management Doesn't Want",
            28: "Not Charging - OCPP Doesn't Want",
            29: "Not Charging - Reconnect Delay",
            30: "Not Charging - Adapter Blocking",
            31: "Not Charging - Underfrequency Control",
            32: "Not Charging - Unbalanced Load",
            33: "Charging - Discharging PV Battery",
            34: "Not Charging - Grid Monitoring",
            35: "Not Charging - OCPP Fallback",
        },
        description_text="Reason why we allow charging or not right now",
    ),
    WattpilotSensorEntityDescription(
        key="charging_power",
        charger_key="nrg",
        translation_key="charging_power",
        icon="mdi:lightning-bolt-circle",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="W",
        default_state=0,
        value_id=11,
        attribute_ids=[
            "L1_Voltage:0",
            "L2_Voltage:1",
            "L3_Voltage:2",
            "N_Voltage:3",
            "L1_Ampere:4",
            "L2_Ampere:5",
            "L3_Ampere:6",
            "L1_Power:7",
            "L2_Power:8",
            "L3_Power:9",
            "N_Power:10",
            "TotalPower:11",
            "L1_PowerRelative:12",
            "L2_PowerRelative:13",
            "L3_PowerRelative:14",
            "N_PowerRelative:15",
        ],
        description_text="Current charging power. Use this sensor for Home Assistant Energy Dashboard device power tracking.",
    ),
    WattpilotSensorEntityDescription(
        key="webserver_queue",
        charger_key="qsw",
        translation_key="webserver_queue",
        icon="mdi:web-sync",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
        firmware="<=40.7",
        description_text="Queue size webserver/websocket",
    ),
    WattpilotSensorEntityDescription(
        key="reboot_counter",
        charger_key="rbc",
        translation_key="reboot_counter",
        icon="mdi:restart",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
        description_text="Counts the number of boot operations.",
    ),
    WattpilotSensorEntityDescription(
        key="reboot_timer",
        charger_key="rbt",
        translation_key="reboot_timer",
        icon="mdi:av-time",
        entity_registry_enabled_default=False,
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement="ms",
        entity_category=EntityCategory.DIAGNOSTIC,
        description_text="Counts the milliseconds since the last boot. Expires after 49 days, increasing the reboot_counter.",
    ),
    WattpilotSensorEntityDescription(
        key="wifi_signal",
        charger_key="rssi",
        translation_key="wifi_signal",
        icon="mdi:wifi",
        entity_registry_enabled_default=False,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        default_state=0,
        native_unit_of_measurement="dB",
        entity_category=EntityCategory.DIAGNOSTIC,
        description_text="Signal strength of the connected WiFi",
    ),
    WattpilotSensorEntityDescription(
        key="charger_temp",
        charger_key="tma",
        translation_key="charger_temp",
        icon="mdi:thermometer",
        device_class=SensorDeviceClass.TEMPERATURE,
        default_state=999,
        native_unit_of_measurement="°C",
        entity_category=EntityCategory.DIAGNOSTIC,
        description_text="Temperature of the controller",
    ),
    WattpilotSensorEntityDescription(
        key="id_chip_current",
        charger_key="trx",
        translation_key="id_chip_current",
        icon="mdi:credit-card-wireless",
        entity_registry_enabled_default=False,
        default_state=999,
        enum={
            0: "No Chip",
            1: "ID Chip 0",
            2: "ID Chip 1",
            3: "ID Chip 2",
            4: "ID Chip 3",
            5: "ID Chip 4",
            6: "ID Chip 5",
            7: "ID Chip 6",
            8: "ID Chip 7",
            9: "ID Chip 8",
            10: "ID Chip 9",
            999: "No Transaction",
        },
        description_text="Currently active transaction chip/card",
    ),
    WattpilotSensorEntityDescription(
        key="http_clients",
        charger_key="wcch",
        translation_key="http_clients",
        icon="mdi:web-box",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
        firmware="<=40.7",
        description_text="Webserver connected clients as HTTP",
    ),
    WattpilotSensorEntityDescription(
        key="websocket_clients",
        charger_key="wccw",
        translation_key="websocket_clients",
        icon="mdi:web-box",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
        firmware="<=40.7",
        description_text="Webserver connected clients as WEBSOCKET",
    ),
    WattpilotSensorEntityDescription(
        key="session_energy",
        charger_key="wh",
        translation_key="session_energy",
        icon="mdi:ev-station",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="Wh",
        default_state=0,
        description_text="Energy charged since car connected (resets when car disconnects)",
    ),
    WattpilotSensorEntityDescription(
        key="wifi_state",
        charger_key="wst",
        translation_key="wifi_state",
        icon="mdi:wifi-settings",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
        enum={
            0: "Idle",
            1: "No SSID Available",
            2: "Scan Completed",
            3: "Connected",
            4: "Connect Failed",
            5: "Connection Lost",
            6: "Disconnected",
            8: "Connecting",
            9: "Disconnecting",
            10: "No Shield",
        },
        description_text="WiFi status",
    ),
]


# ---------------------------------------------------------------------------
# Switch descriptions
# ---------------------------------------------------------------------------
@dataclass(frozen=True, kw_only=True)
class WattpilotSwitchEntityDescription(
    WattpilotDescriptionMixin, SwitchEntityDescription
):
    """Describes a Wattpilot switch entity."""

    # Whether the switch value should be inverted
    invert: bool = False


SWITCH_DESCRIPTIONS: list[WattpilotSwitchEntityDescription] = [
    WattpilotSwitchEntityDescription(
        key="lock_level_selection",
        charger_key="bac",
        translation_key="lock_level_selection",
        icon="mdi:account-cancel",
        invert=True,
        firmware="<38.5",
        description_text="Locks the button on the device so that changing the current level is not possible",
    ),
    WattpilotSwitchEntityDescription(
        key="boost",
        charger_key="ebe",
        translation_key="boost",
        icon="mdi:home-battery",
        firmware=">=41.7",
        description_text="Boost charge from battery",
    ),
    WattpilotSwitchEntityDescription(
        key="charge_pause",
        charger_key="fap",
        translation_key="charge_pause",
        icon="mdi:motion-pause",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.CONFIG,
        description_text="Deactivate 'Charge Pause' to prevent charging breaks during cost optimization",
    ),
    WattpilotSwitchEntityDescription(
        key="remain_in_eco_mode",
        charger_key="fre",
        translation_key="remain_in_eco_mode",
        icon="mdi:leaf-circle-outline",
        entity_category=EntityCategory.CONFIG,
        description_text="After reaching the defined kilometer range, switch from Next Trip Mode into Eco Mode",
    ),
    WattpilotSwitchEntityDescription(
        key="lumina_strom_awattar",
        charger_key="ful",
        translation_key="lumina_strom_awattar",
        icon="mdi:chart-timeline-variant",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.CONFIG,
        description_text="Use Lumina Strom/aWattar for charging",
    ),
    WattpilotSwitchEntityDescription(
        key="pv_surplus",
        charger_key="fup",
        translation_key="pv_surplus",
        icon="mdi:solar-power",
        entity_category=EntityCategory.CONFIG,
        description_text="Use photovoltaic surplus energy to charge your car.",
    ),
    WattpilotSwitchEntityDescription(
        key="load_balancing",
        charger_key="loe",
        translation_key="load_balancing",
        icon="mdi:scale-balance",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.CONFIG,
        description_text="Load Balancing Enabled/Disabled",
    ),
    WattpilotSwitchEntityDescription(
        key="led_energy_saving",
        charger_key="lse",
        translation_key="led_energy_saving",
        icon="mdi:led-off",
        entity_category=EntityCategory.CONFIG,
        description_text="Switch off LEDs after 10secs in standby",
    ),
    WattpilotSwitchEntityDescription(
        key="ground_check",
        charger_key="nmo",
        translation_key="ground_check",
        icon="mdi:home-floor-g",
        entity_category=EntityCategory.CONFIG,
        invert=True,
        description_text="Enable/Disable norway_mode / ground check",
    ),
    WattpilotSwitchEntityDescription(
        key="discharge_pv_battery",
        charger_key="pdte",
        translation_key="discharge_pv_battery",
        icon="mdi:battery-arrow-down-outline",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.CONFIG,
        firmware=">=41.7",
        description_text="On PV surplus charging allow to discharge the battery to specific level",
    ),
    WattpilotSwitchEntityDescription(
        key="simulate_unplugging",
        charger_key="su",
        translation_key="simulate_unplugging",
        icon="mdi:connection",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.CONFIG,
        description_text="Simulate unplugging briefly after a charging interrupt",
    ),
    WattpilotSwitchEntityDescription(
        key="network_time_protocol",
        charger_key="tse",
        translation_key="network_time_protocol",
        icon="mdi:timeline-clock-outline",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.CONFIG,
        description_text="Enable/Disable NTP time server",
    ),
    WattpilotSwitchEntityDescription(
        key="unlock_power_outage",
        charger_key="upo",
        translation_key="unlock_power_outage",
        icon="mdi:transmission-tower-off",
        entity_category=EntityCategory.CONFIG,
        description_text="Unlock plug during power outage",
    ),
    WattpilotSwitchEntityDescription(
        key="auto_disable_hotspot",
        charger_key="wda",
        translation_key="auto_disable_hotspot",
        icon="mdi:wifi-cog",
        entity_category=EntityCategory.CONFIG,
        description_text="Disable AccessPoint when cloud is connected for 30sec successfully",
    ),
]


# ---------------------------------------------------------------------------
# Number descriptions
# ---------------------------------------------------------------------------
@dataclass(frozen=True, kw_only=True)
class WattpilotNumberEntityDescription(
    WattpilotDescriptionMixin, NumberEntityDescription
):
    """Describes a Wattpilot number entity."""


NUMBER_DESCRIPTIONS: list[WattpilotNumberEntityDescription] = [
    WattpilotNumberEntityDescription(
        key="max_charging_current_11kw",
        charger_key="amp",
        set_type="int",
        translation_key="max_charging_current",
        icon="mdi:car-electric",
        native_min_value=6.0,
        native_max_value=16.0,
        native_step=1.0,
        mode=NumberMode.SLIDER,
        device_class=NumberDeviceClass.CURRENT,
        native_unit_of_measurement="A",
        variant="11",
        description_text="Maximum charging current allowed per phase",
    ),
    WattpilotNumberEntityDescription(
        key="max_charging_current_22kw",
        charger_key="amp",
        uid="amp_22kw",
        set_type="int",
        translation_key="max_charging_current",
        icon="mdi:car-electric",
        native_min_value=6.0,
        native_max_value=32.0,
        native_step=1.0,
        mode=NumberMode.SLIDER,
        device_class=NumberDeviceClass.CURRENT,
        native_unit_of_measurement="A",
        variant="22",
        description_text="Maximum charging current allowed per phase",
    ),
    WattpilotNumberEntityDescription(
        key="max_price",
        charger_key="awp",
        set_type="float",
        translation_key="max_price",
        icon="mdi:cash-100",
        native_min_value=-99999,
        native_max_value=999999,
        native_step=1,
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.MONETARY,
        native_unit_of_measurement="EUX",
        description_text="Lumina Strom/aWattar maximum price in euro cent",
    ),
    WattpilotNumberEntityDescription(
        key="boost_discharges_until",
        charger_key="ebt",
        set_type="int",
        translation_key="boost_discharges_until",
        icon="mdi:power-plug-battery",
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        device_class=NumberDeviceClass.BATTERY,
        native_unit_of_measurement="%",
        firmware=">=41.7",
        entity_category=EntityCategory.CONFIG,
        description_text="Set the percentage to which the PV battery is discharged in your vehicle during Boost.",
    ),
    WattpilotNumberEntityDescription(
        key="pv_battery_threshold",
        charger_key="fam",
        set_type="int",
        translation_key="pv_battery_threshold",
        icon="mdi:battery-charging-medium",
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        device_class=NumberDeviceClass.BATTERY,
        native_unit_of_measurement="%",
        entity_category=EntityCategory.CONFIG,
        description_text="Minimum battery level until PV Surplus charging is started",
    ),
    WattpilotNumberEntityDescription(
        key="min_charging_time",
        charger_key="fmt",
        set_type="int",
        translation_key="min_charging_time",
        icon="mdi:car-clock",
        device_class=NumberDeviceClass.DURATION,
        native_min_value=60000,
        native_max_value=3600000,
        native_step=60000,
        native_unit_of_measurement="ms",
        entity_category=EntityCategory.CONFIG,
        description_text="Minimum charging time after the charging has started",
    ),
    WattpilotNumberEntityDescription(
        key="ohmpilot_threshold",
        charger_key="fot",
        set_type="int",
        translation_key="ohmpilot_threshold",
        icon="mdi:thermometer-water",
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement="°C",
        entity_category=EntityCategory.CONFIG,
        description_text="Minimum water temperature until PV Surplus charging is started",
    ),
    WattpilotNumberEntityDescription(
        key="start_charging_at",
        charger_key="fst",
        set_type="float",
        translation_key="start_charging_at",
        icon="mdi:solar-power",
        native_min_value=0,
        native_max_value=999999,
        native_step=1,
        native_unit_of_measurement="W",
        device_class=NumberDeviceClass.POWER,
        entity_category=EntityCategory.CONFIG,
        description_text="PV Surplus start charging power",
    ),
    WattpilotNumberEntityDescription(
        key="next_trip_charging",
        charger_key="fte",
        set_type="float",
        translation_key="next_trip_charging",
        icon="mdi:road-variant",
        native_min_value=0,
        native_max_value=999999,
        native_step=10,
        device_class=NumberDeviceClass.ENERGY,
        native_unit_of_measurement="Wh",
        description_text="Defined amount of energy will be provided until the next scheduled ride",
    ),
    WattpilotNumberEntityDescription(
        key="phase_switch_delay",
        charger_key="mpwst",
        set_type="int",
        translation_key="phase_switch_delay",
        icon="mdi:solar-power",
        native_min_value=0,
        native_max_value=99999999,
        native_unit_of_measurement="ms",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.CONFIG,
        description_text="Phase switching if '3-Phase power level' is permanently exceeded during this time",
    ),
    WattpilotNumberEntityDescription(
        key="phase_switch_interval",
        charger_key="mptwt",
        set_type="int",
        translation_key="phase_switch_interval",
        icon="mdi:sun-clock-outline",
        native_min_value=0,
        native_max_value=99999999,
        native_unit_of_measurement="ms",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.CONFIG,
        description_text="Minimum time between phase switching events",
    ),
    WattpilotNumberEntityDescription(
        key="pv_battery_discharges_until",
        charger_key="pdt",
        set_type="int",
        translation_key="pv_battery_discharges_until",
        icon="mdi:power-plug-battery",
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        device_class=NumberDeviceClass.BATTERY,
        entity_registry_enabled_default=False,
        native_unit_of_measurement="%",
        firmware=">=41.7",
        entity_category=EntityCategory.CONFIG,
        description_text="Set the percentage to which the PV battery is discharged in your vehicle during PV surplus.",
    ),
    WattpilotNumberEntityDescription(
        key="three_phase_power_level",
        charger_key="spl3",
        set_type="int",
        translation_key="three_phase_power_level",
        icon="mdi:connection",
        native_min_value=0,
        native_max_value=999999,
        device_class=NumberDeviceClass.ENERGY,
        native_unit_of_measurement="W",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.CONFIG,
        description_text="Value at which the Wattpilot switches from 1- to 3-phase surplus energy charging",
    ),
]


# ---------------------------------------------------------------------------
# Select descriptions
# ---------------------------------------------------------------------------
@dataclass(frozen=True, kw_only=True)
class WattpilotSelectEntityDescription(
    WattpilotDescriptionMixin, SelectEntityDescription
):
    """Describes a Wattpilot select entity."""

    # Static options dict: {api_value: display_string}
    select_options: dict[Any, str] | None = None
    # Dynamic options: charger attribute name containing options dict
    options_attribute: str | None = None


SELECT_DESCRIPTIONS: list[WattpilotSelectEntityDescription] = [
    WattpilotSelectEntityDescription(
        key="access_control",
        charger_key="acs",
        translation_key="access_control",
        icon="mdi:access-point-check",
        entity_category=EntityCategory.CONFIG,
        select_options={
            0: "Open",
            1: "Authentication Required",
        },
        description_text="Access control user setting",
    ),
    WattpilotSelectEntityDescription(
        key="awattar_country",
        charger_key="awc",
        translation_key="awattar_country",
        icon="mdi:map-marker",
        entity_category=EntityCategory.CONFIG,
        select_options={
            0: "Austria",
            10043: "Belgium",
            10016: "Bulgaria",
            10003: "Croatia",
            10019: "Czechia",
            10024: "Denmark DK1",
            10036: "Denmark DK2",
            10020: "Estonia",
            10004: "Finland",
            10015: "France",
            1: "Germany",
            10006: "Greece",
            10042: "Hungary",
            10017: "Italy Calabria",
            10031: "Italy Centre-Noth",
            10009: "Italy Centre-South",
            10034: "Italy North",
            10023: "Italy SacoAC",
            10001: "Italy SacoDC",
            10029: "Italy Sardinia",
            10005: "Italy Sicily",
            10041: "Italy South",
            10010: "Latvia",
            10030: "Lithuania",
            10012: "Montenegro",
            10038: "Netherlands",
            10057: "Norway Elspot1",
            10058: "Norway Elspot2",
            10059: "Norway Elspot3",
            10060: "Norway Elspot4",
            10061: "Norway Elspot5",
            10021: "Norway NO2NSL",
            10037: "Poland",
            10027: "Portugal",
            10044: "Romania",
            10039: "Serbia",
            10040: "Slovakia",
            10025: "Slovenia",
            10018: "Spain",
            10062: "Sweden Elspot1",
            10063: "Sweden Elspot2",
            10064: "Sweden Elspot3",
            10065: "Sweden Elspot4",
            10045: "Sweden Tibber Elspot1",
            10046: "Sweden Tibber Elspot2",
            10047: "Sweden Tibber Elspot3",
            10048: "Sweden Tibber Elspot4",
            10035: "Switzerland",
            10002: "Ukraine",
        },
        description_text="Lumina Strom/aWattar country",
    ),
    WattpilotSelectEntityDescription(
        key="lock_level_selection",
        charger_key="bac",
        translation_key="lock_level_selection",
        icon="mdi:account-cancel",
        firmware=">=38.5",
        select_options={
            0: "Always locked",
            1: "Locked when car is connected",
            3: "Never locked",
        },
        description_text="Locks the button on the device so that changing the current level is not possible",
    ),
    WattpilotSelectEntityDescription(
        key="boost_type",
        charger_key="ebo",
        translation_key="boost_type",
        icon="mdi:battery-clock",
        firmware=">=41.7",
        entity_category=EntityCategory.CONFIG,
        select_options={
            True: "One-Time",
            False: "Repeat for as long as vehicle is plugged in",
        },
        description_text="Type of boost charge from battery",
    ),
    WattpilotSelectEntityDescription(
        key="charging_mode",
        charger_key="lmo",
        translation_key="charging_mode",
        icon="mdi:leaf",
        options_attribute="lmoValues",
        description_text="Charging mode Default, Eco or Next Trip",
    ),
    WattpilotSelectEntityDescription(
        key="phase_switch",
        charger_key="psm",
        translation_key="phase_switch",
        icon="mdi:car-3-plus",
        entity_category=EntityCategory.CONFIG,
        select_options={
            0: "Auto",
            1: "1 Phase",
            2: "3 Phases",
        },
        description_text="Choose how the charger switches phases",
    ),
    WattpilotSelectEntityDescription(
        key="daylight_saving",
        charger_key="tds",
        translation_key="daylight_saving",
        icon="mdi:map-clock",
        entity_category=EntityCategory.CONFIG,
        select_options={
            0: "None",
            1: "EuropeanSummerTime",
            2: "UsDaylightTime",
            3: "AUEasternDaylightTime",
        },
        description_text="Timezone daylight saving mode",
    ),
    WattpilotSelectEntityDescription(
        key="cable_unlock",
        charger_key="ust",
        translation_key="cable_unlock_select",
        icon="mdi:lock-outline",
        entity_category=EntityCategory.CONFIG,
        options_attribute="ustValues",
        description_text="Lock cable when the car is connected (Normal), while the car is charging (AutoUnlock) or (AlwaysLock)",
    ),
]


# ---------------------------------------------------------------------------
# Button descriptions
# ---------------------------------------------------------------------------
@dataclass(frozen=True, kw_only=True)
class WattpilotButtonEntityDescription(
    WattpilotDescriptionMixin, ButtonEntityDescription
):
    """Describes a Wattpilot button entity."""

    # Value to send on press
    set_value: Any = None


BUTTON_DESCRIPTIONS: list[WattpilotButtonEntityDescription] = [
    WattpilotButtonEntityDescription(
        key="start_charging",
        charger_key="frc",
        uid="frc0",
        source=SOURCE_NONE,
        translation_key="start_charging",
        icon="mdi:play",
        set_value=0,
        description_text="Manually start the charging process",
    ),
    WattpilotButtonEntityDescription(
        key="stop_charging",
        charger_key="frc",
        uid="frc1",
        source=SOURCE_NONE,
        translation_key="stop_charging",
        icon="mdi:stop",
        set_value=1,
        description_text="Manually stop the charging process",
    ),
    WattpilotButtonEntityDescription(
        key="start_charging_force",
        charger_key="frc",
        uid="frc2",
        source=SOURCE_NONE,
        translation_key="start_charging_force",
        icon="mdi:play-circle-outline",
        set_value=2,
        description_text="Force the charging start (required for some vehicles instead of normal start)",
    ),
    WattpilotButtonEntityDescription(
        key="restart",
        charger_key="rst",
        source=SOURCE_NONE,
        translation_key="restart",
        device_class=ButtonDeviceClass.RESTART,
        set_value=1,
        description_text="Restart the charger",
    ),
    WattpilotButtonEntityDescription(
        key="authenticate",
        charger_key="trx",
        source=SOURCE_NONE,
        translation_key="authenticate",
        icon="mdi:credit-card-wireless-outline",
        entity_registry_enabled_default=False,
        set_value=0,
        description_text="Authenticate the charger without ID card",
    ),
]


# ---------------------------------------------------------------------------
# Update descriptions
# ---------------------------------------------------------------------------
@dataclass(frozen=True, kw_only=True)
class WattpilotUpdateEntityDescription(
    WattpilotDescriptionMixin, UpdateEntityDescription
):
    """Describes a Wattpilot update entity."""

    # Charger property key for installed version
    id_installed: str | None = None
    # Charger property key to trigger update install
    id_trigger: str | None = None
    # Charger property key for install status percentage
    id_status: str | None = None


UPDATE_DESCRIPTIONS: list[WattpilotUpdateEntityDescription] = [
    WattpilotUpdateEntityDescription(
        key="firmware_update",
        charger_key="onv",
        translation_key="firmware_update",
        icon="mdi:update",
        device_class=UpdateDeviceClass.FIRMWARE,
        entity_category=EntityCategory.DIAGNOSTIC,
        set_type="string",
        id_installed="fwv",
        id_trigger="oct",
        description_text="Install firmware update available",
    ),
]
