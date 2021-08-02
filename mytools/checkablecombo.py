from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QComboBox, QStylePainter, QStyleOptionComboBox, QStyle
from PyQt5.QtCore import pyqtSignal


class CheckableComboBox(QComboBox):

    popupClosed = pyqtSignal()

    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)

        self.emptyCheckText = "Выберите запись..."
        self.fullCheckText = "Набор записей..."

    def paintEvent(self, e):
        painter = QStylePainter(self)
        painter.setPen(self.palette().color(QPalette.Text))

        opt = QStyleOptionComboBox()
        self.initStyleOption(opt)

        count = self.model().checkedCount()
        if count == 0:
            opt.currentText = self.emptyCheckText
        elif count == 3:
            opt.currentText = self.model().singleCheckText
        else:
            opt.currentText = self.fullCheckText

        painter.drawComplexControl(QStyle.CC_ComboBox, opt)

        painter.drawControl(QStyle.CE_ComboBoxLabel, opt)

    def hidePopup(self):
        super(CheckableComboBox, self).hidePopup()
        self.popupClosed.emit()

