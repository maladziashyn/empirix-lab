# from gi.repository import GObject

from gresource.sanity_check import SanityCheckScrolledWindow
from gresource.monte_carlo import MonteCarloScrolledWindow


# # NB: GObject.type_ensure is applicable when gresource is not used
# def load_widgets():
#     GObject.type_ensure(MonteCarloScrolledWindow)
#     # GObject.type_ensure(AnotherNewClass)
