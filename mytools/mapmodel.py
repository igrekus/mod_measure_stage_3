import bisect

import mytools.const
from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex, QVariant


class MapModel(QAbstractListModel):

    RoleNodeId = mytools.const.RoleNodeId

    def __init__(self, parent=None, data=None, sort=True):
        super(MapModel, self).__init__(parent)
        self.mapData = dict()
        self.strList = list()
        self.tooltipList = list()

        self._sort = sort

        if data is not None:
            self.initModel(data)

    def initModel(self, data: dict):
        self.beginResetModel()
        self.mapData = data
        vals = sorted(self.mapData.values(), key=lambda v: v[0]) if self._sort else list(self.mapData.values())
        if isinstance(vals[0], tuple):
            self.strList = [val[0] for val in vals]
            self.tooltipList = [val[1] for val in vals]
        else:
            self.strList = [val for val in vals]
            self.tooltipList = [val for val in vals]
        self.endResetModel()

    def copyItems(self, model: dict):
        self.beginResetModel()
        for k, v in model.mapData.items():
            self.mapData[k] = v
        self.strList = list(sorted(self.mapData.values()))
        self.endResetModel()

    def clear(self):
        self.beginRemoveRows(QModelIndex(), 0, len(self.mapData) - 1)
        self.mapData.clear()
        self.strList.clear()
        self.endRemoveRows()

    def addItemAtPosition(self, pos, id_, string):
        self.beginInsertRows(QModelIndex(), pos, pos)
        self.mapData[id_] = string
        self.strList.insert(pos, string)
        self.endInsertRows()

    def addItem(self, id_, string):
        self.mapData[id_] = string

        tmplist = self.strList.copy()[1:]

        pos = bisect.bisect_left(tmplist, string) + 1

        self.beginInsertRows(QModelIndex(), pos, pos)
        self.strList.insert(pos, string)
        self.endInsertRows()

    def updateItem(self, id_, string):
        pos = self.strList.index(self.mapData[id_])

        self.mapData[id_] = string
        self.strList[pos] = string

    def removeItem(self, id_):
        self.strList.remove(self.mapData[id_])
        del self.mapData[id_]

    def isEmpty(self):
        return not bool(self.strList)

    def headerData(self, section, orientation, role=None):
        headers = ["Имя"]
        if orientation == Qt.Horizontal and section < len(headers):
            return QVariant(headers[section])

        return QVariant()

    def rowCount(self, parent):
        if parent.isValid():
            return 0
        return len(self.strList)

    def data(self, index, role=None):
        if not index.isValid():
            return QVariant

        row = index.row()

        if role == Qt.DisplayRole:
            if index.column() == 0:
                return QVariant(self.strList[row])
        elif role == Qt.ToolTipRole:
            if index.column() == 0:
                return QVariant(self.tooltipList[row])

        elif role == mytools.const.RoleNodeId:
            return QVariant(self.getId(self.strList[row]))

        return QVariant()

    def getId(self, search_str=""):
        for i, string in self.mapData.items():
            if isinstance(string, tuple):
                if string[0] == search_str:
                    return i
            else:
                if string == search_str:
                    return i

    def getData(self, id_=None):
        return self.mapData[id_]

    def getIdByIndex(self, index):
        return self.getId(self.strList[index])
