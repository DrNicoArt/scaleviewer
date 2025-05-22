import numpy as np


class CrystalDetector:
    """
    Class for detecting potential time crystal candidates based on
    object properties and criteria.
    """
    
    def __init__(self):
        # Define criteria for time crystal candidates and their analogies across all scales
        self.time_crystal_criteria = {
            # Properties that suggest time crystal behavior or analogous periodicity
            "criteria": [
                # Periodicity is the most essential feature on any scale - increased priority
                {"field": "period", "exists": True, "priority": 3},
                {"field": "orbital_period", "exists": True, "priority": 3},
                {"field": "rotation_period", "exists": True, "priority": 3},
                {"field": "oscillation_period", "exists": True, "priority": 3},
                {"field": "cycle_duration", "exists": True, "priority": 3},
                
                # Frequency-related properties - high priority across scales
                {"field": "frequency", "exists": True, "priority": 3},
                {"field": "peak_frequency", "exists": True, "priority": 3},
                {"field": "resonance_frequency", "exists": True, "priority": 3},
                {"field": "pulsation_frequency", "exists": True, "priority": 3},
                
                # Rotation and orbital characteristics - macroscale analogies
                {"field": "rotation_curve_flat_velocity", "exists": True, "priority": 2},
                {"field": "rotation_velocity", "exists": True, "priority": 2},
                {"field": "angular_velocity", "exists": True, "priority": 2},
                
                # Quantum properties - important for true time crystals
                {"field": "spin", "values": ["1/2", "1", "3/2"], "priority": 2},
                {"field": "elementary_charge", "exists": True, "priority": 2},
                {"field": "energy", "exists": True, "priority": 2},
                
                # Stability and coherence - relevant across scales
                {"field": "lifetime", "min_value": 100, "priority": 1},
                {"field": "age", "exists": True, "priority": 1},
                {"field": "coherence_time", "exists": True, "priority": 1},
                
                # Symmetry properties
                {"field": "symmetry", "pattern": "breaking", "priority": 1},
                {"field": "bond_angle", "exists": True, "priority": 1}
            ],
            # All scales are now considered for finding periodicity
            "preferred_scales": ["quantum", "atomic", "molecular", "cellular", "human", "planetary", "stellar", "galactic", "cosmic"]
        }
    
    def find_candidates(self, objects):
        """
        Find objects that could be time crystal candidates.
        
        Args:
            objects: List of objects to analyze
            
        Returns:
            List of potential time crystal candidates with confidence scores
        """
        candidates = []
        
        for obj in objects:
            score = self._evaluate_candidate(obj)
            
            if score > 0:
                # Create a candidate entry with the object and its score
                candidates.append({
                    "object": obj,
                    "score": score,
                    "explanation": self._generate_explanation(obj, score)
                })
        
        # Sort by score in descending order
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        return candidates
    
    def _evaluate_candidate(self, obj):
        """Evaluate an object as a time crystal candidate or periodicity analog."""
        if not obj or "data" not in obj:
            return 0
        
        # Start with a base score
        score = 0
        
        # Wszystkie skale są teraz tak samo istotne, ponieważ szukamy periodyczności na każdej skali
        obj_scale = obj.get("scale", "")
        if obj_scale in self.time_crystal_criteria["preferred_scales"]:
            score += 1  # Basic score for all scales (was 3 for quantum/atomic/molecular only)
        
        # Rozszerzona mapa kategorii pól, uwzględniająca więcej typów periodyczności
        field_categories = {
            # Wszystkie pola związane z okresowością (najważniejsza kategoria)
            "periodicity_fields": [
                "frequency", "period", "orbital_period", "rotation_period", 
                "oscillation_period", "cycle_duration", "peak_frequency", 
                "pulsation_frequency", "resonance_frequency", "angular_velocity",
                "rotation_curve_flat_velocity", "rotation_velocity"
            ],
            # Pola związane z kwantowymi właściwościami (ważne dla właściwych kryształów czasu)
            "quantum_fields": [
                "spin", "elementary_charge", "first_ionization_energy", 
                "electron_affinity", "energy", "momentum", "ground_state_wavelength"
            ],
            # Pola związane z długim czasem życia (stabilność fenomenu)
            "longevity_fields": [
                "lifetime", "age", "life_expectancy_global", "coherence_time",
                "half_life", "stability"
            ],
            # Pola związane z symetrią
            "symmetry_fields": [
                "symmetry", "bond_angle", "H–O–H bond_angle", "lattice_symmetry",
                "molecular_symmetry", "spatial_symmetry"
            ],
            # Pola związane z masą (inercja w oscylacjach)
            "mass_fields": [
                "mass", "stellar_mass", "rest_mass", "atomic_radius", 
                "molecular_weight", "density", "critical_density"
            ],
            # Nowa kategoria - amplituda drgań/oscylacji
            "amplitude_fields": [
                "amplitude", "temperature_anisotropy_rms", "wave_height",
                "oscillation_amplitude", "vibration_amplitude", "luminosity"
            ]
        }
        
        # Check for specific criteria
        obj_data = obj.get("data", {})
        criteria_matched = 0
        periodicity_matched = 0  # Specjalny licznik dla cech okresowości
        
        # Analiza dopasowania kryteriów z uwzględnieniem priorytetów
        for criterion in self.time_crystal_criteria["criteria"]:
            if "field" not in criterion:
                continue
            
            criterion_field = criterion["field"]
            priority = criterion.get("priority", 1)  # Default priority is 1
            
            # Znajdź pola należące do tej samej kategorii
            matched_field = None
            matched_value = None
            
            # Sprawdź czy pole istnieje bezpośrednio
            if criterion_field in obj_data:
                matched_field = criterion_field
                matched_value = obj_data[criterion_field]
            else:
                # Szukaj pól z tej samej kategorii w danych obiektu
                for category_name, fields in field_categories.items():
                    if criterion_field in fields:
                        for obj_field, obj_value in obj_data.items():
                            if obj_field in fields:
                                matched_field = obj_field
                                matched_value = obj_value
                                break
                    if matched_field:
                        break
            
            # Jeśli nie znaleziono pasującego pola, spróbuj znaleźć pola semantycznie podobne
            if not matched_field or matched_value is None:
                # Szukaj pól, które mogą sugerować okresowość
                if criterion.get("exists", False) and "field" in criterion:
                    # Dla pól periodyczności sprawdź wszystkie pola, które mogą sugerować cykliczność
                    if criterion["field"] in field_categories["periodicity_fields"]:
                        for obj_field, obj_value in obj_data.items():
                            # Sprawdź czy nazwa pola sugeruje okresowość/cykliczność
                            if any(term in obj_field.lower() for term in ["period", "cycle", "frequen", "rotat", "orbit", "oscill", "veloc"]):
                                matched_field = obj_field
                                matched_value = obj_value
                                score += 2 * priority  # Bonus za znalezienie ukrytej okresowości
                                criteria_matched += 1
                                periodicity_matched += 1
                                break
                continue
            
            # Naliczanie punktów w zależności od rodzaju dopasowania
            match_score = 0
            
            # Check minimum value
            if "min_value" in criterion:
                numeric_value = self._extract_numeric_value(matched_value)
                if numeric_value is not None and numeric_value >= criterion["min_value"]:
                    match_score = 2
            
            # Check for specific values
            elif "values" in criterion and isinstance(criterion["values"], list):
                str_value = str(matched_value).lower()
                for valid_value in criterion["values"]:
                    if str(valid_value).lower() in str_value:
                        match_score = 2
                        break
            
            # Check for text patterns
            elif "pattern" in criterion and isinstance(matched_value, str):
                str_value = matched_value.lower()
                pattern = criterion["pattern"].lower()
                if pattern in str_value:
                    match_score = 2
            
            # Check for existence
            elif "exists" in criterion and criterion["exists"]:
                match_score = 1
            
            # Pomnóż wynik o priorytet kryterium
            if match_score > 0:
                score += match_score * priority
                criteria_matched += 1
                
                # Jeśli dopasowane pole dotyczy periodyczności, zwiększ odpowiedni licznik
                if matched_field in field_categories["periodicity_fields"]:
                    periodicity_matched += 1
            
            # Dodatkowe punkty dla specyficznych pól w zależności od skali
            if matched_field:
                # Pole periodyczności
                if matched_field in field_categories["periodicity_fields"]:
                    score += 2  # Dodatkowe punkty za każdą cechę periodyczności
                
                # Sprawdzenia specyficzne dla skali
                if obj_scale == "quantum" and matched_field in field_categories["quantum_fields"]:
                    # Kwantowe obiekty z polami kwantowymi
                    score += 2
                elif obj_scale == "atomic" and matched_field in field_categories["quantum_fields"]:
                    # Atomy z kwantowymi właściwościami
                    score += 1
                elif obj_scale == "molecular" and "bond" in matched_field:
                    # Molekuły z wiązaniami
                    score += 1
                elif obj_scale == "planetary" and matched_field in field_categories["periodicity_fields"]:
                    # Planety z cechami okresowości
                    score += 2
                elif obj_scale == "stellar" and matched_field in field_categories["periodicity_fields"]:
                    # Gwiazdy z cechami okresowości
                    score += 2
                elif obj_scale == "galactic" and "rotation" in matched_field:
                    # Galaktyki z rotacją
                    score += 2
        
        # Bonusy za dopasowania wielu kryteriów
        if criteria_matched >= 4:
            score += 4
        elif criteria_matched >= 3:
            score += 3
        elif criteria_matched >= 2:
            score += 1
        
        # Specjalny bonus za dopasowanie wielu cech periodyczności
        if periodicity_matched >= 2:
            score += 3
        elif periodicity_matched >= 1:
            score += 1
        
        # Normalizacja wyniku do zakresu 0-10
        score = min(10, score)
        
        return score
    
    def _generate_explanation(self, obj, score):
        """Generate an explanation for why this object is a candidate for time crystal or periodicity analog."""
        obj_name = obj.get("name", "Object")
        obj_scale = obj.get("scale", "unknown")
        obj_data = obj.get("data", {})
        
        # Określ poziom pewności na podstawie wyniku
        if score >= 9:
            confidence = "Bardzo wysoki"
            if obj_scale in ["quantum", "atomic", "molecular"]:
                reason = "spełnia większość kluczowych kryteriów kryształów czasu"
            else:
                reason = "wykazuje silną okresowość analogiczną do kryształów czasu"
        elif score >= 7:
            confidence = "Wysoki"
            if obj_scale in ["quantum", "atomic", "molecular"]:
                reason = "wykazuje znaczące właściwości charakterystyczne dla kryształów czasu"
            else:
                reason = "posiada wyraźne cechy okresowości podobne do kryształów czasu"
        elif score >= 4:
            confidence = "Średni"
            if obj_scale in ["quantum", "atomic", "molecular"]:
                reason = "posiada pewne cechy kryształów czasu"
            else:
                reason = "wykazuje pewne cechy okresowości przypominające kryształy czasu"
        elif score >= 2:
            confidence = "Niski"
            if obj_scale in ["quantum", "atomic", "molecular"]:
                reason = "wykazuje minimalne właściwości kryształów czasu"
            else:
                reason = "posiada tylko kilka cech okresowości"
        else:
            confidence = "Bardzo niski"
            reason = "prawdopodobnie nie wykazuje istotnej periodyczności"
        
        # Przygotuj szczegółowe wyjaśnienie w zależności od skali
        scale_explanation = {
            "quantum": "Obiekty kwantowe mogą wykazywać zachowanie kryształów czasu poprzez efekty kwantowe wielu ciał. Właściwości takie jak spin, ładunek elementarny i energia stanu podstawowego są kluczowe dla prawdziwych kryształów czasu.",
            
            "atomic": "Obiekty atomowe mogą demonstrować periodyczne oscylacje w stanie podstawowym, szczególnie przy odpowiednich wartościach energii jonizacji i promienia atomowego. To poziom na którym można obserwować kwantową krystaliczność czasową.",
            
            "molecular": "Systemy molekularne mogą wykazywać periodyczne zachowanie w określonych warunkach, zwłaszcza gdy występują specyficzne wiązania i symetrie. Mogą demonstrować własności przypominające kryształy czasu na poziomie agregacji atomów.",
            
            "cellular": "Struktury komórkowe wykazują złożone rytmy biologiczne i cykle metaboliczne, które można rozpatrywać jako makroskopową analogię kryształów czasu. Cykliczność procesów biochemicznych tworzy stabilne wzorce okresowości.",
            
            "human": "Na skali ludzkiej, periodyczność przejawia się poprzez cykle biologiczne (biorytmy), rytmy aktywności i zaangażowane procesy poznawcze. Te zjawiska, choć nie są kwantowymi kryształami czasu, reprezentują emergentne formy periodyczności na poziomie złożonych systemów biologicznych.",
            
            "planetary": "Obiekty planetarne wykazują wysoce stabilne periodyczne zachowania (orbity, rotacje, pory roku), które są makroskopowymi analogiami kryształów czasu. Stabilność tych cykli mimo zakłóceń odzwierciedla fundamentalną cechę kryształów czasu - odporność na perturbacje.",
            
            "stellar": "Gwiazdy demonstrują różnorodne formy okresowości - od pulsacji i cykli aktywności, po regularną emisję energii. Niektóre zjawiska jak pulsary wykazują niezwykle precyzyjną periodyczność, przypominającą jedną z kluczowych cech kryształów czasu - stabilnych oscylacji w czasie.",
            
            "galactic": "Galaktyki wykazują złożone wzorce periodyczności w rotacji, falach gęstości i cyklach aktywności. Rotacja dyferencyjna i krzywej prędkości rotacji galaktyk tworzą stabilne struktury podobnie jak kryształy czasu tworzą uporządkowane wzorce w czasie.",
            
            "cosmic": "Na skali kosmicznej, można obserwować długoterminowe oscylacje i cykle w ekspansji wszechświata, promieniowaniu tła i rozkładzie wielkoskalowych struktur. Te periodyczności są fundamentalne dla kosmologii, podobnie jak kryształy czasu są fundamentalne dla fizyki kwantowej."
        }
        
        # Zidentyfikuj specyficzne właściwości obiektu, które przyczyniły się do wyniku
        specific_properties = []
        periodicity_properties = []
        
        # Listy pól dla różnych kategorii
        periodicity_fields = ["period", "orbital_period", "rotation_period", "cycle_duration", 
                             "frequency", "peak_frequency", "resonance_frequency", "pulsation_frequency",
                             "rotation_curve_flat_velocity", "rotation_velocity", "angular_velocity", 
                             "oscillation_period"]
        
        quantum_fields = ["spin", "elementary_charge", "first_ionization_energy", "energy", 
                        "momentum", "ground_state_wavelength"]
        
        amplitude_fields = ["amplitude", "oscillation_amplitude", "luminosity", "brightness", 
                          "temperature_anisotropy_rms"]
        
        # Sprawdź pola związane z okresowością
        found_periodicity = False
        for field in periodicity_fields:
            if field in obj_data:
                periodicity_properties.append(f"{field.replace('_', ' ')}: {obj_data[field]}")
                found_periodicity = True
        
        # Szukaj innych pól sugerujących periodyczność
        if not found_periodicity:
            for field, value in obj_data.items():
                if any(term in field.lower() for term in ["period", "cycle", "frequency", "rotation", "orbit", "oscillation"]):
                    periodicity_properties.append(f"{field.replace('_', ' ')}: {value}")
        
        # Dodaj właściwości kwantowe, jeśli istnieją
        for field in quantum_fields:
            if field in obj_data:
                specific_properties.append(f"{field.replace('_', ' ')}: {obj_data[field]}")
        
        # Dodaj właściwości związane z amplitudą, jeśli istnieją
        for field in amplitude_fields:
            if field in obj_data:
                specific_properties.append(f"{field.replace('_', ' ')}: {obj_data[field]}")
        
        # Konstruowanie opisów właściwości
        properties_text = ""
        periodicity_text = ""
        
        if periodicity_properties:
            periodicity_text = f" Cechy okresowości: {', '.join(periodicity_properties)}."
        
        if specific_properties:
            properties_text = f" Dodatkowe istotne właściwości: {', '.join(specific_properties)}."
        
        # Wybierz odpowiedni tytuł w zależności od skali
        if obj_scale in ["quantum", "atomic", "molecular"]:
            title = "Potencjalny kryształ czasu"
        else:
            title = "Analogia kryształu czasu"
        
        # Konstruowanie pełnego wyjaśnienia z tytułem i podsumowaniem
        explanation = f"{title} - {confidence} poziom pewności: {obj_name} {reason}.{periodicity_text}{properties_text} {scale_explanation.get(obj_scale, '')}"
        
        return explanation
    
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
