"""Constants for PRE Distribuce HDO integration."""

from zoneinfo import ZoneInfo

DOMAIN = "pre_hdo"

PRAGUE_TZ = ZoneInfo("Europe/Prague")

CONF_RECEIVER_COMMAND_ID = "receiver_command_id"

BASE_URL = "https://www.predistribuce.cz"
HDO_ONE_DAY_URL = f"{BASE_URL}/com/PREdi/UI/Forms/Hdo/HdoForm:hdoOneDayAjax"
HDO_MULTI_DAY_URL = f"{BASE_URL}/com/PREdi/UI/Forms/Hdo/HdoForm:hdoMoreDaysAjax"

TARIFF_LOW = "NT"
TARIFF_HIGH = "VT"
