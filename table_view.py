from PyQt5.QtWidgets import (QTableView, QWidget, QVBoxLayout, QHBoxLayout, 
                           QHeaderView, QAbstractItemView, QMenu, QAction)
from PyQt5.QtCore import Qt, QSortFilterProxyModel, pyqtSignal, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap

import numpy as np


class ObjectTableView(QWidget):
    """Table view component for displaying object data."""
    
    # Signal emitted when an object is selected
    object_selected = pyqtSignal(dict)
    
    # Signal emitted when object info is requested
    object_info_requested = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        
        self.setup_ui()
        self.objects_data = []
    
    def setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create table view
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_view.setSortingEnabled(True)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_view.horizontalHeader().customContextMenuRequested.connect(self.show_header_menu)
        self.table_view.clicked.connect(self.on_table_item_clicked)
        
        # Set up the model and proxy model for sorting and filtering
        self.table_model = QStandardItemModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.table_model)
        self.table_view.setModel(self.proxy_model)
        
        # Add table to layout
        layout.addWidget(self.table_view)
    
    def set_data(self, objects):
        """Populate the table with object data."""
        self.objects_data = objects
        
        # Clear existing data
        self.table_model.clear()
        
        if not objects:
            return
        
        # Set headers by collecting all unique data fields
        headers = ["ID", "Scale", "Name"]
        data_fields = set()
        
        for obj in objects:
            if "data" in obj and isinstance(obj["data"], dict):
                for key in obj["data"].keys():
                    data_fields.add(key)
        
        # Sort data fields for consistent column order
        headers.extend(sorted(data_fields))
        
        self.table_model.setHorizontalHeaderLabels(headers)
        
        # Add data rows
        for obj in objects:
            row_items = []
            
            # Add ID, Scale, Name
            id_item = QStandardItem(obj.get("id", ""))
            id_item.setData(obj, Qt.UserRole)  # Store the full object data
            row_items.append(id_item)
            
            row_items.append(QStandardItem(obj.get("scale", "")))
            row_items.append(QStandardItem(obj.get("name", "")))
            
            # Add data fields
            obj_data = obj.get("data", {})
            for field in sorted(data_fields):
                value = obj_data.get(field, "")
                item = QStandardItem(str(value))
                
                # Set tooltip with unit information if available
                if isinstance(value, str):
                    item.setToolTip(f"{field}: {value}")
                
                row_items.append(item)
            
            self.table_model.appendRow(row_items)
        
        # Resize columns to content
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_view.horizontalHeader().setStretchLastSection(True)
    
    def on_table_item_clicked(self, index):
        """Handle table item click event."""
        # Get the item from the proxy model
        source_index = self.proxy_model.mapToSource(index)
        row = source_index.row()
        
        # Get the ID item which stores the full object data
        id_item = self.table_model.item(row, 0)
        
        if id_item:
            obj_data = id_item.data(Qt.UserRole)
            self.object_selected.emit(obj_data)
    
    def select_object(self, obj_data):
        """Select the row corresponding to the given object."""
        if not obj_data:
            return
        
        obj_id = obj_data.get("id", "")
        
        # Find the row with this object ID
        for row in range(self.table_model.rowCount()):
            id_item = self.table_model.item(row, 0)
            
            if id_item and id_item.text() == obj_id:
                # Convert to proxy index and select
                proxy_index = self.proxy_model.mapFromSource(self.table_model.index(row, 0))
                self.table_view.selectRow(proxy_index.row())
                self.table_view.scrollTo(proxy_index)
                break
    
    def show_header_menu(self, pos):
        """Show context menu for table header to hide/show columns."""
        header = self.table_view.horizontalHeader()
        menu = QMenu(self)
        
        # Add actions for each column
        for col in range(self.table_model.columnCount()):
            column_name = self.table_model.horizontalHeaderItem(col).text()
            action = QAction(column_name, self)
            action.setCheckable(True)
            action.setChecked(not header.isSectionHidden(col))
            action.triggered.connect(lambda checked, col=col: self.toggle_column(col, checked))
            menu.addAction(action)
        
        # Show the menu at cursor position
        menu.exec_(header.mapToGlobal(pos))
    
    def toggle_column(self, column, show):
        """Show or hide the specified column."""
        self.table_view.horizontalHeader().setSectionHidden(column, not show)
    
    def highlight_similar_objects(self, similar_objects):
        """Highlight rows for objects that are similar to the selected one."""
        # Reset all highlighting first
        for row in range(self.table_model.rowCount()):
            for col in range(self.table_model.columnCount()):
                item = self.table_model.item(row, col)
                if item:
                    item.setBackground(Qt.transparent)
        
        # Highlight similar objects
        similar_ids = [obj.get("id", "") for obj in similar_objects]
        
        for row in range(self.table_model.rowCount()):
            id_item = self.table_model.item(row, 0)
            
            if id_item and id_item.text() in similar_ids:
                for col in range(self.table_model.columnCount()):
                    item = self.table_model.item(row, col)
                    if item:
                        item.setBackground(Qt.green)
    
    def take_screenshot(self):
        """Take a screenshot of the current table view."""
        # Create a pixmap the size of the viewport
        pixmap = QPixmap(self.table_view.viewport().size())
        pixmap.fill(Qt.transparent)
        
        # Render the table to the pixmap
        self.table_view.render(pixmap)
        
        return pixmap
