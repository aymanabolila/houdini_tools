'''
This python script created to generate flipbook from houdini and convert the output to mp4 or mov video
no worries about color space, what you see in viewport will be ouptput.
Created by: Ayman Abolila: https://about.me/ayman.abolila
Created date: 18/11/2023
'''

import hou, json, os
from PySide2 import QtWidgets, QtCore, QtGui

def is_font_file(filename):
    return filename.lower().endswith(('.ttf', '.otf')) and os.path.isfile(filename)

input_path = hou.text.expandString('$HIP')+'/flipbook/'
if not os.path.exists(input_path):
    os.makedirs(input_path)
    
settings_file = hou.text.expandString('$HIP')+'/flipbook/settings.json'


if not os.path.exists(settings_file):
    with open(settings_file, 'w') as file:
        info = {
                    'video_format': 'mp4',
                    'start_frame': '`$RFSTART`',
                    'end_frame': '`$RFEND`',
                    'all_viewports': False,
                    'auto_backup': True,
                    'comment': True,
                    'font_size': 25,
                    'sys_font_path': 'C:\\Windows\\fonts\\arialbd.ttf',
                    'custom_font': False,
                    'comment_text': '[shotcam]\n`$F`/`$FEND`',
                    'width': 500,
                    'height': 350,
                }
        file.write(json.dumps(info, indent=4))


