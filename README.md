The “CosmicAnalyzer” application is designed to analyze periodic correlations of energy in objects from different cosmic and quantum scales.



Features



- **View objects at different scales**: From quantum to cosmic scales

- **Data visualizations**: Table, radar chart, wave and crystal visualization (does not work).

- **Time Crystal Animations**: Interactive animations with oscillation effects (doesn't work).

- **Object Comparison**: Advanced algorithms for comparing properties of objects at different scales.

- **Time Crystal Detection**: Analyze object properties for behaviors characteristic of time crystals.

- **Report Export**: Generate PDF reports with screenshots and data analysis (does not work).

## Requirements

- Python 3.9+
- PyQt5
- matplotlib
- numpy
- pyqtgraph
- scipy
- scikit-learn
- reportlab

## Installation

``bash
# Install dependencies
pip install PyQt5 pyqtgraph matplotlib numpy scipy scikit-learn reportlab
```.

## Running

### Graph mode (desktop)

``bash
python main.py --gui
```.

### Non-interface mode (e.g. for Replit environment)

```bash
python main.py --headless
```.

## Project structure

- `analysis/` - Algorithms for data analysis and similarity detection
- `data/` - Classes for loading and managing data
- `export/` - Functions for exporting data and reports
- `ui/` - User interface components
- `utils/` - Support tools and constants
- `attached_assets/` - Sample data

## Usage

1 Start the application in GUI mode
2. load a data file with various objects (e.g. `attached_assets/new_objects.json`)
3. browse the objects in different scales on the tree on the left side
4. select an object to see its details in different views
5. compare objects using the "Find Similar" function
6. analyze objects for time crystal properties
7. generate PDF reports with analysis and visualizations

## Contact

If you have questions or need help, please contact the author of the project:
biuro@drnico.pl
