if __name__ == "__main__":
    from sys import platform

    if platform == "win32":
        from multiprocessing import freeze_support
        freeze_support()

    import gi
    gi.require_version("Adw", "1")
    gi.require_version("Gtk", "4.0")
    import sqlite3

    from gi.repository import Adw, Gio, Gtk
    from os.path import isfile

    import config as c

    from core import init_work_env
    init_work_env.main()  # must init work env before load_widgets as they need the DB to use.

    from gresource import compile_register
    from gresource import load_widgets
    from gresource.window import AppWindow


    class MyApp(Adw.Application):
        """The main application singleton class."""

        def __init__(self):
            super().__init__(application_id=c.APP_ID,
                            flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

            self.create_action("quit", lambda *_: self.quit(), ["<primary>q"])
            self.create_action("about", self.on_about_action)

        def do_activate(self):
            """Called when the application is activated.
            We raise the application's main window, creating it if necessary."""

            win = self.props.active_window
            if not win:
                win = AppWindow(application=self)
            win.present()

        # Add actions for the menu

        def on_about_action(self, *args):
            """Callback for the app.about action."""
            about = Adw.AboutDialog(
                application_name=c.APP_NAME,
                application_icon=c.APP_ID,
                developer_name=c.APP_DEV_NAME,
                version=c.VERSION,
                developers=c.APP_DEVS,
                copyright=c.APP_COPYRIGHT,
                website=c.WEB_HOMEPAGE
            )
            about.set_license_type(Gtk.License.GPL_3_0_ONLY)
            # Translators: Replace "translator-credits" with your name/username, and optionally an email or URL.
            # about.set_translator_credits(_('translator-credits'))
            about.present(self.props.active_window)

        def create_action(self, name, callback, shortcuts=None):
            """Add an application action.

            Args:
                name: the name of the action
                callback: the function to be called when the action is
                activated
                shortcuts: an optional list of accelerators
            """
            action = Gio.SimpleAction.new(name, None)
            action.connect("activate", callback)
            self.add_action(action)
            if shortcuts:
                self.set_accels_for_action(f"app.{name}", shortcuts)


    def main():
        """The application's entry point."""

        # Show main window
        app = MyApp()
        app.run(None)


    main()
