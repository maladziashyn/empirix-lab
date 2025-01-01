import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


@Gtk.Template(resource_path="/eu/rsmlabs/EmpirixLab/monte_carlo.ui")
class MonteCarloScrolledWindow(Gtk.ScrolledWindow):
    __gtype_name__ = "MonteCarloScrolledWindow"

    entry_mc_target_dir = Gtk.Template.Child()  # entry row
    btn_target_dir = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @Gtk.Template.Callback("btn_callback_01")
    def pick_target_dir(self, *args):
        # self.en_directory.set_text(c.PROJ_SRC)
        # print(self.entry_mc_target_dir.get_text())
        native = Gtk.FileDialog()
        native.select_folder(self, None, self._on_select_folder_complete)

    def _on_select_folder_complete(self, dialog, result):
        # folder = dialog.select_folder_finish(result)
        if (folder := dialog.select_folder_finish(result)):
            print(folder.get_path())
            self.entry_mc_target_dir.set_text(folder.get_path())
