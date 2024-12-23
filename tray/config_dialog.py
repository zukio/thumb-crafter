from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QSpinBox, QComboBox,
                             QPushButton, QFileDialog, QCheckBox, QWidget, QSizePolicy)


class ConfigDialog(QDialog):
    def __init__(self, config=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thumb Crafter Settings")
        self.setModal(False)  # 非モーダルに設定
        self.setup_ui()

        # 現在の監視対象ディレクトリを設定
        if config:
            # 設定を反映
            self.load_config(config)

    def load_config(self, config):
        """JSON設定をUIに反映"""
        self.dir_edit.setText(config.get('target', ''))
        self.exclude_check.setChecked(config.get('ignore_subfolders', False))
        self.protocol_combo.setCurrentText(config.get('protocol', 'none'))
        self.ip_edit.setText(config.get('ip', 'localhost'))
        self.port_spin.setValue(config.get('port', 12345))
        self.second_spin.setValue(config.get('thumbnail_time_seconds', 1))
        self.delay_spin.setValue(config.get('send_interval', 1))
        self.ppt_combo.setCurrentText(config.get('convert_slide', 'none'))
        self.pdf_combo.setCurrentText(config.get('convert_document', 'none'))
        self.page_duration_spin.setValue(config.get('page_duration', 5))

    def setup_ui(self):
        self.layout = QVBoxLayout()

        # Target Directory
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Target Dir:"))
        self.dir_edit = QLineEdit()
        dir_layout.addWidget(self.dir_edit)
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(self.browse_btn)
        self.layout.addLayout(dir_layout)

        # Exclude Subdirectories
        self.exclude_check = QCheckBox("Ignore Subfolders")
        self.layout.addWidget(self.exclude_check)

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        spacer.setMinimumHeight(20)  # 高さを設定
        self.layout.addWidget(spacer)

        # Conversion Options (PowerPoint and PDF)
        conversion_layout = QHBoxLayout()

        self.video_combo = QComboBox()
        self.video_combo.addItems(['thumbnail'])
        self.video_combo.setEnabled(False)
        conversion_layout.addWidget(QLabel("Video:"))
        conversion_layout.addWidget(self.video_combo)

        self.ppt_combo = QComboBox()
        self.ppt_combo.addItems(['none', 'video', 'sequence'])
        conversion_layout.addWidget(QLabel("PPT:"))
        conversion_layout.addWidget(self.ppt_combo)

        self.pdf_combo = QComboBox()
        self.pdf_combo.addItems(['none', 'video', 'sequence'])
        conversion_layout.addWidget(QLabel("PDF:"))
        conversion_layout.addWidget(self.pdf_combo)

        self.layout.addLayout(conversion_layout)

        # Separator Line
        separator = QWidget()
        separator.setFixedHeight(2)
        separator.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        separator.setStyleSheet("background-color: #c0c0c0;")
        self.layout.addWidget(separator)

        # Protocol Selection
        protocol_layout = QHBoxLayout()
        protocol_layout.addWidget(QLabel("Notify:"))
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(['none', 'udp'])
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

        # Thumbnail Time (Second)
        self.thumbnail_widget = QWidget()
        second_layout = QHBoxLayout(self.thumbnail_widget)
        second_layout.addWidget(QLabel("動画の何秒目をサムネにする (秒):"))
        self.second_spin = QSpinBox()
        self.second_spin.setRange(0, 3600)
        self.second_spin.setValue(1)
        second_layout.addWidget(self.second_spin)
        self.layout.addWidget(self.thumbnail_widget)
        self.thumbnail_widget.setVisible(False)  # 非表示に設定

        # Page Duration (Second)
        self.page_widget = QWidget()
        page_duration_layout = QHBoxLayout(self.page_widget)
        page_duration_layout.addWidget(QLabel("PDFのページ表示時間 (秒):"))
        self.page_duration_spin = QSpinBox()
        self.page_duration_spin.setRange(1, 60)
        self.page_duration_spin.setValue(5)
        page_duration_layout.addWidget(self.page_duration_spin)
        self.layout.addWidget(self.page_widget)
        self.page_widget.setVisible(False)  # 非表示に設定

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

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        spacer.setMinimumHeight(30)  # 高さを設定
        self.layout.addWidget(spacer)

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

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.dir_edit.setText(directory)

    def get_config(self):
        return {
            'target': self.dir_edit.text(),
            'ignore_subfolders': self.exclude_check.isChecked(),
            'protocol': self.protocol_combo.currentText(),
            'ip': self.ip_edit.text(),
            'port': self.port_spin.value(),
            'thumbnail_time_seconds': self.second_spin.value(),
            'send_interval': self.delay_spin.value(),
            'convert_slide': self.ppt_combo.currentText(),
            'convert_document': self.pdf_combo.currentText(),
            'page_duration': self.page_duration_spin.value()
        }
