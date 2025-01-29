import gi
gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")
import sqlite3
import time

from concurrent.futures import ProcessPoolExecutor
from gi.repository import Adw, Gio, Gtk
from itertools import repeat

import config as c


class MyApp(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id=c.APP_ID,
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

    def do_activate(self):
        """Called when the application is activated.
        We raise the application's main window, creating it if necessary."""

        win = self.props.active_window
        if not win:
            win = AppWindowMp(application=self)
        win.present()


@Gtk.Template(filename="/home/rsm/Documents/MyProjects/empirix-lab/gresource/window_mp.ui")
class AppWindowMp(Adw.ApplicationWindow):
    __gtype_name__ = "AppWindowMp"

    # new_page = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title(c.APP_NAME)

    @Gtk.Template.Callback("btn_callback_01")
    def click_button(self, *args):
        print("click")
        result = self.run_mp()
        print(result)


    def run_mp(self):
        complete_res = list()
        with ProcessPoolExecutor() as executor:
            results = executor.map(
                long_computation,
                # repeat(ins_mapped, len(files)),
                [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
            )
            for res in results:
                complete_res.append(res)

        return complete_res


def long_computation(n):
    time.sleep(2)
    return n ** 2


def main():
    """The application's entry point."""

    # Show main window
    app = MyApp()
    app.run(None)


if __name__ == "__main__":
    main()
