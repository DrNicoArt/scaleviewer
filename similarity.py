import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.cluster import KMeans


class SimilarityFinder:
    """
    Class for finding similar objects using scikit-learn metrics
    and clustering algorithms.
    """
    
    def __init__(self):
        self.distance_metric = "cosine"  # "cosine" or "euclidean"
    
    def find_similar(self, source_object, all_objects, n=5, metric=None):
        """
        Find objects similar to the source object.
        
        Args:
            source_object: The reference object
            all_objects: List of all objects to search from
            n: Number of similar objects to return
            metric: Distance metric to use (None uses the default)
            
        Returns:
            List of similar objects sorted by similarity
        """
        if not source_object or not all_objects:
            return []
        
        # Use specified metric or default
        metric = metric or self.distance_metric
        
        # Extract features from objects
        features, objects, field_names = self._extract_features(source_object, all_objects)
        
        if len(features) <= 1:
            return []
        
        # Standardize features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        
        # Find source object index
        source_idx = None
        source_id = source_object.get('id')
        
        for i, obj in enumerate(objects):
            if obj.get('id') == source_id:
                source_idx = i
                break
        
        if source_idx is None:
            return []
        
        # Calculate similarities
        if metric == "cosine":
            # For cosine similarity, higher is better (more similar)
            similarities = cosine_similarity(scaled_features)
            # Get top N indices (excluding self)
            indices = np.argsort(similarities[source_idx])[::-1][1:n+1]
            # Sort objects by decreasing similarity
            similar_objects = [objects[i] for i in indices]
        else:  # euclidean
            # For euclidean distance, lower is better (more similar)
            distances = euclidean_distances(scaled_features)
            # Get top N indices (excluding self)
            indices = np.argsort(distances[source_idx])[1:n+1]
            # Sort objects by increasing distance
            similar_objects = [objects[i] for i in indices]
        
        # Add the source object as the first item
        similar_objects.insert(0, source_object)
        
        return similar_objects
    
    def find_clusters(self, all_objects, n_clusters=3):
        """
        Cluster objects into groups based on their features.
        
        Args:
            all_objects: List of all objects to cluster
            n_clusters: Number of clusters to create
            
        Returns:
            Dictionary mapping cluster_id to list of objects
        """
        if not all_objects:
            return {}
        
        # Extract features from objects (using a placeholder object as source)
        features, objects, _ = self._extract_features(all_objects[0], all_objects)
        
        if len(features) <= 1 or len(objects) < n_clusters:
            return {}
        
        # Standardize features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        
        # Apply KMeans clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(scaled_features)
        
        # Group objects by cluster
        cluster_map = {}
        for i, cluster_id in enumerate(clusters):
            if cluster_id not in cluster_map:
                cluster_map[cluster_id] = []
            
            cluster_map[cluster_id].append(objects[i])
        
        return cluster_map
    
    def _extract_features(self, source_object, all_objects):
        """
        Extract numeric features from objects for comparison.
        
        Returns:
            tuple: (feature_matrix, objects_with_features, field_names)
        """
        # Start with fields from the source object
        source_fields = []
        if source_object and 'data' in source_object:
            for key, value in source_object['data'].items():
                # Only include numeric fields
                if self._is_numeric_field(value):
                    source_fields.append(key)
        
        # If no source fields, collect numeric fields from all objects
        if not source_fields:
            source_fields = set()
            for obj in all_objects:
                if 'data' in obj:
                    for key, value in obj['data'].items():
                        if self._is_numeric_field(value):
                            source_fields.add(key)
            source_fields = list(source_fields)
        
        # Create feature matrix
        features = []
        objects_with_features = []
        
        # Mapa podobnych pól (aby porównywać obiekty z różnymi nazwami pól)
        # Bazując na wiedzy dziedzinowej, grupujemy podobne parametry
        similar_fields_map = {
            # Masa
            'mass': ['mass', 'stellar_mass', 'mass_mean', 'rest_mass'],
            # Średnica/Promień
            'radius': ['radius', 'mean_radius', 'comoving_diameter', 'disk_diameter', 'diameter', 'soma_diameter'],
            # Energia
            'energy': ['energy', 'luminosity', 'first_ionization_energy'],
            # Czas
            'time': ['age', 'orbital_period', 'lifetime', 'life_expectancy_global'],
            # Temperatura
            'temperature': ['mean_temperature', 'temperature_anisotropy_rms'],
        }
        
        # Odwrotna mapa dla szybkiego wyszukiwania
        field_to_category = {}
        for category, fields in similar_fields_map.items():
            for field in fields:
                field_to_category[field] = category
        
        for obj in all_objects:
            if 'data' not in obj:
                continue
            
            # Extract features for this object
            obj_features = []
            valid_object = True
            fields_found = 0
            
            for field in source_fields:
                # Sprawdź dokładne dopasowanie pola
                if field in obj['data']:
                    value = obj['data'][field]
                    numeric_value = self._extract_numeric_value(value)
                    
                    if numeric_value is not None:
                        obj_features.append(numeric_value)
                        fields_found += 1
                    else:
                        obj_features.append(0)  # Zastępnik dla brakującej wartości
                # Sprawdź kategorie podobnych pól
                elif field in field_to_category:
                    category = field_to_category[field]
                    found_match = False
                    
                    # Szukaj pola z tej samej kategorii w danych obiektu
                    for obj_field, obj_value in obj['data'].items():
                        if obj_field in field_to_category and field_to_category[obj_field] == category:
                            numeric_value = self._extract_numeric_value(obj_value)
                            if numeric_value is not None:
                                obj_features.append(numeric_value)
                                fields_found += 1
                                found_match = True
                                break
                    
                    if not found_match:
                        obj_features.append(0)  # Zastępnik dla brakującej wartości
                else:
                    obj_features.append(0)  # Zastępnik dla brakującej wartości
            
            # Obiekt jest ważny, jeśli znaleziono co najmniej 2 odpowiadające pola
            if fields_found >= 2:
                features.append(obj_features)
                objects_with_features.append(obj)
        
        if not features:
            return np.array([]), [], []
            
        return np.array(features), objects_with_features, source_fields
    
    def _is_numeric_field(self, value):
        """Check if a field value can be represented as a number."""
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
    
    def _extract_numeric_value(self, value):
        """Extract a numeric value from a field value."""
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
