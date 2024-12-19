from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QSpinBox, QComboBox,
                             QPushButton, QFileDialog, QCheckBox)


class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thumb Crafter Settings")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Target Directory
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Target Directory:"))
        self.dir_edit = QLineEdit()
        dir_layout.addWidget(self.dir_edit)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(browse_btn)
        layout.addLayout(dir_layout)

        # Exclude Subdirectories
        self.exclude_check = QCheckBox("Exclude Subdirectories")
        layout.addWidget(self.exclude_check)

        # Protocol Selection
        protocol_layout = QHBoxLayout()
        protocol_layout.addWidget(QLabel("Protocol:"))
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(['none', 'udp', 'tcp'])
        protocol_layout.addWidget(self.protocol_combo)
        layout.addLayout(protocol_layout)

        # IP and Port
        network_layout = QHBoxLayout()
        network_layout.addWidget(QLabel("IP:"))
        self.ip_edit = QLineEdit("localhost")
        network_layout.addWidget(self.ip_edit)
        network_layout.addWidget(QLabel("Port:"))
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(12345)
        network_layout.addWidget(self.port_spin)
        layout.addLayout(network_layout)

        # Thumbnail Second
        second_layout = QHBoxLayout()
        second_layout.addWidget(QLabel("Thumbnail Second:"))
        self.second_spin = QSpinBox()
        self.second_spin.setRange(0, 3600)
        self.second_spin.setValue(1)
        second_layout.addWidget(self.second_spin)
        layout.addLayout(second_layout)

        # Delay
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("Delay (seconds):"))
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(1, 10)
        self.delay_spin.setValue(1)
        delay_layout.addWidget(self.delay_spin)
        layout.addLayout(delay_layout)

        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.dir_edit.setText(directory)

    def get_config(self):
        return {
            'target': self.dir_edit.text(),
            'exclude_subdirectories': self.exclude_check.isChecked(),
            'protocol': self.protocol_combo.currentText(),
            'ip': self.ip_edit.text(),
            'port': self.port_spin.value(),
            'seconds': self.second_spin.value(),
            'delay': self.delay_spin.value()
        }
