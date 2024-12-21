from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QSpinBox, QComboBox,
                             QPushButton, QFileDialog, QCheckBox, QWidget)


class ConfigDialog(QDialog):
    def __init__(self, current_path=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thumb Crafter Settings")
        self.setModal(False)  # 非モーダルに設定
        self.setup_ui()

        # 現在の監視対象ディレクトリを設定
        if current_path:
            self.dir_edit.setText(current_path)

    def setup_ui(self):
        self.layout = QVBoxLayout()

        # Target Directory
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Target Directory:"))
        self.dir_edit = QLineEdit()
        dir_layout.addWidget(self.dir_edit)
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(self.browse_btn)
        self.layout.addLayout(dir_layout)

        # Exclude Subdirectories
        self.exclude_check = QCheckBox("Ignore Subfolders")
        self.layout.addWidget(self.exclude_check)

        # Protocol Selection
        protocol_layout = QHBoxLayout()
        protocol_layout.addWidget(QLabel("Protocol:"))
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(['none', 'udp', 'tcp'])
        protocol_layout.addWidget(self.protocol_combo)
        self.layout.addLayout(protocol_layout)

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
        self.layout.addLayout(network_layout)

        # Thumbnail Second
        self.thumbnail_widget = QWidget()
        second_layout = QHBoxLayout(self.thumbnail_widget)
        second_layout.addWidget(QLabel("動画の何秒目をサムネにする (秒):"))
        self.second_spin = QSpinBox()
        self.second_spin.setRange(0, 3600)
        self.second_spin.setValue(1)
        second_layout.addWidget(self.second_spin)
        self.layout.addWidget(self.thumbnail_widget)
        self.thumbnail_widget.setVisible(False)  # 非表示に設定

        # send_interval
        self.delay_widget = QWidget()
        delay_layout = QHBoxLayout(self.delay_widget)
        delay_layout.addWidget(QLabel("UDP送信の間隔 (秒):"))
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(1, 10)
        self.delay_spin.setValue(1)
        delay_layout.addWidget(self.delay_spin)
        self.layout.addWidget(self.delay_widget)
        self.delay_widget.setVisible(False)  # 非表示に設定

        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        self.layout.addLayout(button_layout)

        self.setLayout(self.layout)

        # プロトコル変更時のイベント
        self.protocol_combo.currentTextChanged.connect(
            self.toggle_ip_port_fields)
        self.toggle_ip_port_fields(self.protocol_combo.currentText())

    def reject(self):  # デフォルトのreject処理がメインイベントループを終了している可能性があるため、rejectメソッドをオーバーライド
        print("Dialog rejected")  # デバッグ出力
        super().reject()          # 親クラスのreject()を呼び出してダイアログを閉じる

    def toggle_ip_port_fields(self, protocol):
        """プロトコルがNoneの場合、IPとPortを無効または非表示にする"""
        is_enabled = protocol.lower() in ("udp", "tcp")
        self.ip_edit.setEnabled(is_enabled)
        self.port_spin.setEnabled(is_enabled)

    def get_config(self):
        return {
            "protocol": self.protocol_combo.currentText(),
            "ip": self.ip_edit.text(),
            "port": self.port_spin.text()
        }

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
            'send_interval': self.delay_spin.value()
        }
