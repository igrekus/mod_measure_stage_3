from io import BytesIO

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThreadPool, QRunnable
from PyQt5.QtWidgets import QWidget

from .deviceselectwidget import DeviceSelectWidget


markup = BytesIO(bytes('''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>widgetMeasure</class>
 <widget class="QWidget" name="widgetMeasure">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>224</width>
    <height>113</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Form</string>
  </property>
  <layout class="QVBoxLayout" name="layparams">
   <property name="leftMargin">
    <number>3</number>
   </property>
   <property name="topMargin">
    <number>3</number>
   </property>
   <property name="rightMargin">
    <number>3</number>
   </property>
   <property name="bottomMargin">
    <number>0</number>
   </property>
   <item>
    <widget class="QGroupBox" name="grpParams">
     <property name="sizePolicy">
      <sizepolicy hsizetype="Minimum" vsizetype="Minimum">
       <horstretch>0</horstretch>
       <verstretch>0</verstretch>
      </sizepolicy>
     </property>
     <property name="minimumSize">
      <size>
       <width>0</width>
       <height>0</height>
      </size>
     </property>
     <property name="title">
      <string>Параметры</string>
     </property>
     <property name="checkable">
      <bool>true</bool>
     </property>
     <layout class="QVBoxLayout" name="verticalLayout">
      <property name="spacing">
       <number>3</number>
      </property>
      <property name="leftMargin">
       <number>3</number>
      </property>
      <property name="topMargin">
       <number>3</number>
      </property>
      <property name="rightMargin">
       <number>2</number>
      </property>
      <property name="bottomMargin">
       <number>6</number>
      </property>
      <item>
       <widget class="QWidget" name="widgetContainer" native="true">
        <layout class="QVBoxLayout" name="layParams">
         <property name="spacing">
          <number>2</number>
         </property>
         <property name="leftMargin">
          <number>0</number>
         </property>
         <property name="topMargin">
          <number>0</number>
         </property>
         <property name="rightMargin">
          <number>0</number>
         </property>
         <property name="bottomMargin">
          <number>0</number>
         </property>
         <item>
          <layout class="QHBoxLayout" name="horizontalLayout_2">
           <property name="leftMargin">
            <number>0</number>
           </property>
           <property name="topMargin">
            <number>0</number>
           </property>
           <property name="rightMargin">
            <number>8</number>
           </property>
           <property name="bottomMargin">
            <number>0</number>
           </property>
           <item>
            <spacer name="horizontalSpacer_2">
             <property name="orientation">
              <enum>Qt::Horizontal</enum>
             </property>
             <property name="sizeHint" stdset="0">
              <size>
               <width>40</width>
               <height>20</height>
              </size>
             </property>
            </spacer>
           </item>
           <item>
            <widget class="QPushButton" name="btnCheck">
             <property name="enabled">
              <bool>false</bool>
             </property>
             <property name="text">
              <string>Проверить</string>
             </property>
            </widget>
           </item>
          </layout>
         </item>
         <item>
          <layout class="QHBoxLayout" name="horizontalLayout_3">
           <property name="leftMargin">
            <number>0</number>
           </property>
           <property name="topMargin">
            <number>0</number>
           </property>
           <property name="rightMargin">
            <number>8</number>
           </property>
           <property name="bottomMargin">
            <number>0</number>
           </property>
           <item>
            <spacer name="horizontalSpacer_3">
             <property name="orientation">
              <enum>Qt::Horizontal</enum>
             </property>
             <property name="sizeHint" stdset="0">
              <size>
               <width>40</width>
               <height>20</height>
              </size>
             </property>
            </spacer>
           </item>
           <item>
            <widget class="QPushButton" name="btnCalibrateLO">
             <property name="enabled">
              <bool>false</bool>
             </property>
             <property name="text">
              <string>Кал. LO</string>
             </property>
            </widget>
           </item>
           <item>
            <widget class="QPushButton" name="btnCalibrateMod">
             <property name="enabled">
              <bool>false</bool>
             </property>
             <property name="text">
              <string>Кал. мод.</string>
             </property>
            </widget>
           </item>
           <item>
            <widget class="QPushButton" name="btnCalibrateRF">
             <property name="enabled">
              <bool>false</bool>
             </property>
             <property name="text">
              <string>Кал. RF</string>
             </property>
            </widget>
           </item>
          </layout>
         </item>
         <item>
          <layout class="QHBoxLayout" name="horizontalLayout">
           <property name="rightMargin">
            <number>8</number>
           </property>
           <item>
            <spacer name="horizontalSpacer">
             <property name="orientation">
              <enum>Qt::Horizontal</enum>
             </property>
             <property name="sizeHint" stdset="0">
              <size>
               <width>40</width>
               <height>20</height>
              </size>
             </property>
            </spacer>
           </item>
           <item>
            <widget class="QPushButton" name="btnMeasure">
             <property name="enabled">
              <bool>false</bool>
             </property>
             <property name="text">
              <string>Измерить</string>
             </property>
            </widget>
           </item>
           <item>
            <widget class="QPushButton" name="btnCancel">
             <property name="enabled">
              <bool>false</bool>
             </property>
             <property name="text">
              <string>Отменить</string>
             </property>
            </widget>
           </item>
          </layout>
         </item>
        </layout>
       </widget>
      </item>
     </layout>
    </widget>
   </item>
  </layout>
 </widget>
 <resources/>
 <connections/>
</ui>''', encoding='utf-8'))


