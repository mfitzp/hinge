# Generic configuration dialog handling class
class GenericDialog(QDialog):
    '''
    A generic dialog wrapper that handles most common dialog setup/shutdown functions.
    
    Support for config, etc. to be added for auto-handling widgets and config load/save. 
    '''

    def __init__(self, parent, buttons=['ok', 'cancel'], **kwargs):
        super(GenericDialog, self).__init__(parent, **kwargs)

        self.sizer = QVBoxLayout()
        self.layout = QVBoxLayout()

        QButtons = {
            'ok': QDialogButtonBox.Ok,
            'cancel': QDialogButtonBox.Cancel,
        }
        Qbtn = 0
        for k in buttons:
            Qbtn = Qbtn | QButtons[k]

        # Setup default button configurations etc.
        self.buttonBox = QDialogButtonBox(Qbtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def dialogFinalise(self):
        self.sizer.addLayout(self.layout)
        self.sizer.addWidget(self.buttonBox)

        # Set dialog layout
        self.setLayout(self.sizer)

    def setListControl(self, control, list, checked):
        # Automatically set List control checked based on current options list
        items = control.GetItems()
        try:
            idxs = [items.index(e) for e in list]
            for idx in idxs:
                if checked:
                    control.Select(idx)
                else:
                    control.Deselect(idx)
        except:
            pass





class ExportImageDialog(GenericDialog):
    """
    Standard dialog to handle image export fromm any view.

    Dialog box presenting a set of options for image export, including dimensions and
    resolution. Resolution is handled as dpm (dots per metre) in keeping with
    internal Qt usage, but convertor functions are available.

    :param parent: Parent window to attach dialog to
    :type QObject: object inherited from QObject
    :param size: Default dimensions for export
    :type size: QSize
    :param dpm: Default dots per metre
    :type dpm: int
    :param show_rerender_options: Show options to re-render/scale output
    :type show_rerender_options: bool

    """
    print_u = {  # Qt uses pixels/meter as it's default resolution so measure relative to meters
        'in': 39.3701,
        'mm': 1000,
        'cm': 100,
        'm': 1,
        }

    print_p = {  # Spinbox parameters dp, increment
        'in': (3, 1, 0.01, 1000),
        'mm': (2, 1, 0.1, 100000),
        'cm': (3, 1, 0.01, 10000),
        'm': (5, 1, 0.0001, 100),
    }

    resolution_u = {  # Qt uses pixels/meter as it's default resolution so scale to that
                    'dpi': 39.3701,
                    'px/mm': 1000,
                    'px/cm': 100,
                    'px/m': 1,
                    }

    convert_res_to_unit = {'dpi': 'in', 'px/mm': 'mm', 'px/cm': 'cm', 'px/m': 'm'}

    def __init__(self, parent, size=QSize(800, 600), dpm=11811, show_rerender_options=False, **kwargs):
        super(ExportImageDialog, self).__init__(parent, **kwargs)

        self.setWindowTitle(tr("Export Image"))

        # Handle measurements internally as pixels, convert to/from
        self._w = size.width()
        self._h = size.height()
        self.default_print_units = 'cm'
        self.default_resolution_units = 'dpi'

        self._updating = False

        r = 0
        w = QGridLayout()

        w.addWidget(QLabel('<b>Image Size</b>'), r, 0)
        r += 1

        self.width = QSpinBox()
        self.width.setRange(1, 100000)
        w.addWidget(QLabel('Width'), r, 0)
        w.addWidget(self.width, r, 1)
        r += 1

        self.height = QSpinBox()
        self.height.setRange(1, 100000)
        w.addWidget(QLabel('Height'), r, 0)
        w.addWidget(self.height, r, 1)
        r += 1
        w.addItem(QSpacerItem(1, 10), r, 0)
        r += 1

        w.addWidget(QLabel('<b>Print Size</b>'), r, 0)
        r += 1

        self.width_p = QDoubleSpinBox()
        self.width_p.setRange(0.0001, 10000)
        w.addWidget(QLabel('Width'), r, 0)
        w.addWidget(self.width_p, r, 1)
        r += 1

        self.height_p = QDoubleSpinBox()
        self.height_p.setRange(0.0001, 10000)
        w.addWidget(QLabel('Height'), r, 0)
        w.addWidget(self.height_p, r, 1)

        self.print_units = QComboBox()
        self.print_units.addItems(list(self.print_u.keys()))
        self.print_units.setCurrentIndex(self.print_units.findText(self.default_print_units))

        w.addWidget(self.print_units, r, 2)
        r += 1

        self.resolution = QDoubleSpinBox()
        self.resolution.setRange(1, 1000000)
        self.resolution.setValue(300)
        self.resolution.setDecimals(2)

        self.resolution_units = QComboBox()
        self.resolution_units.addItems(list(self.resolution_u.keys()))
        self.resolution_units.setCurrentIndex(self.resolution_units.findText(self.default_resolution_units))

        w.addWidget(QLabel('Resolution'), r, 0)
        w.addWidget(self.resolution, r, 1)
        w.addWidget(self.resolution_units, r, 2)
        r += 1
        w.addItem(QSpacerItem(1, 10), r, 0)
        r += 1

        if show_rerender_options:
            w.addWidget(QLabel('<b>Scaling</b>'), r, 0)
            r += 1
            self.scaling = QComboBox()
            self.scaling.addItems(['Resample', 'Resize'])
            self.scaling.setCurrentIndex(self.scaling.findText('Resample'))
            w.addWidget(QLabel('Scaling method'), r, 0)
            w.addWidget(self.scaling, r, 1)
            r += 1
            w.addItem(QSpacerItem(1, 20), r, 0)
        else:
            self.scaling = False

        # Set values
        self.width.setValue(self._w)
        self.height.setValue(self._h)
        self.update_print_dimensions()

        # Set event handlers (here so not triggered while setting up)
        self.width.valueChanged.connect(self.changed_image_dimensions)
        self.height.valueChanged.connect(self.changed_image_dimensions)
        self.width_p.valueChanged.connect(self.changed_print_dimensions)
        self.height_p.valueChanged.connect(self.changed_print_dimensions)
        self.resolution_units.currentIndexChanged.connect(self.changed_resolution_units)
        self.resolution.valueChanged.connect(self.changed_print_resolution)
        self.print_units.currentIndexChanged.connect(self.changed_print_units)

        self.layout.addLayout(w)

        self.setMinimumSize(QSize(300, 150))
        self.layout.setSizeConstraint(QLayout.SetMinimumSize)

        self._current_dimension = self.print_units.currentText()
        self._current_resolution = self.resolution.value()
        self._current_resolution_units = self.resolution_units.currentText()

        # Build dialog layout
        self.dialogFinalise()

    def changed_image_dimensions(self):
        if not self._updating:
            self._updating = True
            self.update_print_dimensions()
        self._updating = False

        # Keep internal data synced
        self._w = self.width.value()
        self._h = self.height.value()

    def changed_print_dimensions(self):
        if not self._updating:
            self._updating = True
            self.update_image_dimensions()
        self._updating = False

    def changed_print_resolution(self):
        w_p = self.width_p.value()
        h_p = self.height_p.value()

        new_resolution = self.resolution.value()
        self.width_p.setValue((w_p / self._current_resolution) * new_resolution)
        self.height_p.setValue((h_p / self._current_resolution) * new_resolution)
        self._current_resolution = self.resolution.value()

    def changed_print_units(self):
        dimension_t = self.print_units.currentText()
        for o in [self.height_p, self.width_p]:
            o.setDecimals(self.print_p[dimension_t][0])
            o.setSingleStep(self.print_p[dimension_t][1])
            o.setRange(self.print_p[dimension_t][2], self.print_p[dimension_t][3])

        if dimension_t != self._current_dimension:
            # We've had a change, so convert
            self.width_p.setValue(self.get_converted_measurement(self.width_p.value(), self._current_dimension, dimension_t))
            self.height_p.setValue(self.get_converted_measurement(self.height_p.value(), self._current_dimension, dimension_t))

        self._current_dimension = dimension_t

    def changed_resolution_units(self):
        ru = self.resolution_units.currentText()
        self.resolution.setValue(self.resolution.value() * self.resolution_u[self._current_resolution_units] / float(self.resolution_u[ru]))
        self._current_resolution_units = ru

    # Update print dimensions using the image dimensions and resolutions
    def update_print_dimensions(self):
        self._w = self.width.value()
        self._h = self.height.value()

        print_units = self.print_units.currentText()
        w_p = self.get_as_print_size(self._w, print_units)
        h_p = self.get_as_print_size(self._h, print_units)

        self.width_p.setValue(w_p)
        self.height_p.setValue(h_p)

    def get_as_print_size(self, s, u):
        ps = self.resolution.value()
        ps_u = self.resolution_units.currentText()
        s = s / (ps * self.resolution_u[ps_u])  # Get size in metres
        return self.get_converted_measurement(s, 'm', u)  # Return converted value

    def get_print_size(self, u):
        return (
            self.get_as_print_size(self._w, u),
            self.get_as_print_size(self._h, u)
            )

    # Update image dimensions using the print dimensions and resolutions
    def update_image_dimensions(self):
        w_p = self.width_p.value()
        h_p = self.height_p.value()

        print_units = self.print_units.currentText()
        resolution = self.resolution.value()
        resolution_units = self.resolution_units.currentText()

        self._w = self.get_pixel_size(w_p, print_units, resolution, resolution_units)
        self._h = self.get_pixel_size(h_p, print_units, resolution, resolution_units)

        self.width.setValue(self._w)
        self.height.setValue(self._h)

    def get_pixel_size(self, s, pu, r, ru):
        s = s / self.print_u[pu]  # Convert to metres
        rm = r * self.resolution_u[ru]  # Dots per metre
        return s * rm

    def get_converted_measurement(self, x, f, t):
        # Convert measurement from f to t
        f = self.print_u[f]
        t = self.print_u[t]
        return (float(x) / float(f)) * t

    def get_pixel_dimensions(self):
        return QSize(self._w, self._h)

    def get_dots_per_meter(self):
        return self.resolution.value() * self.resolution_u[self.resolution_units.currentText()]

    def get_dots_per_inch(self):
        if self.resolution_units.currentText() == 'in':
            return self.resolution.value()
        else:
            return self.get_converted_measurement(self.resolution.value(), self.convert_res_to_unit[self.resolution_units.currentText()], 'in')

    def get_resample(self):
        if self.scaling:
            return self.scaling.currentText() == 'Resample'
        else:
            return False
            
                        
