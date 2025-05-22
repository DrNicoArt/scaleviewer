"""
Funkcje do integracji nowych komponentów wizualizacji w głównym oknie aplikacji.
Ten plik zawiera tylko funkcje do zintegrowania z istniejącym ui/main_window.py.
"""

def integrate_multi_object_visualizations(self):
    """Integruje wizualizacje wielu obiektów jednocześnie w głównym oknie."""
    from ui.netgraph_view import NetGraphView
    from ui.heatmap_view import HeatmapView
    from ui.waveform_view import WaveformView
    
    # Dodaj akcje do menu Analiza
    self.netgraph_action = self.create_action(
        "&Graf Powiązań", 
        "Wyświetl graf powiązań między obiektami na różnych skalach",
        self.on_show_netgraph
    )
    
    self.heatmap_action = self.create_action(
        "&Mapa Cieplna Korelacji", 
        "Pokaż mapę cieplną korelacji periodyczności między obiektami",
        self.on_show_heatmap
    )
    
    self.waveform_action = self.create_action(
        "&Wykres Falowy Porównawczy", 
        "Porównaj oscylacje różnych obiektów na jednym wykresie",
        self.on_show_waveform
    )
    
    # Dodaj nowe akcje do menu Analiza
    self.analysis_menu.addSeparator()
    self.analysis_menu.addAction(self.netgraph_action)
    self.analysis_menu.addAction(self.heatmap_action)
    self.analysis_menu.addAction(self.waveform_action)
    
    # Dodaj przyciski do paska narzędzi
    self.toolbar.addSeparator()
    self.toolbar.addAction(self.netgraph_action)
    self.toolbar.addAction(self.heatmap_action)
    self.toolbar.addAction(self.waveform_action)
    
    # Przygotuj komponenty (leniwa inicjalizacja)
    self._netgraph_view = None
    self._heatmap_view = None
    self._waveform_view = None

def on_show_netgraph(self):
    """Wyświetla wizualizację grafu powiązań między obiektami."""
    if not hasattr(self, '_netgraph_view') or self._netgraph_view is None:
        from ui.netgraph_view import NetGraphView
        self._netgraph_view = NetGraphView()
        
    if self.data_model:
        # Pobierz wszystkie obiekty ze wszystkich skal
        all_objects = []
        for scale in self.data_model.get_scales():
            scale_objects = self.data_model.get_objects_by_scale(scale)
            all_objects.extend(scale_objects)
        
        # Załaduj dane do grafu
        self._netgraph_view.set_data(all_objects)
    
    # Pokaż w osobnym oknie
    self._netgraph_view.setWindowTitle("CosmicAnalyzer - Graf Powiązań")
    self._netgraph_view.resize(800, 600)
    self._netgraph_view.show()
    self._netgraph_view.raise_()

def on_show_heatmap(self):
    """Wyświetla wizualizację mapy cieplnej korelacji między obiektami."""
    if not hasattr(self, '_heatmap_view') or self._heatmap_view is None:
        from ui.heatmap_view import HeatmapView
        self._heatmap_view = HeatmapView()
        
    if self.data_model:
        # Pobierz wszystkie obiekty ze wszystkich skal
        all_objects = []
        for scale in self.data_model.get_scales():
            scale_objects = self.data_model.get_objects_by_scale(scale)
            all_objects.extend(scale_objects)
        
        # Załaduj dane do mapy cieplnej
        self._heatmap_view.set_data(all_objects)
    
    # Pokaż w osobnym oknie
    self._heatmap_view.setWindowTitle("CosmicAnalyzer - Mapa Cieplna Korelacji")
    self._heatmap_view.resize(800, 600)
    self._heatmap_view.show()
    self._heatmap_view.raise_()

def on_show_waveform(self):
    """Wyświetla wykres falowy porównujący oscylacje różnych obiektów."""
    if not hasattr(self, '_waveform_view') or self._waveform_view is None:
        from ui.waveform_view import WaveformView
        self._waveform_view = WaveformView()
        
    if self.data_model:
        # Pobierz wszystkie obiekty ze wszystkich skal
        all_objects = []
        for scale in self.data_model.get_scales():
            scale_objects = self.data_model.get_objects_by_scale(scale)
            all_objects.extend(scale_objects)
        
        # Załaduj dane do wykresu falowego
        self._waveform_view.set_data(all_objects)
    
    # Pokaż w osobnym oknie
    self._waveform_view.setWindowTitle("CosmicAnalyzer - Wykres Falowy Porównawczy")
    self._waveform_view.resize(800, 600)
    self._waveform_view.show()
    self._waveform_view.raise_()

def on_find_periodicity(self):
    """Znajduje periodyczność na wszystkich skalach (analogie do kryształów czasu)."""
    if not self.data_model:
        self.show_status_message("Brak danych do analizy")
        return
        
    from analysis.crystal_detection import CrystalDetector
    
    # Pobierz wszystkie obiekty ze wszystkich skal
    all_objects = []
    for scale in self.data_model.get_scales():
        scale_objects = self.data_model.get_objects_by_scale(scale)
        all_objects.extend(scale_objects)
    
    # Szukaj obiektów z periodycznością (analogie do kryształów czasu)
    detector = CrystalDetector()
    candidates = detector.find_candidates(all_objects)
    
    # Wyświetl wyniki
    if candidates:
        result_html = self.format_periodicity_results(candidates)
        
        # Pokaż wyniki w InfoDock
        if hasattr(self, 'info_dock'):
            self.info_dock.set_html_content(result_html)
            self.info_dock.show()
            
            # Opcjonalnie - pokaż periodyczność na wykresie falowym
            if hasattr(self, '_waveform_view') and self._waveform_view is not None:
                # Wybierz pierwszych 5 najlepszych kandydatów
                top_candidates = candidates[:min(5, len(candidates))]
                candidate_ids = [c["object"]["id"] for c in top_candidates]
                self._waveform_view.select_objects_by_ids(candidate_ids)
                self._waveform_view.show()
                self._waveform_view.raise_()
        
        self.show_status_message(f"Znaleziono {len(candidates)} potencjalnych obiektów z periodycznością")
    else:
        self.show_status_message("Nie znaleziono obiektów z periodycznością")

def format_periodicity_results(self, candidates):
    """Formatuje wyniki wyszukiwania periodyczności do wyświetlenia w HTML."""
    html = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; margin: 10px; }
            h1 { color: #2c3e50; font-size: 20px; margin-bottom: 15px; }
            h2 { color: #3498db; font-size: 16px; margin-top: 15px; margin-bottom: 5px; }
            .candidate { margin-bottom: 15px; padding: 10px; border-left: 4px solid #3498db; background-color: #ecf0f1; }
            .high { border-left-color: #e74c3c; }
            .medium { border-left-color: #f39c12; }
            .low { border-left-color: #2ecc71; }
            .score { font-weight: bold; margin-top: 5px; }
            .explanation { margin-top: 5px; font-style: italic; }
            .properties { margin-top: 5px; font-size: 0.9em; }
            .scale { color: #7f8c8d; font-size: 0.8em; }
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