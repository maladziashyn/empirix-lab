import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, GLib, Gtk
from os.path import dirname,realpath
from sys import path
project_home_dir = dirname(dirname(realpath(__file__)))
if project_home_dir not in path:
    path.insert(0, project_home_dir)

from config import APP_URL
from core import sanity_check
from core.db_manager import select_var


@Gtk.Template(resource_path=f"{APP_URL}/sanity_check.ui")
class SanityCheckScrolledWindow(Gtk.ScrolledWindow):
    __gtype_name__ = "SanityCheckScrolledWindow"

    # paned = Gtk.Template.Child()
    entry_declared_strategy = Gtk.Template.Child()
    entry_source_dir = Gtk.Template.Child()
    spin_max_size_megabytes = Gtk.Template.Child()
    switch_show_on_end = Gtk.Template.Child()
    # text_view = Gtk.Template.Child()

    initial_folder = Gio.File.new_for_path(select_var("file_dialog_initial_folder"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_dir = None
        # self.paned.set_shrink_start_child(False)

        # Access the associated Gtk.TextBuffer
        # self.text_buffer = self.text_view.get_buffer()
        # self.text_buffer.set_text("Welcome to Gtk.TextView!\nFeel free to edit this text.")


    @Gtk.Template.Callback("btn_callback_01")
    def pick_source_dir(self, *args):
        file_dialog = Gtk.FileDialog.new()
        file_dialog.props.accept_label = "Select"
        file_dialog.props.title = "Select folder"
        file_dialog.props.initial_folder = self.initial_folder
        file_dialog.select_folder(
            parent=self.get_ancestor(Adw.ApplicationWindow),
            cancellable=None,
            callback=self._on_select_folder_finish
        )

    def _on_select_folder_finish(self, dialog, result):
        try:
            self.selected_dir = dialog.select_folder_finish(result).get_path()
            self.entry_source_dir.set_text(self.selected_dir)
        except GLib.Error:
            pass  # Dismissed by user

    @Gtk.Template.Callback("btn_callback_03")
    def run_sanity_check(self, *args):
        # self.text_buffer.set_text("some new text")
        sanity_check.run_check(
            alert_dialog_parent=self.get_ancestor(Adw.ApplicationWindow),
            declared_strategy=self.entry_declared_strategy.get_text(),
            selected_dir=self.selected_dir,
            max_size=int(self.spin_max_size_megabytes.get_text()),
            open_excel=self.switch_show_on_end.get_active(),
            text_buffer=None
        )
