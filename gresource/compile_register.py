"""
GResource: compile to binary (if necessary, especially in development)
and register for use.
All is done during the import, to avoid calling the below functions in main.py.
"""

from gi.repository import Gio
from os import system
from os.path import dirname, realpath
from sys import path
project_home = dirname(dirname(realpath(__file__)))
if project_home not in path:
    path.insert(0, project_home)

import config as c


def gresource_compile():
    system(
        f"glib-compile-resources --sourcedir {c.GRESOURCE_HOME_DIR} " \
        f"--target {c.GRESOURCE_BIN} " \
        f"{c.GRESOURCE_XML}"
    )
    # print("GRESOURCE COMPILED")


def gresource_register():
    Gio.resources_register(Gio.Resource.load(c.GRESOURCE_BIN))


if c.GRESOURCE_RECOMPILE:
    gresource_compile()

gresource_register()
