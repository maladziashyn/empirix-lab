from os.path import dirname, join, realpath


# General
GRESOURCE_RECOMPILE = False  # set to False in PRODUCTION
PROJECT_HOME_DIR = dirname(realpath(__file__))

# UI, about
APP_NAME = "Empirix Lab"
APP_COPYRIGHT = "© 2025 Raman Maładziašyn"
APP_DEV_NAME = "Raman Maładziašyn"
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

# GResource
APP_ID = "eu.rsmlabs.EmpirixLab"
APP_URL = "/eu/rsmlabs/EmpirixLab"
GRESOURCE_HOME_DIR = join(PROJECT_HOME_DIR, "gresource")
GRESOURCE_BIN = join(GRESOURCE_HOME_DIR, f"{PACKAGE_NAME}.gresource")
GRESOURCE_XML = GRESOURCE_BIN + ".xml"
