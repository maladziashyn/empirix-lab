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
# from core import backtest_processor as bp
from core.db_manager import select_var


@Gtk.Template(resource_path=f"{APP_URL}/process_raw_page.ui")
class ProcessRawScrolledWindow(Gtk.ScrolledWindow):
    __gtype_name__ = "ProcessRawScrolledWindow"

    entry_source_dir = Gtk.Template.Child()
    initial_folder = Gio.File.new_for_path(select_var("file_dialog_initial_folder"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_dir = None

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

    @Gtk.Template.Callback("btn_callback_02")
    def process_html(self, *args):
        print("process html")

        # sanity_check.run_check(
        #     alert_dialog_parent=self.get_ancestor(Adw.ApplicationWindow),
        #     declared_strategy=self.entry_declared_strategy.get_text(),
        #     selected_dir=self.selected_dir,
        #     max_size=int(self.spin_max_size_megabytes.get_text()),
        #     open_excel=self.switch_show_on_end.get_active(),
        #     text_buffer=None
        # )

    @Gtk.Template.Callback("btn_callback_03")
    def insert_into_db(self, *args):
        print("insert into db")

        # sanity_check.run_check(
        #     alert_dialog_parent=self.get_ancestor(Adw.ApplicationWindow),
        #     declared_strategy=self.entry_declared_strategy.get_text(),
        #     selected_dir=self.selected_dir,
        #     max_size=int(self.spin_max_size_megabytes.get_text()),
        #     open_excel=self.switch_show_on_end.get_active(),
        #     text_buffer=None
        # )
