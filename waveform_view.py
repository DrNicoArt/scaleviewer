from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QComboBox, QSlider, QPushButton, 
                           QCheckBox, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QPixmap

import numpy as np
import pyqtgraph as pg
import random
import math

class WaveformView(QWidget):
    """
    Waveform visualization component for comparing oscillations 
    across different objects and scales.
    """
    
    def __init__(self):
        super().__init__()
        self.objects = []
        self.selected_objects = []
        self.max_objects = 6  # Maximum number of objects to display
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.animation_speed = 30  # ms
        self.animation_running = False
        self.animation_frame = 0
        self.waveform_data = {}  # Stores waveform data for each object
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components."""
        self.layout = QVBoxLayout(self)
        
        # Controls layout
        controls_layout = QHBoxLayout()
        
        # Object selection
        selection_layout = QVBoxLayout()
        selection_label = QLabel("Wybierz obiekty (max 6):")
        self.object_list = QListWidget()
        self.object_list.setSelectionMode(QListWidget.MultiSelection)
        self.object_list.itemSelectionChanged.connect(self.on_selection_changed)
        
        selection_layout.addWidget(selection_label)
        selection_layout.addWidget(self.object_list)
        
        # Visualization controls
        vis_controls_layout = QVBoxLayout()
        
        # Frequency slider
        freq_layout = QHBoxLayout()
        freq_label = QLabel("Częstotliwość:")
        self.freq_slider = QSlider(Qt.Horizontal)
        self.freq_slider.setMinimum(1)
        self.freq_slider.setMaximum(100)
        self.freq_slider.setValue(20)
        self.freq_slider.valueChanged.connect(self.update_waveforms)
        
        freq_layout.addWidget(freq_label)
        freq_layout.addWidget(self.freq_slider)
        
        # Amplitude slider
        amp_layout = QHBoxLayout()
        amp_label = QLabel("Amplituda:")
        self.amp_slider = QSlider(Qt.Horizontal)
        self.amp_slider.setMinimum(10)
        self.amp_slider.setMaximum(100)
        self.amp_slider.setValue(50)
        self.amp_slider.valueChanged.connect(self.update_waveforms)
        
        amp_layout.addWidget(amp_label)
        amp_layout.addWidget(self.amp_slider)
        
        # Waveform type
        type_layout = QHBoxLayout()
        type_label = QLabel("Typ fali:")
        self.wave_type_combo = QComboBox()
        self.wave_type_combo.addItem("Sinus", "sine")
        self.wave_type_combo.addItem("Kwadrat", "square")
        self.wave_type_combo.addItem("Trójkąt", "triangle")
        self.wave_type_combo.addItem("Piła", "sawtooth")
        self.wave_type_combo.addItem("Szum", "noise")
        self.wave_type_combo.currentIndexChanged.connect(self.update_waveforms)
        
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.wave_type_combo)
        
        # Normalization checkbox
        normalize_layout = QHBoxLayout()
        self.normalize_check = QCheckBox("Normalizacja")
        self.normalize_check.setChecked(True)
        self.normalize_check.toggled.connect(self.update_waveforms)
        
        # Animation button
        self.animate_btn = QPushButton("Animacja")
        self.animate_btn.setCheckable(True)
        self.animate_btn.toggled.connect(self.toggle_animation)
        
        normalize_layout.addWidget(self.normalize_check)
        normalize_layout.addWidget(self.animate_btn)
        
        # Screenshot button
        screenshot_layout = QHBoxLayout()
        self.screenshot_btn = QPushButton("Zrzut ekranu")
        self.screenshot_btn.clicked.connect(self.take_screenshot)
        
        screenshot_layout.addWidget(self.screenshot_btn)
        
        # Add all controls to the vis_controls layout
        vis_controls_layout.addLayout(freq_layout)
        vis_controls_layout.addLayout(amp_layout)
        vis_controls_layout.addLayout(type_layout)
        vis_controls_layout.addLayout(normalize_layout)
        vis_controls_layout.addLayout(screenshot_layout)
        
        # Add control layouts to the main controls layout
        controls_layout.addLayout(selection_layout, 1)
        controls_layout.addLayout(vis_controls_layout, 2)
        
        self.layout.addLayout(controls_layout)
        
        # Setup plot
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('k')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('bottom', 'Czas')
        self.plot_widget.setLabel('left', 'Amplituda')
        self.plot_widget.addLegend()
        
        self.layout.addWidget(self.plot_widget)
        
        # Description label
        self.description = QLabel(
            "Wykres falowy pokazuje porównanie oscylacji i periodyczności różnych obiektów. "
            "Różnice w częstotliwości i amplitudzie odzwierciedlają rzeczywiste różnice między skalami."
        )
        self.description.setWordWrap(True)
        self.layout.addWidget(self.description)
        
        # Create empty plot lines
        self.plot_lines = {}
    
    def set_data(self, objects):
        """Set the dataset and initialize object list."""
        self.objects = objects
        
        # Clear previous data
        self.object_list.clear()
        self.waveform_data = {}
        self.selected_objects = []
        self.plot_widget.clear()
        self.plot_lines = {}
        
        # Add objects to list
        for obj in self.objects:
            obj_id = obj.get("id")
            obj_name = obj.get("name")
            obj_scale = obj.get("scale", "").capitalize()
            
            # Create list item
            item = QListWidgetItem(f"{obj_scale}: {obj_name}")
            item.setData(Qt.UserRole, obj_id)
            self.object_list.addItem(item)
            
            # Generate waveform parameters based on object properties
            self.waveform_data[obj_id] = self.generate_waveform_parameters(obj)
        
        # Select first few objects by default
        for i in range(min(3, self.object_list.count())):
            self.object_list.item(i).setSelected(True)
    
    def generate_waveform_parameters(self, obj):
        """Generate waveform parameters based on object properties."""
        obj_data = obj.get("data", {})
        obj_scale = obj.get("scale", "")
        
        # Base parameters
        params = {
            "base_frequency": 1.0,
            "frequency_modifier": 1.0,
            "amplitude": 1.0,
            "phase_shift": 0.0,
            "harmonic_content": [],  # For complex waveforms
            "wave_type": "sine"
        }
        
        # Extract values that might influence the waveform
        # Frequency-related properties
        for field in ["frequency", "peak_frequency", "period", "orbital_period", 
                     "rotation_period", "oscillation_period", "rotation_velocity"]:
            if field in obj_data:
                value = self.extract_numeric_value(obj_data[field])
                if value is not None:
                    # Period fields are inversely related to frequency
                    if "period" in field:
                        value = 1.0 / max(value, 0.001)  # Prevent division by zero
                    
                    params["frequency_modifier"] = self.normalize_frequency(value, obj_scale)
                    break
        
        # Amplitude-related properties
        for field in ["amplitude", "luminosity", "energy", "mass", "brightness", 
                     "temperature_anisotropy_rms", "first_ionization_energy"]:
            if field in obj_data:
                value = self.extract_numeric_value(obj_data[field])
                if value is not None:
                    params["amplitude"] = self.normalize_amplitude(value, obj_scale)
                    break
        
        # Phase shift based on object properties
        # Use a hash of the object ID for consistent random
        obj_id = obj.get("id", "")
        random.seed(hash(obj_id))
        params["phase_shift"] = random.uniform(0, 2 * math.pi)
        
        # Add harmonics for complex waveform approximation
        if "quantum" in obj_scale:
            # Quantum objects have more harmonics (quantum jumps)
            params["harmonic_content"] = [
                {"harmonic": 2, "amplitude": 0.5, "phase": random.uniform(0, 2 * math.pi)},
                {"harmonic": 3, "amplitude": 0.3, "phase": random.uniform(0, 2 * math.pi)},
                {"harmonic": 5, "amplitude": 0.2, "phase": random.uniform(0, 2 * math.pi)}
            ]
        elif "atomic" in obj_scale:
            # Atomic objects have some harmonics
            params["harmonic_content"] = [
                {"harmonic": 2, "amplitude": 0.4, "phase": random.uniform(0, 2 * math.pi)},
                {"harmonic": 3, "amplitude": 0.2, "phase": random.uniform(0, 2 * math.pi)}
            ]
        elif "molecular" in obj_scale:
            # Molecular objects have a few harmonics
            params["harmonic_content"] = [
                {"harmonic": 2, "amplitude": 0.3, "phase": random.uniform(0, 2 * math.pi)}
            ]
        else:
            # Other scales have minimal harmonics
            params["harmonic_content"] = [
                {"harmonic": 2, "amplitude": 0.15, "phase": random.uniform(0, 2 * math.pi)}
            ]
        
        # Apply some randomization to make each object unique
        params["frequency_modifier"] *= random.uniform(0.9, 1.1)
        params["amplitude"] *= random.uniform(0.9, 1.1)
        
        return params
    
    def normalize_frequency(self, frequency, scale):
        """Normalize frequency based on scale."""
        # Scale adjustments to make visualization meaningful
        scale_factors = {
            "quantum": 1000,
            "atomic": 500,
            "molecular": 200,
            "cellular": 100,
            "human": 50,
            "planetary": 10,
            "stellar": 5,
            "galactic": 2,
            "cosmic": 1
        }
        
        factor = scale_factors.get(scale, 1.0)
        
        # Normalize to a reasonable range
        normalized = frequency / factor
        return min(max(normalized, 0.1), 10.0)
    
    def normalize_amplitude(self, amplitude, scale):
        """Normalize amplitude based on scale."""
        # Scale adjustments to make visualization meaningful
        scale_factors = {
            "quantum": 0.2,
            "atomic": 0.4,
            "molecular": 0.6,
            "cellular": 0.7,
            "human": 0.8,
            "planetary": 0.9,
            "stellar": 1.0,
            "galactic": 1.1,
            "cosmic": 1.2
        }
        
        factor = scale_factors.get(scale, 1.0)
        
        # Normalize to a reasonable range
        return min(max(amplitude * factor, 0.1), 1.0)
    
    def extract_numeric_value(self, value):
        """Extract a numeric value from a field value."""
        if value is None:
            return None
            
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Extract numeric part
            numeric_str = ''.join(c for c in value if c.isdigit() or c == '.' or c == '-')
            if numeric_str:
                try:
                    return float(numeric_str)
                except:
                    pass
        
        return None
    
    def update_waveforms(self):
        """Update the waveform display based on current settings."""
        # Clear previous plot
        self.plot_widget.clear()
        self.plot_lines = {}
        
        # Get current settings
        frequency_factor = self.freq_slider.value() / 20.0  # Scale to 0.05-5.0
        amplitude_factor = self.amp_slider.value() / 50.0   # Scale to 0.2-2.0
        wave_type = self.wave_type_combo.currentData()
        normalize = self.normalize_check.isChecked()
        
        # Get colors for different scales
        scale_colors = {
            "quantum": (255, 0, 255),      # Magenta
            "atomic": (128, 0, 255),       # Purple
            "molecular": (0, 0, 255),      # Blue
            "cellular": (0, 255, 255),     # Cyan
            "human": (0, 255, 0),          # Green
            "planetary": (255, 255, 0),    # Yellow
            "stellar": (255, 128, 0),      # Orange
            "galactic": (255, 0, 0),       # Red
            "cosmic": (128, 0, 0)          # Dark red
        }
        
        # Create time array
        t = np.linspace(0, 10, 1000)
        
        # Calculate waveforms for selected objects
        waveforms = []
        
        for obj_id in self.selected_objects:
            obj = next((o for o in self.objects if o.get("id") == obj_id), None)
            if not obj or obj_id not in self.waveform_data:
                continue
            
            obj_name = obj.get("name")
            obj_scale = obj.get("scale", "")
            params = self.waveform_data[obj_id]
            
            # Create waveform based on parameters and settings
            frequency = params["base_frequency"] * params["frequency_modifier"] * frequency_factor
            amplitude = params["amplitude"] * amplitude_factor
            phase = params["phase_shift"]
            
            # Generate waveform based on type
            if wave_type == "sine":
                y = amplitude * np.sin(2 * np.pi * frequency * t + phase)
                
                # Add harmonic content for complexity
                for harmonic in params["harmonic_content"]:
                    h_freq = frequency * harmonic["harmonic"]
                    h_amp = amplitude * harmonic["amplitude"]
                    h_phase = phase + harmonic["phase"]
                    y += h_amp * np.sin(2 * np.pi * h_freq * t + h_phase)
                    
            elif wave_type == "square":
                y = amplitude * np.sign(np.sin(2 * np.pi * frequency * t + phase))
            elif wave_type == "triangle":
                y = amplitude * (2/np.pi) * np.arcsin(np.sin(2 * np.pi * frequency * t + phase))
            elif wave_type == "sawtooth":
                y = amplitude * ((t * frequency + phase/(2*np.pi)) % 1) * 2 - 1
            elif wave_type == "noise":
                # Generate pseudo-random noise with periodicity
                np.random.seed(hash(obj_id))
                base = np.sin(2 * np.pi * frequency * t + phase)
                noise = np.random.normal(0, 0.5, len(t))
                filtered_noise = np.convolve(noise, np.ones(10)/10, mode='same')
                y = amplitude * (base * 0.7 + filtered_noise * 0.3)
            
            # Add waveform to list
            waveforms.append({
                "obj_id": obj_id,
                "name": obj_name,
                "scale": obj_scale,
                "y": y,
                "amplitude": amplitude,
                "frequency": frequency
            })
        
        # Normalize amplitudes if requested
        if normalize and waveforms:
            # Find maximum amplitude
            max_amp = max([np.max(np.abs(w["y"])) for w in waveforms])
            
            if max_amp > 0:
                # Normalize all waveforms
                for w in waveforms:
                    w["y"] = w["y"] / max_amp
        
        # Plot waveforms
        for waveform in waveforms:
            # Get color for this scale
            color = scale_colors.get(waveform["scale"], (128, 128, 128))
            
            # Convert to Qt color
            qt_color = QColor(*color)
            
            # Create curve name with scale and frequency info
            display_name = f"{waveform['scale'].capitalize()}: {waveform['name']} (f={waveform['frequency']:.2f})"
            
            # Create plot line
            pen = pg.mkPen(color=qt_color, width=2)
            plot_line = self.plot_widget.plot(t, waveform["y"], name=display_name, pen=pen)
            
            # Store reference
            self.plot_lines[waveform["obj_id"]] = plot_line
    
    def on_selection_changed(self):
        """Handle selection change in the object list."""
        # Get selected items
        selected_items = self.object_list.selectedItems()
        
        # Limit selection to max_objects
        if len(selected_items) > self.max_objects:
            # Deselect the last selected item
            current_item = self.object_list.currentItem()
            if current_item:
                current_item.setSelected(False)
            return
        
        # Update selected objects
        self.selected_objects = [
            item.data(Qt.UserRole) for item in selected_items
        ]
        
        # Update waveforms
        self.update_waveforms()
    
    def toggle_animation(self, state):
        """Toggle animation on/off."""
        self.animation_running = state
        
        if state:
            self.timer.start(self.animation_speed)
        else:
            self.timer.stop()
    
    def update_animation(self):
        """Update animation frame."""
        # Increment animation frame
        self.animation_frame += 1
        
        # Skip if no waveforms are displayed
        if not self.selected_objects or not self.plot_lines:
            return
        
        # Get current settings
        frequency_factor = self.freq_slider.value() / 20.0
        amplitude_factor = self.amp_slider.value() / 50.0
        wave_type = self.wave_type_combo.currentData()
        normalize = self.normalize_check.isChecked()
        
        # Time array with shifting window for scrolling effect
        t_offset = (self.animation_frame / 100) % 10
        t = np.linspace(t_offset, t_offset + 10, 1000)
        
        # Update waveforms
        waveforms = []
        
        for obj_id in self.selected_objects:
            if obj_id not in self.waveform_data or obj_id not in self.plot_lines:
                continue
                
            obj = next((o for o in self.objects if o.get("id") == obj_id), None)
            if not obj:
                continue
                
            params = self.waveform_data[obj_id]
            
            # Create waveform based on parameters and settings
            frequency = params["base_frequency"] * params["frequency_modifier"] * frequency_factor
            amplitude = params["amplitude"] * amplitude_factor
            phase = params["phase_shift"]
            
            # Generate waveform based on type
            if wave_type == "sine":
                y = amplitude * np.sin(2 * np.pi * frequency * t + phase)
                
                # Add harmonic content for complexity
                for harmonic in params["harmonic_content"]:
                    h_freq = frequency * harmonic["harmonic"]
                    h_amp = amplitude * harmonic["amplitude"]
                    h_phase = phase + harmonic["phase"]
                    y += h_amp * np.sin(2 * np.pi * h_freq * t + h_phase)
                    
            elif wave_type == "square":
                y = amplitude * np.sign(np.sin(2 * np.pi * frequency * t + phase))
            elif wave_type == "triangle":
                y = amplitude * (2/np.pi) * np.arcsin(np.sin(2 * np.pi * frequency * t + phase))
            elif wave_type == "sawtooth":
                y = amplitude * ((t * frequency + phase/(2*np.pi)) % 1) * 2 - 1
            elif wave_type == "noise":
                # Generate pseudo-random noise with periodicity
                np.random.seed(hash(obj_id) + self.animation_frame // 10)
                base = np.sin(2 * np.pi * frequency * t + phase)
                noise = np.random.normal(0, 0.5, len(t))
                filtered_noise = np.convolve(noise, np.ones(10)/10, mode='same')
                y = amplitude * (base * 0.7 + filtered_noise * 0.3)
            
            # Add to waveforms list
            waveforms.append({
                "obj_id": obj_id,
                "y": y,
                "amplitude": amplitude
            })
        
        # Normalize amplitudes if requested
        if normalize and waveforms:
            # Find maximum amplitude
            max_amp = max([np.max(np.abs(w["y"])) for w in waveforms])
            
            if max_amp > 0:
                # Normalize all waveforms
                for w in waveforms:
                    w["y"] = w["y"] / max_amp
        
        # Update plot lines
        for waveform in waveforms:
            obj_id = waveform["obj_id"]
            if obj_id in self.plot_lines:
                t_display = np.linspace(0, 10, 1000)  # Fixed x-axis for display
                self.plot_lines[obj_id].setData(t_display, waveform["y"])
    
    def take_screenshot(self):
        """Take a screenshot of the current waveform view."""
        return self.grab()
    
    def select_objects_by_ids(self, object_ids):
        """Select objects by their IDs."""
        # Deselect all
        for i in range(self.object_list.count()):
            self.object_list.item(i).setSelected(False)
        
        # Select specified objects
        for i in range(self.object_list.count()):
            item = self.object_list.item(i)
            if item.data(Qt.UserRole) in object_ids:
                item.setSelected(True)