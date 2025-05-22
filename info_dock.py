from PyQt5.QtWidgets import (QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QTextEdit, QPushButton, QGridLayout,
                           QGroupBox, QScrollArea, QStackedWidget, QTextBrowser,
                           QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QTextCharFormat, QTextCursor


class InfoDockWidget(QDockWidget):
    """
    Dock widget to display detailed information about a selected object,
    including metadata and user comments.
    """
    
    def __init__(self):
        super().__init__("Szczegółowa Analiza Naukowa")
        
        self.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetFloatable)
        self.setMinimumWidth(500)  # Zwiększona szerokość dla lepszej czytelności
        self.setMinimumHeight(600)  # Dodana minimalna wysokość
        
        self.setup_ui()
        self.current_object = None
    
    def setup_ui(self):
        """Setup the UI components."""
        # Create main widget
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        
        # Dodajemy dwa typy widoków - podstawowy oraz rozszerzony HTML
        self.stacked_view = QStackedWidget()
        layout.addWidget(self.stacked_view)
        
        # 1. Podstawowy widok z polami tekstowymi
        basic_view = QWidget()
        basic_layout = QVBoxLayout(basic_view)
        
        # Create scroll area for content
        basic_scroll = QScrollArea()
        basic_scroll.setWidgetResizable(True)
        basic_scroll.setFrameShape(QScrollArea.NoFrame)
        
        # Create scrollable content widget
        basic_content = QWidget()
        basic_scroll.setWidget(basic_content)
        basic_content_layout = QVBoxLayout(basic_content)
        
        # Create title label
        self.title_label = QLabel("")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setWordWrap(True)
        basic_content_layout.addWidget(self.title_label)
        
        # Create basic info group
        basic_group = QGroupBox("Informacje podstawowe")
        basic_info_layout = QGridLayout(basic_group)
        
        # ID and Scale
        basic_info_layout.addWidget(QLabel("ID:"), 0, 0)
        self.id_label = QLabel("")
        basic_info_layout.addWidget(self.id_label, 0, 1)
        
        basic_info_layout.addWidget(QLabel("Skala:"), 1, 0)
        self.scale_label = QLabel("")
        basic_info_layout.addWidget(self.scale_label, 1, 1)
        
        basic_content_layout.addWidget(basic_group)
        
        # Create data group
        self.data_group = QGroupBox("Dane")
        self.data_layout = QGridLayout(self.data_group)
        basic_content_layout.addWidget(self.data_group)
        
        # Create comments group
        comments_group = QGroupBox("Komentarze i interpretacja")
        comments_layout = QVBoxLayout(comments_group)
        
        self.comments_edit = QTextEdit()
        self.comments_edit.setPlaceholderText("Dodaj swoje komentarze...")
        comments_layout.addWidget(self.comments_edit)
        
        basic_content_layout.addWidget(comments_group)
        
        # Add controls
        controls_layout = QHBoxLayout()
        
        # Przycisk do przełączania na widok HTML
        show_analysis_btn = QPushButton("Pokaż szczegółową analizę")
        show_analysis_btn.clicked.connect(lambda: self.stacked_view.setCurrentIndex(1))
        controls_layout.addWidget(show_analysis_btn)
        
        # Przycisk zamknięcia
        close_button = QPushButton("Zamknij")
        close_button.clicked.connect(self.hide)
        controls_layout.addWidget(close_button)
        
        basic_content_layout.addLayout(controls_layout)
        
        # Add scroll area to basic view
        basic_layout.addWidget(basic_scroll)
        
        # 2. Rozszerzony widok HTML dla szczegółowej analizy naukowej
        html_view = QWidget()
        html_layout = QVBoxLayout(html_view)
        
        # Dodajemy przeglądarkę HTML
        self.html_browser = QTextBrowser()
        self.html_browser.setOpenExternalLinks(True)
        self.html_browser.setStyleSheet("background-color: white; color: black;")
        html_layout.addWidget(self.html_browser)
        
        # Przyciski kontrolne dla widoku HTML
        html_controls = QHBoxLayout()
        
        # Przycisk do przełączania na widok podstawowy
        back_btn = QPushButton("Wróć do widoku podstawowego")
        back_btn.clicked.connect(lambda: self.stacked_view.setCurrentIndex(0))
        html_controls.addWidget(back_btn)
        
        # Przycisk do drukowania/eksportu analizy
        export_btn = QPushButton("Eksportuj analizę")
        export_btn.clicked.connect(self.export_analysis)
        html_controls.addWidget(export_btn)
        
        html_layout.addLayout(html_controls)
        
        # Dodajemy oba widoki do przełącznika
        self.stacked_view.addWidget(basic_view)
        self.stacked_view.addWidget(html_view)
        
        # Set the main widget
        self.setWidget(main_widget)
    
    def set_html_content(self, html_content):
        """Ustaw zawartość widoku HTML z analizą naukową."""
        self.html_browser.setHtml(html_content)
        self.stacked_view.setCurrentIndex(1)  # Przełącz na widok HTML
    
    def export_analysis(self):
        """Eksportuj analizę naukową do pliku."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Eksportuj analizę", "", "Pliki HTML (*.html);;Wszystkie pliki (*)")
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.html_browser.toHtml())
                QMessageBox.information(self, "Eksport zakończony", 
                                      f"Analiza została wyeksportowana do {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Błąd eksportu", 
                                    f"Nie udało się wyeksportować analizy: {str(e)}")
    
    def set_object(self, obj_data):
        """Set the object data to display."""
        self.current_object = obj_data
        
        if not obj_data:
            self.clear_content()
            return
        
        # Update title
        self.title_label.setText(obj_data.get("name", "Unknown Object"))
        
        # Update basic info
        self.id_label.setText(obj_data.get("id", ""))
        self.scale_label.setText(obj_data.get("scale", "").capitalize())
        
        # Update data fields
        self.update_data_fields(obj_data.get("data", {}))
        
        # Load comments if they exist (in a real app, this would come from a database)
        # For this demo, we'll just set a placeholder
        scale_comment_templates = {
            "quantum": "Quantum objects exhibit wave-particle duality governed by Schrödinger's equation.",
            "atomic": "Atomic structures are defined by electron orbitals around a nucleus.",
            "molecular": "Molecular properties emerge from atomic bonds and electronic interactions.",
            "cellular": "Cellular components perform specialized functions within biological systems.",
            "human": "Human-scale objects follow Newtonian mechanics in everyday experience.",
            "planetary": "Planetary bodies are governed by gravitational forces and orbital mechanics.",
            "stellar": "Stellar objects generate energy through nuclear fusion and evolve over billions of years.",
            "galactic": "Galactic structures are shaped by gravitational interactions and dark matter.",
            "cosmic": "Cosmic structures reveal the large-scale properties and history of the universe."
        }
        
        scale = obj_data.get("scale", "")
        default_comment = scale_comment_templates.get(scale, "")
        
        self.comments_edit.setText(f"[Analysis Notes]\n{default_comment}\n\n[Time Crystal Relevance]\nThis object {'might' if scale in ['quantum', 'atomic'] else 'does not'} exhibit time crystal properties.")
    
    def update_data_fields(self, data_dict):
        """Update the data fields display."""
        # Clear existing fields
        while self.data_layout.count():
            item = self.data_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add data fields
        row = 0
        for key, value in sorted(data_dict.items()):
            # Create label for key
            key_label = QLabel(f"{key}:")
            key_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Format key to be bold
            font = key_label.font()
            font.setBold(True)
            key_label.setFont(font)
            
            # Create label for value
            value_label = QLabel(str(value))
            value_label.setWordWrap(True)
            
            # Add to layout
            self.data_layout.addWidget(key_label, row, 0)
            self.data_layout.addWidget(value_label, row, 1)
            
            row += 1
    
    def clear_content(self):
        """Clear all content from the dock widget."""
        self.title_label.setText("")
        self.id_label.setText("")
        self.scale_label.setText("")
        self.comments_edit.clear()
        
        # Clear data fields
        while self.data_layout.count():
            item = self.data_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
