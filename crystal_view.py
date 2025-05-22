from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QSlider, QLabel, QComboBox, QGraphicsView, QGraphicsScene,
                           QGroupBox, QCheckBox)
from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF, pyqtSignal
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter, QPixmap

import numpy as np
import math


class CrystalGraphicsView(QGraphicsView):
    """Custom QGraphicsView for crystal visualization."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setRenderHint(QPainter.TextAntialiasing)
        
        # Set dark background
        self.setBackgroundBrush(QBrush(QColor(28, 28, 28)))
        
        # Create scene
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Fit in view
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        
        # Enable wheel zoom
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        
        # Initial zoom
        self.zoom_factor = 1.0
        
        # Reset transformations
        self.resetTransform()
    
    def wheelEvent(self, event):
        """Handle wheel events for zooming."""
        # Calculate zoom factor
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        
        # Set anchor to mouse position
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        
        # Zoom
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        
        # Apply zoom
        self.scale(zoom_factor, zoom_factor)
        
        # Update current zoom
        self.zoom_factor *= zoom_factor


class CrystalView(QWidget):
    """
    Crystal View component for visualization of crystal structures
    with time-crystal animation based on Floquet theory.
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize variables
        self.current_object = None
        self.playing = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.animation_speed = 50  # milliseconds
        self.animation_frame = 0
        self.max_frames = 60
        self.phase = 0.0
        
        # Crystal parameters
        self.num_particles = 50
        self.crystal_type = "time_crystal"  # time_crystal, space_crystal, cubic, hexagonal
        self.particle_size = 10
        self.show_bonds = True
        self.color_by_energy = True
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        
        # Create graphics view for crystal visualization
        self.graphics_view = CrystalGraphicsView()
        
        # Create controls
        controls_layout = QHBoxLayout()
        
        # Play/Pause button
        self.play_button = QPushButton("Animate")
        self.play_button.clicked.connect(self.toggle_play)
        controls_layout.addWidget(self.play_button)
        
        # Reset view button
        self.reset_button = QPushButton("Reset View")
        self.reset_button.clicked.connect(self.reset_view)
        controls_layout.addWidget(self.reset_button)
        
        # Phase slider
        self.phase_label = QLabel("Phase:")
        controls_layout.addWidget(self.phase_label)
        
        self.phase_slider = QSlider(Qt.Horizontal)
        self.phase_slider.setMinimum(0)
        self.phase_slider.setMaximum(100)
        self.phase_slider.setValue(0)
        self.phase_slider.valueChanged.connect(self.on_phase_changed)
        controls_layout.addWidget(self.phase_slider, 1)  # 1 = stretch factor
        
        # Settings group box
        settings_group = QGroupBox("Crystal Settings")
        settings_layout = QHBoxLayout(settings_group)
        
        # Crystal type selector
        self.type_label = QLabel("Type:")
        settings_layout.addWidget(self.type_label)
        
        self.type_selector = QComboBox()
        self.type_selector.addItems(["Time Crystal", "Space Crystal", "Cubic", "Hexagonal"])
        self.type_selector.currentIndexChanged.connect(self.on_type_changed)
        settings_layout.addWidget(self.type_selector)
        
        # Particle count selector
        self.particles_label = QLabel("Particles:")
        settings_layout.addWidget(self.particles_label)
        
        self.particles_slider = QSlider(Qt.Horizontal)
        self.particles_slider.setMinimum(10)
        self.particles_slider.setMaximum(100)
        self.particles_slider.setValue(self.num_particles)
        self.particles_slider.valueChanged.connect(self.on_particles_changed)
        settings_layout.addWidget(self.particles_slider)
        
        self.particles_value = QLabel(str(self.num_particles))
        settings_layout.addWidget(self.particles_value)
        
        # Show bonds checkbox
        self.bonds_check = QCheckBox("Show Bonds")
        self.bonds_check.setChecked(self.show_bonds)
        self.bonds_check.stateChanged.connect(self.on_bonds_changed)
        settings_layout.addWidget(self.bonds_check)
        
        # Color by energy checkbox
        self.color_check = QCheckBox("Color by Energy")
        self.color_check.setChecked(self.color_by_energy)
        self.color_check.stateChanged.connect(self.on_color_changed)
        settings_layout.addWidget(self.color_check)
        
        # Add all widgets to main layout
        layout.addWidget(self.graphics_view)
        layout.addLayout(controls_layout)
        layout.addWidget(settings_group)
    
    def set_data(self, objects):
        """Store the dataset."""
        self.objects_data = objects
    
    def select_object(self, obj_data):
        """Select an object to visualize."""
        self.current_object = obj_data
        self.update_crystal()
    
    def update_crystal(self):
        """Update the crystal visualization."""
        if not self.current_object:
            return
        
        # Stop animation if playing
        if self.playing:
            self.toggle_play()
        
        # Reset phase
        self.phase = 0.0
        self.phase_slider.setValue(0)
        
        # Clear the scene
        self.graphics_view.scene.clear()
        
        # Generate the crystal structure
        self.generate_crystal()
    
    def generate_crystal(self):
        """Generate crystal structure based on current settings and object data."""
        if not self.current_object:
            return
        
        # Get crystal type
        crystal_type_idx = self.type_selector.currentIndex()
        crystal_types = ["time_crystal", "space_crystal", "cubic", "hexagonal"]
        self.crystal_type = crystal_types[crystal_type_idx]
        
        # Extract parameters from object data if possible
        obj_data = self.current_object.get("data", {})
        obj_scale = self.current_object.get("scale", "")
        
        # Clear scene
        self.graphics_view.scene.clear()
        
        # Set scene rectangle (size of the view)
        scene_size = 500
        self.graphics_view.scene.setSceneRect(-scene_size/2, -scene_size/2, scene_size, scene_size)
        
        # Create particles based on crystal type
        if self.crystal_type == "time_crystal":
            self.create_time_crystal(obj_data, obj_scale)
        elif self.crystal_type == "space_crystal":
            self.create_space_crystal(obj_data, obj_scale)
        elif self.crystal_type == "cubic":
            self.create_cubic_crystal(obj_data, obj_scale)
        elif self.crystal_type == "hexagonal":
            self.create_hexagonal_crystal(obj_data, obj_scale)
        
        # Reset the view to see the whole scene
        self.graphics_view.fitInView(self.graphics_view.scene.sceneRect(), Qt.KeepAspectRatio)
    
    def create_time_crystal(self, obj_data, obj_scale):
        """Create a time crystal visualization."""
        # Time crystals: particles arranged in a ring with periodic phase modulation
        
        # Base radius depending on the number of particles
        radius = 150
        center_x = 0
        center_y = 0
        
        # Clear previous collections
        self.particles = []
        self.bonds = []
        
        # Create particles
        for i in range(self.num_particles):
            # Calculate particle position on a ring with phase modulation
            angle = 2 * math.pi * i / self.num_particles + self.phase
            
            # Add some radial variation based on phase and index
            radial_mod = 10 * math.sin(angle * 2 + self.phase)
            current_radius = radius + radial_mod
            
            x = center_x + current_radius * math.cos(angle)
            y = center_y + current_radius * math.sin(angle)
            
            # Create particle
            particle = self.create_particle(x, y, i)
            self.particles.append(particle)
        
        # Create bonds between particles if enabled
        if self.show_bonds:
            for i in range(self.num_particles):
                p1 = self.particles[i]
                p2 = self.particles[(i + 1) % self.num_particles]
                bond = self.create_bond(p1, p2)
                self.bonds.append(bond)
        
        # Add a title with the object name
        self.title_text = self.graphics_view.scene.addText(
            f"{self.current_object.get('name', '')}\nTime Crystal Visualization")
        self.title_text.setDefaultTextColor(Qt.white)
        self.title_text.setPos(-self.title_text.boundingRect().width()/2, -radius - 50)
    
    def create_space_crystal(self, obj_data, obj_scale):
        """Create a space crystal visualization."""
        # Space crystals: particles arranged in a 2D lattice with varying spacing
        
        # Grid dimensions
        rows = int(math.sqrt(self.num_particles))
        cols = math.ceil(self.num_particles / rows)
        
        # Spacing between particles
        spacing = 400 / max(rows, cols)
        
        # Calculate offset to center
        offset_x = -spacing * (cols - 1) / 2
        offset_y = -spacing * (rows - 1) / 2
        
        # Create particles
        particles = []
        particle_index = 0
        
        for row in range(rows):
            for col in range(cols):
                if particle_index < self.num_particles:
                    x = offset_x + col * spacing
                    y = offset_y + row * spacing
                    
                    # Add some randomness based on the phase
                    x += 10 * math.sin(self.phase + row * 0.5)
                    y += 10 * math.cos(self.phase + col * 0.5)
                    
                    particle = self.create_particle(x, y, particle_index)
                    particles.append(particle)
                    particle_index += 1
        
        # Create bonds between neighboring particles if enabled
        if self.show_bonds:
            for row in range(rows):
                for col in range(cols):
                    idx = row * cols + col
                    if idx < self.num_particles:
                        # Create horizontal bonds
                        if col + 1 < cols and idx + 1 < self.num_particles:
                            self.create_bond(particles[idx], particles[idx + 1])
                        
                        # Create vertical bonds
                        if row + 1 < rows and idx + cols < self.num_particles:
                            self.create_bond(particles[idx], particles[idx + cols])
        
        # Add a title with the object name
        title_text = self.graphics_view.scene.addText(
            f"{self.current_object.get('name', '')}\nSpace Crystal Visualization")
        title_text.setDefaultTextColor(Qt.white)
        title_text.setPos(-title_text.boundingRect().width()/2, -250)
    
    def create_cubic_crystal(self, obj_data, obj_scale):
        """Create a cubic crystal visualization."""
        # Determine cubic dimensions
        side = math.ceil(math.pow(self.num_particles, 1/3))
        
        # Spacing between particles
        spacing = 300 / side
        
        # Calculate offset to center
        offset = -spacing * (side - 1) / 2
        
        # Create particles
        particles = []
        particle_index = 0
        
        # We'll use a simpler 2D projection of a 3D cubic structure
        for x_idx in range(side):
            for y_idx in range(side):
                for z_idx in range(side):
                    if particle_index < self.num_particles:
                        # Calculate 3D position
                        x3d = offset + x_idx * spacing
                        y3d = offset + y_idx * spacing
                        z3d = offset + z_idx * spacing
                        
                        # Project 3D to 2D (simple isometric projection)
                        x = x3d - z3d * math.cos(math.pi/6)
                        y = y3d - z3d * math.sin(math.pi/6)
                        
                        particle = self.create_particle(x, y, particle_index)
                        particles.append(particle)
                        particle_index += 1
        
        # Create bonds between neighboring particles if enabled
        if self.show_bonds:
            # This is simplified - in a real app you would create a proper 3D adjacency graph
            for i in range(len(particles) - 1):
                dist = math.sqrt(
                    pow(particles[i].pos().x() - particles[i+1].pos().x(), 2) +
                    pow(particles[i].pos().y() - particles[i+1].pos().y(), 2)
                )
                if dist < spacing * 1.5:
                    self.create_bond(particles[i], particles[i+1])
        
        # Add a title with the object name
        title_text = self.graphics_view.scene.addText(
            f"{self.current_object.get('name', '')}\nCubic Crystal Visualization")
        title_text.setDefaultTextColor(Qt.white)
        title_text.setPos(-title_text.boundingRect().width()/2, -250)
    
    def create_hexagonal_crystal(self, obj_data, obj_scale):
        """Create a hexagonal crystal visualization."""
        # Hexagonal packing
        rows = int(math.sqrt(self.num_particles * 2 / math.sqrt(3)))
        cols = math.ceil(self.num_particles / rows)
        
        # Spacing between particles
        spacing = 400 / max(rows, cols)
        
        # Calculate offset to center
        offset_x = -spacing * (cols - 1) / 2
        offset_y = -spacing * (rows - 1) * math.sqrt(3) / 4
        
        # Create particles
        particles = []
        particle_index = 0
        
        for row in range(rows):
            for col in range(cols):
                if particle_index < self.num_particles:
                    # In hexagonal packing, alternate rows are offset
                    col_offset = (row % 2) * 0.5
                    
                    x = offset_x + (col + col_offset) * spacing
                    y = offset_y + row * spacing * math.sqrt(3) / 2
                    
                    particle = self.create_particle(x, y, particle_index)
                    particles.append(particle)
                    particle_index += 1
        
        # Create bonds between neighboring particles if enabled
        if self.show_bonds:
            # For hexagonal packing, each particle has up to 6 neighbors
            for i in range(len(particles)):
                for j in range(i+1, len(particles)):
                    dist = math.sqrt(
                        pow(particles[i].pos().x() - particles[j].pos().x(), 2) +
                        pow(particles[i].pos().y() - particles[j].pos().y(), 2)
                    )
                    if dist < spacing * 1.1:
                        self.create_bond(particles[i], particles[j])
        
        # Add a title with the object name
        title_text = self.graphics_view.scene.addText(
            f"{self.current_object.get('name', '')}\nHexagonal Crystal Visualization")
        title_text.setDefaultTextColor(Qt.white)
        title_text.setPos(-title_text.boundingRect().width()/2, -250)
    
    def create_particle(self, x, y, index):
        """Create a particle at the specified position."""
        # Particle size
        size = self.particle_size
        
        # Determine particle color based on index and energy if enabled
        if self.color_by_energy:
            # Use color gradient based on index and phase
            hue = (index / self.num_particles * 360 + self.phase * 30) % 360
            color = QColor.fromHsv(int(hue), 255, 255)
        else:
            # Fixed color based on scale
            scale_colors = {
                "quantum": QColor(255, 50, 50),    # Red
                "atomic": QColor(255, 150, 50),    # Orange
                "molecular": QColor(255, 255, 50), # Yellow
                "cellular": QColor(50, 255, 50),   # Green
                "human": QColor(50, 200, 255),     # Cyan
                "planetary": QColor(100, 100, 255),# Blue
                "stellar": QColor(200, 50, 255),   # Purple
                "galactic": QColor(255, 50, 255),  # Magenta
                "cosmic": QColor(255, 255, 255)    # White
            }
            object_scale = self.current_object.get("scale", "cosmic")
            color = scale_colors.get(object_scale, QColor(200, 200, 200))
        
        # Create the particle as a colored circle
        brush = QBrush(color)
        particle = self.graphics_view.scene.addEllipse(-size/2, -size/2, size, size, QPen(Qt.black), brush)
        particle.setPos(x, y)
        particle.setZValue(10)  # Ensure particles are on top of bonds
        
        # Add shadow effect for better visibility
        shadow_color = QColor(0, 0, 0, 80)
        shadow = self.graphics_view.scene.addEllipse(
            -size/2 - 2, -size/2 - 2, size + 4, size + 4, 
            QPen(shadow_color), QBrush(shadow_color)
        )
        shadow.setPos(x, y)
        shadow.setZValue(5)
        
        return particle
    
    def create_bond(self, particle1, particle2):
        """Create a bond between two particles."""
        # Get particle positions
        pos1 = particle1.pos()
        pos2 = particle2.pos()
        
        # Create a line between the particles
        pen = QPen(QColor(200, 200, 200, 150))
        pen.setWidth(2)
        
        # Draw the bond
        bond = self.graphics_view.scene.addLine(
            pos1.x(), pos1.y(), pos2.x(), pos2.y(), pen
        )
        bond.setZValue(1)  # Ensure bonds are behind particles
        
        return bond
    
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
            self.update_crystal()  # Revert to normal display
    
    def update_animation(self):
        """Update animation frame with smoother transitions."""
        if not self.playing or not self.current_object:
            return
        
        # Increment animation frame
        self.animation_frame += 1
        
        # Calculate phase based on animation frame
        self.phase = (self.animation_frame % self.max_frames) / self.max_frames * 2 * math.pi
        
        # Update phase slider
        self.phase_slider.blockSignals(True)
        self.phase_slider.setValue(int(self.phase / (2 * math.pi) * 100))
        self.phase_slider.blockSignals(False)
        
        # Store current scene items before updating
        if not hasattr(self, 'particles'):
            # Initialize tracking collections if not already existing
            self.particles = []
            self.bonds = []
            
        # Instead of regenerating everything, update particle positions
        if self.crystal_type == "time_crystal" and self.particles:
            self._animate_time_crystal()
        elif self.crystal_type == "space_crystal" and self.particles:
            self._animate_space_crystal()
        else:
            # For other types or first run, regenerate the crystal
            self.update_crystal()
    
    def on_phase_changed(self, value):
        """Handle phase slider change."""
        self.phase = value / 100.0 * 2 * math.pi
        self.update_crystal()
    
    def on_type_changed(self, index):
        """Handle crystal type selector change."""
        self.update_crystal()
    
    def on_particles_changed(self, value):
        """Handle particle count slider change."""
        self.num_particles = value
        self.particles_value.setText(str(value))
        self.update_crystal()
    
    def on_bonds_changed(self, state):
        """Handle show bonds checkbox change."""
        self.show_bonds = state == Qt.Checked
        self.update_crystal()
    
    def on_color_changed(self, state):
        """Handle color by energy checkbox change."""
        self.color_by_energy = state == Qt.Checked
        self.update_crystal()
    
    def reset_view(self):
        """Reset the view to show the entire crystal."""
        self.graphics_view.fitInView(self.graphics_view.scene.sceneRect(), Qt.KeepAspectRatio)
    
    def take_screenshot(self):
        """Take a screenshot of the current crystal view."""
        pixmap = QPixmap(self.size())
        self.render(pixmap)
        return pixmap
        
    def _animate_time_crystal(self):
        """Animuje kryształ czasu z płynnymi efektami oscylacji."""
        if not self.particles:
            return
            
        # Bazowy promień
        radius = 150
        center_x = 0
        center_y = 0
        
        # Aktualizuj pozycje cząstek
        for i, particle in enumerate(self.particles):
            try:
                # Oblicz pozycję z efektem oscylacji fazowej
                base_angle = 2 * math.pi * i / len(self.particles)
                # Dodaj modulację fazy dla efektu kryształu czasu (nieperiodyczne oscylacje)
                phase_mod = self.phase * (1 + 0.2 * math.sin(base_angle * 3))
                angle = base_angle + phase_mod * 0.3
                
                # Modulacja promienia dla efektu pulsowania
                radial_mod = 15 * math.sin(base_angle * 4 + self.phase * 2)
                current_radius = radius + radial_mod
                
                # Nowa pozycja
                x = center_x + current_radius * math.cos(angle)
                y = center_y + current_radius * math.sin(angle)
                
                # Aktualizuj pozycję cząstki
                particle.setPos(x, y)
                
                # Aktualizuj kolor w zależności od fazy jeśli włączone
                if self.color_by_energy:
                    energy = 0.5 + 0.5 * math.sin(base_angle + self.phase)
                    # Tęczowy efekt z przesunięciem fazowym
                    hue = int((i / len(self.particles) * 360 + self.phase * 30) % 360)
                    saturation = 200 + int(energy * 55)
                    value = 150 + int(energy * 105)
                    color = QColor.fromHsv(hue, saturation, value)
                    particle.setBrush(QBrush(color))
            except Exception as e:
                print(f"Error in time crystal animation: {e}")
                
        # Aktualizuj także pozycje wiązań, jeśli istnieją
        if self.show_bonds and hasattr(self, 'bonds') and self.bonds:
            try:
                for i, bond in enumerate(self.bonds):
                    p1 = self.particles[i]
                    p2 = self.particles[(i + 1) % len(self.particles)]
                    
                    # Pobierz nowe pozycje cząstek
                    pos1 = p1.pos()
                    pos2 = p2.pos()
                    
                    # Aktualizuj linię wiązania
                    bond.setLine(pos1.x(), pos1.y(), pos2.x(), pos2.y())
            except Exception as e:
                print(f"Error updating bonds: {e}")
        
        # Aktualizuj więzi między cząstkami jeśli włączone
        if self.show_bonds and self.bonds:
            for i, bond in enumerate(self.bonds):
                p1 = self.particles[i]
                p2 = self.particles[(i + 1) % len(self.particles)]
                
                # Utwórz nową linię łączącą cząstki na ich aktualnych pozycjach
                bond.setLine(p1.pos().x(), p1.pos().y(), p2.pos().x(), p2.pos().y())

    def _animate_space_crystal(self):
        """Animuje kryształ przestrzenny z efektami fal."""
        if not self.particles:
            return
            
        # Określ wymiary siatki
        rows = int(math.sqrt(len(self.particles)))
        cols = math.ceil(len(self.particles) / rows)
        
        # Odstęp między cząstkami
        spacing = 400 / max(rows, cols)
        
        # Oblicz przesunięcie do wycentrowania
        offset_x = -spacing * (cols - 1) / 2
        offset_y = -spacing * (rows - 1) / 2
        
        # Aktualizuj pozycje cząstek tworząc efekt fali przestrzennej
        particle_index = 0
        for row in range(rows):
            for col in range(cols):
                if particle_index < len(self.particles):
                    # Bazowa pozycja w siatce
                    base_x = offset_x + col * spacing
                    base_y = offset_y + row * spacing
                    
                    # Dodaj efekt fali propagującej się przez siatkę
                    wave_x = 20 * math.sin(self.phase + (row + col) * 0.5)
                    wave_y = 20 * math.cos(self.phase * 1.3 + (row - col) * 0.5)
                    
                    # Dodaj efekt rozchodzących się kręgów
                    distance = math.sqrt(row**2 + col**2)
                    radial_wave = 10 * math.sin(distance - self.phase * 3)
                    
                    # Oblicz końcową pozycję
                    x = base_x + wave_x + radial_wave * (col / (cols or 1))
                    y = base_y + wave_y + radial_wave * (row / (rows or 1))
                    
                    # Aktualizuj pozycję cząstki
                    self.particles[particle_index].setPos(x, y)
                    
                    # Aktualizuj kolor w zależności od fazy jeśli włączone
                    if self.color_by_energy:
                        energy = 0.5 + 0.5 * math.sin(distance - self.phase * 2)
                        # Kolor oparty na energii i pozycji
                        hue = int((distance / (rows + cols) * 360 + self.phase * 20) % 360)
                        saturation = 200 + int(energy * 55)
                        value = 150 + int(energy * 105)
                        color = QColor.fromHsv(hue, saturation, value)
                        self.particles[particle_index].setBrush(QBrush(color))
                    
                    particle_index += 1
        
        # Aktualizuj więzi między cząstkami jeśli włączone
        if self.show_bonds and self.bonds:
            bond_index = 0
            for i in range(len(self.particles)):
                # Znajdź sąsiadów w siatce
                row = i // cols
                col = i % cols
                
                # Aktualizuj poziome więzi
                if col + 1 < cols and i + 1 < len(self.particles) and bond_index < len(self.bonds):
                    p1 = self.particles[i]
                    p2 = self.particles[i + 1]
                    self.bonds[bond_index].setLine(p1.pos().x(), p1.pos().y(), p2.pos().x(), p2.pos().y())
                    bond_index += 1
                
                # Aktualizuj pionowe więzi
                if row + 1 < rows and i + cols < len(self.particles) and bond_index < len(self.bonds):
                    p1 = self.particles[i]
                    p2 = self.particles[i + cols]
                    self.bonds[bond_index].setLine(p1.pos().x(), p1.pos().y(), p2.pos().x(), p2.pos().y())
                    bond_index += 1
