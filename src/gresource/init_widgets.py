from gi.repository import GObject

from gresource.monte_carlo import MonteCarloScrolledWindow
# from gresource.another_new_page import AnotherNewClass


def load_widgets():
    GObject.type_ensure(MonteCarloScrolledWindow)
    # GObject.type_ensure(AnotherNewClass)
