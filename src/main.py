import gi
# gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio
from sys import path

import session_var as sv

if sv.HOME_SRC not in path:
    path.append(sv.HOME_SRC)

# from ui.load_widgets import load_widgets  # load custom widget templates
from widget.window import AppWindow


class MyApp(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id=sv.APP_ID,
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

    def do_activate(self):
        """Called when the application is activated.
        We raise the application's main window, creating it if necessary."""

        win = self.props.active_window
        if not win:
            win = AppWindow(application=self)
        win.present()


def main():
    """The application's entry point."""

    app = MyApp()
    app.run(None)


if __name__ == "__main__":
    main()
