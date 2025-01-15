import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from os.path import basename

from config import APP_URL

from core.monte_carlo import build_one_curve


@Gtk.Template(resource_path=f"{APP_URL}/sanity_check.ui")
class SanityCheckScrolledWindow(Gtk.ScrolledWindow):
    __gtype_name__ = "SanityCheckScrolledWindow"

    entry_source_dir = Gtk.Template.Child()  # entry row
    spin_curves_count = Gtk.Template.Child()
    spin_bins = Gtk.Template.Child()
    spin_simulations_count = Gtk.Template.Child()
    spin_ruin_level = Gtk.Template.Child()
    spin_sim_trades = Gtk.Template.Child()
    spin_sim_years = Gtk.Template.Child()
    spin_sim_win_rate = Gtk.Template.Child()
    spin_sim_win_loss_ratio = Gtk.Template.Child()
    spin_sim_fraction = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @Gtk.Template.Callback("btn_callback_01")
    def pick_target_dir(self, *args):
        native = Gtk.FileDialog()
        native.open_multiple(
            parent=None,
            cancellable=None,
            callback=self._on_open_multiple_finish
        )

    def _on_open_multiple_finish(self, dialog, result):
        files_picked = dialog.open_multiple_finish(result)
        n_files = files_picked.get_n_items()
        file_paths = list()
        for i in range(n_files):
            gfile = files_picked.get_item(i)
            file_path = gfile.get_path()
            print(basename(file_path))
            file_paths.append(file_path)
        self.entry_source_dir.set_text(", ".join(file_paths))


    @Gtk.Template.Callback("btn_callback_02")
    def click_run_randnum(self, *args):
        print("Clicked Run RANDNUM Simulation button")
        print(self.entry_source_dir.get_text())
        print(self.spin_curves_count.get_text())
        print(self.spin_bins.get_text())
        print(self.spin_simulations_count.get_text())
        print(self.spin_ruin_level.get_text())
        print(self.spin_sim_trades.get_text())
        print(self.spin_sim_years.get_text())
        print(self.spin_sim_win_rate.get_text())
        print(self.spin_sim_win_loss_ratio.get_text())
        print(self.spin_sim_fraction.get_text())

        trades = self.spin_sim_trades.get_text()
        win_rate = self.spin_sim_win_rate.get_text()
        wl_ratio = self.spin_sim_win_loss_ratio.get_text()
        fraction = self.spin_sim_fraction.get_text()

        print(build_one_curve(trades, win_rate, wl_ratio, fraction))

        # # self.en_directory.set_text(c.PROJ_SRC)
        # # print(self.entry_mc_target_dir.get_text())
        # native = Gtk.FileDialog()
        # # on select_folder: https://docs.gtk.org/gtk4/method.FileDialog.select_folder.html
        # native.select_folder(self, None, self._on_select_folder_complete)
