from io import BytesIO

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QRunnable, QThreadPool
from PyQt5.QtWidgets import QWidget

from mytools.instrumentwidget import InstrumentWidget


markup = BytesIO(bytes('''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>widgetInstrumentController</class>
 <widget class="QWidget" name="widgetInstrumentController">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>152</width>
    <height>68</height>
   </rect>
  </property>
  <property name="sizePolicy">
   <sizepolicy hsizetype="Minimum" vsizetype="Minimum">
    <horstretch>0</horstretch>
    <verstretch>0</verstretch>
   </sizepolicy>
  </property>
  <property name="windowTitle">
   <string/>
  </property>
  <layout class="QVBoxLayout" name="verticalLayout_3">
   <property name="leftMargin">
    <number>3</number>
   </property>
   <property name="topMargin">
    <number>0</number>
   </property>
   <property name="rightMargin">
    <number>3</number>
   </property>
   <property name="bottomMargin">
    <number>2</number>
   </property>
   <item>
    <widget class="QGroupBox" name="grpInstruments">
     <property name="enabled">
      <bool>true</bool>
     </property>
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
      <string>Инструменты</string>
     </property>
     <property name="checkable">
      <bool>true</bool>
     </property>
     <property name="checked">
      <bool>true</bool>
     </property>
     <layout class="QVBoxLayout" name="verticalLayout_2">
      <item>
       <widget class="QWidget" name="widgetContainer" native="true">
        <layout class="QVBoxLayout" name="layInstruments">
         <property name="spacing">
          <number>0</number>
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
          <layout class="QHBoxLayout" name="horizontalLayout">
           <property name="rightMargin">
            <number>1</number>
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
            <widget class="QPushButton" name="btnConnect">
             <property name="text">
              <string>Подключить</string>
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
</ui>
''', encoding='utf-8'))


class ConnectTask(QRunnable):

    def __init__(self, fn, end, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.end = end
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.fn(*self.args, **self.kwargs)
        self.end()


class ConnectionWidget(QWidget):

    connected = pyqtSignal()

    def __init__(self, parent=None, controller=None):
        super().__init__(parent=parent)

        self._ui = uic.loadUi(markup, self)
        self._controller = controller
        self._threads = QThreadPool()

        self._widgets = {
            k: InstrumentWidget(parent=self, title=f'{k}', addr=f'{v.addr}')
            for k, v in self._controller.requiredInstruments.items()
        }

        self._setupUi()

    def _setupUi(self):
        for i, iw in enumerate(self._widgets.items()):
            self._ui.layInstruments.insertWidget(i, iw[1])

    @pyqtSlot()
    def on_btnConnect_clicked(self):
        print('connect')

        self._threads.start(ConnectTask(self._controller.connect,
                                        self.connectTaskComplete,
                                        {k: w.address for k, w in self._widgets.items()}))

    @pyqtSlot(bool)
    def on_grpInstruments_toggled(self, state):
        self._ui.widgetContainer.setVisible(state)

    def connectTaskComplete(self):
        if not self._controller.found:
            print('connect error, check connection')
            return

        for w, s in zip(self._widgets.values(), self._controller.status):
            w.status = s
        self.connected.emit()
