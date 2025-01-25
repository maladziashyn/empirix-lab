import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, GLib, Gtk
from os.path import dirname,realpath
from sys import path
project_home_dir = dirname(dirname(realpath(__file__)))
if project_home_dir not in path:
    path.insert(0, project_home_dir)

from config import APP_URL, ARCH_EXTENSIONS
from core import sanity_check
from core.db_manager import select_var


@Gtk.Template(resource_path=f"{APP_URL}/sanity_check.ui")
class SanityCheckScrolledWindow(Gtk.ScrolledWindow):
    __gtype_name__ = "SanityCheckScrolledWindow"

    entry_declared_strategy = Gtk.Template.Child()
    entry_source_dirs = Gtk.Template.Child()
    entry_source_files = Gtk.Template.Child()
    spin_max_size_megabytes = Gtk.Template.Child()

    initial_folder = Gio.File.new_for_path(select_var("file_dialog_initial_folder"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.files_picked = None
        self.folders_picked = None

    @Gtk.Template.Callback("btn_callback_01")
    def pick_source_dirs(self, *args):
        file_dialog = Gtk.FileDialog.new()
        file_dialog.props.accept_label = "Select"
        file_dialog.props.title = "Select folders"
        file_dialog.props.initial_folder = self.initial_folder
        file_dialog.select_multiple_folders(
            parent=self.get_ancestor(Adw.ApplicationWindow),
            cancellable=None,
            callback=self._on_select_multiple_folders_complete
        )

    def _on_select_multiple_folders_complete(self, dialog, result):
        try:
            folders_list_model = dialog.select_multiple_folders_finish(result)
            n_folders = folders_list_model.get_n_items()
            self.folders_picked = list()
            for i in range(n_folders):
                model_folder = folders_list_model.get_item(i)
                folder_path = model_folder.get_path()
                self.folders_picked.append(folder_path)
            self.entry_source_dirs.set_text(", ".join(self.folders_picked))
            self.entry_source_files.set_text("")
            self.files_picked = None

        except GLib.Error:
            pass  # Dismissed by user

    @Gtk.Template.Callback("btn_callback_02")
    def pick_source_files(self, *args):
        file_dialog = Gtk.FileDialog.new()
        file_dialog.props.accept_label = "Select"
        file_dialog.props.title = "Select files: zip or 7z"

        # Add filters for archive files
        archive_filter = Gtk.FileFilter()
        archive_filter.set_name(f"Archive Files ({", ".join(ARCH_EXTENSIONS)})")
        for ext in ARCH_EXTENSIONS:
            archive_filter.add_pattern(f"*.{ext}")
        # Create a Gio.ListStore and add the filter
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(archive_filter)
        file_dialog.set_filters(filters)

        file_dialog.props.initial_folder = self.initial_folder
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
                self.files_picked.append(file_path)
            self.entry_source_files.set_text(", ".join(self.files_picked))
            self.entry_source_dirs.set_text("")
            self.folders_picked = None
        except GLib.Error:
            pass  # Dismissed by user

    @Gtk.Template.Callback("btn_callback_03")
    def run_sanity_check(self, *args):
        sanity_check.run_check(
            alert_dialog_parent=self.get_ancestor(Adw.ApplicationWindow),
            declared_strategy=self.entry_declared_strategy.get_text(),
            folders_picked=self.folders_picked,
            files_picked=self.files_picked,
            max_size=int(self.spin_max_size_megabytes.get_text())
        )
