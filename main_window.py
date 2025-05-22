import os
from PyQt5.QtWidgets import (QMainWindow, QAction, QSplitter, QTabWidget, 
                            QFileDialog, QMessageBox, QDockWidget, QToolBar, 
                            QStatusBar, QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QPushButton, QGridLayout, QTextEdit, QGroupBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QColor

from ui.tree_view import ScaleTreeView
from ui.table_view import ObjectTableView
from ui.waveform_view import WaveformView
from ui.radar_view import RadarView
from ui.crystal_view import CrystalView
from ui.info_dock import InfoDockWidget
# Nowe komponenty wizualizacji wielu obiektów
from ui.netgraph_view import NetGraphView
from ui.heatmap_view import HeatmapView
from data.data_loader import DataLoader
from export.pdf_report import PDFReportGenerator
from export.data_export import DataExporter
from analysis.similarity import SimilarityFinder
from analysis.crystal_detection import CrystalDetector
from utils.constants import SCALE_NAMES, APP_NAME, APP_VERSION, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT


class MainWindow(QMainWindow):
    """Main application window that contains all UI components."""
    
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.data_loader = DataLoader()
        self.similarity_finder = SimilarityFinder()
        self.crystal_detector = CrystalDetector()  # Dodany detektor kryształów
        self.current_file = ""
        
        self.setup_ui()
        self.load_window_state()
        self.show_status_message("Ready. Load data file to begin analysis.")
    
    def setup_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Cosmic Analyzer - Multi-scale Scientific Data Visualization")
        self.resize(1200, 800)
        
        # Create main splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.main_splitter)
        
        # Create left panel (tree view)
        self.scale_tree_view = ScaleTreeView()
        self.main_splitter.addWidget(self.scale_tree_view)
        
        # Create right panel (tab widget)
        self.tab_widget = QTabWidget()
        self.main_splitter.addWidget(self.tab_widget)
        
        # Set splitter proportions
        self.main_splitter.setSizes([300, 900])
        
        # Create tab views
        self.table_view = ObjectTableView()
        self.waveform_view = WaveformView()
        self.radar_view = RadarView()
        self.crystal_view = CrystalView()
        
        # Add tabs
        self.tab_widget.addTab(self.table_view, "Table")
        self.tab_widget.addTab(self.waveform_view, "Waveform")
        self.tab_widget.addTab(self.radar_view, "Radar")
        self.tab_widget.addTab(self.crystal_view, "Crystal View")
        
        # Create info dock widget
        self.info_dock = InfoDockWidget()
        self.addDockWidget(Qt.RightDockWidgetArea, self.info_dock)
        self.info_dock.hide()  # Hidden by default, shown when user clicks [i]
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Create menu bar and actions
        self.create_actions()
        self.create_menus()
        self.create_toolbar()
        
        # Przygotuj komponenty do wizualizacji wielu obiektów jednocześnie
        self._netgraph_view = None  # Leniwa inicjalizacja
        self._heatmap_view = None   # Leniwa inicjalizacja
        self._waveform_compare_view = None  # Leniwa inicjalizacja
        
        # Connect signals
        self.scale_tree_view.object_selected.connect(self.on_object_selected)
        self.scale_tree_view.object_info_requested.connect(self.on_info_requested)
        self.table_view.object_selected.connect(self.on_object_selected)
        self.table_view.object_info_requested.connect(self.on_info_requested)
    
    def create_actions(self):
        """Create application actions."""
        # File actions
        self.open_action = QAction("&Open JSON...", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self.on_open_file)
        
        self.reload_action = QAction("&Reload", self)
        self.reload_action.setShortcut("F5")
        self.reload_action.triggered.connect(self.on_reload_file)
        self.reload_action.setEnabled(False)
        
        self.exit_action = QAction("E&xit", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)
        
        # Analysis actions
        self.find_similar_action = QAction("Find &Similar...", self)
        self.find_similar_action.setShortcut("Ctrl+S")
        self.find_similar_action.triggered.connect(self.on_find_similar)
        self.find_similar_action.setEnabled(False)
        
        self.find_crystals_action = QAction("Find Time &Crystals", self)
        self.find_crystals_action.setShortcut("Ctrl+T")
        self.find_crystals_action.triggered.connect(self.on_find_crystals)
        self.find_crystals_action.setEnabled(False)
        
        # Nowa akcja: wykrywanie periodyczności we wszystkich skalach
        self.find_periodicity_action = QAction("Find &Periodicity (All Scales)", self)
        self.find_periodicity_action.setShortcut("Ctrl+P")
        self.find_periodicity_action.triggered.connect(self.on_find_periodicity)
        self.find_periodicity_action.setEnabled(False)
        
        # Akcje dla nowych wizualizacji
        self.netgraph_action = QAction("&Connection Network", self)
        self.netgraph_action.setShortcut("Ctrl+N")
        self.netgraph_action.triggered.connect(self.on_show_netgraph)
        self.netgraph_action.setEnabled(False)
        
        self.heatmap_action = QAction("&Heatmap Correlation", self)
        self.heatmap_action.setShortcut("Ctrl+H")
        self.heatmap_action.triggered.connect(self.on_show_heatmap)
        self.heatmap_action.setEnabled(False)
        
        self.waveform_compare_action = QAction("&Waveform Comparison", self)
        self.waveform_compare_action.setShortcut("Ctrl+W")
        self.waveform_compare_action.triggered.connect(self.on_show_waveform)
        self.waveform_compare_action.setEnabled(False)
        
        # Export actions
        self.export_pdf_action = QAction("Export PDF &Report...", self)
        self.export_pdf_action.setShortcut("Ctrl+R")
        self.export_pdf_action.triggered.connect(self.on_export_pdf)
        self.export_pdf_action.setEnabled(False)
        
        self.export_csv_action = QAction("Export &CSV...", self)
        self.export_csv_action.triggered.connect(lambda: self.on_export_data("csv"))
        self.export_csv_action.setEnabled(False)
        
        self.export_json_action = QAction("Export &JSON...", self)
        self.export_json_action.triggered.connect(lambda: self.on_export_data("json"))
        self.export_json_action.setEnabled(False)
        
        self.export_txt_action = QAction("Export &Text...", self)
        self.export_txt_action.triggered.connect(lambda: self.on_export_data("txt"))
        self.export_txt_action.setEnabled(False)
    
    def create_menus(self):
        """Create application menus."""
        # File menu
        self.file_menu = self.menuBar().addMenu("&File")
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.reload_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)
        
        # Analysis menu
        self.analysis_menu = self.menuBar().addMenu("&Analysis")
        self.analysis_menu.addAction(self.find_similar_action)
        self.analysis_menu.addAction(self.find_crystals_action)
        self.analysis_menu.addAction(self.find_periodicity_action)
        
        # Multi-object visualizations submenu
        self.visualization_menu = self.menuBar().addMenu("&Multi-object Visualization")
        self.visualization_menu.addAction(self.netgraph_action)
        self.visualization_menu.addAction(self.heatmap_action)
        self.visualization_menu.addAction(self.waveform_compare_action)
        
        # Export menu
        self.export_menu = self.menuBar().addMenu("&Export")
        self.export_menu.addAction(self.export_pdf_action)
        self.export_menu.addAction(self.export_csv_action)
        self.export_menu.addAction(self.export_json_action)
        self.export_menu.addAction(self.export_txt_action)
        
        # View menu
        self.view_menu = self.menuBar().addMenu("&View")
        self.view_menu.addAction(self.info_dock.toggleViewAction())
    
    def create_toolbar(self):
        """Create application toolbar."""
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.toolbar)
        
        # Podstawowe akcje
        self.toolbar.addAction(self.open_action)
        self.toolbar.addAction(self.reload_action)
        self.toolbar.addSeparator()
        
        # Akcje analityczne
        self.toolbar.addAction(self.find_similar_action)
        self.toolbar.addAction(self.find_crystals_action)
        self.toolbar.addAction(self.find_periodicity_action)
        self.toolbar.addSeparator()
        
        # Nowe wizualizacje wielu obiektów
        self.toolbar.addAction(self.netgraph_action)
        self.toolbar.addAction(self.heatmap_action)
        self.toolbar.addAction(self.waveform_compare_action)
        self.toolbar.addSeparator()
        
        # Eksport
        self.toolbar.addAction(self.export_pdf_action)
    
    def on_open_file(self):
        """Handle open file action."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Data File", "", "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            # Sprawdź, czy to nowy plik czy dodajemy dane
            append_mode = False
            if self.data_loader.objects:
                # Zapytaj użytkownika, czy chce zastąpić czy dodać dane
                reply = QMessageBox.question(
                    self, 
                    "Append Data?",
                    "Do you want to add these objects to existing data?\n\nYes - Add to existing objects\nNo - Replace existing objects",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                append_mode = (reply == QMessageBox.Yes)
            
            self.load_data_file(file_path, append_mode)
    
    def load_data_file(self, file_path, append=False):
        """
        Load data from the specified file.
        
        Args:
            file_path: Path to the data file
            append: If True, new objects will be added to existing ones instead of replacing them
        """
        try:
            data = self.data_loader.load_file(file_path, append=append)
            
            if data:
                self.current_file = file_path
                self.settings.setValue("last_opened_file", file_path)
                
                # Update UI components with the loaded data
                self.scale_tree_view.set_data(data)
                self.table_view.set_data(data)
                self.waveform_view.set_data(data)
                self.radar_view.set_data(data)
                self.crystal_view.set_data(data)
                
                # Enable actions
                self.reload_action.setEnabled(True)
                self.find_similar_action.setEnabled(True)
                self.find_crystals_action.setEnabled(True)
                self.find_periodicity_action.setEnabled(True)  # Nowa akcja: wykrywanie periodyczności
                self.export_pdf_action.setEnabled(True)
                self.export_csv_action.setEnabled(True)
                self.export_json_action.setEnabled(True)
                self.export_txt_action.setEnabled(True)
                
                # Włącz akcje dla wizualizacji wielu obiektów
                self.netgraph_action.setEnabled(True)
                self.heatmap_action.setEnabled(True)
                self.waveform_compare_action.setEnabled(True)
                
                # Pokaż odpowiedni komunikat w zależności od trybu
                if append:
                    self.show_status_message(f"Added objects from {os.path.basename(file_path)}. Total objects: {len(data)}")
                else:
                    self.show_status_message(f"Loaded {len(data)} objects from {os.path.basename(file_path)}")
            else:
                self.show_status_message("No valid data found in the file.")
        
        except Exception as e:
            QMessageBox.critical(self, "Error Loading Data", f"Failed to load data: {str(e)}")
            self.show_status_message("Error loading data file.")
    
    def on_reload_file(self):
        """Handle reload file action."""
        if self.current_file:
            self.load_data_file(self.current_file)
    
    def on_find_similar(self):
        """Handle find similar action."""
        if not self.scale_tree_view.get_selected_object():
            QMessageBox.information(self, "Selection Required", 
                                    "Please select an object to find similar items.")
            return
        
        try:
            source_object = self.scale_tree_view.get_selected_object()
            similar_objects = self.similarity_finder.find_similar(
                source_object, 
                self.data_loader.objects,
                n=5
            )
            
            # Update UI to highlight similar objects
            self.scale_tree_view.highlight_similar_objects(similar_objects)
            self.table_view.highlight_similar_objects(similar_objects)
            
            self.show_status_message(f"Found {len(similar_objects)} objects similar to {source_object['name']}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error Finding Similar Objects", 
                                 f"An error occurred: {str(e)}")
                                 
    def on_find_crystals(self):
        """Handle find time crystals action."""
        if not self.data_loader.objects:
            QMessageBox.information(self, "No Data", 
                                   "No data loaded. Please load a data file first.")
            return
            
        try:
            # Użyj detektora kryształów do znalezienia potencjalnych kandydatów
            crystal_candidates = self.crystal_detector.find_candidates(self.data_loader.objects)
            
            if not crystal_candidates:
                QMessageBox.information(self, "No Candidates", 
                                       "No time crystal candidates found in the current dataset.")
                return
                
            # Sortuj kandydatów według wyniku pewności (malejąco)
            sorted_candidates = sorted(crystal_candidates, key=lambda x: x["score"], reverse=True)
            
            # Utwórz listę obiektów kandydatów (tylko obiekty, bez wyników i wyjaśnień)
            candidate_objects = [candidate["object"] for candidate in sorted_candidates]
            
            # Podświetl kandydatów w widokach
            self.scale_tree_view.highlight_similar_objects(candidate_objects)
            self.table_view.highlight_similar_objects(candidate_objects)
            
            # Wyświetl szczegółowy komunikat z wyjaśnieniami
            message = "Potential time crystal candidates:\n\n"
            for candidate in sorted_candidates[:5]:  # Pokaż top 5 kandydatów
                obj = candidate["object"]
                score = candidate["score"]
                explanation = candidate["explanation"]
                message += f"• {obj['name']} (Confidence: {score:.0f}%)\n"
                message += f"  {explanation}\n\n"
            
            QMessageBox.information(self, "Time Crystal Candidates", message)
            
            self.show_status_message(f"Found {len(crystal_candidates)} potential time crystal candidates")
            
        except Exception as e:
            QMessageBox.critical(self, "Error Finding Time Crystals", 
                               f"An error occurred: {str(e)}")
                               
    def on_find_periodicity(self):
        """Wyszukuje periodyczność na wszystkich skalach (analogie do kryształów czasu)."""
        if not self.data_loader.objects:
            QMessageBox.information(self, "No Data", 
                                   "No data loaded. Please load a data file first.")
            return
            
        try:
            # Pobierz wszystkie obiekty ze wszystkich skal
            all_objects = self.data_loader.objects
            
            # Szukaj obiektów z periodycznością (analogie do kryształów czasu)
            candidates = self.crystal_detector.find_candidates(all_objects)
            
            # Wyświetl wyniki
            if candidates:
                result_html = self.format_periodicity_results(candidates)
                
                # Pokaż wyniki w InfoDock
                self.info_dock.set_html_content(result_html)
                self.info_dock.show()
                
                # Opcjonalnie - pokaż periodyczność na wykresie falowym
                if hasattr(self, '_waveform_compare_view') and self._waveform_compare_view is not None:
                    # Wybierz pierwszych 5 najlepszych kandydatów
                    top_candidates = candidates[:min(5, len(candidates))]
                    candidate_ids = [c["object"]["id"] for c in top_candidates]
                    self._waveform_compare_view.select_objects_by_ids(candidate_ids)
                    self._waveform_compare_view.show()
                    self._waveform_compare_view.raise_()
                
                self.show_status_message(f"Znaleziono {len(candidates)} potencjalnych obiektów z periodycznością")
            else:
                self.show_status_message("Nie znaleziono obiektów z periodycznością")
                QMessageBox.information(self, "No Periodicity Found", 
                                       "No objects with periodicity were found in the current dataset.")
        except Exception as e:
            QMessageBox.critical(self, "Error Finding Periodicity", 
                               f"An error occurred: {str(e)}")
                               
    def format_periodicity_results(self, candidates):
        """Formatuje wyniki wyszukiwania periodyczności do wyświetlenia w HTML."""
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 10px; background-color: #1e1e1e; color: #f0f0f0; }
                h1 { color: #58a6ff; font-size: 20px; margin-bottom: 15px; }
                h2 { color: #79c0ff; font-size: 16px; margin-top: 15px; margin-bottom: 5px; }
                .candidate { margin-bottom: 15px; padding: 10px; border-left: 4px solid #3498db; background-color: #2d333b; }
                .high { border-left-color: #ff7b72; }
                .medium { border-left-color: #d29922; }
                .low { border-left-color: #7ee787; }
                .score { font-weight: bold; margin-top: 5px; }
                .explanation { margin-top: 5px; font-style: italic; }
                .properties { margin-top: 5px; font-size: 0.9em; }
                .scale { color: #8b949e; font-size: 0.8em; }
            </style>
        </head>
        <body>
            <h1>Wykryte Obiekty z Periodycznością (Analogie Kryształów Czasu)</h1>
            <p>Analiza wykryła następujące obiekty wykazujące periodyczność na różnych skalach:</p>
        """
        
        for candidate in candidates:
            obj = candidate["object"]
            score = candidate["score"]
            explanation = candidate["explanation"]
            
            # Określ klasę CSS w zależności od wyniku
            css_class = "candidate "
            if score >= 7:
                css_class += "high"
            elif score >= 4:
                css_class += "medium"
            else:
                css_class += "low"
            
            # Dodaj informacje o obiekcie
            html += f"""
            <div class="{css_class}">
                <h2>{obj["name"]}</h2>
                <div class="scale">Skala: {obj["scale"]}</div>
                <div class="score">Wynik: {score}/10</div>
                <div class="explanation">{explanation}</div>
                <div class="properties">
                    <strong>Własności:</strong><br>
            """
            
            # Dodaj własności obiektu
            for key, value in obj.get("data", {}).items():
                html += f"&nbsp;&nbsp;• {key}: {value}<br>"
            
            html += """
                </div>
            </div>
            """
        
        html += """
            <p>Właściwości periodyczne na różnych skalach mogą być analogami kwantowych kryształów czasu, 
               pokazując jak podobne wzorce występują w całym spektrum skal.</p>
        </body>
        </html>
        """
        
        return html
                         
    def on_show_netgraph(self):
        """Wyświetla wizualizację grafu powiązań między obiektami."""
        if not self.data_loader.objects:
            QMessageBox.information(self, "No Data", 
                                   "No data loaded. Please load a data file first.")
            return
            
        if not self._netgraph_view:
            self._netgraph_view = NetGraphView()
            
        # Pobierz wszystkie obiekty ze wszystkich skal
        all_objects = self.data_loader.objects
        
        # Załaduj dane do grafu
        self._netgraph_view.set_data(all_objects)
        
        # Pokaż w osobnym oknie
        self._netgraph_view.setWindowTitle("CosmicAnalyzer - Graf Powiązań")
        self._netgraph_view.resize(800, 600)
        self._netgraph_view.show()
        self._netgraph_view.raise_()
        
        self.show_status_message("Displaying network graph of object connections")
        
    def on_show_heatmap(self):
        """Wyświetla wizualizację mapy cieplnej korelacji między obiektami."""
        if not self.data_loader.objects:
            QMessageBox.information(self, "No Data", 
                                   "No data loaded. Please load a data file first.")
            return
            
        if not self._heatmap_view:
            self._heatmap_view = HeatmapView()
            
        # Pobierz wszystkie obiekty ze wszystkich skal
        all_objects = self.data_loader.objects
        
        # Załaduj dane do mapy cieplnej
        self._heatmap_view.set_data(all_objects)
        
        # Pokaż w osobnym oknie
        self._heatmap_view.setWindowTitle("CosmicAnalyzer - Mapa Cieplna Korelacji")
        self._heatmap_view.resize(900, 700)
        self._heatmap_view.show()
        self._heatmap_view.raise_()
        
        self.show_status_message("Displaying correlation heatmap of objects")
        
    def on_show_waveform(self):
        """Wyświetla wykres falowy porównujący oscylacje różnych obiektów."""
        if not self.data_loader.objects:
            QMessageBox.information(self, "No Data", 
                                   "No data loaded. Please load a data file first.")
            return
            
        # Użyj waveform_view.py, ale traktuj go jako widok porównujący wiele obiektów
        if not self._waveform_compare_view:
            from ui.waveform_view import WaveformView
            self._waveform_compare_view = WaveformView()
            
        # Pobierz wszystkie obiekty ze wszystkich skal
        all_objects = self.data_loader.objects
        
        # Załaduj dane
        self._waveform_compare_view.set_data(all_objects)
        
        # Pokaż w osobnym oknie
        self._waveform_compare_view.setWindowTitle("CosmicAnalyzer - Wykres Falowy Porównawczy")
        self._waveform_compare_view.resize(800, 600)
        self._waveform_compare_view.show()
        self._waveform_compare_view.raise_()
        
        self.show_status_message("Displaying waveform comparison chart")
    
    def on_export_pdf(self):
        """Handle export PDF report action."""
        if not self.data_loader.objects:
            QMessageBox.information(self, "No Data", "No data available to export.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export PDF Report", "", "PDF Files (*.pdf);;All Files (*)"
        )
        
        if file_path:
            try:
                selected_objects = self.scale_tree_view.get_selected_objects()
                report_gen = PDFReportGenerator()
                
                # Generate screenshots of current visualizations
                table_img = self.table_view.take_screenshot()
                waveform_img = self.waveform_view.take_screenshot()
                radar_img = self.radar_view.take_screenshot()
                crystal_img = self.crystal_view.take_screenshot()
                
                # Generate the report
                report_gen.generate_report(
                    file_path,
                    selected_objects if selected_objects else self.data_loader.objects,
                    {
                        "table": table_img,
                        "waveform": waveform_img,
                        "radar": radar_img,
                        "crystal": crystal_img
                    }
                )
                
                self.show_status_message(f"PDF report exported to {os.path.basename(file_path)}")
            
            except Exception as e:
                QMessageBox.critical(self, "Error Exporting PDF", 
                                     f"Failed to export PDF: {str(e)}")
    
    def on_export_data(self, format_type):
        """Handle export data action."""
        if not self.data_loader.objects:
            QMessageBox.information(self, "No Data", "No data available to export.")
            return
        
        filter_map = {
            "csv": "CSV Files (*.csv);;All Files (*)",
            "json": "JSON Files (*.json);;All Files (*)",
            "txt": "Text Files (*.txt);;All Files (*)"
        }
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"Export {format_type.upper()} Data", "", filter_map[format_type]
        )
        
        if file_path:
            try:
                selected_objects = self.scale_tree_view.get_selected_objects()
                exporter = DataExporter()
                
                exporter.export_data(
                    file_path,
                    selected_objects if selected_objects else self.data_loader.objects,
                    format_type
                )
                
                self.show_status_message(f"Data exported to {os.path.basename(file_path)}")
            
            except Exception as e:
                QMessageBox.critical(self, "Error Exporting Data", 
                                     f"Failed to export data: {str(e)}")
    
    def on_object_selected(self, obj_data):
        """Handle object selection from tree or table views."""
        # Update all views to reflect the selected object
        self.table_view.select_object(obj_data)
        self.waveform_view.select_object(obj_data)
        self.radar_view.select_object(obj_data)
        self.crystal_view.select_object(obj_data)
        
        # Generate scientific analysis for the selected object
        self.generate_scientific_analysis(obj_data)
        
        # Update status bar
        self.show_status_message(f"Selected: {obj_data['name']} ({obj_data['scale']})")
    
    def on_info_requested(self, obj_data):
        """Show the info dock when user requests object information."""
        self.info_dock.set_object(obj_data)
        self.info_dock.show()
    
    def generate_scientific_analysis(self, obj_data):
        """Tworzy szczegółową analizę naukową dla wybranego obiektu."""
        if not obj_data:
            return
            
        # Przygotuj dane do analizy
        obj_name = obj_data.get("name", "Nieznany obiekt")
        obj_scale = obj_data.get("scale", "Nieznana skala")
        obj_id = obj_data.get("id", "Nieznany ID")
        
        # Interpretacje naukowe dla różnych skal
        scale_interpretations = {
            "quantum": {
                "title": "Kwantowa interpretacja",
                "description": """Obiekty kwantowe podlegają zasadom mechaniki kwantowej, wykazując właściwości takie jak dualizm korpuskularno-falowy, 
                               zasada nieoznaczoności, superpozycja stanów i splątanie kwantowe. Na tej skali obserwujemy fundamentalne składniki materii, 
                               które zachowują się zarówno jak cząstki, jak i fale.""",
                "time_crystal": """Kryształy czasu na poziomie kwantowym są układami cząstek, które spontanicznie łamią symetrię translacji w czasie,
                               wykazując periodyczne zachowania w stanie podstawowym bez dostarczania energii. Mogą być realizowane w układach spinów,
                               ultrazimnych atomów lub pułapkowanych jonów."""
            },
            "atomic": {
                "title": "Atomowa interpretacja",
                "description": """Atomy są podstawowymi jednostkami materii, składającymi się z jądra (protony i neutrony) oraz otaczającej go chmury elektronów.
                               Właściwości chemiczne pierwiastków są określone głównie przez liczbę elektronów i ich konfigurację na powłokach elektronowych.""",
                "time_crystal": """Układy atomowe mogą wykazywać właściwości podobne do kryształów czasu gdy są pułapkowane i poddawane periodycznym zaburzeniom.
                               W takich układach można obserwować subharmoniczne rezonanse i spontaniczną periodyczność czasową."""
            },
            "molecular": {
                "title": "Molekularna interpretacja",
                "description": """Cząsteczki są utworzone przez atomy połączone wiązaniami chemicznymi. Ich struktura, geometria i rozkład ładunku elektrycznego
                               determinują ich właściwości chemiczne i funkcje biologiczne.""",
                "time_crystal": """Molekuły zwykle nie wykazują właściwości kryształów czasu w ścisłym sensie kwantowym, ale mogą wykazywać periodyczne
                               zachowania w reakcjach chemicznych i dynamice molekularnej."""
            },
            "cellular": {
                "title": "Komórkowa interpretacja",
                "description": """Komórki są podstawowymi jednostkami strukturalnymi i funkcjonalnymi wszystkich organizmów żywych. Zawierają organelle
                               odpowiedzialne za różne funkcje, w tym DNA niosące informację genetyczną.""",
                "time_crystal": """Systemy biologiczne na poziomie komórkowym wykazują rytmiczne zachowania (np. cykle komórkowe, oscylacje biochemiczne),
                               które przypominają kryształy czasu, choć mają inną naturę fizyczną."""
            },
            "human": {
                "title": "Interpretacja w skali człowieka",
                "description": """Skala ludzka odnosi się do złożonych systemów biologicznych i społecznych. Obejmuje zarówno fizjologię, 
                               anatomię jak i aspekty psychologiczne, socjologiczne i behawioralne.""",
                "time_crystal": """W skali ludzkiej nie obserwujemy kryształów czasu w sensie fizycznym, jednak rytmy biologiczne 
                               (np. rytmy snu, bicie serca) wykazują pewne analogie do periodycznego zachowania kryształów czasu."""
            },
            "planetary": {
                "title": "Planetarna interpretacja",
                "description": """Planety są dużymi ciałami niebieskimi krążącymi wokół gwiazd. Ich właściwości fizyczne, skład chemiczny
                               i dynamika determinują ich ewolucję i potencjał do podtrzymania życia.""",
                "time_crystal": """Układy planetarne wykazują periodyczne zachowania (orbity, pory roku, obrót), które są analogiczne do
                               periodyczności kryształów czasu, jednak wynikają z zachowania praw dynamiki klasycznej."""
            },
            "stellar": {
                "title": "Gwiazdowa interpretacja",
                "description": """Gwiazdy są masywnym kulami plazmy, w których zachodzą reakcje termojądrowe. Ich ewolucja zależy głównie od masy początkowej,
                               która determinuje ich temperaturę, luminancję i cykl życia.""",
                "time_crystal": """Gwiazdy mogą wykazywać periodyczne zachowania, takie jak pulsacje i aktywność cykliczna, 
                               które są analogiczne do kryształów czasu. Szczególnie gwiazdy zmienne wykazują regularne oscylacje jasności."""
            },
            "galactic": {
                "title": "Galaktyczna interpretacja",
                "description": """Galaktyki to masywne układy gwiazd, gazu, pyłu i ciemnej materii połączone grawitacją. Ich struktura i ewolucja
                               są kształtowane przez dynamikę gwiezdną i oddziaływania grawitacyjne.""",
                "time_crystal": """W skali galaktycznej nie obserwujemy bezpośrednich analogii do kryształów czasu, choć rotacja galaktyk 
                               i fale gęstości spiralnej mogą wykazywać periodyczne właściwości."""
            },
            "cosmic": {
                "title": "Kosmiczna interpretacja",
                "description": """Skala kosmiczna odnosi się do całego obserwowalnego Wszechświata. Na tej skali dominują efekty rozszerzania się przestrzeni,
                               ciemnej energii i wielkoskalowej struktury.""",
                "time_crystal": """W kosmologii nie ma bezpośrednich odpowiedników kryształów czasu, choć niektóre modele teoretyczne
                               sugerują możliwość periodycznych oscylacji w globalnych parametrach kosmologicznych."""
            }
        }
        
        # Wybierz interpretację dla tej skali
        interpretation = scale_interpretations.get(obj_scale, {
            "title": "Ogólna interpretacja",
            "description": "Ten obiekt należy do niezdefiniowanej lub niestandardowej skali.",
            "time_crystal": "Brak danych o potencjale jako kryształ czasu dla tej skali."
        })
        
        # Określ potencjał jako kryształ czasu
        crystal_score = 0
        if hasattr(self, 'crystal_detector'):
            crystal_score = self.crystal_detector._evaluate_candidate(obj_data)
            
        crystal_potential = ""
        if crystal_score > 6:
            crystal_potential = f"<span style='color: green;'><b>Wysoki potencjał</b> (punktacja: {crystal_score:.1f}/10)</span> - Ten obiekt wykazuje liczne właściwości charakterystyczne dla kryształów czasu."
        elif crystal_score > 3:
            crystal_potential = f"<span style='color: orange;'><b>Umiarkowany potencjał</b> (punktacja: {crystal_score:.1f}/10)</span> - Ten obiekt posiada niektóre cechy sugerujące potencjał do zachowań charakterystycznych dla kryształów czasu."
        else:
            crystal_potential = f"<span style='color: red;'><b>Niski potencjał</b> (punktacja: {crystal_score:.1f}/10)</span> - Ten obiekt prawdopodobnie nie jest kandydatem na kryształ czasu."
        
        # Szczegółowa analiza właściwości
        property_analysis = ""
        for key, value in obj_data.get("data", {}).items():
            property_analysis += f"<tr><td><b>{key}</b></td><td>{value}</td><td>"
            
            # Dodaj szczegółowe interpretacje dla konkretnych właściwości
            if "spin" in key.lower() and "1/2" in str(value):
                property_analysis += "Wartość spinu 1/2 jest charakterystyczna dla fermionów. Obiekty o takim spinie podlegają zakazowi Pauliego i mogą tworzyć układy o złożonej strukturze kwantowej."
            elif "spin" in key.lower():
                property_analysis += "Spin jest fundamentalną właściwością kwantową związaną z momentem pędu cząstki. Jest kluczowy dla zrozumienia oddziaływań magnetycznych i struktury materii."
            elif "charge" in key.lower():
                property_analysis += "Ładunek elektryczny determinuje oddziaływania elektromagnetyczne. Podstawowy ładunek elementarny jest najmniejszą obserwowaną jednostką ładunku w przyrodzie."
            elif "mass" in key.lower():
                property_analysis += "Masa jest miarą inercji i oddziaływań grawitacyjnych. Determinuje wiele właściwości fizycznych obiektu, w tym jego zachowanie w polu grawitacyjnym."
            elif "energy" in key.lower():
                property_analysis += "Energia jest podstawową wielkością fizyczną związaną ze zdolnością układu do wykonania pracy. W mechanice kwantowej energia jest skwantowana i powiązana z częstotliwością."
            elif "frequency" in key.lower() or "period" in key.lower():
                property_analysis += "Periodyczność jest kluczowym parametrem dla potencjalnych kryształów czasu. Regularność oscylacji może wskazywać na koherencję kwantową."
            elif "lifetime" in key.lower() or "age" in key.lower():
                property_analysis += "Długi czas życia sugeruje stabilność i może być istotny dla utrzymania koherencji kwantowej w potencjalnych kryształach czasu."
            elif "temperature" in key.lower():
                property_analysis += "Temperatura wpływa na stopień uporządkowania i efekty kwantowe. Niskie temperatury sprzyjają zachowaniu koherencji kwantowej."
            else:
                property_analysis += "Parametr fizyczny charakteryzujący właściwości obiektu w danej skali."
            
            property_analysis += "</td></tr>"
        
        # Utwórz zawartość HTML
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 10px; color: #333; }}
                h1 {{ color: #2c3e50; font-size: 22px; text-align: center; border-bottom: 1px solid #ddd; padding-bottom: 10px; }}
                h2 {{ color: #3498db; font-size: 18px; margin-top: 20px; }}
                p {{ line-height: 1.5; text-align: justify; }}
                .section {{ margin-bottom: 20px; padding: 15px; border-radius: 5px; background-color: #f9f9f9; }}
                .properties {{ background-color: #f5f5f5; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #3498db; color: white; }}
                .crystal {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin-top: 20px; }}
                .footer {{ font-style: italic; text-align: center; margin-top: 30px; font-size: 12px; color: #777; }}
            </style>
        </head>
        <body>
            <h1>Analiza naukowa: {obj_name}</h1>
            
            <div class="section">
                <h2>{interpretation["title"]}</h2>
                <p>{interpretation["description"]}</p>
            </div>
            
            <div class="section properties">
                <h2>Szczegółowa analiza właściwości</h2>
                <table>
                    <tr>
                        <th style="width: 20%;">Właściwość</th>
                        <th style="width: 30%;">Wartość</th>
                        <th style="width: 50%;">Interpretacja naukowa</th>
                    </tr>
                    {property_analysis}
                </table>
            </div>
            
            <div class="crystal">
                <h2>Analiza potencjału jako kryształ czasu</h2>
                <p>{crystal_potential}</p>
                <p><b>Interpretacja dla tej skali:</b> {interpretation["time_crystal"]}</p>
            </div>
            
            <div class="footer">
                <p>Cosmic Analyzer - Wieloskalowa analiza danych naukowych - {obj_scale.capitalize()} Scale Object #{obj_id}</p>
            </div>
        </body>
        </html>
        """
        
        # Wyświetl analizę w panelu informacyjnym
        if hasattr(self.info_dock, 'set_html_content'):
            self.info_dock.set_html_content(html_content)
            self.info_dock.show()
    
    def show_status_message(self, message, timeout=5000):
        """Display a message in the status bar."""
        self.status_bar.showMessage(message, timeout)
    
    def save_window_state(self):
        """Save window position, size and state."""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        self.settings.setValue("splitterSizes", self.main_splitter.saveState())
    
    def load_window_state(self):
        """Load window position, size and state."""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        window_state = self.settings.value("windowState")
        if window_state:
            self.restoreState(window_state)
        
        splitter_state = self.settings.value("splitterSizes")
        if splitter_state:
            self.main_splitter.restoreState(splitter_state)
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.save_window_state()
        event.accept()
