"""Constants for Aldes Local."""

DOMAIN = "aldes_local"
CONF_TOKEN = "token"
DEFAULT_NAME = "Aldes Local"
DEFAULT_SCAN_INTERVAL = 30
TELEMETRY_STALE_AFTER = 300

AIR_MODES = {
    "Off": (0, "A"),
    "Heating comfort": (1, "B"),
    "Heating eco": (2, "C"),
    "Heating program A": (3, "D"),
    "Heating program B": (4, "E"),
    "Cooling comfort": (5, "F"),
    "Cooling boost": (6, "G"),
    "Cooling program C": (7, "H"),
    "Cooling program D": (8, "I"),
}

WATER_MODES = {
    "Off": (0, "L"),
    "On": (1, "M"),
    "Boost": (2, "N"),
}
