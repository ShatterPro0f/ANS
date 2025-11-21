"""
Signal definitions for the ANS application.

This module provides a centralized SignalBroker class that defines all signals
used for communication between components. This eliminates signal duplication
and provides a single source of truth for signal definitions.
"""
from PyQt5 import QtCore


class SignalBroker(QtCore.QObject):
    """
    Central signal broker for all ANS application signals.
    
    This class serves as a neutral hub for signal communication between
    BackgroundThread and ANSWindow, preventing circular dependencies.
    
    Signals:
        BackgroundThread → UI Signals (12):
            processing_finished(str): Processing complete with result
            processing_error(str): Error during processing
            processing_progress(str): Progress updates
            log_update(str): Logging from thread
            init_complete(): Initialization phase complete
            synopsis_ready(str): Initial synopsis generated
            new_synopsis(str): Refined synopsis ready
            new_outline(str): Generated or refined outline
            new_characters(str): Generated character JSON array
            new_world(str): Generated world-building JSON dict
            new_timeline(str): Generated timeline with dates and events
            new_draft(str): Polished/enhanced draft section
            
        UI → BackgroundThread Signals (5):
            start_signal(str): Initiate novel generation with config string
            approve_signal(str): Approve content (emits content type)
            adjust_signal(str, str): Request adjustments (type, feedback)
            pause_signal(): Pause operations
            resume_signal(): Resume operations
            
        UI Internal Signals (3):
            refinement_start(): Synopsis refinement phase starting
            outline_refinement_start(): Outline refinement phase starting
            timeline_refinement_start(): Timeline refinement phase starting
            
        UI Utility Signals (2):
            error_signal(str): Error notifications
            test_result_signal(str): Test results from background threads
    """
    
    # BackgroundThread → UI Signals
    processing_finished = QtCore.pyqtSignal(str)
    processing_error = QtCore.pyqtSignal(str)
    processing_progress = QtCore.pyqtSignal(str)
    log_update = QtCore.pyqtSignal(str)
    init_complete = QtCore.pyqtSignal()
    synopsis_ready = QtCore.pyqtSignal(str)
    new_synopsis = QtCore.pyqtSignal(str)
    new_outline = QtCore.pyqtSignal(str)
    new_characters = QtCore.pyqtSignal(str)
    new_world = QtCore.pyqtSignal(str)
    new_timeline = QtCore.pyqtSignal(str)
    new_draft = QtCore.pyqtSignal(str)
    
    # UI → BackgroundThread Signals
    start_signal = QtCore.pyqtSignal(str)
    approve_signal = QtCore.pyqtSignal(str)
    adjust_signal = QtCore.pyqtSignal(str, str)
    pause_signal = QtCore.pyqtSignal()
    resume_signal = QtCore.pyqtSignal()
    
    # UI Internal Signals
    refinement_start = QtCore.pyqtSignal()
    outline_refinement_start = QtCore.pyqtSignal()
    timeline_refinement_start = QtCore.pyqtSignal()
    
    # UI Utility Signals
    error_signal = QtCore.pyqtSignal(str)
    test_result_signal = QtCore.pyqtSignal(str)
    
    def __init__(self):
        """Initialize the signal broker."""
        super().__init__()
