from gi.repository import GObject

from gresource.new_page import MyClass
# from gresource.another_new_page import AnotherNewClass


def load_widgets():
    GObject.type_ensure(MyClass)
    # GObject.type_ensure(AnotherNewClass)
