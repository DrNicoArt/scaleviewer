from PyQt5.QtWidgets import (QTreeView, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLineEdit, QCheckBox, QLabel, QHeaderView, 
                            QAbstractItemView)
from PyQt5.QtCore import Qt, QSortFilterProxyModel, pyqtSignal, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QBrush, QColor

from utils.constants import SCALE_NAMES


class ScaleTreeView(QWidget):
    """Tree view component for browsing objects by scale."""
    
    # Signal emitted when an object is selected
    object_selected = pyqtSignal(dict)
    
    # Signal emitted when object info is requested
    object_info_requested = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        
        self.setup_ui()
        self.objects_data = []
        self.initialize_tree()
    
    def setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search objects...")
        self.search_edit.textChanged.connect(self.on_search_text_changed)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        
        # Create observed only checkbox
        observed_layout = QHBoxLayout()
        self.observed_only_checkbox = QCheckBox("Observed only")
        self.observed_only_checkbox.stateChanged.connect(self.on_observed_only_changed)
        observed_layout.addWidget(self.observed_only_checkbox)
        observed_layout.addStretch()
        
        # Create tree view
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tree_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tree_view.clicked.connect(self.on_tree_item_clicked)
        
        # Set up the model and proxy model for filtering
        self.tree_model = QStandardItemModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.tree_model)
        self.proxy_model.setRecursiveFilteringEnabled(True)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.tree_view.setModel(self.proxy_model)
        
        # Add all widgets to the layout
        layout.addLayout(search_layout)
        layout.addLayout(observed_layout)
        layout.addWidget(self.tree_view, 1)  # 1 = stretch factor
    
    def initialize_tree(self):
        """Initialize the tree with scale categories."""
        self.tree_model.clear()
        self.tree_model.setHorizontalHeaderLabels(["Objects"])
        
        # Create root items for each scale
        self.scale_items = {}
        
        for scale_name in SCALE_NAMES:
            scale_item = QStandardItem(scale_name.capitalize())
            scale_item.setData({"is_scale": True, "scale": scale_name}, Qt.UserRole)
            self.tree_model.appendRow(scale_item)
            self.scale_items[scale_name] = scale_item
    
    def set_data(self, objects):
        """Populate the tree with object data."""
        self.objects_data = objects
        
        # Clear existing objects but keep the scale structure
        for scale_name, scale_item in self.scale_items.items():
            scale_item.removeRows(0, scale_item.rowCount())
        
        # Add objects to their respective scales
        for obj in objects:
            scale = obj.get("scale", "")
            
            if scale in self.scale_items:
                # Create object item
                item = QStandardItem(obj.get("name", "Unknown"))
                # Store the full object data
                item.setData(obj, Qt.UserRole)
                
                # Create info button item
                info_item = QStandardItem("[i]")
                info_item.setData(obj, Qt.UserRole)
                info_item.setData("info_button", Qt.UserRole + 1)
                info_item.setTextAlignment(Qt.AlignRight)
                
                # Add to tree
                self.scale_items[scale].appendRow([item, info_item])
        
        # Expand all items
        self.tree_view.expandAll()
    
    def on_search_text_changed(self, text):
        """Filter the tree based on search text."""
        self.proxy_model.setFilterFixedString(text)
        self.tree_view.expandAll()
    
    def on_observed_only_changed(self, state):
        """Filter the tree based on 'observed only' checkbox."""
        # This is a placeholder for actual observed filter logic
        # For a real implementation, you would need to know which objects are observed
        # and filter accordingly
        pass
    
    def on_tree_item_clicked(self, index):
        """Handle tree item click event."""
        # Get the item from the proxy model
        source_index = self.proxy_model.mapToSource(index)
        item = self.tree_model.itemFromIndex(source_index)
        
        if not item:
            return
        
        # Check if it's an info button
        if item.data(Qt.UserRole + 1) == "info_button":
            obj_data = item.data(Qt.UserRole)
            self.object_info_requested.emit(obj_data)
            return
        
        # Get the item data
        item_data = item.data(Qt.UserRole)
        
        # Check if it's an object (not a scale)
        if item_data and not item_data.get("is_scale", False):
            self.object_selected.emit(item_data)
    
    def get_selected_object(self):
        """Get the currently selected object data."""
        indexes = self.tree_view.selectedIndexes()
        
        if not indexes:
            return None
        
        # Use the first selected index
        source_index = self.proxy_model.mapToSource(indexes[0])
        item = self.tree_model.itemFromIndex(source_index)
        
        if not item:
            return None
        
        item_data = item.data(Qt.UserRole)
        
        # Check if it's an object (not a scale)
        if item_data and not item_data.get("is_scale", False):
            return item_data
        
        return None
    
    def get_selected_objects(self):
        """Get all selected object data."""
        selected_objects = []
        indexes = self.tree_view.selectedIndexes()
        
        for index in indexes:
            source_index = self.proxy_model.mapToSource(index)
            item = self.tree_model.itemFromIndex(source_index)
            
            if not item:
                continue
            
            item_data = item.data(Qt.UserRole)
            
            # Check if it's an object (not a scale) and not an info button
            if (item_data and not item_data.get("is_scale", False) and 
                item.data(Qt.UserRole + 1) != "info_button"):
                if item_data not in selected_objects:
                    selected_objects.append(item_data)
        
        return selected_objects
    
    def highlight_similar_objects(self, similar_objects):
        """Highlight objects that are similar to the selected object."""
        # Reset all highlighting first
        for scale_name, scale_item in self.scale_items.items():
            for row in range(scale_item.rowCount()):
                item = scale_item.child(row, 0)
                if item:
                    item.setForeground(QBrush())  # Reset to default
        
        # Highlight similar objects
        for obj in similar_objects:
            scale = obj.get("scale", "")
            obj_id = obj.get("id", "")
            
            if scale in self.scale_items:
                scale_item = self.scale_items[scale]
                
                for row in range(scale_item.rowCount()):
                    item = scale_item.child(row, 0)
                    if item:
                        item_data = item.data(Qt.UserRole)
                        if item_data and item_data.get("id") == obj_id:
                            item.setForeground(QBrush(QColor(0, 255, 0)))  # Highlight in green
                            break
        
        # Expand all to make highlighted items visible
        self.tree_view.expandAll()
