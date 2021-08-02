from pyqtgraph import GraphicsLayoutWidget, LabelItem


class GraphWidget(GraphicsLayoutWidget):
    def __init__(self, *args, bg='w', **kwargs):
        super().__init__(*args, **kwargs)
        self.setBackground(background=bg)

        self._plots = []
        self._labels = []
        self._curves = {}

    def addPlot(self, *args, justify='right', **kwargs):
        # self._plots.append(super().addPlot(args, kwargs))
        # self._labels.append(LabelItem(justify=justify))
        # self.addItem(self._labels[-1])

        print(self._plots, self._labels)
        return self._plots[-1]
