import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk

from config import APP_ID, APP_NAME, APP_URL


@Gtk.Template(resource_path=f"{APP_URL}/window.ui")
class AppWindow(Adw.ApplicationWindow):
    __gtype_name__ = "AppWindow"

    # new_page = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # self.set_icon_name(APP_ID)
        self.set_title(APP_NAME)
