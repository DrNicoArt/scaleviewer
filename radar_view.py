from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QComboBox, QLabel, QSlider, QCheckBox, QGroupBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap

import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class RadarView(QWidget):
    """
    Radar chart visualization component that can display 
    multi-dimensional data and animate comparisons.
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize variables
        self.objects_data = []
        self.current_object = None
        self.comparison_object = None
        self.playing = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.animation_speed = 50  # milliseconds
        self.animation_frame = 0
        self.max_frames = 20
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        
        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(5, 5), facecolor='#2a2a2a')
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111, polar=True)
        
        # Style the plot
        self.ax.set_facecolor('#2a2a2a')
        self.figure.patch.set_facecolor('#2a2a2a')
        self.ax.grid(color='gray', linestyle='-', linewidth=0.3, alpha=0.5)
        self.ax.tick_params(colors='white')
        
        # Create controls
        controls_layout = QHBoxLayout()
        
        # Play/Pause button
        self.play_button = QPushButton("Animate")
        self.play_button.clicked.connect(self.toggle_play)
        controls_layout.addWidget(self.play_button)
        
        # Compare with selector
        self.compare_label = QLabel("Compare with:")
        controls_layout.addWidget(self.compare_label)
        
        self.compare_selector = QComboBox()
        self.compare_selector.currentIndexChanged.connect(self.on_comparison_changed)
        controls_layout.addWidget(self.compare_selector, 1)  # 1 = stretch factor
        
        # Settings group box
        settings_group = QGroupBox("Radar Settings")
        settings_layout = QHBoxLayout(settings_group)
        
        # Fields selector
        self.fields_label = QLabel("Max Fields:")
        settings_layout.addWidget(self.fields_label)
        
        self.fields_slider = QSlider(Qt.Horizontal)
        self.fields_slider.setMinimum(3)
        self.fields_slider.setMaximum(10)
        self.fields_slider.setValue(5)
        self.fields_slider.valueChanged.connect(self.on_fields_changed)
        settings_layout.addWidget(self.fields_slider)
        
        self.fields_value = QLabel("5")
        settings_layout.addWidget(self.fields_value)
        
        # Fill area checkbox
        self.fill_check = QCheckBox("Fill Area")
        self.fill_check.setChecked(True)
        self.fill_check.stateChanged.connect(self.update_radar)
        settings_layout.addWidget(self.fill_check)
        
        # Add all widgets to main layout
        layout.addWidget(self.canvas)
        layout.addLayout(controls_layout)
        layout.addWidget(settings_group)
    
    def set_data(self, objects):
        """Set the dataset and update selectors."""
        self.objects_data = objects
        
        # Update compare selector
        self.compare_selector.clear()
        self.compare_selector.addItem("None")
        
        for obj in objects:
            self.compare_selector.addItem(f"{obj.get('name', '')} ({obj.get('scale', '')})")
    
    def select_object(self, obj_data):
        """Select an object to visualize."""
        self.current_object = obj_data
        self.update_radar()
    
    def on_comparison_changed(self, index):
        """Handle comparison object selection change."""
        if index == 0:  # "None" option
            self.comparison_object = None
        else:
            # Adjust index to account for the "None" option
            self.comparison_object = self.objects_data[index-1] if index-1 < len(self.objects_data) else None
        
        self.update_radar()
    
    def on_fields_changed(self, value):
        """Handle fields slider change."""
        self.fields_value.setText(str(value))
        self.update_radar()
    
    def update_radar(self):
        """Update the radar chart display."""
        if not self.current_object:
            return
        
        # Stop animation if playing
        if self.playing:
            self.toggle_play()
        
        # Clear the plot
        self.ax.clear()
        
        # Extract data fields to display
        obj_data = self.current_object.get("data", {})
        if not obj_data:
            return
        
        # Prepare data for radar chart
        fields, values, comp_values = self.prepare_radar_data(obj_data)
        
        # Draw the radar chart
        self.draw_radar_chart(fields, values, comp_values)
        
        # Update canvas
        self.canvas.draw()
    
    def prepare_radar_data(self, obj_data):
        """Prepare data for radar chart display."""
        # Get all numeric fields from the object data
        fields = []
        values = []
        
        # Determine if we need numeric conversion
        for key, value in obj_data.items():
            try:
                # Try to extract a numeric value from the string
                if isinstance(value, str):
                    # Simple extraction of first numeric part
                    numeric_str = ''.join(c for c in value if c.isdigit() or c == '.' or c == '-')
                    if numeric_str:
                        numeric_value = float(numeric_str)
                        fields.append(key)
                        values.append(numeric_value)
                else:
                    fields.append(key)
                    values.append(float(value))
            except:
                # Skip non-numeric fields
                pass
        
        # Limit to the max number of fields specified by the slider
        max_fields = self.fields_slider.value()
        if len(fields) > max_fields:
            fields = fields[:max_fields]
            values = values[:max_fields]
        
        # Get comparison values if a comparison object is selected
        comp_values = []
        if self.comparison_object:
            comp_data = self.comparison_object.get("data", {})
            
            for field in fields:
                try:
                    comp_value = comp_data.get(field, "0")
                    if isinstance(comp_value, str):
                        numeric_str = ''.join(c for c in comp_value if c.isdigit() or c == '.' or c == '-')
                        if numeric_str:
                            comp_values.append(float(numeric_str))
                        else:
                            comp_values.append(0)
                    else:
                        comp_values.append(float(comp_value))
                except:
                    comp_values.append(0)
        
        return fields, values, comp_values
    
    def draw_radar_chart(self, fields, values, comp_values):
        """Draw the radar chart with given data."""
        if not fields or not values:
            return
        
        # Number of variables
        num_vars = len(fields)
        
        # Ensure at least 3 points for polygon
        if num_vars < 3:
            # Pad with dummy fields
            dummy_count = 3 - num_vars
            fields.extend([f"Field {i+1}" for i in range(dummy_count)])
            values.extend([0] * dummy_count)
            if comp_values:
                comp_values.extend([0] * dummy_count)
            num_vars = len(fields)
        
        # Compute the angles for each variable
        angles = np.linspace(0, 2*np.pi, num_vars, endpoint=False).tolist()
        
        # Make the plot circular by repeating the first value
        values = values.copy()
        values.append(values[0])
        angles.append(angles[0])
        fields.append(fields[0])
        
        # Set up the plot
        self.ax.set_theta_offset(np.pi / 2)  # Start at top
        self.ax.set_theta_direction(-1)  # Go clockwise
        
        # Label each spoke
        self.ax.set_thetagrids(np.degrees(angles[:-1]), fields[:-1])
        
        # Normalize values for display
        max_value = max(values) if values else 1
        normalized_values = [v/max_value for v in values]
        
        # Draw the polygon
        self.ax.plot(angles, normalized_values, 'o-', linewidth=2, color='cyan')
        
        # Fill the area if checked
        if self.fill_check.isChecked():
            self.ax.fill(angles, normalized_values, alpha=0.25, color='cyan')
        
        # Draw comparison object if available
        if comp_values:
            comp_values = comp_values.copy()
            comp_values.append(comp_values[0])
            
            # Normalize comparison values
            comp_max = max(comp_values) if comp_values else 1
            norm_comp = [v/comp_max for v in comp_values]
            
            # Scale to match main object for comparison
            scale_factor = max_value / comp_max if comp_max > 0 else 1
            norm_comp = [v * scale_factor for v in norm_comp]
            
            # Draw comparison polygon
            self.ax.plot(angles, norm_comp, 'o-', linewidth=2, color='magenta')
            
            if self.fill_check.isChecked():
                self.ax.fill(angles, norm_comp, alpha=0.1, color='magenta')
        
        # Set chart title
        title = f"{self.current_object.get('name', '')}"
        if self.comparison_object:
            title += f" vs {self.comparison_object.get('name', '')}"
        self.ax.set_title(title, color='white', pad=20)
    
    def toggle_play(self):
        """Toggle animation play/pause state."""
        self.playing = not self.playing
        
        if self.playing:
            self.play_button.setText("Stop")
            self.animation_frame = 0
            self.timer.start(self.animation_speed)
        else:
            self.play_button.setText("Animate")
            self.timer.stop()
            self.update_radar()  # Revert to normal display
    
    def update_animation(self):
        """Update animation frame."""
        if not self.playing or not self.current_object:
            return
        
        # Increment animation frame
        self.animation_frame += 1
        
        # Reset if reached max frames
        if self.animation_frame > self.max_frames:
            self.animation_frame = 0
        
        # Update the visualization based on animation frame
        self.animate_radar_frame()
    
    def animate_radar_frame(self):
        """Update radar chart for current animation frame with zaawansowanymi efektami wizualnymi."""
        if not self.current_object:
            return
        
        # Clear the plot
        self.ax.clear()
        
        # Extract data for radar chart
        obj_data = self.current_object.get("data", {})
        if not obj_data:
            return
        
        # Prepare data for radar chart
        fields, values, comp_values = self.prepare_radar_data(obj_data)
        
        # Zaawansowane efekty animacji
        phase = self.animation_frame / self.max_frames * np.pi * 2
        
        # Indywidualne modulacje dla każdej wartości - dają efekt fali
        animated_values = []
        for i, v in enumerate(values):
            # Każda wartość ma nieco przesunięty efekt falowania
            field_phase = phase + (i / len(values)) * np.pi
            # Efekt pulsacji z modulacją indywidualną dla każdego pola
            pulse = 0.15 * np.sin(field_phase) + 0.1 * np.sin(field_phase * 2)
            animated_values.append(v * (1.0 + pulse))
        
        # Animacja dla obiektu porównawczego (w przeciwnej fazie)
        animated_comp = []
        if comp_values:
            comp_phase = phase + np.pi  # Przeciwna faza
            for i, v in enumerate(comp_values):
                field_comp_phase = comp_phase + (i / len(comp_values)) * np.pi
                comp_pulse = 0.15 * np.sin(field_comp_phase) + 0.1 * np.sin(field_comp_phase * 2)
                animated_comp.append(v * (1.0 + comp_pulse))
        
        # Prepare data for radar chart animation
        if not fields or not animated_values:
            return
        
        # Number of variables
        num_vars = len(fields)
        
        # Ensure at least 3 points for polygon
        if num_vars < 3:
            # Pad with dummy fields
            dummy_count = 3 - num_vars
            fields.extend([f"Pole {i+1}" for i in range(dummy_count)])
            animated_values.extend([0] * dummy_count)
            if animated_comp:
                animated_comp.extend([0] * dummy_count)
            num_vars = len(fields)
        
        # Compute the angles for each variable
        angles = np.linspace(0, 2*np.pi, num_vars, endpoint=False).tolist()
        
        # Make the plot circular by repeating the first value
        animated_values.append(animated_values[0])
        angles.append(angles[0])
        fields.append(fields[0])
        
        # Set up the plot
        self.ax.set_theta_offset(np.pi / 2)
        self.ax.set_theta_direction(-1)
        
        # Label each spoke with nieco mniejszą czcionką
        self.ax.set_thetagrids(np.degrees(angles[:-1]), fields[:-1], fontsize=9)
        
        # Normalize values for display
        max_value = max(animated_values) if animated_values else 1
        normalized_values = [v/max_value for v in animated_values]
        
        # Dynamicznie zmieniający się kolor głównego obiektu
        hue_main = (phase / (2*np.pi) * 60) % 30 + 180  # Zakres kolorów od niebieskiego do cyjanowego
        main_color = plt.cm.cool(hue_main/360)
        
        # Animowana grubość linii
        line_width = 2 + 0.5 * np.sin(phase * 2)
        
        # Rysuj główny obiekt
        self.ax.plot(angles, normalized_values, 'o-', linewidth=line_width, color=main_color)
        
        # Fill the area if checked, z pulsującą przezroczystością
        if self.fill_check.isChecked():
            fill_alpha = 0.25 + 0.1 * np.sin(phase * 3)
            self.ax.fill(angles, normalized_values, alpha=fill_alpha, color=main_color)
            
            # Dodaj efekt poświaty
            glow_values = [v * (1.03 + 0.02 * np.sin(phase * 4)) for v in normalized_values]
            self.ax.fill(angles, glow_values, alpha=fill_alpha * 0.4, color=main_color)
        
        # Draw comparison object if available
        if comp_values and animated_comp:
            animated_comp.append(animated_comp[0])  # Make circular
            
            # Normalize comparison values
            comp_max = max(animated_comp) if animated_comp else 1
            norm_comp = [v/comp_max for v in animated_comp]
            
            # Scale to match main object for comparison
            scale_factor = max_value / comp_max if comp_max > 0 else 1
            norm_comp = [v * scale_factor for v in norm_comp]
            
            # Kontrastowy kolor dla obiektu porównawczego
            hue_comp = (phase / (2*np.pi) * 60 + 180) % 360  # Przeciwna strona koła kolorów
            comp_color = plt.cm.hot(hue_comp/360)
            
            # Animowana grubość linii w przeciwnej fazie
            comp_width = 2 + 0.5 * np.sin(phase * 2 + np.pi)
            
            # Draw comparison polygon
            self.ax.plot(angles, norm_comp, 'o-', linewidth=comp_width, color=comp_color)
            
            if self.fill_check.isChecked():
                comp_alpha = 0.15 + 0.05 * np.sin(phase * 3 + np.pi)
                self.ax.fill(angles, norm_comp, alpha=comp_alpha, color=comp_color)
        
        # Set chart title with animation effect
        title = f"{self.current_object.get('name', '')}"
        if self.comparison_object:
            # Prosty efekt animacji w tytule
            pulse_char = "◊" if np.sin(phase * 4) > 0 else "◇"
            title += f" {pulse_char} {self.comparison_object.get('name', '')}"
        
        self.ax.set_title(title, color='white', pad=20, fontsize=11)
        
        # Dodaj subtelną adnotację wskazującą na animację
        phase_indicator = np.sin(phase * 8)  # Szybsza oscylacja
        indicator_char = "●" if phase_indicator > 0.7 else "○" if phase_indicator > 0 else "◌"
        self.ax.text(0.97, 0.03, indicator_char, transform=self.ax.transAxes, 
                   ha='right', va='bottom', fontsize=8, color='white', alpha=0.7)
        
        # Stwórz siatki z nieco bardziej przezroczystymi liniami
        self.ax.grid(True, color='gray', alpha=0.3, linestyle='-', linewidth=0.3)
        self.ax.spines['polar'].set_visible(False)
        
        # Update canvas
        self.canvas.draw()
    
    def take_screenshot(self):
        """Take a screenshot of the current radar view."""
        pixmap = QPixmap(self.size())
        self.render(pixmap)
        return pixmap
