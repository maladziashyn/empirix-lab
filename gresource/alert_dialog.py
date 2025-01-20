import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk

from config import APP_URL


@Gtk.Template(resource_path=f"{APP_URL}/alert_dialog.ui")
class AlertDialogTest(Adw.AlertDialog):
    __gtype_name__ = "AlertDialogTest"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
