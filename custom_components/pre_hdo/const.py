"""Constants for PRE Distribuce HDO integration."""

DOMAIN = "pre_hdo"

CONF_RECEIVER_COMMAND_ID = "receiver_command_id"
CONF_PERIODS = "periods"
CONF_PERIOD_NAME = "name"
CONF_PERIOD_MINUTES = "minutes"

BASE_URL = "https://www.predistribuce.cz"
HDO_ONE_DAY_URL = f"{BASE_URL}/com/PREdi/UI/Forms/Hdo/HdoForm:hdoOneDayAjax"
HDO_PAGE_URL = f"{BASE_URL}/cs/potrebuji-zaridit/zakaznici/stav-hdo/"

DEFAULT_SCAN_INTERVAL = 900  # 15 minutes

TARIFF_LOW = "NT"
TARIFF_HIGH = "VT"
