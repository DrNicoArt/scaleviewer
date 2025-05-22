from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QComboBox, QSlider, QPushButton, 
                           QGraphicsView, QGraphicsScene, QGraphicsRectItem)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QRectF
from PyQt5.QtGui import QColor, QBrush, QPen, QFont, QPixmap

import numpy as np
import pyqtgraph as pg
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.cm as cm
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import io

class HeatmapView(QWidget):
    """
    Heatmap visualization component for showing correlations 
    of periodicity across different scales and objects.
    """
    
    def __init__(self):
        super().__init__()
        self.objects = []
        self.correlation_data = None
        self.selected_property = "periodicity"
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.animation_speed = 100  # ms
        self.animation_running = False
        self.animation_frame = 0
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components."""
        self.layout = QVBoxLayout(self)
        
        # Controls for the heatmap
        controls_layout = QHBoxLayout()
        
        # Property selector
        self.property_label = QLabel("Właściwość:")
        self.property_combo = QComboBox()
        self.property_combo.addItem("Periodyczność", "periodicity")
        self.property_combo.addItem("Energia", "energy")
        self.property_combo.addItem("Masa", "mass")
        self.property_combo.currentIndexChanged.connect(self.on_property_changed)
        
        # Color scale selector
        self.colormap_label = QLabel("Skala kolorów:")
        self.colormap_combo = QComboBox()
        self.colormap_combo.addItem("Viridis", "viridis")
        self.colormap_combo.addItem("Plasma", "plasma")
        self.colormap_combo.addItem("Inferno", "inferno")
        self.colormap_combo.addItem("Tęczowa", "rainbow")
        self.colormap_combo.currentIndexChanged.connect(self.on_colormap_changed)
        
        # Animation toggle
        self.animate_btn = QPushButton("Animacja")
        self.animate_btn.setCheckable(True)
        self.animate_btn.toggled.connect(self.toggle_animation)
        
        # Screenshot button
        self.screenshot_btn = QPushButton("Zrzut ekranu")
        self.screenshot_btn.clicked.connect(self.take_screenshot)
        
        # Add controls to layout
        controls_layout.addWidget(self.property_label)
        controls_layout.addWidget(self.property_combo)
        controls_layout.addWidget(self.colormap_label)
        controls_layout.addWidget(self.colormap_combo)
        controls_layout.addWidget(self.animate_btn)
        controls_layout.addWidget(self.screenshot_btn)
        
        self.layout.addLayout(controls_layout)
        
        # Figure for matplotlib heatmap
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        
        # Description label
        self.description = QLabel(
            "Heatmapa przedstawia korelację właściwości periodycznych między obiektami różnych skal. "
            "Ciemniejsze kolory oznaczają silniejszą korelację."
        )
        self.description.setWordWrap(True)
        self.layout.addWidget(self.description)
    
    def set_data(self, objects):
        """Set the dataset and generate initial heatmap."""
        self.objects = objects
        self.calculate_correlation_matrix()
        self.update_heatmap()
    
    def calculate_correlation_matrix(self):
        """Calculate the correlation matrix between objects based on selected property."""
        if not self.objects:
            return
        
        # Get property fields based on selection
        property_fields = self.get_property_fields(self.selected_property)
        
        # Get all object IDs and scales
        object_ids = [obj.get("id") for obj in self.objects]
        object_names = [obj.get("name") for obj in self.objects]
        object_scales = [obj.get("scale") for obj in self.objects]
        
        # Create empty correlation matrix
        n_objects = len(self.objects)
        correlation_matrix = np.zeros((n_objects, n_objects))
        
        # Calculate correlations between all pairs of objects
        for i, obj1 in enumerate(self.objects):
            correlation_matrix[i, i] = 1.0  # Perfect correlation with self
            
            for j in range(i+1, n_objects):
                obj2 = self.objects[j]
                
                # Calculate property similarity
                similarity = self.calculate_property_similarity(obj1, obj2, property_fields)
                
                # Set symmetric correlation values
                correlation_matrix[i, j] = similarity
                correlation_matrix[j, i] = similarity
        
        # Store correlation data
        self.correlation_data = {
            "matrix": correlation_matrix,
            "object_ids": object_ids,
            "object_names": object_names,
            "object_scales": object_scales
        }
    
    def get_property_fields(self, property_type):
        """Get list of fields relevant to the selected property."""
        property_fields = {
            "periodicity": [
                "period", "frequency", "orbital_period", "rotation_period", 
                "oscillation_period", "cycle_duration", "peak_frequency", 
                "rotation_curve_flat_velocity", "rotation_velocity",
                "angular_velocity"
            ],
            "energy": [
                "energy", "luminosity", "first_ionization_energy", 
                "electron_affinity", "mean_temperature", "critical_density"
            ],
            "mass": [
                "mass", "stellar_mass", "rest_mass", "density", 
                "molecular_weight", "atomic_radius"
            ]
        }
        
        return property_fields.get(property_type, [])
    
    def calculate_property_similarity(self, obj1, obj2, property_fields):
        """Calculate similarity between two objects based on specific properties."""
        # Get data
        data1 = obj1.get("data", {})
        data2 = obj2.get("data", {})
        
        # Find matching properties
        matching_props = []
        
        for field in property_fields:
            if field in data1 and field in data2:
                matching_props.append(field)
                
        # If no matching properties, try to find properties with similar meanings
        if not matching_props:
            for field1, value1 in data1.items():
                for field2, value2 in data2.items():
                    # Check if fields are semantically similar
                    if any(term in field1.lower() and term in field2.lower() 
                           for term in ["period", "frequency", "mass", "energy", "time", "cycle"]):
                        matching_props.append((field1, field2))
                        break
        
        # If still no matches, check if any fields contain similar substrings
        if not matching_props:
            for field1, value1 in data1.items():
                for field2, value2 in data2.items():
                    if (field1[:5] == field2[:5] and len(field1) > 4) or field1 == field2:
                        matching_props.append((field1, field2))
                        break
        
        # If no matching properties, return minimum similarity
        if not matching_props:
            # Give a minimal base similarity for objects of the same scale
            if obj1.get("scale") == obj2.get("scale"):
                return 0.3
            return 0.1
        
        # Calculate similarity score
        similarity = 0.0
        
        # Handle exact field matches
        for field in matching_props:
            if isinstance(field, str):
                value1 = self.extract_numeric_value(data1.get(field))
                value2 = self.extract_numeric_value(data2.get(field))
                
                if value1 is not None and value2 is not None:
                    # Calculate normalized similarity between values
                    max_val = max(value1, value2)
                    min_val = min(value1, value2)
                    if max_val > 0:
                        ratio = min_val / max_val
                        similarity += ratio * 0.5  # Weight for exact field match
            else:
                # Handle field pairs that are semantically similar
                field1, field2 = field
                value1 = self.extract_numeric_value(data1.get(field1))
                value2 = self.extract_numeric_value(data2.get(field2))
                
                if value1 is not None and value2 is not None:
                    # Calculate normalized similarity between values
                    max_val = max(value1, value2)
                    min_val = min(value1, value2)
                    if max_val > 0:
                        ratio = min_val / max_val
                        similarity += ratio * 0.3  # Lower weight for semantic matches
        
        # Bonus for same scale
        if obj1.get("scale") == obj2.get("scale"):
            similarity += 0.3
        
        # Normalize and clamp to [0,1]
        return min(1.0, similarity)
    
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
    
    def update_heatmap(self):
        """Update the heatmap visualization."""
        if self.correlation_data is None:
            return
        
        # Clear previous plot
        self.figure.clear()
        
        # Get correlation data
        matrix = self.correlation_data["matrix"]
        object_names = self.correlation_data["object_names"]
        object_scales = self.correlation_data["object_scales"]
        
        # Create axis
        ax = self.figure.add_subplot(111)
        
        # Get colormap
        cmap_name = self.colormap_combo.currentData()
        cmap = plt.get_cmap(cmap_name)
        
        # Create custom labels with scale prefix
        labels = [f"{scale.capitalize()}: {name}" for name, scale in zip(object_names, object_scales)]
        
        # Plot heatmap
        im = ax.imshow(matrix, cmap=cmap, interpolation='nearest')
        
        # Add colorbar
        cbar = self.figure.colorbar(im, ax=ax)
        cbar.set_label('Korelacja')
        
        # Set ticks and labels
        ax.set_xticks(np.arange(len(labels)))
        ax.set_yticks(np.arange(len(labels)))
        ax.set_xticklabels(labels, rotation=90, fontsize=8)
        ax.set_yticklabels(labels, fontsize=8)
        
        # Loop over data and create text annotations
        for i in range(len(object_names)):
            for j in range(len(object_names)):
                # Only show correlation values above threshold to reduce clutter
                if matrix[i, j] >= 0.5:
                    text_color = "white" if matrix[i, j] > 0.7 else "black"
                    ax.text(j, i, f"{matrix[i, j]:.2f}",
                           ha="center", va="center", color=text_color, fontsize=7)
        
        # Set title
        property_title = {
            "periodicity": "Periodyczność",
            "energy": "Energia",
            "mass": "Masa"
        }.get(self.selected_property, "Właściwość")
        
        ax.set_title(f"Korelacja: {property_title}")
        
        # Adjust layout and render
        self.figure.tight_layout()
        self.canvas.draw()
    
    def on_property_changed(self, index):
        """Handle property selection change."""
        self.selected_property = self.property_combo.currentData()
        self.calculate_correlation_matrix()
        self.update_heatmap()
    
    def on_colormap_changed(self, index):
        """Handle colormap selection change."""
        self.update_heatmap()
    
    def toggle_animation(self, state):
        """Toggle animation on/off."""
        self.animation_running = state
        
        if state:
            self.timer.start(self.animation_speed)
        else:
            self.timer.stop()
    
    def update_animation(self):
        """Update animation frame with morphing patterns."""
        if self.correlation_data is None:
            return
        
        # Get the current correlation matrix
        matrix = self.correlation_data["matrix"].copy()
        
        # Create time-varying animation effect
        t = self.animation_frame * 0.05
        
        # Apply wave effect to matrix values (preserving diagonal)
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                if i != j:  # Don't modify self-correlation (diagonal)
                    # Add subtle sinusoidal variation
                    phase_offset = 0.2 * ((i+1) * (j+1) % 5)  # Creates different patterns
                    variation = 0.15 * np.sin(t + phase_offset)
                    matrix[i, j] = np.clip(matrix[i, j] + variation, 0.0, 1.0)
        
        # Update the figure with the animated matrix
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Get colormap
        cmap_name = self.colormap_combo.currentData()
        cmap = plt.get_cmap(cmap_name)
        
        # Create custom labels with scale prefix
        object_names = self.correlation_data["object_names"]
        object_scales = self.correlation_data["object_scales"]
        labels = [f"{scale.capitalize()}: {name}" for name, scale in zip(object_names, object_scales)]
        
        # Plot heatmap
        im = ax.imshow(matrix, cmap=cmap, interpolation='nearest')
        
        # Add colorbar
        cbar = self.figure.colorbar(im, ax=ax)
        cbar.set_label('Korelacja (Animowana)')
        
        # Set ticks and labels
        ax.set_xticks(np.arange(len(labels)))
        ax.set_yticks(np.arange(len(labels)))
        ax.set_xticklabels(labels, rotation=90, fontsize=8)
        ax.set_yticklabels(labels, fontsize=8)
        
        # Loop over data and create text annotations for stronger correlations
        for i in range(len(object_names)):
            for j in range(len(object_names)):
                # Only show correlation values above threshold to reduce clutter
                if matrix[i, j] >= 0.5:
                    text_color = "white" if matrix[i, j] > 0.7 else "black"
                    ax.text(j, i, f"{matrix[i, j]:.2f}",
                           ha="center", va="center", color=text_color, fontsize=7)
        
        # Set title with animation indicator
        property_title = {
            "periodicity": "Periodyczność",
            "energy": "Energia",
            "mass": "Masa"
        }.get(self.selected_property, "Właściwość")
        
        ax.set_title(f"Korelacja: {property_title} (Animacja)")
        
        # Adjust layout and render
        self.figure.tight_layout()
        self.canvas.draw()
        
        # Increment frame counter
        self.animation_frame += 1
    
    def take_screenshot(self):
        """Take a screenshot of the current heatmap view."""
        return self.grab()
    
    def highlight_objects(self, object_ids):
        """Highlight specific objects in the heatmap."""
        if self.correlation_data is None or not object_ids:
            return
        
        # Get indices of the objects to highlight
        all_ids = self.correlation_data["object_ids"]
        indices = [all_ids.index(obj_id) for obj_id in object_ids if obj_id in all_ids]
        
        if not indices:
            return
        
        # Redraw heatmap with highlighted rows/columns
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Get data
        matrix = self.correlation_data["matrix"]
        object_names = self.correlation_data["object_names"]
        object_scales = self.correlation_data["object_scales"]
        
        # Get colormap
        cmap_name = self.colormap_combo.currentData()
        cmap = plt.get_cmap(cmap_name)
        
        # Create custom labels with scale prefix
        labels = [f"{scale.capitalize()}: {name}" for name, scale in zip(object_names, object_scales)]
        
        # Plot heatmap
        im = ax.imshow(matrix, cmap=cmap, interpolation='nearest')
        
        # Add colorbar
        cbar = self.figure.colorbar(im, ax=ax)
        cbar.set_label('Korelacja')
        
        # Set ticks and labels
        ax.set_xticks(np.arange(len(labels)))
        ax.set_yticks(np.arange(len(labels)))
        ax.set_xticklabels(labels, rotation=90, fontsize=8)
        ax.set_yticklabels(labels, fontsize=8)
        
        # Highlight selected rows and columns
        for idx in indices:
            # Highlight row
            ax.axhline(y=idx, color='yellow', linewidth=2, alpha=0.5)
            # Highlight column
            ax.axvline(x=idx, color='yellow', linewidth=2, alpha=0.5)
        
        # Loop over data and create text annotations
        for i in range(len(object_names)):
            for j in range(len(object_names)):
                # Only show correlation values above threshold to reduce clutter
                if matrix[i, j] >= 0.5 or (i in indices and j in indices):
                    text_color = "white" if matrix[i, j] > 0.7 else "black"
                    ax.text(j, i, f"{matrix[i, j]:.2f}",
                           ha="center", va="center", color=text_color, fontsize=7)
        
        # Set title
        property_title = {
            "periodicity": "Periodyczność",
            "energy": "Energia",
            "mass": "Masa"
        }.get(self.selected_property, "Właściwość")
        
        highlighted_names = [object_names[i] for i in indices]
        ax.set_title(f"Korelacja: {property_title} (wyróżniono: {', '.join(highlighted_names)})")
        
        # Adjust layout and render
        self.figure.tight_layout()
        self.canvas.draw()