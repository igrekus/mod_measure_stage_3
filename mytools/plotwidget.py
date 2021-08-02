from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.figure import Figure


class PlotWidget(QWidget):

    def __init__(self, parent=None, toolbar=False):
        super().__init__(parent=parent)

        self._layout = QVBoxLayout(self)
        self._figure = Figure()
        self._layout.addWidget(FigureCanvasQTAgg(self._figure))
        if toolbar:
            self._layout.addWidget(NavigationToolbar2QT(canvas=self._figure.canvas, parent=None))

        self._ax = self._figure.gca()

    def set_tight_layout(self, *args, **kwargs):
        self._figure.set_tight_layout(*args, **kwargs)

    def subplots_adjust(self, *args, **kwargs):
        self._figure.subplots_adjust(*args, **kwargs)

    def set_title(self, *args, **kwargs):
        self._ax.set_title(*args, **kwargs)

    def set_xscale(self, *args, **kwargs):
        self._ax.set_xscale(*args, **kwargs)

    def set_xlabel(self, *args, **kwargs):
        self._ax.set_xlabel(*args, **kwargs)

    def set_xlim(self, *args, **kwargs):
        self._ax.set_xlim(*args, **kwargs)

    def set_yscale(self, *args, **kwargs):
        self._ax.set_yscale(*args, **kwargs)

    def set_ylabel(self, *args, **kwargs):
        self._ax.set_ylabel(*args, **kwargs)

    def set_ylim(self, *args, **kwargs):
        self._ax.set_ylim(*args, **kwargs)

    def grid(self, *args, **kwargs):
        self._ax.grid(*args, **kwargs)

    def clear(self, *args, **kwargs):
        self._ax.clear(*args, **kwargs)
        self._figure.canvas.draw()

    def plot(self, *args, **kwargs):
        self._ax.plot(*args, **kwargs)
        self._figure.canvas.draw()
        self._figure.tight_layout()

    def draw(self, *args, **kwargs):
        self._figure.canvas.draw(*args, **kwargs)

    def axhline(self, *args, **kwargs):
        self._ax.axhline(*args, **kwargs)
        self._figure.canvas.draw()

    def axvline(self, *args, **kwargs):
        self._ax.axvline(*args, **kwargs)
        self._figure.canvas.draw()

    def set_yticks(self, *args, **kwargs):
        self._ax.set_yticks(*args, **kwargs)
        self._figure.canvas.draw()

    def get_yticks(self):
        return self._ax.get_yticks(), self._ax.get_yticklabels()

    def savefig(self, *args, **kwargs):
        self._figure.savefig(*args, **kwargs)

    def legend(self, *args, **kwargs):
        self._ax.legend(*args, **kwargs)
        self._figure.canvas.draw()

    def tight_layout(self, *args, **kwargs):
        self._figure.tight_layout(*args, **kwargs)

