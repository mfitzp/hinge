from .qt import *


class QColorButton(QPushButton):
    '''
    Custom Qt Widget to show a chosen color.
    
    Left-clicking the button shows the color-chooser, while
    right-clicking resets the color to None (no-color).    
    '''

    colorChanged = pyqtSignal()

    def __init__(self, is_reset_enabled=True, *args, **kwargs):
        super(QColorButton, self).__init__(*args, **kwargs)

        self._color = None
        self.setMaximumWidth(32)
        self.pressed.connect(self.onColorPicker)

        self.is_reset_enabled = is_reset_enabled

    def setColor(self, color):
        if color != self._color:
            self._color = color
            self.colorChanged.emit()

        if self._color:
            self.setStyleSheet("background-color: %s;" % self._color)
        else:
            self.setStyleSheet("")

    def color(self):
        return self._color

    def onColorPicker(self):
        '''
        Show color-picker dialog to select color.
        
        This should use the Qt-defined non-native dialog so custom colours
        can be auto-defined from the currently set palette - but it doesn't work due
        to a known bug - should auto-fix on Qt 5.2.2.
        '''
        dlg = QColorDialog(self)
        if self._color:
            dlg.setCurrentColor(QColor(self._color))

        dlg.setOption(QColorDialog.DontUseNativeDialog)
        # FIXME: Add colors from current default set to the custom color table
        # dlg.setCustomColor(0, QColor('red') )
        if dlg.exec_():
            self.setColor(dlg.currentColor().name())

    def mousePressEvent(self, e):
        if self.is_reset_enabled and e.button() == Qt.RightButton:
            self.setColor(None)
        else:
            return super(QColorButton, self).mousePressEvent(e)


class QNoneDoubleSpinBox(QDoubleSpinBox):
    '''
    Custom Qt widget to offer a DoubleSpinBox that can hold null values.
    
    The value can be set to null with right-click. When set to null the widget
    appears faded.
    '''

    def __init__(self, *args, **kwargs):
        super(QNoneDoubleSpinBox, self).__init__(*args, **kwargs)
        self.is_None = False

    def value(self):
        if self.is_None:
            return None
        else:
            return super(QNoneDoubleSpinBox, self).value()

    def setValue(self, v):
        if v is None:
            self.is_None = True
            self.setEnabled(False)
            self.valueChanged.emit(-65535)  # Dummy value
        else:
            self.is_None = False
            self.setEnabled(True)
            super(QNoneDoubleSpinBox, self).setValue(v)

    def event(self, e):
        if type(e) == QContextMenuEvent:  # int and event.button() == QtCore.Qt.RightButton:
            e.accept()
            if self.is_None:
                self.setValue(super(QNoneDoubleSpinBox, self).value())
            else:
                self.setValue(None)
            return True
        else:
            return super(QNoneDoubleSpinBox, self).event(e)


class QListWidgetAddRemove(QListWidget):
    itemAddedOrRemoved = pyqtSignal()

    def addItem(self, *args, **kwargs):
        r = super(QListWidgetAddRemove, self).addItem(*args, **kwargs)
        self.itemAddedOrRemoved.emit()
        return r

    def addItems(self, *args, **kwargs):
        r = super(QListWidgetAddRemove, self).addItems(*args, **kwargs)
        self.itemAddedOrRemoved.emit()
        return r

    def removeItemAt(self, row, *args, **kwargs):
        r = super(QListWidgetAddRemove, self).takeItem(row)
        self.itemAddedOrRemoved.emit()
        return r

    def clear(self, *args, **kwargs):
        r = super(QListWidgetAddRemove, self).clear(*args, **kwargs)
        self.itemAddedOrRemoved.emit()
        return r


class QFileOpenLineEdit(QWidget):

    textChanged = pyqtSignal(object)
    icon = 'disk--arrow.png'

    def __init__(self, parent=None, description=tr("Select file"), filename_filter=tr("All Files") + " (*.*);;", **kwargs):
        super(QFileOpenLineEdit, self).__init__(parent, **kwargs)

        self._text = None

        self.description = description
        self.filename_filter = filename_filter

        self.lineedit = QLineEdit()
        self.button = QToolButton()
        self.button.setIcon(QIcon(os.path.join(utils.scriptdir, 'icons', self.icon)))

        layout = QHBoxLayout(self)
        layout.addWidget(self.lineedit)
        layout.addWidget(self.button, stretch=1)
        self.setLayout(layout)

        self.button.pressed.connect(self.onSelectPath)

        # Reciprocal setting of values; keep in sync
        self.textChanged.connect(self.lineedit.setText)
        self.lineedit.textChanged.connect(self.setText)

    def onSelectPath(self):

        filename, _ = QFileDialog.getOpenFileName(self, self.description, '', self.filename_filter)
        if filename:
            self.setText(filename)

    def text(self):
        return self._text

    def setText(self, text):
        self._text = text
        self.textChanged.emit(self._text)


class QFileSaveLineEdit(QFileOpenLineEdit):

    icon = 'disk--pencil.png'

    def __init__(self, parent=None, description=tr("Select save filename"), filename_filter=tr("All Files") + " (*.*);;", **kwargs):
        super(QFileSaveLineEdit, self).__init__(parent, description, filename_filter, **kwargs)

    def onSelectPath(self):
        filename, _ = QFileDialog.getSaveFileName(self.w, self.description, '', self.filename_filter)
        if filename:
            self.setText(filename)


class QFolderLineEdit(QFileOpenLineEdit):

    icon = 'folder-horizontal-open.png'

    def __init__(self, parent=None, description=tr("Select folder"), filename_filter="", **kwargs):
        super(QFolderLineEdit, self).__init__(parent, description, filename_filter, **kwargs)

    def onSelectPath(self):
        Qd = QFileDialog()
        Qd.setFileMode(QFileDialog.Directory)
        Qd.setOption(QFileDialog.ShowDirsOnly)

        folder = Qd.getExistingDirectory(self, self.description)
        if folder:
            self.setText(folder)
