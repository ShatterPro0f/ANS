"""
Main entry point for the ANS (Automated Novel System) application.

This module provides the main() function that initializes and runs the application.
Once the refactoring is complete, this will be the primary entry point.
"""
import sys
from PyQt5 import QtWidgets

# Note: Once main_window.py is fully extracted, import from there
# from ans.ui.main_window import ANSWindow

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
    # TODO: Once main_window.py is extracted, uncomment these lines:
    # app = QtWidgets.QApplication(sys.argv)
    # window = ANSWindow()
    # window.show()
    # return app.exec_()
    
    # Temporary: Import from original ans.py until extraction is complete
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Import main from ans.py (original monolith)
    import ans as original_ans
    return original_ans.main()


if __name__ == '__main__':
    sys.exit(main())