class CustomPanel(QtWidgets.QWidget):
    def __init__(self):
        super(CustomPanel, self).__init__()

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)


        with open(settings_file, 'r') as file:
            info = json.loads(file.read())

        self.setWindowTitle("AAB Flipbook Settings")
        self.setGeometry(100, 100, info['width'], info['height'])
        
        self.move(QtGui.QCursor.pos())
        
        # Create a main layout
        main_layout = QtWidgets.QVBoxLayout()

        # Create a layout for video format
        layout = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel("Select Format:")
        layout.addWidget(self.label)
        self.format_combobox = QtWidgets.QComboBox()
        self.format_combobox.addItems(['mp4', 'mov'])
        self.format_combobox.setCurrentIndex(0 if info['video_format'] == 'mp4' else 1)
        self.format_combobox.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        layout.addWidget(self.format_combobox)

        # Create a horizontal layout for String Input 1
        string_input1_layout = QtWidgets.QHBoxLayout()
        label1 = QtWidgets.QLabel("Frame Range:")
        self.string_input1 = QtWidgets.QLineEdit()
        self.string_input1.setPlaceholderText('`$RFSTART`')
        self.string_input1.setText(info['start_frame'])
        string_input1_layout.addWidget(label1)
        string_input1_layout.addWidget(self.string_input1)

        # Create a horizontal layout for String Input 2
        self.string_input2 = QtWidgets.QLineEdit()
        self.string_input2.setPlaceholderText('`$RFEND`')
        self.string_input2.setText(info['end_frame'])
        string_input1_layout.addWidget(self.string_input2)

        # Toggle 1
        self.toggle1 = QtWidgets.QCheckBox("All Viewports")
        self.toggle1.setChecked(info['all_viewports'])
        
        # Toggle 2
        self.toggle2 = QtWidgets.QCheckBox("Auto Backup")
        self.toggle2.setChecked(info['auto_backup'])

        # Toggle 3
        self.toggle3 = QtWidgets.QCheckBox("Comment and Shot Info")       
        self.toggle3.setChecked(info['comment'])
        self.toggle3.stateChanged.connect(self.on_toggle3_state_changed)
        

        # Create a horizontal layout for the Font Size Slider
        font_size_layout = QtWidgets.QHBoxLayout()
        self.font_size_label = QtWidgets.QLabel("Font Size:")
        self.font_size_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.font_size_slider.setMinimum(10)
        self.font_size_slider.setMaximum(70)
        self.font_size_slider.setValue(info['font_size'])
        self.font_size_slider.valueChanged.connect(self.update_font_size)
        self.value_indicator = QtWidgets.QLabel(str(self.font_size_slider.value()))

        self.font_size_label.setDisabled(not info['comment'])
        self.font_size_slider.setDisabled(not info['comment'])
        self.value_indicator.setDisabled(not info['comment'])

        font_size_layout.addWidget(self.font_size_label)
        font_size_layout.addWidget(self.value_indicator)
        font_size_layout.addWidget(self.font_size_slider)

        
        # Create a horizontal layout for String Input 3
        string_input3_layout = QtWidgets.QHBoxLayout()
        self.toggle4 = QtWidgets.QCheckBox()
        self.toggle4.setDisabled(not info['comment'])  # Initially disabled
        self.toggle4.setChecked(info['comment'])
        self.toggle4.setChecked(info['custom_font'])

        self.label3 = QtWidgets.QLabel("Custom Font Path:")
        self.label3.setDisabled(not info['comment'] or not info['custom_font'])

        self.string_input3 = QtWidgets.QLineEdit()
        self.string_input3.setPlaceholderText('C:\\Windows\\fonts\\arial.ttf')
        self.string_input3.setStyleSheet("color: green;" if is_font_file(info['sys_font_path']) else "color: red;")
        self.string_input3.setText(info['sys_font_path'])
        self.string_input3.setDisabled(not info['comment'] or not info['custom_font'])
        
        string_input3_layout.addWidget(self.toggle4)
        string_input3_layout.addWidget(self.label3)
        string_input3_layout.addWidget(self.string_input3)

        self.string_input3.textChanged.connect(self.check_font_availability)    
        self.toggle4.stateChanged.connect(self.on_toggle4_state_changed)
        
        # Multi-line Input
        self.multi_line_input = QtWidgets.QTextEdit()
        self.multi_line_input.setText(info['comment_text'])
        self.multi_line_input.setPlaceholderText("Scene Comment (You can place Houdini expressions here)")
        self.multi_line_input.setDisabled(not info['comment'])  # Initially disabled

        # Create a horizontal layout for the buttons
        button_layout = QtWidgets.QHBoxLayout()

        # OK Button
        self.ok_button = QtWidgets.QPushButton("OK")
        self.ok_button.clicked.connect(self.on_ok_clicked)

        # Cancel Button
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        
        # Revert Button
        self.revert_button = QtWidgets.QPushButton("Revert")
        self.revert_button.clicked.connect(self.revert)

        # Add the buttons to the button layout
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        # Add all layouts to the main layout
        main_layout.addLayout(layout)
        main_layout.addLayout(string_input1_layout)
        main_layout.addWidget(self.toggle1)
        main_layout.addWidget(self.toggle2)
        main_layout.addWidget(self.toggle3)
        main_layout.addLayout(font_size_layout)
        main_layout.addLayout(string_input3_layout)
        main_layout.addWidget(self.multi_line_input)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.revert_button)

        # Set the main layout for the widget
        self.setLayout(main_layout)


    def check_font_availability(self):
        if is_font_file(self.string_input3.text()):
            self.string_input3.setStyleSheet("color: green;")
        else:
            self.string_input3.setStyleSheet("color: red;")
    
    def on_toggle3_state_changed(self):
        if self.toggle3.isChecked():
        
            # Enable the multi-line input when Toggle 3 is checked
            self.multi_line_input.setDisabled(False)
            self.font_size_label.setDisabled(False)
            self.font_size_slider.setDisabled(False)
            self.value_indicator.setDisabled(False)
            self.toggle4.setDisabled(False)
            if self.toggle4.isChecked():
                self.label3.setDisabled(False)
                self.string_input3.setDisabled(False)

        else:
            # Disable the multi-line input when Toggle 3 is unchecked
            self.multi_line_input.setDisabled(True)
            self.font_size_label.setDisabled(True)
            self.font_size_slider.setDisabled(True)
            self.value_indicator.setDisabled(True)
            self.toggle4.setDisabled(True)
            self.label3.setDisabled(True)
            if self.toggle4.isChecked():
                self.label3.setDisabled(True)
                self.string_input3.setDisabled(True)


    def on_toggle4_state_changed(self):
        if self.toggle4.isChecked():
            self.string_input3.setDisabled(False)
            self.label3.setDisabled(False)
        else:
            self.string_input3.setDisabled(True)
            self.label3.setDisabled(True)

    def update_font_size(self):
        font_size = self.font_size_slider.value()
        # font = self.multi_line_input.font()
        # font.setPointSize(font_size)
        # self.multi_line_input.setFont(font)
        self.value_indicator.setText(str(font_size))

            
    def on_ok_clicked(self):
        video_format = self.format_combobox.currentText()
        input1 = self.string_input1.text()
        input2 = self.string_input2.text()
        toggle1_checked = self.toggle1.isChecked()
        toggle2_checked = self.toggle2.isChecked()
        toggle3_checked = self.toggle3.isChecked()
        toggle4_checked = self.toggle4.isChecked()
        font_size_value = self.font_size_slider.value()
        sys_font_path = self.string_input3.text()
        multi_line_text = self.multi_line_input.toPlainText()

        
        # Perform actions based on user inputs
        video_format = video_format 
        start_frame = input1
        end_frame = input2
        all_viewports = toggle1_checked
        auto_backup = toggle2_checked
        comment = toggle3_checked
        font_size = font_size_value
        comment_text = multi_line_text
        is_custom_font = toggle4_checked
        
        if not is_font_file(sys_font_path):
            hou.ui.displayMessage('Default font is selected as "{}" not found.'.format(sys_font_path))
        
        with open(settings_file, 'w') as file:
            info = {
                        'video_format': video_format,
                        'start_frame': start_frame,
                        'end_frame': end_frame,
                        'all_viewports': all_viewports,
                        'auto_backup': auto_backup,
                        'comment': comment,
                        'font_size': font_size,
                        'sys_font_path': sys_font_path,
                        'custom_font': is_custom_font,
                        'comment_text': comment_text,
                        'width': self.size().width(),
                        'height': self.size().height(),
                    }
            file.write(json.dumps(info, indent=4))


        # Close the panel
        self.close()

    def revert(self):
        self.format_combobox.setCurrentIndex(0)
        self.string_input1.setText('`$RFSTART`')
        self.string_input2.setText('`$RFEND`')
        self.toggle1.setChecked(False)
        self.toggle2.setChecked(True)
        self.toggle3.setChecked(True)
        self.font_size_slider.setValue(25)
        self.string_input3.setText('C:\\Windows\\fonts\\arialbd.ttf')
        self.multi_line_input.setText('[shotcam]\n`$F`/`$FEND`')
        
    def keyPressEvent(self, event):
        # Handle key events
        if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
            # Trigger "OK" action when Enter is pressed
            self.on_ok_clicked()
        elif event.key() == QtCore.Qt.Key_Escape:
            # Close the panel when Escape is pressed
            self.close()

panel = CustomPanel()
panel.show()


