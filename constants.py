"""
Constants used throughout the application.
"""

# Application metadata
APP_NAME = "Cosmic Analyzer"
APP_VERSION = "1.0.0"
ORGANIZATION_NAME = "ScientificViz"

# Scale names in order from largest to smallest
SCALE_NAMES = [
    "cosmic",
    "galactic",
    "stellar",
    "planetary",
    "human", 
    "cellular",
    "molecular",
    "atomic",
    "quantum"
]

# Colors for different scales
SCALE_COLORS = {
    "cosmic": "#8B00FF",    # Violet
    "galactic": "#4B0082",  # Indigo
    "stellar": "#0000FF",   # Blue
    "planetary": "#00FF00", # Green
    "human": "#FFFF00",     # Yellow
    "cellular": "#FF7F00",  # Orange
    "molecular": "#FF0000", # Red
    "atomic": "#FF00FF",    # Magenta
    "quantum": "#00FFFF"    # Cyan
}

# Time intervals for animations (milliseconds)
ANIMATION_SLOW = 100
ANIMATION_MEDIUM = 50
ANIMATION_FAST = 20

# File extensions for exports
EXPORT_EXTENSIONS = {
    "csv": ".csv",
    "json": ".json",
    "txt": ".txt",
    "pdf": ".pdf"
}

# Default number of similar objects to find
DEFAULT_SIMILAR_COUNT = 5

# Default observation flag (all observations are considered "observed" by default)
DEFAULT_OBSERVED_STATUS = True

# Window dimensions
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800
DEFAULT_SPLITTER_RATIO = 0.3  # 30% left, 70% right

# Visualization settings
MAX_TABLE_ROWS = 1000  # Maximum rows to display in table view
MAX_RADAR_FIELDS = 10  # Maximum fields to display in radar chart
MAX_WAVEFORM_TIME = 10  # Maximum time (seconds) for waveform visualization
MAX_CRYSTAL_PARTICLES = 100  # Maximum particles in crystal visualization

# Crystal detection threshold (minimum score to be considered a candidate)
CRYSTAL_CANDIDATE_THRESHOLD = 3

# Format for date and time display
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
