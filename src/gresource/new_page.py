import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


@Gtk.Template(resource_path="/eu/rsmlabs/EmpirixLab/new_page.ui")
class MyClass(Gtk.Label):
    __gtype_name__ = 'MyClass'

    # label = Gtk.Template.Child()
    # my_widget_template = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
