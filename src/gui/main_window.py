import sys
import os
import time
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout, 
                             QLineEdit, QPushButton, QMessageBox, QLabel, 
                             QSystemTrayIcon, QMenu, QStyle, QApplication, QComboBox)
from PySide6.QtGui import QIcon, QAction, QClipboard, QImage, QPixmap
from PySide6.QtCore import Qt, QBuffer, QIODevice, Signal, QObject, Slot, QMimeData, QTimer
from core.i18n import LanguageManager

def get_asset_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # In development, look relative to the src directory
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(base_path, "assets", relative_path)

class MainWindow(QMainWindow):
    def __init__(self, config_manager, uploader):
        super().__init__()
        self.config_manager = config_manager
        self.uploader = uploader
        self.i18n = LanguageManager(self.config_manager.get("language", "zh"))
        
        self.setFixedSize(450, 450)
        
        # Load app icon
        self.app_icon = QIcon(get_asset_path("picfofo.ico"))
        self.setWindowIcon(self.app_icon)
        
        self.init_ui()
        self.setup_tray()
        self.update_ui_text()
        
        # Clipboard monitoring
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.on_clipboard_change)
        self._last_uploaded_url = ""
        self._is_uploading = False
        self._last_upload_time = 0  # Cooldown timestamp

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        self.form_layout = QFormLayout()
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["简体中文", "English"])
        self.lang_combo.setCurrentIndex(0 if self.i18n.language == "zh" else 1)
        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)
        
        self.endpoint_input = QLineEdit()
        self.endpoint_input.setPlaceholderText("https://<accountid>.r2.cloudflarestorage.com")

        self.access_key_input = QLineEdit()
        self.secret_key_input = QLineEdit()
        self.secret_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.bucket_input = QLineEdit()
        
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("https://images.example.com")
        
        self.path_input = QLineEdit()

        self.layout.addLayout(self.form_layout)

        self.save_button = QPushButton()
        self.save_button.clicked.connect(self.save_config)
        self.layout.addWidget(self.save_button)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.status_label)

        # Load existing config values
        self.load_ui_from_config()

    def update_ui_text(self):
        self.setWindowTitle(self.i18n.get("title"))
        
        # Clear and rebuild form to update labels
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        self.form_layout.addRow(self.i18n.get("language"), self.lang_combo)
        self.form_layout.addRow(self.i18n.get("endpoint"), self.endpoint_input)
        self.form_layout.addRow(self.i18n.get("access_key"), self.access_key_input)
        self.form_layout.addRow(self.i18n.get("secret_key"), self.secret_key_input)
        self.form_layout.addRow(self.i18n.get("bucket"), self.bucket_input)
        self.form_layout.addRow(self.i18n.get("domain"), self.domain_input)
        self.form_layout.addRow(self.i18n.get("path"), self.path_input)
        
        self.save_button.setText(self.i18n.get("save"))
        self.status_label.setText(self.i18n.get("status_monitoring"))
        
        # Update tray menu if it exists
        if hasattr(self, 'tray_menu'):
            self.show_action.setText(self.i18n.get("tray_show"))
            self.quit_action.setText(self.i18n.get("tray_quit"))

    def load_ui_from_config(self):
        self.endpoint_input.setText(self.config_manager.get("endpoint_url"))
        self.access_key_input.setText(self.config_manager.get("access_key"))
        self.secret_key_input.setText(self.config_manager.get("secret_key"))
        self.bucket_input.setText(self.config_manager.get("bucket_name"))
        self.domain_input.setText(self.config_manager.get("custom_domain"))
        self.path_input.setText(self.config_manager.get("upload_path"))

    def on_language_changed(self, index):
        lang = "zh" if index == 0 else "en"
        self.i18n.set_language(lang)
        self.update_ui_text()

    def save_config(self):
        self.config_manager.set("language", "zh" if self.lang_combo.currentIndex() == 0 else "en")
        self.config_manager.set("endpoint_url", self.endpoint_input.text().strip())
        self.config_manager.set("access_key", self.access_key_input.text().strip())
        self.config_manager.set("secret_key", self.secret_key_input.text().strip())
        self.config_manager.set("bucket_name", self.bucket_input.text().strip())
        self.config_manager.set("custom_domain", self.domain_input.text().strip())
        self.config_manager.set("upload_path", self.path_input.text().strip())
        QMessageBox.information(self, self.i18n.get("msg_save_success"), self.i18n.get("msg_save_success"))

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.app_icon)
        
        self.tray_menu = QMenu()
        self.show_action = QAction(self.i18n.get("tray_show"), self)
        self.show_action.triggered.connect(self.showNormal)
        
        self.quit_action = QAction(self.i18n.get("tray_quit"), self)
        self.quit_action.triggered.connect(sys.exit)
        
        self.tray_menu.addAction(self.show_action)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.quit_action)
        
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.showNormal()

    def closeEvent(self, event):
        if self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.showMessage(
                self.i18n.get("tray_minimized_title"),
                self.i18n.get("tray_minimized_msg"),
                QSystemTrayIcon.Information,
                2000
            )
            event.ignore()

    def on_clipboard_change(self):
        # 1. Check if we are currently uploading
        if self._is_uploading:
            return
            
        # 2. Cooldown check: ignore signals within 2 seconds of the last successful upload trigger
        if time.time() - self._last_upload_time < 2.0:
            return

        mime_data = self.clipboard.mimeData()
        
        if mime_data.hasText():
            text = mime_data.text()
            if text.startswith("![image]") and text == self._last_uploaded_url:
                return

        if mime_data.hasImage():
            image = self.clipboard.image()
            if not image.isNull():
                self._last_upload_time = time.time() # Update trigger time
                self.process_upload(image)

    def process_upload(self, qimage):
        if not self.config_manager.is_valid():
            self.status_label.setText(self.i18n.get("status_error_config"))
            return

        self._is_uploading = True
        self.status_label.setText(self.i18n.get("status_uploading"))
        
        # Ensure we have a clean buffer
        byte_array = QBuffer()
        byte_array.open(QIODevice.OpenModeFlag.WriteOnly)
        if not qimage.save(byte_array, "PNG"):
            self.status_label.setText("Error: Failed to save image to buffer")
            self._is_uploading = False
            return
            
        image_bytes = byte_array.data().data()
        
        try:
            # 1. Upload to R2
            url = self.uploader.upload_image(image_bytes, "png")
            
            # 2. Generate Markdown link
            template = self.config_manager.get("markdown_template", "![image]({url})")
            markdown_link = template.format(url=url)
            
            # 3. Update Clipboard with a small delay
            # Windows screenshot tool often locks or overrides the clipboard immediately after capture.
            # Using QTimer.singleShot(100, ...) ensures our overwrite happens AFTER the system settles.
            self._last_uploaded_url = markdown_link
            QTimer.singleShot(100, lambda: self.set_clipboard_text(markdown_link))
            
            # Debug check
            print(f"Successfully uploaded: {url}")
            
            self.status_label.setText(self.i18n.get("status_success"))
            self.tray_icon.showMessage(
                self.i18n.get("tray_minimized_title"), 
                self.i18n.get("tray_success_msg"), 
                QSystemTrayIcon.Information, 
                2000
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            error_msg = self.i18n.get("status_error_upload", error=str(e))
            self.status_label.setText(error_msg)
            QMessageBox.warning(self, self.i18n.get("msg_upload_failed"), str(e))
        finally:
            self._is_uploading = False

    def set_clipboard_text(self, text):
        mime_data = QMimeData()
        mime_data.setText(text)
        self.clipboard.setMimeData(mime_data)
        print(f"Clipboard confirmed update with: {text}")
