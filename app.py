import os
import sys
from PyQt5.QtWidgets import QApplication, QStyleFactory
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt, QSettings

from ui.main_window import MainWindow
from ui.styles import apply_dark_theme
from utils.constants import APP_NAME, APP_VERSION, ORGANIZATION_NAME


class CosmicAnalyzerApp(QApplication):
    """Main application class that initializes the PyQt5 application."""
    
    def __init__(self, argv):
        super().__init__(argv)
        
        # Set application metadata
        self.setApplicationName(APP_NAME)
        self.setApplicationVersion(APP_VERSION)
        self.setOrganizationName(ORGANIZATION_NAME)
        
        # Apply dark theme
        apply_dark_theme(self)
        
        # Load settings
        self.settings = QSettings()
        
        # Create and show main window
        self.main_window = MainWindow(self.settings)
        self.main_window.show()
        
        # Try to load last opened file if exists, or default to nowe_obiekty.json
        last_file = self.settings.value("last_opened_file", "")
        
        # Zawsze ładuj domyślny plik przy starcie
        default_file = os.path.join("attached_assets", "nowe_obiekty.json")
        
        if os.path.exists(default_file):
            print(f"Ładowanie domyślnego pliku danych: {default_file}")
            self.main_window.load_data_file(default_file)
        elif last_file and os.path.exists(last_file):
            print(f"Ładowanie ostatnio używanego pliku: {last_file}")
            self.main_window.load_data_file(last_file)
        else:
            print("Nie znaleziono pliku danych do załadowania")
