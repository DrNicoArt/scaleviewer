import os
import json
import csv


class DataExporter:
    """
    Class for exporting data in various formats (CSV, JSON, TXT).
    """
    
    def __init__(self):
        pass
    
    def export_data(self, file_path, objects, format_type):
        """
        Export object data to the specified file format.
        
        Args:
            file_path (str): Path where the file will be saved
            objects (list): List of objects to export
            format_type (str): Format to export ("csv", "json", or "txt")
        
        Returns:
            bool: True if export was successful, False otherwise
        """
        if not objects:
            raise ValueError("No objects to export")
        
        if format_type == "csv":
            return self._export_csv(file_path, objects)
        elif format_type == "json":
            return self._export_json(file_path, objects)
        elif format_type == "txt":
            return self._export_txt(file_path, objects)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def _export_csv(self, file_path, objects):
        """Export objects to CSV format."""
        if not objects:
            return False
        
        # Collect all possible data fields from all objects
        fields = set()
        for obj in objects:
            if "data" in obj and isinstance(obj["data"], dict):
                for key in obj["data"].keys():
                    fields.add(key)
        
        # Create headers with ID, Scale, Name, and all data fields
        headers = ["ID", "Scale", "Name"] + sorted(fields)
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header row
                writer.writerow(headers)
                
                # Write data rows
                for obj in objects:
                    row = [
                        obj.get("id", ""),
                        obj.get("scale", ""),
                        obj.get("name", "")
                    ]
                    
                    # Add data fields
                    obj_data = obj.get("data", {})
                    for field in sorted(fields):
                        row.append(obj_data.get(field, ""))
                    
                    writer.writerow(row)
            
            return True
        
        except Exception as e:
            raise Exception(f"Error exporting to CSV: {str(e)}")
    
    def _export_json(self, file_path, objects):
        """Export objects to JSON format."""
        if not objects:
            return False
        
        try:
            # Create a dictionary with 'objects' key
            data = {"objects": objects}
            
            with open(file_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=2, ensure_ascii=False)
            
            return True
        
        except Exception as e:
            raise Exception(f"Error exporting to JSON: {str(e)}")
    
    def _export_txt(self, file_path, objects):
        """Export objects to plain text format."""
        if not objects:
            return False
        
        try:
            with open(file_path, 'w', encoding='utf-8') as txtfile:
                txtfile.write(f"Data Export - {len(objects)} Objects\n")
                txtfile.write("=" * 60 + "\n\n")
                
                # Group objects by scale
                objects_by_scale = {}
                for obj in objects:
                    scale = obj.get("scale", "unknown")
                    
                    if scale not in objects_by_scale:
                        objects_by_scale[scale] = []
                    
                    objects_by_scale[scale].append(obj)
                
                # Write objects by scale
                for scale, scale_objects in sorted(objects_by_scale.items()):
                    txtfile.write(f"{scale.upper()} SCALE\n")
                    txtfile.write("-" * 60 + "\n\n")
                    
                    for obj in scale_objects:
                        # Write object header
                        txtfile.write(f"Name: {obj.get('name', 'Unknown')}\n")
                        txtfile.write(f"ID: {obj.get('id', '')}\n")
                        
                        # Write data fields
                        obj_data = obj.get("data", {})
                        if obj_data:
                            txtfile.write("Data:\n")
                            
                            for key, value in sorted(obj_data.items()):
                                txtfile.write(f"  {key}: {value}\n")
                        
                        txtfile.write("\n")
                    
                    txtfile.write("\n")
            
            return True
        
        except Exception as e:
            raise Exception(f"Error exporting to TXT: {str(e)}")
    
    def export_selection_to_format(self, file_path, objects, fields, format_type):
        """
        Export selected objects with specific fields to the specified format.
        
        Args:
            file_path (str): Path where the file will be saved
            objects (list): List of objects to export
            fields (list): List of field names to include
            format_type (str): Format to export ("csv", "json", or "txt")
        
        Returns:
            bool: True if export was successful, False otherwise
        """
        if not objects:
            raise ValueError("No objects to export")
        
        if not fields:
            # Use all fields if none specified
            return self.export_data(file_path, objects, format_type)
        
        # Create a filtered version of the objects
        filtered_objects = []
        
        for obj in objects:
            filtered_obj = {
                "id": obj.get("id", ""),
                "scale": obj.get("scale", ""),
                "name": obj.get("name", "")
            }
            
            # Filter data fields
            if "data" in obj and isinstance(obj["data"], dict):
                filtered_data = {}
                for field in fields:
                    if field in obj["data"]:
                        filtered_data[field] = obj["data"][field]
                
                if filtered_data:
                    filtered_obj["data"] = filtered_data
            
            filtered_objects.append(filtered_obj)
        
        # Export the filtered objects
        return self.export_data(file_path, filtered_objects, format_type)
