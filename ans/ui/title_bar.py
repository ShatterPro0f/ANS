"""
Custom title bar for the ANS application.

This module provides a CustomTitleBar widget for use with frameless windows,
with support for dark mode, window controls, and Windows Aero snap.
"""
import os
from PyQt5 import QtWidgets, QtCore, QtGui

from ans.utils.constants import (
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
    TITLE_BAR_HEIGHT,
    COLOR_DARK_BG,
    COLOR_DARK_TEXT,
    COLOR_LIGHT_BG,
    COLOR_LIGHT_TEXT,
    COLOR_CLOSE_HOVER,
    COLOR_CLOSE_PRESSED
)

# Optional import for frameless window support
try:
    from qframelesswindow.utils import startSystemMove
    HAS_FRAMELESS_WINDOW_UTILS = True
except ImportError:
    HAS_FRAMELESS_WINDOW_UTILS = False


class CustomTitleBar(QtWidgets.QWidget):
    """Custom title bar for frameless window with dark mode support and Windows 10 classic icons."""
    
    def __init__(self, parent_window, window_title="", light_logo_path="", dark_logo_path=""):
        """Initialize custom title bar.
        
        Args:
            parent_window: Parent window instance (FramelessMainWindow or QMainWindow)
            window_title: Title text to display
            light_logo_path: Path to logo for light mode
            dark_logo_path: Path to logo for dark mode
        """
        super().__init__()
        self.parent_window = parent_window
        self.is_dark_mode = False
        self.drag_start_pos = None
        self.light_logo_path = light_logo_path
        self.dark_logo_path = dark_logo_path
        
        # Create layout with proper spacing and alignment
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 0, 0)  # Left padding for icon spacing
        layout.setSpacing(4)
        
        # Window icon label (will be updated in set_dark_mode)
        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setFixedSize(24, 24)
        layout.addWidget(self.icon_label)
        
        # Window title label
        self.title_label = QtWidgets.QLabel(window_title)
        self.title_label.setStyleSheet(f"color: {COLOR_LIGHT_TEXT}; font-weight: bold; margin: 0px 4px;")
        layout.addWidget(self.title_label, 1)
        
        # Spacer to push buttons to the right
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        layout.addItem(spacer)
        
        # Minimize button with Windows 10 icon
        self.minimize_btn = self._create_window_button("_", "minimize")
        self.minimize_btn.clicked.connect(self.minimize_window)
        layout.addWidget(self.minimize_btn)
        
        # Maximize button with Windows 10 icon
        self.maximize_btn = self._create_window_button("□", "maximize")
        self.maximize_btn.clicked.connect(self.maximize_window)
        layout.addWidget(self.maximize_btn)
        
        # Close button with Windows 10 icon
        self.close_btn = self._create_window_button("✕", "close")
        self.close_btn.clicked.connect(self.close_window)
        layout.addWidget(self.close_btn)
        
        # Set height and background
        self.setFixedHeight(TITLE_BAR_HEIGHT)
        self.set_dark_mode(False)
    
    def _create_window_button(self, text, button_type):
        """Create a window control button with Windows 10 styling.
        
        Args:
            text: Button text/icon
            button_type: Type of button ('minimize', 'maximize', 'close')
            
        Returns:
            QPushButton instance
        """
        btn = QtWidgets.QPushButton(text)
        btn.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
        btn.setFlat(True)
        
        # Different font sizing for different button types
        if button_type == "minimize":
            font_size = "14px"  # Smaller for minimize
            padding = "2px 0px 0px 0px"  # Lift up the minimize icon
        elif button_type == "maximize":
            font_size = "16px"  # Larger for maximize (matches close)
            padding = "0px"
        else:  # close button
            font_size = "16px"
            padding = "0px"
        
        btn.setStyleSheet(
            f"QPushButton {{ background-color: transparent; border: none; color: {COLOR_LIGHT_TEXT}; font-size: {font_size}; font-weight: normal; padding: {padding}; }}"
            "QPushButton:hover { background-color: rgba(0, 0, 0, 0.06); }"
            "QPushButton:pressed { background-color: rgba(0, 0, 0, 0.12); }"
        )
        return btn
    
    def set_dark_mode(self, is_dark: bool):
        """Update title bar colors and logo for dark/light mode.
        
        Args:
            is_dark: True for dark mode, False for light mode
        """
        self.is_dark_mode = is_dark
        
        # Update logo
        logo_path = self.dark_logo_path if is_dark else self.light_logo_path
        if logo_path and os.path.exists(logo_path):
            pixmap = QtGui.QPixmap(logo_path).scaledToHeight(24)
            self.icon_label.setPixmap(pixmap)
        
        if is_dark:
            bg_color = COLOR_DARK_BG
            text_color = COLOR_DARK_TEXT
            self.setStyleSheet(f"background-color: {bg_color};")
            self.title_label.setStyleSheet(f"color: {text_color}; font-weight: bold; margin: 0px 4px;")
            
            # Update button styles for dark mode
            self._update_button_style(self.minimize_btn, text_color, is_dark, button_type="minimize")
            self._update_button_style(self.maximize_btn, text_color, is_dark, button_type="maximize")
            self._update_button_style(self.close_btn, text_color, is_dark, close_button=True)
        else:
            bg_color = COLOR_LIGHT_BG
            text_color = COLOR_LIGHT_TEXT
            self.setStyleSheet(f"background-color: {bg_color}; border: none;")
            self.title_label.setStyleSheet(f"color: {text_color}; font-weight: bold; margin: 0px 4px; background-color: transparent;")
            
            # Update button styles for light mode
            self._update_button_style(self.minimize_btn, text_color, is_dark, button_type="minimize")
            self._update_button_style(self.maximize_btn, text_color, is_dark, button_type="maximize")
            self._update_button_style(self.close_btn, text_color, is_dark, close_button=True)
    
    def _update_button_style(self, button, text_color, is_dark, close_button=False, button_type=None):
        """Update button styling for light or dark mode.
        
        Args:
            button: QPushButton to update
            text_color: Text color for button
            is_dark: True if in dark mode
            close_button: True if this is the close button
            button_type: Type of button ('minimize', 'maximize', None)
        """
        # Determine sizing based on button type
        if button_type == "minimize":
            font_size = "14px"
            padding = "2px 0px 0px 0px"
        elif button_type == "maximize":
            font_size = "16px"
            padding = "0px"
        else:
            font_size = "16px"
            padding = "0px"
        
        if close_button:
            button.setStyleSheet(
                f"QPushButton {{ background-color: transparent; border: none; color: {text_color}; font-size: {font_size}; font-weight: normal; padding: {padding}; }}"
                f"QPushButton:hover {{ background-color: {COLOR_CLOSE_HOVER}; color: white; }}"
                f"QPushButton:pressed {{ background-color: {COLOR_CLOSE_PRESSED}; color: white; }}"
            )
        else:
            if is_dark:
                button.setStyleSheet(
                    f"QPushButton {{ background-color: transparent; border: none; color: {text_color}; font-size: {font_size}; font-weight: normal; padding: {padding}; }}"
                    f"QPushButton:hover {{ background-color: rgba(255, 255, 255, 0.08); }}"
                    f"QPushButton:pressed {{ background-color: rgba(255, 255, 255, 0.12); }}"
                )
            else:
                button.setStyleSheet(
                    f"QPushButton {{ background-color: transparent; border: none; color: {text_color}; font-size: {font_size}; font-weight: normal; padding: {padding}; }}"
                    f"QPushButton:hover {{ background-color: rgba(0, 0, 0, 0.06); }}"
                    f"QPushButton:pressed {{ background-color: rgba(0, 0, 0, 0.12); }}"
                )
    
    def mousePressEvent(self, event):
        """Enable window dragging from title bar.
        
        Args:
            event: QMouseEvent
        """
        if event.button() == 1:  # Left button
            if HAS_FRAMELESS_WINDOW_UTILS:
                # For FramelessMainWindow, use the library's system move helper
                try:
                    startSystemMove(self.parent_window, event)
                    event.accept()
                except Exception:
                    # Fallback if import fails
                    self.drag_start_pos = event.globalPos() - self.parent_window.frameGeometry().topLeft()
                    event.accept()
            else:
                # For standard QMainWindow, use manual dragging
                self.drag_start_pos = event.globalPos() - self.parent_window.frameGeometry().topLeft()
                event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle window dragging.
        
        When using FramelessMainWindow from qframelesswindow library:
        - startSystemMove() in mousePressEvent handles all dragging and snap detection
        - We don't need manual handling here
        
        When using standard QMainWindow:
        - Manual dragging is implemented here
        
        Args:
            event: QMouseEvent
        """
        if not HAS_FRAMELESS_WINDOW_UTILS and self.drag_start_pos and event.buttons() & 1:
            global_pos = event.globalPos()
            self.parent_window.move(global_pos - self.drag_start_pos)
            event.accept()
    
    def mouseDoubleClickEvent(self, event):
        """Toggle maximize on title bar double-click.
        
        Args:
            event: QMouseEvent
        """
        self.maximize_window()
    
    def minimize_window(self):
        """Minimize the window."""
        self.parent_window.showMinimized()
    
    def maximize_window(self):
        """Toggle maximize/restore window."""
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
            self.maximize_btn.setText("□")
        else:
            self.parent_window.showMaximized()
            self.maximize_btn.setText("▢")
    
    def close_window(self):
        """Close the window."""
        self.parent_window.close()
