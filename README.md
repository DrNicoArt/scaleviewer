# CosmicAnalyzer

CosmicAnalyzer to zaawansowana aplikacja desktopowa do przeglądania, analizowania i porównywania danych naukowych w różnych skalach - od kwantowej do kosmicznej.

![CosmicAnalyzer Screenshot](attached_assets/image_1747785190385.png)

## Funkcje

- **Przeglądanie obiektów w różnych skalach**: Od skali kwantowej po kosmiczną
- **Wizualizacje danych**: Tabela, wykres radarowy, wizualizacja fal i kryształów
- **Animacje kryształów czasu**: Interaktywne animacje z efektami oscylacji
- **Porównywanie obiektów**: Zaawansowane algorytmy do porównywania właściwości obiektów w różnych skalach
- **Wykrywanie kryształów czasu**: Analiza właściwości obiektów pod kątem zachowań charakterystycznych dla kryształów czasu
- **Eksport raportów**: Generowanie raportów PDF ze zrzutami ekranu i analizą danych

## Wymagania

- Python 3.9+
- PyQt5
- matplotlib
- numpy
- pyqtgraph
- scipy
- scikit-learn
- reportlab

## Instalacja

```bash
# Instalacja zależności
pip install PyQt5 pyqtgraph matplotlib numpy scipy scikit-learn reportlab
```

## Uruchamianie

### Tryb graficzny (desktop)

```bash
python main.py --gui
```

### Tryb bez interfejsu (np. dla środowiska Replit)

```bash
python main.py --headless
```

## Struktura projektu

- `analysis/` - Algorytmy analizy danych i wykrywania podobieństw
- `data/` - Klasy do ładowania i zarządzania danymi
- `export/` - Funkcje eksportu danych i raportów
- `ui/` - Komponenty interfejsu użytkownika
- `utils/` - Narzędzia pomocnicze i stałe
- `attached_assets/` - Dane przykładowe

## Wykorzystanie

1. Uruchom aplikację w trybie GUI
2. Załaduj plik danych z różnymi obiektami (np. `attached_assets/nowe_obiekty.json`)
3. Przeglądaj obiekty w różnych skalach na drzewie po lewej stronie
4. Wybierz obiekt, aby zobaczyć jego szczegóły w różnych widokach
5. Porównuj obiekty używając funkcji "Find Similar"
6. Analizuj obiekty pod kątem właściwości kryształów czasu
7. Generuj raporty PDF z analizą i wizualizacjami

## Kontakt

Jeśli masz pytania lub potrzebujesz pomocy, skontaktuj się z autorem projektu.