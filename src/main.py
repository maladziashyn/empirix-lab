import gi
# gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio

from gresource import init_gresource as ir
ir.init_resources()

from gresource.init_widgets import load_widgets
from gresource.window import AppWindow


class MyApp(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id=ir.APP_ID,
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
