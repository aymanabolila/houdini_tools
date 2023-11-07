'''
This python script created to generate flipbook from houdini and convert the output to mp4 video
no worries about color space, what you see in viewport will be ouptut.
Created by: Ayman Abolila: https://about.me/ayman.abolila
Created date: 11/7/2023
'''


import hou, json, os
from PySide2 import QtWidgets, QtCore


input_path = hou.text.expandString('$HIP')+'/flipbook/'
if not os.path.exists(input_path):
    os.makedirs(input_path)
    
settings_file = hou.text.expandString('$HIP')+'/flipbook/settings.txt'

if not os.path.exists(settings_file):
    with open(settings_file, 'w') as file:
        info = {
            'start_frame': '$RFSTART',
            'end_frame': '$RFEND',
            'all_viewports': False,
            'auto_backup': True,
            'comment': True,
            'comment_text': 'Frame: `$F`',      
                   }
        file.write(json.dumps(info, indent=4))

with open(settings_file, 'r') as file:
    info = json.loads(file.read())


class CustomPanel(QtWidgets.QWidget):
    def __init__(self):
        super(CustomPanel, self).__init__()

        self.setWindowTitle("Flipbook Default Options")
        self.setGeometry(100, 100, 400, 400)

        # Create a main layout
        main_layout = QtWidgets.QVBoxLayout()

        # Create a horizontal layout for String Input 1
        string_input1_layout = QtWidgets.QHBoxLayout()
        label1 = QtWidgets.QLabel("Start Frame:")
        self.string_input1 = QtWidgets.QLineEdit()
        self.string_input1.setPlaceholderText('$RFSTART')
        self.string_input1.setText(info['start_frame'])
        string_input1_layout.addWidget(label1)
        string_input1_layout.addWidget(self.string_input1)

        # Create a horizontal layout for String Input 2
        string_input2_layout = QtWidgets.QHBoxLayout()
        label2 = QtWidgets.QLabel("End Frame:")
        self.string_input2 = QtWidgets.QLineEdit()
        self.string_input2.setPlaceholderText('$RFEND')
        self.string_input2.setText(info['end_frame'])
        string_input2_layout.addWidget(label2)
        string_input2_layout.addWidget(self.string_input2)

        # Toggle 1
        self.toggle1 = QtWidgets.QCheckBox("All Viewports")
        self.toggle1.setChecked(info['all_viewports'])
        self.toggle1.setToolTip('This allows you to caputre entire viewport, when disabled, only camera view will be renderd.')

        
        # Toggle 2
        self.toggle2 = QtWidgets.QCheckBox("Auto Backup")
        self.toggle2.setChecked(info['auto_backup'])
        self.toggle2.setToolTip('This allows you to make a backup hip file with same name as recent flipbook name, location -> $HIP/flipbook/bk .')


        # Toggle 3
        self.toggle3 = QtWidgets.QCheckBox("Comment and Shot Info")       
        self.toggle3.setChecked(info['comment'])
        self.toggle3.setToolTip('You can write HScript here like `ch("/obj/geo1/tx")` also you can place camera name that you looking from.')

        
        # Multi-line Input
        self.multi_line_input = QtWidgets.QTextEdit()
        self.multi_line_input.setText(info['comment_text'])
        self.multi_line_input.setPlaceholderText("Scene Comment (You can place Houdini expressions here)")
        self.multi_line_input.setDisabled(not info['comment'])  # Initially disabled

        # Create a horizontal layout for the buttons        # Create a horizontal layout for the buttons
        button_layout = QtWidgets.QHBoxLayout()

        # OK Button
        self.ok_button = QtWidgets.QPushButton("OK")
        self.ok_button.clicked.connect(self.on_ok_clicked)

        # Cancel Button
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)

        # Add the buttons to the button layout
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        # Add all layouts to the main layout
        main_layout.addLayout(string_input1_layout)
        main_layout.addLayout(string_input2_layout)
        main_layout.addWidget(self.toggle1)
        main_layout.addWidget(self.toggle2)
        main_layout.addWidget(self.toggle3)
        main_layout.addWidget(self.multi_line_input)
        main_layout.addLayout(button_layout)

        # Set the main layout for the widget
        self.setLayout(main_layout)

        # Connect the toggle state change to the function
        self.toggle3.stateChanged.connect(self.on_toggle3_state_changed)

    def on_toggle3_state_changed(self):
        if self.toggle3.isChecked():
            # Enable the multi-line input when Toggle 3 is checked
            self.multi_line_input.setDisabled(False)
        else:
            # Disable the multi-line input when Toggle 3 is unchecked
            self.multi_line_input.setDisabled(True)

    def on_ok_clicked(self):
        input1 = self.string_input1.text()
        input2 = self.string_input2.text()
        toggle1_checked = self.toggle1.isChecked()
        toggle2_checked = self.toggle2.isChecked()
        toggle3_checked = self.toggle3.isChecked()
        multi_line_text = self.multi_line_input.toPlainText()

        # Perform actions based on user inputs
        # For example, print the values to the console
        
        start_frame = input1
        end_frame = input2
        all_viewports = toggle1_checked
        auto_backup = toggle2_checked
        comment = toggle3_checked
        comment_text = multi_line_text

        
        with open(settings_file, 'w') as file:
            info = {
                'start_frame': start_frame,
                'end_frame': end_frame,
                'all_viewports': all_viewports,
                'auto_backup': auto_backup,
                'comment': comment,
                'comment_text': comment_text,      
               }
            file.write(json.dumps(info, indent=4))


        # Close the panel
        self.close()

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
