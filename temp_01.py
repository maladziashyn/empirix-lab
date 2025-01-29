import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib

class MyWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="TextView Example")
        self.set_default_size(400, 300)

        # Create TextView and ScrolledWindow
        self.textview = Gtk.TextView()
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.buffer = self.textview.get_buffer()

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.textview)
        self.set_child(scrolled_window)

        # Button to start computation
        self.button = Gtk.Button(label="Start Computation")
        self.button.connect("clicked", self.start_computation)
        self.set_titlebar(self.button)

    def start_computation(self, button):
        # Disable button to prevent re-clicks
        button.set_sensitive(False)

        # Start a long computation incrementally
        self.counter = 0
        self.max_count = 100  # Simulating a task with 100 steps
        GLib.idle_add(self.perform_step)

    def perform_step(self):
        if self.counter < self.max_count:
            # Simulate computation
            self.counter += 1

            # Update TextView
            end_iter = self.buffer.get_end_iter()
            self.buffer.insert(end_iter, f"Step {self.counter} completed\n")

            # Allow GUI to update
            return True  # Continue calling this function
        else:
            # Re-enable button when done
            self.button.set_sensitive(True)
            return False  # Stop calling this function

def main():
    # Create application
    app = Gtk.Application()
    app.connect("activate", lambda app: MyWindow().show())
    app.run()


if __name__ == "__main__":
    main()
