import re

from os.path import dirname, expanduser, join, realpath


# General
GRESOURCE_RECOMPILE = True  # set to False in PRODUCTION
PROJECT_HOME_DIR = dirname(realpath(__file__))

# UI, about
APP_NAME = "Empirix Lab"
APP_COPYRIGHT = "© 2025 Raman Maładziašyn"
APP_DEV_NAME = "Raman Maładziašyn & Empirix.ru team"
APP_DEVS = ["Raman Maładziašyn"]

# Distribution
VERSION = "25.1"
PACKAGE_NAME = "empirix-lab"
CONTROL_FILE_DESC = f"{APP_NAME}\n Tools for algorithmic trading by Empirix."
DESKTOP_ITEM_COMMENT = "Tools for algorithmic trading by Empirix"
DESKTOP_ITEM_LOGO = f"{PACKAGE_NAME}.xpm"
MAINTAINER = "Raman Maładziašyn <maladziashyn@gmail.com>"
WEB_HOMEPAGE = "https://empirix.ru/"
SETUP_FILE_LINUX = f"{PACKAGE_NAME}-{VERSION}-setup_all"
SETUP_FILE_WINDOWS = f"{PACKAGE_NAME}-{VERSION}-setup"
INTERNAL_DIR = "_internal"

# GResource
APP_ID = "eu.rsmlabs.EmpirixLab"
APP_URL = "/eu/rsmlabs/EmpirixLab"
GRESOURCE_HOME_DIR = join(PROJECT_HOME_DIR, "gresource")
GRESOURCE_BIN = join(GRESOURCE_HOME_DIR, f"{PACKAGE_NAME}.gresource")
GRESOURCE_XML = GRESOURCE_BIN + ".xml"

# Variables db
VAR_DB_FNAME = "state_var.db"
VAR_DB_FPATH = join(PROJECT_HOME_DIR, "core", VAR_DB_FNAME)
VAR_TBL_NAME = "state_var"
DEFAULT_VARS_JSON = join(PROJECT_HOME_DIR, "core", "default_variables.json")
DEFAULT_WORK_DIR = join(expanduser("~"), "Documents", APP_NAME)
DEFAULT_SANITY_CHECKS_DIR = "sanity_checks"
DEFAULT_SQLITE_DB_DIR = "my_db"
DEFAULT_SQLITE_DB_NAME = "my.db"

# Specs
SPECS_TBL_DB = join(PROJECT_HOME_DIR, "core", "db_tables_specs.json")

# Xpath
XP_0 = "/html/body/div[3]/"  # beginning of all Xpaths
xp_h1 = XP_0 + "h1"  # "/html/body/div[3]/h1"
xp_params = XP_0 + "table[2]"

# RegEx patterns
re_strategy = re.compile(r"^\w+\b")
re_vjf_endings = re.compile(r"_(mux|mxu|cux|cxu)")

re_date = re.compile(r"\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\b")
re_instrument = re.compile(r"\b\w{3}/\w{3}")

instr_meta_keys_mapped = {
    "First tick time": "d_first_tick",
    "First BID": "d_first_bid",
    "First tick bid value": "d_first_bid",
    "First ASK": "d_first_ask",
    "First tick ask value": "d_first_ask",
    "Last tick time": "d_last_tick",
    "Last BID": "d_last_bid",
    "Last tick bid value": "d_last_bid",
    "Last ASK": "d_last_ask",
    "Last tick ask value": "d_last_ask",
    "Positions total": "d_pos_total",
    "Closed positions": "d_closed_pos",
    "Orders total": "d_orders",
    "Amount bought": "d_bought",
    "Bought": "d_bought",
    "Amount sold": "d_sold",
    "Sold": "d_sold",
    "Turnover": "d_turnover",
    "Commission Fees": "d_commission",
    "Commission": "d_commission",
}

date_columns = ["h1_date_from", "h1_date_to", "d_first_tick", "d_last_tick"]
