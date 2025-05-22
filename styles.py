from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

def apply_dark_theme(app):
    """Apply dark theme to the application."""
    # Set the style to Fusion which works well with custom palettes
    app.setStyle("Fusion")
    
    # Create dark palette
    dark_palette = QPalette()
    
    # Set colors
    # Window background and foreground
    dark_palette.setColor(QPalette.Window, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    
    # Base background and foreground (for views)
    dark_palette.setColor(QPalette.Base, QColor(28, 28, 28))
    dark_palette.setColor(QPalette.AlternateBase, QColor(35, 35, 35))
    dark_palette.setColor(QPalette.Text, Qt.white)
    
    # Button colors
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    
    # Link colors
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.LinkVisited, QColor(130, 80, 200))
    
    # Highlight colors
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    
    # Disabled colors
    dark_palette.setColor(QPalette.Disabled, QPalette.Text, QColor(150, 150, 150))
    dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(150, 150, 150))
    
    # Apply the palette
    app.setPalette(dark_palette)
    
    # Apply additional stylesheet for other widgets
    app.setStyleSheet("""
    QToolTip { 
        color: #ffffff; 
        background-color: #2a2a2a; 
        border: 1px solid #3a3a3a;
        padding: 4px;
        border-radius: 2px;
        opacity: 200;
    }
    
    QTabWidget::pane {
        border: 1px solid #444;
        top: -1px;
    }
    
    QTabBar::tab {
        background: #333;
        border: 1px solid #444;
        min-width: 8ex;
        padding: 6px 14px;
        border-top-left-radius: 3px;
        border-top-right-radius: 3px;
    }
    
    QTabBar::tab:selected {
        background: #444;
        border-bottom-color: #444; 
    }
    
    QTabBar::tab:!selected {
        margin-top: 2px; 
    }
    
    QSplitter::handle {
        background-color: #3a3a3a;
    }
    
    QHeaderView::section {
        background-color: #3a3a3a;
        border: 1px solid #444;
        padding: 4px;
    }
    
    QTreeView, QTableView {
        alternate-background-color: #333;
        background: #2a2a2a;
    }
    
    QTreeView::item:selected, QTableView::item:selected {
        background-color: #2a82da;
    }
    
    QDockWidget {
        titlebar-close-icon: url(close.png);
        titlebar-normal-icon: url(undock.png);
    }
    
    QDockWidget::title {
        text-align: center;
        background: #3a3a3a;
        padding: 4px;
    }
    
    QDockWidget::close-button, QDockWidget::float-button {
        border: 1px solid transparent;
        background: transparent;
        padding: 2px;
    }
    
    QDockWidget::close-button:hover, QDockWidget::float-button:hover {
        background: rgba(255, 255, 255, 20);
    }
    
    QLineEdit, QComboBox, QSpinBox, QDateEdit, QDateTimeEdit, QTimeEdit {
        background-color: #2a2a2a;
        border: 1px solid #3a3a3a;
        border-radius: 2px;
        padding: 3px;
        color: white;
    }
    
    QPushButton {
        background-color: #3a3a3a;
        border: 1px solid #545454;
        border-radius: 2px;
        padding: 4px 12px;
        color: white;
    }
    
    QPushButton:hover {
        background-color: #434343;
    }
    
    QPushButton:pressed {
        background-color: #2a2a2a;
    }
    
    QToolBar {
        background-color: #3a3a3a;
        border: 1px solid #444;
        spacing: 3px;
    }
    
    QStatusBar {
        background-color: #3a3a3a;
        color: white;
    }
    """)
