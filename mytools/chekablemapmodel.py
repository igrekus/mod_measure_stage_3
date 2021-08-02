import bisect

import mytools.const
from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex, QVariant


class CheckableMapModel(QAbstractListModel):

    def __init__(self, parent=None, data=None, sort: bool=True):
        super(CheckableMapModel, self).__init__(parent)
        self.mapData = dict()
        self.strList = list()
        self.checkList = list()

        self.itemsCheckable = True
        self.singleCheckText = ""

        if data is not None:
            if sort:
                self.initModel(data, sort=True)
            else:
                self.initModel(data, sort=False)

    def initModel(self, data: dict, sort: bool=True):
        count = len(data.values()) - 1
        if count < 0:
            count = 0
        # self.beginResetModel()
        self.beginInsertRows(QModelIndex(), 0, count)
        self.mapData = data
        if sort:
            self.strList = list(sorted(self.mapData.values()))
        else:
            self.strList = list(self.mapData.values())
        self.checkList = [2 for i in range(len(self.strList))]
        self.endInsertRows()
        # self.endResetModel()

    def copyItems(self, model):
        self.beginResetModel()
        for k, v in model.mapData.items():
            self.mapData[k] = v
        self.strList = list(sorted(self.mapData.values()))
        self.checkList = [2 for i in range(len(self.strList))]
        self.endResetModel()

    def clear(self):
        self.beginRemoveRows(QModelIndex(), 0, len(self.mapData) - 1)
        self.mapData.clear()
        self.strList.clear()
        self.checkList.clear()
        self.endRemoveRows()

    def addItemAtPosition(self, pos, id_, string):
        self.beginInsertRows(QModelIndex(), pos, pos)
        self.mapData[id_] = string
        self.strList.insert(pos, string)
        self.checkList.insert(pos, 2)
        self.endInsertRows()

    def addItem(self, id_, string):
        self.mapData[id_] = string

        tmplist = self.strList.copy()[1:]

        pos = bisect.bisect_left(tmplist, string) + 1

        self.beginInsertRows(QModelIndex(), pos, pos)
        self.strList.insert(pos, string)
        self.checkList.insert(pos, 2)
        self.endInsertRows()

    def updateItem(self, id_, string):
        pos = self.strList.index(self.mapData[id_])

        self.mapData[id_] = string
        self.strList[pos] = string

        # self.dataChanged(self.index(pos, 0, QModelIndex()), self.index(pos, 0, QModelIndex()))

    def removeItem(self, id_):
        # self.beginRemoveRows()
        self.strList.remove(self.mapData[id_])
        self.checkList = [2 for i in range(len(self.strList))]
        del self.mapData[id_]
        # self.endRemoveRows()

    def isEmpty(self):
        return not bool(self.strList)

    def checkedCount(self):
        return sum(self.checkList)

    def makeCheckable(self):
        self.itemsCheckable = True

    def makeUncheckable(self):
        self.itemsCheckable = False

    def headerData(self, section, orientation, role=None):
        if orientation == Qt.Horizontal:
            return QVariant("Имя")
        return QVariant()

    def rowCount(self, parent):
        if parent.isValid():
            return 0
        return len(self.strList)

    def setData(self, index, value, role=None):
        row = index.row()
        if role == Qt.CheckStateRole and index.column() == 0:
            if row == 0:
                self.checkList = [value for i in range(len(self.strList))]
            else:
                self.checkList[row] = value
                if sum(self.checkList[1:]) < len(self.checkList[1:]) * 2:
                    self.checkList[0] = 1
                elif sum(self.checkList[1:]) == len(self.checkList[1:]) * 2:
                    self.checkList[0] = 2

            self.dataChanged.emit(self.index(0, 0, QModelIndex()),
                                  self.index(len(self.strList) - 1, 0, QModelIndex()), [])
            if sum(self.checkList) == 3:
                self.singleCheckText = self.strList[self.checkList.index(2)]
            return True

        return False

    def data(self, index, role=None):
        if not index.isValid():
            return QVariant

        row = index.row()

        if role == Qt.DisplayRole or role == Qt.ToolTipRole:
            if index.column() == 0:
                return QVariant(self.strList[row])

        if role == Qt.CheckStateRole:
            if self.itemsCheckable:
                return QVariant(self.checkList[row])

        elif role == mytools.const.RoleNodeId:
            return QVariant(self.getId(self.strList[row]))

        elif role == mytools.const.RoleFilterData:
            return self.getSelectedIds()

        return QVariant()

    def flags(self, index):
        if self.itemsCheckable:
            if index.column() == 0:
                return Qt.ItemIsUserCheckable | Qt.ItemIsEnabled
        return super(CheckableMapModel, self).flags(index)

    def getId(self, search_str=""):
        for i, string in self.mapData.items():
            if string == search_str:
                return i

    def getSelectedIds(self):
        data = list()
        for string, check in zip(self.strList, self.checkList):
            if check:
                data.append(self.getId(string))

        if 0 in data:
            data.remove(0)
        return data

    def getData(self, id_=None):
        return self.mapData[id_]

    def getIdByIndex(self, index):
        return self.getId(self.strList[index])

