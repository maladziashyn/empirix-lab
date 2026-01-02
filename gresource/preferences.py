import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk

from config import APP_URL


@Gtk.Template(resource_path=f"{APP_URL}/preferences.ui")
class AppPreferences(Adw.PreferencesDialog):
    __gtype_name__ = "AppPreferences"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
