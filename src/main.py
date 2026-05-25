import sys
import os

# Add src to sys.path to allow relative-looking imports when running main.py directly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from core.config import ConfigManager
from core.uploader import R2Uploader
from gui.main_window import MainWindow

def main():
    # Ensure we are in the right directory or handle paths correctly
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    config_manager = ConfigManager()
    uploader = R2Uploader(config_manager)
    
    window = MainWindow(config_manager, uploader)
    
    # Check if config is already valid, if so, maybe start minimized?
    # For the first run, we show the window.
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
