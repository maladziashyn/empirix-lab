from os.path import dirname, join, realpath


# General
GRESOURCE_RECOMPILE = False  # set to False in PRODUCTION
PROJECT_HOME_DIR = dirname(realpath(__file__))

# UI, about
APP_NAME = "Empirix Lab"
APP_COPYRIGHT = "© 2025 Raman Maładziašyn"
APP_DEV_NAME = "Raman Maładziašyn"
APP_DEVS = ["Raman Maładziašyn", "Arciom Kośmin"]

# Distribution
VERSION = "25.1"
PACKAGE_NAME = "empirix-lab"
CONTROL_FILE_DESC = f"{APP_NAME}\n Tools for algorithmic trading by Empirix."
DESKTOP_ITEM_COMMENT = "Tools for algorithmic trading by Empirix"
DESKTOP_ITEM_LOGO = f"{PACKAGE_NAME}.xpm"
# SPEC_JINJA_TPL_FPATH = join(DIST_HOME, "tpl.jinja")

# GResource
APP_ID = "eu.rsmlabs.EmpirixLab"
APP_URL = "/eu/rsmlabs/EmpirixLab"
GRESOURCE_HOME_DIR = join(PROJECT_HOME_DIR, "gresource")
GRESOURCE_XML = join(GRESOURCE_HOME_DIR, f"{PACKAGE_NAME}.gresource.xml")
GRESOURCE_BIN = join(GRESOURCE_HOME_DIR, f"{PACKAGE_NAME}.gresource")
