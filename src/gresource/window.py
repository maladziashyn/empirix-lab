import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk


@Gtk.Template(resource_path="/eu/rsmlabs/EmpirixLab/window.ui")
class AppWindow(Adw.ApplicationWindow):
    __gtype_name__ = "AppWindow"

    # new_page = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