class MeasureTask(QRunnable):

    def __init__(self, fn, end, token, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.end = end
        self.token = token
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.fn(self.token, *self.args, **self.kwargs)
        self.end()


class CancelToken:
    def __init__(self):
        self.cancelled = False


class MeasureWidget(QWidget):

    selectedChanged = pyqtSignal(int)
    sampleFound = pyqtSignal()
    measureComplete = pyqtSignal()
    measureStarted = pyqtSignal()
    calibrateFinished = pyqtSignal()

    def __init__(self, parent=None, controller=None):
        super().__init__(parent=parent)

        self._ui = uic.loadUi(markup, self)
        self._controller = controller
        self._threads = QThreadPool()

        self._token = CancelToken()

        self._paramInputWidget = DeviceSelectWidget(parent=self, params=self._controller.deviceParams)
        self._ui.layParams.insertWidget(0, self._paramInputWidget)
        self._paramInputWidget.selectedChanged.connect(self.on_selectedChanged)

        self._selectedDevice = self._paramInputWidget.selected

    def check(self):
        print('checking...')
        self._modeDuringCheck()
        self._threads.start(MeasureTask(self._controller.check,
                                        self.checkTaskComplete,
                                        self._selectedDevice))

    def checkTaskComplete(self):
        if not self._controller.present:
            print('sample not found')
            # QMessageBox.information(self, 'Ошибка', 'Не удалось найти образец, проверьте подключение')
            self._modePreCheck()
            return False

        print('found sample')
        self._modePreMeasure()
        self.sampleFound.emit()
        return True

    def calibrate(self, what):
        raise NotImplementedError

    def calibrateTaskComplete(self):
        raise NotImplementedError

    def measure(self):
        print('measuring...')
        self._modeDuringMeasure()
        self._threads.start(MeasureTask(self._controller.measure,
                                        self.measureTaskComplete,
                                        self._selectedDevice))

    def cancel(self):
        pass

    def measureTaskComplete(self):
        if not self._controller.hasResult:
            print('error during measurement')
            return False

        self._modePreCheck()
        self.measureComplete.emit()
        return True

    @pyqtSlot()
    def on_instrumentsConnected(self):
        self._modePreCheck()

    @pyqtSlot()
    def on_btnCheck_clicked(self):
        print('checking sample presence')
        self.check()

    @pyqtSlot()
    def on_btnCalibrateLO_clicked(self):
        print('start LO calibration')
        self.calibrate('LO')

    @pyqtSlot()
    def on_btnCalibrateRF_clicked(self):
        print('start RF calibration')
        self.calibrate('RF')

    @pyqtSlot()
    def on_btnCalibrateMod_clicked(self):
        print('start Mod calibration')
        self.calibrate('Mod')

    @pyqtSlot()
    def on_btnMeasure_clicked(self):
        print('start measure')
        self.measureStarted.emit()
        self.measure()

    @pyqtSlot()
    def on_btnCancel_clicked(self):
        print('cancel click')
        self.cancel()

    @pyqtSlot(int)
    def on_selectedChanged(self, value):
        self._selectedDevice = value
        self.selectedChanged.emit(value)

    @pyqtSlot(bool)
    def on_grpParams_toggled(self, state):
        self._ui.widgetContainer.setVisible(state)

    def _modePreConnect(self):
        self._ui.btnCheck.setEnabled(False)
        self._ui.btnMeasure.setEnabled(False)
        self._ui.btnCancel.setEnabled(False)
        self._ui.btnCalibrateLO.setEnabled(False)
        self._ui.btnCalibrateRf.setEnabled(False)
        self._ui.btnCalibrateMod.setEnabled(False)
        self._paramInputWidget.enabled = True

    def _modePreCheck(self):
        self._ui.btnCheck.setEnabled(True)
        self._ui.btnMeasure.setEnabled(False)
        self._ui.btnCancel.setEnabled(False)
        self._ui.btnCalibrateLO.setEnabled(False)
        self._ui.btnCalibrateRF.setEnabled(False)
        self._ui.btnCalibrateMod.setEnabled(False)
        self._paramInputWidget.enabled = True

    def _modeDuringCheck(self):
        self._ui.btnCheck.setEnabled(False)
        self._ui.btnMeasure.setEnabled(False)
        self._ui.btnCancel.setEnabled(False)
        self._ui.btnCalibrateLO.setEnabled(False)
        self._ui.btnCalibrateRF.setEnabled(False)
        self._ui.btnCalibrateMod.setEnabled(False)
        self._paramInputWidget.enabled = False

    def _modePreMeasure(self):
        self._ui.btnCheck.setEnabled(False)
        self._ui.btnMeasure.setEnabled(True)
        self._ui.btnCancel.setEnabled(False)
        self._ui.btnCalibrateLO.setEnabled(True)
        self._ui.btnCalibrateRF.setEnabled(True)
        self._ui.btnCalibrateMod.setEnabled(True)
        self._paramInputWidget.enabled = False

    def _modeDuringMeasure(self):
        self._ui.btnCheck.setEnabled(False)
        self._ui.btnMeasure.setEnabled(False)
        self._ui.btnCancel.setEnabled(True)
        self._ui.btnCalibrateLO.setEnabled(False)
        self._ui.btnCalibrateRF.setEnabled(False)
        self._ui.btnCalibrateMod.setEnabled(False)
        self._paramInputWidget.enabled = False

    def updateWidgets(self, params):
        raise NotImplementedError
