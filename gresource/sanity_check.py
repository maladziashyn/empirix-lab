import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, GLib, Gtk
from os.path import basename

from config import APP_URL


@Gtk.Template(resource_path=f"{APP_URL}/sanity_check.ui")
class SanityCheckScrolledWindow(Gtk.ScrolledWindow):
    __gtype_name__ = "SanityCheckScrolledWindow"

    entry_source_files = Gtk.Template.Child()
    entry_source_dirs = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.files_picked = None

    @Gtk.Template.Callback("btn_callback_01")
    def pick_source_files(self, *args):
        file_dialog = Gtk.FileDialog()
        file_dialog.props.accept_label = "Select"
        file_dialog.props.initial_folder = Gio.File.new_for_path("/home/rsm/Documents/MyProjects/empirix-lab/core")
        file_dialog.open_multiple(
            parent=self.get_ancestor(Adw.ApplicationWindow),
            cancellable=None,
            callback=self._on_open_multiple_finish
        )

    def _on_open_multiple_finish(self, dialog, result):
        try:
            files_list_model = dialog.open_multiple_finish(result)
            n_files = files_list_model.get_n_items()
            self.files_picked = list()
            for i in range(n_files):
                model_file = files_list_model.get_item(i)
                file_path = model_file.get_path()
                print(basename(file_path))
                self.files_picked.append(file_path)
            self.entry_source_files.set_text(", ".join(self.files_picked))
        except GLib.Error:
            pass  # Dismissed by user

    @Gtk.Template.Callback("btn_callback_02")
    def pick_source_dirs(self, *args):
        file_dialog = Gtk.FileDialog()
        file_dialog.props.accept_label = "Select"
        file_dialog.props.initial_folder = Gio.File.new_for_path("/home/rsm/Documents/MyProjects/empirix-lab/core")
        file_dialog.select_multiple_folders(
            parent=self.get_ancestor(Adw.ApplicationWindow),
            cancellable=None,
            callback=self._on_select_multiple_folders_complete
        )

    def _on_select_multiple_folders_complete(self, dialog, result):
        try:
            print("in try")
            folders = dialog.select_multiple_folders_finish(result)
            print(f"items = {folders.get_n_items()}")
        except GLib.Error:
            pass  # Dismissed by user
