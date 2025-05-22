from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QComboBox, QSlider, QPushButton, 
                           QCheckBox, QGraphicsView, QGraphicsScene)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QPen, QBrush, QFont, QPixmap

import numpy as np
import random
import math

class NetGraphView(QWidget):
    """
    Network Graph visualization component that shows connections 
    between objects across different scales based on periodicity properties.
    """
    
    def __init__(self):
        super().__init__()
        self.objects = []
        self.nodes = {}  # Dictionary to store node positions
        self.edges = []  # List to store edges
        self.highlighted_nodes = set()  # Set of highlighted node IDs
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.animation_speed = 50  # ms
        self.animation_running = False
        self.animation_frame = 0
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components."""
        self.layout = QVBoxLayout(self)
        
        # Controls for the network graph
        controls_layout = QHBoxLayout()
        
        # Scale filter selector
        self.scale_label = QLabel("Skala:")
        self.scale_combo = QComboBox()
        self.scale_combo.addItem("Wszystkie", "all")
        # Skale będą dodane po załadowaniu danych
        self.scale_combo.currentIndexChanged.connect(self.on_scale_changed)
        
        # Property selector for defining connections
        self.property_label = QLabel("Właściwość:")
        self.property_combo = QComboBox()
        self.property_combo.addItem("Periodyczność", "periodicity")
        self.property_combo.addItem("Energia", "energy")
        self.property_combo.addItem("Masa", "mass")
        self.property_combo.currentIndexChanged.connect(self.on_property_changed)
        
        # Connection threshold slider
        self.threshold_label = QLabel("Próg powiązania:")
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setMinimum(1)
        self.threshold_slider.setMaximum(10)
        self.threshold_slider.setValue(5)
        self.threshold_slider.setTickPosition(QSlider.TicksBelow)
        self.threshold_slider.valueChanged.connect(self.on_threshold_changed)
        
        # Animation controls
        self.animate_check = QCheckBox("Animacja")
        self.animate_check.setChecked(False)
        self.animate_check.toggled.connect(self.toggle_animation)
        
        # Screenshot button
        self.screenshot_btn = QPushButton("Zrzut ekranu")
        self.screenshot_btn.clicked.connect(self.take_screenshot)
        
        # Add all controls to the layout
        controls_layout.addWidget(self.scale_label)
        controls_layout.addWidget(self.scale_combo)
        controls_layout.addWidget(self.property_label)
        controls_layout.addWidget(self.property_combo)
        controls_layout.addWidget(self.threshold_label)
        controls_layout.addWidget(self.threshold_slider)
        controls_layout.addWidget(self.animate_check)
        controls_layout.addWidget(self.screenshot_btn)
        
        self.layout.addLayout(controls_layout)
        
        # Graphics view for the network visualization
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(self.view.Antialiasing)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setInteractive(True)
        self.layout.addWidget(self.view)
        
        # Network legend
        legend_layout = QHBoxLayout()
        
        # Node legend
        node_legend = QLabel("Węzły: kolor według skali, rozmiar według znaczenia w sieci")
        
        # Edge legend
        edge_legend = QLabel("Krawędzie: grubość według siły powiązania")
        
        legend_layout.addWidget(node_legend)
        legend_layout.addWidget(edge_legend)
        
        self.layout.addLayout(legend_layout)
    
    def set_data(self, objects):
        """Set the dataset and initialize graph."""
        self.objects = objects
        
        # Extract unique scales
        scales = set()
        for obj in objects:
            scale = obj.get("scale", "")
            if scale:
                scales.add(scale)
        
        # Update scale combo
        self.scale_combo.clear()
        self.scale_combo.addItem("Wszystkie", "all")
        for scale in sorted(scales):
            self.scale_combo.addItem(scale, scale)
        
        # Generate initial graph
        self.generate_graph()
    
    def generate_graph(self):
        """Generate the network graph based on current settings."""
        # Clear previous graph
        self.scene.clear()
        self.nodes = {}
        self.edges = []
        
        # Get current settings
        selected_scale = self.scale_combo.currentData()
        selected_property = self.property_combo.currentData()
        threshold = self.threshold_slider.value() / 10.0  # Normalize to 0.1-1.0
        
        # Filter objects by scale if needed
        filtered_objects = self.objects
        if selected_scale != "all":
            filtered_objects = [obj for obj in self.objects if obj.get("scale") == selected_scale]
        
        if not filtered_objects:
            return
        
        # Calculate node positions using force-directed layout
        self.calculate_node_positions(filtered_objects)
        
        # Draw nodes
        self.draw_nodes(filtered_objects)
        
        # Calculate and draw edges based on property and threshold
        self.calculate_edges(filtered_objects, selected_property, threshold)
        self.draw_edges()
        
        # Fit graph in view
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
    
    def calculate_node_positions(self, objects):
        """Calculate node positions using a simple force-directed layout."""
        # Initialize random positions
        width, height = 800, 600
        center_x, center_y = width/2, height/2
        
        # Group nodes by scale for better visualization
        scales = {}
        for obj in objects:
            scale = obj.get("scale", "unknown")
            if scale not in scales:
                scales[scale] = []
            scales[scale].append(obj)
        
        # Position nodes in circular groups by scale
        radius = min(width, height) * 0.4
        scale_count = len(scales)
        scale_idx = 0
        
        for scale, scale_objects in scales.items():
            # Calculate position for this scale's cluster
            angle = (2 * math.pi * scale_idx) / scale_count
            scale_x = center_x + radius * math.cos(angle)
            scale_y = center_y + radius * math.sin(angle)
            
            # Position nodes within this scale's cluster
            obj_count = len(scale_objects)
            cluster_radius = min(50, 100 * (obj_count / 10))  # Adjust cluster size
            
            for i, obj in enumerate(scale_objects):
                obj_angle = (2 * math.pi * i) / max(1, obj_count)
                obj_x = scale_x + cluster_radius * math.cos(obj_angle)
                obj_y = scale_y + cluster_radius * math.sin(obj_angle)
                
                # Store node position
                self.nodes[obj.get("id")] = {
                    "x": obj_x,
                    "y": obj_y,
                    "scale": scale,
                    "name": obj.get("name", "Unknown"),
                    "importance": self.calculate_node_importance(obj)
                }
            
            scale_idx += 1
    
    def calculate_node_importance(self, obj):
        """Calculate node importance based on data properties."""
        # Default importance
        importance = 1.0
        
        # Check for periodicity-related fields which increase importance
        periodicity_fields = ["period", "frequency", "orbital_period", "rotation_period", 
                            "oscillation_period", "cycle_duration", "rotation_velocity"]
        
        data = obj.get("data", {})
        
        # Increase importance for each periodicity field
        for field in periodicity_fields:
            if field in data:
                importance += 0.5
        
        # Normalize importance
        return min(3.0, importance)
    
    def draw_nodes(self, objects):
        """Draw nodes on the scene."""
        # Define colors for different scales
        scale_colors = {
            "quantum": QColor(255, 0, 255),      # Magenta
            "atomic": QColor(128, 0, 255),       # Purple
            "molecular": QColor(0, 0, 255),      # Blue
            "cellular": QColor(0, 255, 255),     # Cyan
            "human": QColor(0, 255, 0),          # Green
            "planetary": QColor(255, 255, 0),    # Yellow
            "stellar": QColor(255, 128, 0),      # Orange
            "galactic": QColor(255, 0, 0),       # Red
            "cosmic": QColor(128, 0, 0)          # Dark red
        }
        
        # Default color
        default_color = QColor(128, 128, 128)    # Gray
        
        # Add nodes
        for obj in objects:
            obj_id = obj.get("id")
            if obj_id not in self.nodes:
                continue
            
            node = self.nodes[obj_id]
            scale = node["scale"]
            
            # Set node color
            color = scale_colors.get(scale, default_color)
            
            # Set node size based on importance
            size = 10 + (node["importance"] * 5)
            
            # Create node circle
            ellipse = self.scene.addEllipse(
                node["x"] - size/2, 
                node["y"] - size/2,
                size, size,
                QPen(color.darker()),
                QBrush(color)
            )
            
            # Add node label
            text = self.scene.addText(node["name"])
            text.setDefaultTextColor(Qt.white if scale in ["quantum", "atomic", "molecular", "galactic", "cosmic"] 
                                  else Qt.black)
            font = QFont()
            font.setPointSize(8)
            text.setFont(font)
            
            # Center text below node
            text_width = text.boundingRect().width()
            text.setPos(node["x"] - text_width/2, node["y"] + size/2 + 2)
            
            # Store references for animation
            node["ellipse"] = ellipse
            node["text"] = text
    
    def calculate_edges(self, objects, property_type, threshold):
        """Calculate edges between nodes based on property similarity."""
        self.edges = []
        
        # Property mapping functions
        property_fields = {
            "periodicity": ["period", "frequency", "orbital_period", "rotation_period", 
                          "oscillation_period", "cycle_duration", "peak_frequency", 
                          "rotation_curve_flat_velocity", "rotation_velocity"],
            "energy": ["energy", "luminosity", "first_ionization_energy", "electron_affinity"],
            "mass": ["mass", "stellar_mass", "rest_mass"]
        }
        
        # Calculate similarity for all pairs of objects
        for i, obj1 in enumerate(objects):
            for j, obj2 in enumerate(objects[i+1:], i+1):
                obj1_id = obj1.get("id")
                obj2_id = obj2.get("id")
                
                # Skip if either node doesn't exist
                if obj1_id not in self.nodes or obj2_id not in self.nodes:
                    continue
                
                # Calculate similarity based on property
                similarity = self.calculate_property_similarity(
                    obj1, obj2, property_fields.get(property_type, [])
                )
                
                # Add edge if similarity is above threshold
                if similarity >= threshold:
                    self.edges.append({
                        "source": obj1_id,
                        "target": obj2_id,
                        "weight": similarity,
                        "property": property_type
                    })
    
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
                return 0.2
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
    
    def draw_edges(self):
        """Draw edges between nodes."""
        for edge in self.edges:
            source_id = edge["source"]
            target_id = edge["target"]
            weight = edge["weight"]
            
            # Skip if either node is missing
            if source_id not in self.nodes or target_id not in self.nodes:
                continue
            
            source = self.nodes[source_id]
            target = self.nodes[target_id]
            
            # Set edge style based on weight
            pen_width = 1 + (weight * 4)  # Scale from 1-5 px
            
            # Color based on property type
            if edge["property"] == "periodicity":
                pen_color = QColor(0, 100, 255)  # Blue for periodicity
            elif edge["property"] == "energy":
                pen_color = QColor(255, 100, 0)  # Orange for energy
            else:
                pen_color = QColor(0, 200, 0)    # Green for mass
            
            pen = QPen(pen_color)
            pen.setWidth(int(pen_width))
            
            # Draw edge
            line = self.scene.addLine(
                source["x"], source["y"],
                target["x"], target["y"],
                pen
            )
            
            # Store edge reference
            edge["line"] = line
    
    def on_scale_changed(self, index):
        """Handle scale selection change."""
        self.generate_graph()
    
    def on_property_changed(self, index):
        """Handle property selection change."""
        self.generate_graph()
    
    def on_threshold_changed(self, value):
        """Handle threshold slider change."""
        self.generate_graph()
    
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
        
        # Create pulsing effect for nodes
        for node_id, node in self.nodes.items():
            if "ellipse" in node:
                # Calculate pulse factor
                pulse = 1.0 + 0.2 * math.sin(0.1 * self.animation_frame + hash(node_id) % 10)
                
                # Get base size from importance
                base_size = 10 + (node["importance"] * 5)
                size = base_size * pulse
                
                # Update ellipse size
                ellipse = node["ellipse"]
                ellipse.setRect(
                    node["x"] - size/2, 
                    node["y"] - size/2,
                    size, size
                )
        
        # Create moving effect for edges
        for edge in self.edges:
            if "line" in edge:
                line = edge["line"]
                
                # Get edge nodes
                source_id = edge["source"]
                target_id = edge["target"]
                
                if source_id in self.nodes and target_id in self.nodes:
                    source = self.nodes[source_id]
                    target = self.nodes[target_id]
                    
                    # Create subtle vibration effect
                    offset_x = 2 * math.sin(0.1 * self.animation_frame + hash(source_id + target_id) % 10)
                    offset_y = 2 * math.cos(0.1 * self.animation_frame + hash(source_id + target_id) % 7)
                    
                    # Update line position with small offset
                    line.setLine(
                        source["x"] + offset_x, source["y"] + offset_y,
                        target["x"] - offset_x, target["y"] - offset_y
                    )
    
    def take_screenshot(self):
        """Take a screenshot of the current graph view."""
        return self.grab()
    
    def highlight_similar_objects(self, similar_objects):
        """Highlight nodes for objects that are similar to the selected one."""
        # Clear previous highlights
        self.highlighted_nodes = set()
        
        # Add new highlights
        for obj in similar_objects:
            obj_id = obj.get("id")
            if obj_id in self.nodes:
                self.highlighted_nodes.add(obj_id)
        
        # Update node appearance
        for node_id, node in self.nodes.items():
            if "ellipse" in node:
                ellipse = node["ellipse"]
                
                if node_id in self.highlighted_nodes:
                    # Highlight node with glow effect
                    pen = QPen(Qt.yellow)
                    pen.setWidth(3)
                    ellipse.setPen(pen)
                else:
                    # Reset to normal appearance
                    scale = node["scale"]
                    color = self.get_scale_color(scale)
                    ellipse.setPen(QPen(color.darker()))
    
    def get_scale_color(self, scale):
        """Get color for a scale."""
        scale_colors = {
            "quantum": QColor(255, 0, 255),      # Magenta
            "atomic": QColor(128, 0, 255),       # Purple
            "molecular": QColor(0, 0, 255),      # Blue
            "cellular": QColor(0, 255, 255),     # Cyan
            "human": QColor(0, 255, 0),          # Green
            "planetary": QColor(255, 255, 0),    # Yellow
            "stellar": QColor(255, 128, 0),      # Orange
            "galactic": QColor(255, 0, 0),       # Red
            "cosmic": QColor(128, 0, 0)          # Dark red
        }
        
        return scale_colors.get(scale, QColor(128, 128, 128))