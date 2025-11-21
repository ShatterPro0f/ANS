"""
Main entry point for the ANS (Automated Novel System) application.

This module provides the main() function that initializes and runs the application.
"""
import sys
from PyQt5 import QtWidgets


def main():
    """
    Main entry point for the ANS application.
    
    This function:
    1. Creates the QApplication instance
    2. Initializes the main window (ANSWindow)
    3. Shows the window
    4. Starts the Qt event loop
    
    Returns:
        int: Application exit code
    """
    try:
        # Import the main window from refactored module
        from ans.ui.main_window import ANSWindow
        
        # Create application
        app = QtWidgets.QApplication(sys.argv)
        
        # Create and show main window
        window = ANSWindow()
        window.show()
        
        # Start event loop
        return app.exec_()
        
    except ImportError as e:
        # Fallback to original if imports fail
        print(f"Import error, falling back to original ans.py: {e}")
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import ans as original_ans
        return original_ans.main()
    except Exception as e:
        print(f"Error launching application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    sys.exit(main())
