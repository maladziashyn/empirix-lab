import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from config import APP_URL

from core.monte_carlo import build_one_curve


@Gtk.Template(resource_path=f"{APP_URL}/monte_carlo.ui")
class MonteCarloScrolledWindow(Gtk.ScrolledWindow):
    __gtype_name__ = "MonteCarloScrolledWindow"

    entry_target_dir = Gtk.Template.Child()  # entry row
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
        # self.en_directory.set_text(c.PROJ_SRC)
        # print(self.entry_mc_target_dir.get_text())
        native = Gtk.FileDialog()

        # on select_folder: https://docs.gtk.org/gtk4/method.FileDialog.select_folder.html
        native.select_folder(
            None,  # self.btn_target_dir.get_ancestor(Gtk.Window),  # can be None
            None,
            self._on_select_folder_complete
        )

    def _on_select_folder_complete(self, dialog, result):
        # folder = dialog.select_folder_finish(result)
        if (folder := dialog.select_folder_finish(result)):
            print(folder.get_path())
            self.entry_target_dir.set_text(folder.get_path())

    @Gtk.Template.Callback("btn_callback_02")
    def click_run_randnum(self, *args):
        print("Clicked Run RANDNUM Simulation button")
        print(self.entry_target_dir.get_text())
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
