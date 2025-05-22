import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal


class DataModel(QObject):
    """
    Central data model for the application that maintains object data
    and provides methods for accessing and manipulating it.
    """
    
    # Signal emitted when the data model changes
    data_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Storage for objects by scale
        self.objects_by_scale = {}
        
        # Storage for all objects
        self.all_objects = []
        
        # Storage for tags and catalogs
        self.tags = set()
        self.catalogs = set()
        
        # Currently selected object
        self.selected_object = None
    
    def set_objects(self, objects):
        """Set the object data and organize it by scale."""
        self.all_objects = objects
        
        # Group objects by scale
        self.objects_by_scale = {}
        for obj in objects:
            scale = obj.get('scale', '')
            
            if scale not in self.objects_by_scale:
                self.objects_by_scale[scale] = []
            
            self.objects_by_scale[scale].append(obj)
        
        # Extract tags and catalogs
        self.extract_metadata()
        
        # Notify listeners that data has changed
        self.data_changed.emit()
    
    def extract_metadata(self):
        """Extract tags and catalogs from object data."""
        self.tags = set()
        self.catalogs = set()
        
        for obj in self.all_objects:
            # Extract tags
            if 'tags' in obj and isinstance(obj['tags'], list):
                for tag in obj['tags']:
                    self.tags.add(tag)
            
            # Extract catalogs
            if 'catalog' in obj and isinstance(obj['catalog'], str):
                self.catalogs.add(obj['catalog'])
    
    def get_objects_by_scale(self, scale):
        """Get all objects for a specific scale."""
        return self.objects_by_scale.get(scale, [])
    
    def get_object_by_id(self, obj_id):
        """Find an object by its ID."""
        for obj in self.all_objects:
            if obj.get('id') == obj_id:
                return obj
        return None
    
    def get_data_field_names(self):
        """Get a set of all data field names across all objects."""
        fields = set()
        
        for obj in self.all_objects:
            if 'data' in obj and isinstance(obj['data'], dict):
                for key in obj['data'].keys():
                    fields.add(key)
        
        return sorted(fields)
    
    def select_object(self, obj):
        """Set the currently selected object."""
        self.selected_object = obj
    
    def get_selected_object(self):
        """Get the currently selected object."""
        return self.selected_object
    
    def get_data_matrix(self, field_names=None):
        """
        Convert object data to a numerical matrix for analysis.
        
        Args:
            field_names: List of field names to include. If None, use all numeric fields.
            
        Returns:
            tuple: (data_matrix, objects_included, field_names_used)
        """
        if not self.all_objects:
            return np.array([]), [], []
        
        # If no field names provided, get all fields that can be converted to numbers
        if field_names is None:
            field_names = []
            for obj in self.all_objects:
                if 'data' in obj and isinstance(obj['data'], dict):
                    for key, value in obj['data'].items():
                        if self._can_convert_to_number(value) and key not in field_names:
                            field_names.append(key)
        
        # Create the data matrix
        data_matrix = []
        objects_included = []
        
        for obj in self.all_objects:
            if 'data' not in obj or not isinstance(obj['data'], dict):
                continue
            
            row = []
            valid_row = True
            
            for field in field_names:
                value = obj['data'].get(field, None)
                
                if value is None:
                    valid_row = False
                    break
                
                # Try to convert to a number
                try:
                    if isinstance(value, str):
                        # Extract numeric part
                        numeric_str = ''.join(c for c in value if c.isdigit() or c == '.' or c == '-')
                        if numeric_str:
                            num_value = float(numeric_str)
                            row.append(num_value)
                        else:
                            valid_row = False
                            break
                    else:
                        row.append(float(value))
                except:
                    valid_row = False
                    break
            
            if valid_row:
                data_matrix.append(row)
                objects_included.append(obj)
        
        # Convert to numpy array
        if data_matrix:
            return np.array(data_matrix), objects_included, field_names
        else:
            return np.array([]), [], field_names
    
    def _can_convert_to_number(self, value):
        """Check if a value can be converted to a number."""
        if isinstance(value, (int, float)):
            return True
        
        if isinstance(value, str):
            # Extract numeric part
            numeric_str = ''.join(c for c in value if c.isdigit() or c == '.' or c == '-')
            if numeric_str:
                try:
                    float(numeric_str)
                    return True
                except:
                    pass
        
        return False
