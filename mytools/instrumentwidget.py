from io import BytesIO

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget


markup = BytesIO(bytes('''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>widgetInstrument</class>
 <widget class="QWidget" name="widgetInstrument">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>168</width>
    <height>59</height>
   </rect>
  </property>
  <property name="sizePolicy">
   <sizepolicy hsizetype="Minimum" vsizetype="Minimum">
    <horstretch>0</horstretch>
    <verstretch>0</verstretch>
   </sizepolicy>
  </property>
  <layout class="QVBoxLayout" name="verticalLayout">
   <property name="spacing">
    <number>2</number>
   </property>
   <property name="sizeConstraint">
    <enum>QLayout::SetMinimumSize</enum>
   </property>
   <property name="leftMargin">
    <number>2</number>
   </property>
   <property name="topMargin">
    <number>2</number>
   </property>
   <property name="rightMargin">
    <number>2</number>
   </property>
   <property name="bottomMargin">
    <number>3</number>
   </property>
   <item>
    <layout class="QHBoxLayout" name="horizontalLayout">
     <property name="sizeConstraint">
      <enum>QLayout::SetMinimumSize</enum>
     </property>
     <item>
      <widget class="QLabel" name="label">
       <property name="text">
        <string>stub</string>
       </property>
      </widget>
     </item>
     <item>
      <widget class="QLineEdit" name="editAddress">
       <property name="sizePolicy">
        <sizepolicy hsizetype="MinimumExpanding" vsizetype="Fixed">
         <horstretch>0</horstretch>
         <verstretch>0</verstretch>
        </sizepolicy>
       </property>
       <property name="minimumSize">
        <size>
         <width>120</width>
         <height>0</height>
        </size>
       </property>
       <property name="placeholderText">
        <string>адрес...</string>
       </property>
      </widget>
     </item>
    </layout>
   </item>
   <item>
    <widget class="QLineEdit" name="editStatus">
     <property name="sizePolicy">
      <sizepolicy hsizetype="MinimumExpanding" vsizetype="Fixed">
       <horstretch>0</horstretch>
       <verstretch>0</verstretch>
      </sizepolicy>
     </property>
     <property name="minimumSize">
      <size>
       <width>150</width>
       <height>0</height>
      </size>
     </property>
     <property name="placeholderText">
      <string>статус...</string>
     </property>
    </widget>
   </item>
  </layout>
 </widget>
 <resources/>
 <connections/>
</ui>
''', encoding='utf-8'))


class InstrumentWidget(QWidget):

    def __init__(self, parent=None, title='stub', addr='stub'):
        super().__init__(parent=parent)

        # TODO fix xml parse error if read from bundled markup
        # HACK project dir must have 'instrumentwidget.ui' file for now
        self._ui = uic.loadUi('instrumentwidget.ui', self)
        # self._ui = uic.loadUi(markup, self)

        self.title = title
        self.address = addr
        self.status = 'нет подключения'

    @property
    def title(self):
        return self._ui.label.text()
    @title.setter
    def title(self, value):
        self._ui.label.setText(value)

    @property
    def address(self):
        return self._ui.editAddress.text()
    @address.setter
    def address(self, value):
        self._ui.editAddress.setText(value)

    @property
    def status(self):
        return self._ui.editStatus.text()
    @status.setter
    def status(self, value):
        self._ui.editStatus.setText(value)
