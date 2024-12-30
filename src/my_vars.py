import gi

from gi.repository import Gio, GObject
from os import system
from os.path import abspath, dirname, join

from gresource.load_widgets import load_widgets


def compile_gresource(gresource_target):
    widget_dir = join(HOME_SRC, GRESOURCE_DIRNAME)
    gresource_xml = join(widget_dir, f"{APP_NAME}.gresource.xml")
    system(
        f"glib-compile-resources --sourcedir {widget_dir} " \
        f"--target {gresource_target} " \
        f"{gresource_xml}"
    )


IS_DEV = True  # set to False for PRODUCTION

APP_ID = "eu.rsmlabs.EmpirixLab"
APP_NAME = "empirix-lab"
GRESOURCE_DIRNAME = "gresource"
HOME_SRC = dirname(abspath(__file__))
# print(f"home src: {HOME_SRC}")
# HOME_TREE = dirname(HOME_SRC)

# GRESOURCE
# 1. Compile & regisger
gresource_bin = join(HOME_SRC, GRESOURCE_DIRNAME, f"{APP_NAME}.gresource")
if IS_DEV:
    print("COMPILING GRESOURCE")
    compile_gresource(gresource_bin)
print("REGISTERING GRESOURCE")
Gio.resources_register(Gio.Resource.load(gresource_bin))

# 2. Load widgets - type ensure
load_widgets()
