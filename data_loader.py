import os
import json
from PyQt5.QtWidgets import QMessageBox

from utils.constants import SCALE_NAMES


class DataLoader:
    """Class for loading and validating data files."""
    
    def __init__(self):
        self.objects = []
    
    def load_file(self, file_path, append=False):
        """
        Load and validate a data file.
        
        Args:
            file_path: Path to the data file
            append: If True, new objects will be added to existing ones instead of replacing them
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # Validate and process data
            new_objects = self._validate_data(raw_data)
            
            if new_objects:
                if append and self.objects:
                    # Unikaj duplikatów na podstawie ID
                    existing_ids = {obj["id"] for obj in self.objects}
                    
                    # Dodaj tylko obiekty, których ID nie istnieją już w kolekcji
                    unique_new_objects = [obj for obj in new_objects if obj["id"] not in existing_ids]
                    
                    # Połącz istniejące obiekty z nowymi
                    self.objects.extend(unique_new_objects)
                    
                    print(f"Dodano {len(unique_new_objects)} nowych unikalnych obiektów do istniejących {len(self.objects) - len(unique_new_objects)}")
                    return self.objects
                else:
                    # Jeśli nie dołączamy lub nie ma jeszcze obiektów, użyj tylko nowych
                    self.objects = new_objects
                    return new_objects
            
            return None
        
        except json.JSONDecodeError as e:
            QMessageBox.critical(None, "JSON Error", f"Invalid JSON format: {str(e)}")
            return None
        
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error loading data file: {str(e)}")
            return None
    
    def _validate_data(self, raw_data):
        """Validate the data structure and return valid objects."""
        valid_objects = []
        
        # Wypisz informacje o strukturze danych do debugowania
        print(f"Typ danych: {type(raw_data)}")
        
        # Check if the data has the expected structure
        if not isinstance(raw_data, dict):
            print("Ostrzeżenie: Dane nie są słownikiem, próba bezpośredniego użycia listy")
            # Spróbuj potraktować dane jako listę obiektów bezpośrednio
            if isinstance(raw_data, list):
                objects_list = raw_data
            else:
                print(f"Nieprawidłowy format danych: {type(raw_data)}")
                return None
        else:
            # Look for 'objects' key
            objects_list = raw_data.get('objects', [])
            print(f"Znaleziono {len(objects_list)} obiektów w pliku")
        
        if not objects_list:
            print("Brak obiektów w danych")
            return None
        
        # Validate each object
        for obj in objects_list:
            if not isinstance(obj, dict):
                print(f"Obiekt nie jest słownikiem: {type(obj)}")
                continue
            
            # Check for required fields
            if 'id' not in obj or 'scale' not in obj or 'name' not in obj:
                print(f"Brak wymaganych pól w obiekcie: {obj.get('id', 'unknown')}")
                continue
            
            # Check if scale is valid - zaakceptujmy wszystkie skale na potrzeby debugowania
            obj_scale = obj.get('scale', '')
            if obj_scale not in SCALE_NAMES:
                print(f"Nieznana skala: {obj_scale}")
                # Dodaj skalę tymczasowo do listy znanych skal
                # SCALE_NAMES.append(obj_scale)
                continue
            
            # Check if data field exists and is a dictionary
            if 'data' not in obj or not isinstance(obj['data'], dict):
                print(f"Brak pola data lub nie jest słownikiem: {obj.get('id', 'unknown')}")
                continue
            
            # Object is valid, add to the list
            valid_objects.append(obj)
        
        if not valid_objects:
            print("Nie znaleziono prawidłowych obiektów w pliku")
            return None
        
        print(f"Załadowano {len(valid_objects)} prawidłowych obiektów")
        return valid_objects
