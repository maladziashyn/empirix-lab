import gi

from gi.repository import Gio
from os import system
from os.path import abspath, dirname, join


IS_DEV = True  # set to False for PRODUCTION

APP_NAME = "empirix-lab"
APP_ID = "eu.rsmlabs.EmpirixLab"
HOME_GRESOURCE = dirname(abspath(__file__))


def compile_gresource(gresource_target):
    gresource_xml = join(HOME_GRESOURCE, f"{APP_NAME}.gresource.xml")
    system(
        f"glib-compile-resources --sourcedir {HOME_GRESOURCE} " \
        f"--target {gresource_target} " \
        f"{gresource_xml}"
    )


def init_resources():
    # Step 1. Compile if dev mode
    gresource_bin = join(HOME_GRESOURCE, f"{APP_NAME}.gresource")

    if IS_DEV:
        print("COMPILING GRESOURCE")
        compile_gresource(gresource_bin)

    # Step 2. Register
    print("REGISTERING GRESOURCE")
    Gio.resources_register(Gio.Resource.load(gresource_bin))
