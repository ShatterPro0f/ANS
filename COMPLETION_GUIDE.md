# Phases 5-9 Completion Guide

This guide provides detailed instructions for completing the remaining refactoring phases.

## Current Status

✅ **Completed (Phases 1-4)**:
- ans/signals.py - SignalBroker
- ans/utils/ - constants, config, export  
- ans/backend/ - project, llm
- ans/ui/title_bar.py - CustomTitleBar
- ans/main.py - Entry point (with fallback)
- ans/__init__.py - Package initialization

⏳ **In Progress (Phases 5-9)**:
- ans/backend/thread_skeleton.py - Structure for BackgroundThread
- ans/ui/tabs/novel_idea.py - Example tab module (complete)
- ans/ui/tabs/logs.py - Example tab module (complete)

## Phase 5: BackgroundThread Extraction

### Status: Skeleton Created

**File**: `ans/backend/thread_skeleton.py` → `ans/backend/thread.py`

### Steps to Complete:

1. **Rename skeleton to thread.py**:
   ```bash
   mv ans/backend/thread_skeleton.py ans/backend/thread.py
   ```

2. **Extract Methods from ans.py** (lines 45-2600):
   
   Copy each method and refactor according to patterns:

   **Method List** (22 methods total):
   - [ ] `__init__` - Already in skeleton, verify
   - [ ] `load_synopsis_from_project` - Already in skeleton  
   - [ ] `run()` - Lines ~124-172 in ans.py
   - [ ] `start_processing()` - Lines ~174-181
   - [ ] `set_paused()`, `is_paused()`, `wait_while_paused()` - Lines ~183-192
   - [ ] `refine_synopsis_with_feedback()` - Lines ~194-258
   - [ ] `generate_outline()` - Lines ~260-398
   - [ ] `refine_outline_with_feedback()` - Lines ~400-500
   - [ ] `generate_characters()` - Lines ~502-642
   - [ ] `refine_characters_with_feedback()` - Lines ~644-758
   - [ ] `generate_world()` - Lines ~760-900
   - [ ] `refine_world_with_feedback()` - Lines ~902-1016
   - [ ] `generate_timeline()` - Lines ~1018-1158
   - [ ] `refine_timeline_with_feedback()` - Lines ~1160-1274
   - [ ] `generate_novel_section()` - Lines ~1276-1532
   - [ ] `refine_section_with_feedback()` - Lines ~1534-1773
   - [ ] `approve_section()` - Lines ~1775-2108
   - [ ] `perform_final_consistency_check()` - Lines ~2110-2305
   - [ ] `start_chapter_research_loop()` - Lines ~2307-2430
   - [ ] `backup()` - Lines ~2432-2470

3. **Refactoring Pattern for Each Method**:

   ```python
   # OLD (in ans.py):
   def some_method(self):
       self.log_update.emit("message")
       parent_window = self.parent()
       stream = parent_window.client.generate(...)
       with open(filepath, 'w') as f:
           f.write(content)
   
   # NEW (in thread.py):
   def some_method(self):
       self.signal_broker.log_update.emit("message")
       stream = self._generate_llm_response(prompt)
       self.project_manager.write_file(filepath, content)
   ```

4. **Remove Parent Window Dependencies**:
   - Replace `self.parent()` with `self.config` or injected deps
   - Replace `parent_window.client` with `self.client`
   - Replace `parent_window.current_project` with parameters

5. **Test Each Method**:
   ```python
   # Create test for each method
   thread = BackgroundThread(config)
   thread.some_method(test_params)
   # Verify signals emitted
   # Verify files written correctly
   ```

### Estimated Time: 8-12 hours

## Phase 6: Tab Module Extraction

### Status: 2 of 7 Complete

**Completed**:
- ✅ ans/ui/tabs/novel_idea.py
- ✅ ans/ui/tabs/logs.py

**Remaining** (5 tabs):

### 6.1 Planning Tab (~800 lines)

**File**: `ans/ui/tabs/planning.py`

**Extract from**: ans.py lines 3182-3519

**Structure**:
```python
def create_planning_tab(main_window, signal_broker):
    # Synopsis displays (initial + refined)
    # Outline display
    # Characters display
    # World display
    # Timeline display
    # Approve/Adjust buttons for each section
    return tab, references
```

**Complexity**: HIGH - Largest tab, many widget references

### 6.2 Settings Tab (~400 lines)

**File**: `ans/ui/tabs/settings.py`

**Extract from**: ans.py lines 3625-4020

**Structure**:
```python
def create_settings_tab(main_window, signal_broker):
    # Dark mode toggle
    # LLM model selection
    # Temperature slider
    # Generation parameters
    # About button
    return tab, references
```

**Complexity**: MEDIUM - Many settings widgets

### 6.3 Initialization Tab (~300 lines)

**File**: `ans/ui/tabs/initialization.py`

**Extract from**: ans.py lines 2870-3120

**Structure**:
```python
def create_initialization_tab(main_window, signal_broker):
    # Logo and branding
    # Project create/load controls
    # LLM connection test
    return tab, references
```

**Complexity**: MEDIUM - Project management integration

### 6.4 Writing Tab (~250 lines)

**File**: `ans/ui/tabs/writing.py`

**Extract from**: ans.py lines 3520-3625

**Structure**:
```python
def create_writing_tab(main_window, signal_broker):
    # Draft display
    # Approve/Adjust buttons
    # Pause/Resume buttons
    return tab, references
```

**Complexity**: MEDIUM - Section workflow

### 6.5 Dashboard Tab (~200 lines)

**File**: `ans/ui/tabs/dashboard.py`

**Extract from**: ans.py lines 3539-3625

**Structure**:
```python
def create_dashboard_tab(main_window, signal_broker):
    # Status labels
    # Progress bar
    # Export buttons (DOCX/PDF)
    return tab, references
```

**Complexity**: LOW - Mostly display widgets

### Tab Module Pattern:

All tabs follow this pattern:

```python
"""Tab module docstring."""
from PyQt5 import QtWidgets

def create_TABNAME_tab(main_window, signal_broker):
    """Create and configure the Tab.
    
    Args:
        main_window: Reference to ANSWindow
        signal_broker: SignalBroker for signals
        
    Returns:
        tuple: (tab_widget, references_dict)
    """
    tab = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(tab)
    
    # Create widgets...
    
    # Define button handlers (use signal_broker)
    def _on_button_click():
        signal_broker.some_signal.emit(data)
    
    # Connect signals
    button.clicked.connect(_on_button_click)
    
    # Return tab and references
    references = {
        'widget_name': widget
    }
    return tab, references
```

### Estimated Time: 6-8 hours

## Phase 7: Main Window Extraction

### Status: Not Started

**File**: `ans/ui/main_window.py`

**Extract from**: ans.py lines 2800-5720 (ANSWindow class)

### Steps:

1. **Create Main Window Structure**:
   ```python
   from ans.ui.title_bar import CustomTitleBar
   from ans.ui.tabs import novel_idea, logs, planning, writing, dashboard, settings, initialization
   from ans.backend.thread import BackgroundThread, ThreadConfig
   from ans.signals import SignalBroker
   
   class ANSWindow(FramelessMainWindow):
       def __init__(self):
           super().__init__()
           self._setup_window_properties()
           self._setup_signal_broker()
           self._setup_title_bar()
           self._setup_backend_thread()
           self._setup_tabs()
           self._setup_signal_connections()
   ```

2. **Split __init__ into Setup Methods**:
   - `_setup_window_properties()` - Size, geometry, icon
   - `_setup_signal_broker()` - Create SignalBroker instance
   - `_setup_title_bar()` - Create CustomTitleBar
   - `_setup_backend_thread()` - Create BackgroundThread with ThreadConfig
   - `_setup_tabs()` - Call all create_tab() functions
   - `_setup_signal_connections()` - Connect all signals

3. **Extract Signal Handlers**:
   
   Create handler classes for organization:
   
   ```python
   class PlanningTabHandlers:
       def __init__(self, window, signal_broker):
           self.window = window
           self.signal_broker = signal_broker
       
       def on_approve_synopsis(self):
           # Handler logic
       
       def on_adjust_synopsis(self):
           # Handler logic
   ```

4. **Update Tab References**:
   
   Store widget references from tabs:
   ```python
   self._setup_tabs(self):
       self.tabs = {}
       
       tab, refs = novel_idea.create_novel_idea_tab(self, self.signal_broker)
       self.tab_widget.addTab(tab, "Novel Idea")
       self.tabs['novel_idea'] = refs
       
       # Repeat for all tabs...
   ```

5. **Connect Signals**:
   ```python
   def _setup_signal_connections(self):
       # BackgroundThread → UI
       self.signal_broker.new_synopsis.connect(self._on_new_synopsis)
       self.signal_broker.log_update.connect(self._on_log_update)
       
       # UI → BackgroundThread  
       self.signal_broker.start_signal.connect(self.thread.start_processing)
   ```

### Estimated Time: 4-6 hours

## Phase 8: Entry Point Finalization

### Status: Partial (Fallback Created)

**File**: `ans/main.py` (already created, needs update)

### Steps:

1. **Update main.py** once main_window.py exists:
   ```python
   from ans.ui.main_window import ANSWindow
   import sys
   from PyQt5 import QtWidgets
   
   def main():
       app = QtWidgets.QApplication(sys.argv)
       window = ANSWindow()
       window.show()
       return app.exec_()
   
   if __name__ == '__main__':
       sys.exit(main())
   ```

2. **Update ans.py as Wrapper**:
   ```python
   # ans.py - Backward compatibility wrapper
   from ans.main import main
   
   if __name__ == '__main__':
       main()
   ```

### Estimated Time: 30 minutes

## Phase 9: Integration Testing

### Status: Not Started

### Test Categories:

1. **Smoke Tests** (`tests/test_smoke.py`):
   ```python
   def test_app_starts():
       # App launches without errors
   
   def test_all_tabs_load():
       # All 7 tabs accessible
   
   def test_ui_elements_visible():
       # Buttons, inputs visible
   ```

2. **Signal Flow Tests** (`tests/test_signals.py`):
   ```python
   def test_start_signal_flow():
       # Click Start → signal → thread.start_processing()
   
   def test_approval_signal_flow():
       # Click Approve → signal → next phase
   ```

3. **Project Tests** (`tests/test_project.py`):
   ```python
   def test_create_project():
       # Project creation works
   
   def test_load_project():
       # Project loading works
   ```

4. **Thread Tests** (`tests/test_thread.py`):
   ```python
   def test_synopsis_generation():
       # Synopsis generation emits signals
   
   def test_outline_generation():
       # Outline generation writes file
   ```

5. **Export Tests** (`tests/test_export.py`):
   ```python
   def test_docx_export():
       # DOCX file created
   
   def test_pdf_export():
       # PDF file created
   ```

### Estimated Time: 8-10 hours

## Total Completion Estimate

- **Phase 5**: 8-12 hours
- **Phase 6**: 6-8 hours
- **Phase 7**: 4-6 hours
- **Phase 8**: 0.5 hours
- **Phase 9**: 8-10 hours

**Total**: 26.5-36.5 hours

## Recommended Approach

### Option A: Complete All Phases
- Single large PR with all phases
- Requires 3-5 days of focused work
- Very thorough but large review burden

### Option B: Incremental PRs (RECOMMENDED)
- **PR 1 (Current)**: Phases 1-4 + skeleton + examples
- **PR 2**: Phase 5 (BackgroundThread) complete
- **PR 3**: Phase 6 (All 7 tabs) complete
- **PR 4**: Phase 7 (Main window) complete
- **PR 5**: Phase 9 (Testing) complete

Benefits: Easier review, incremental validation, lower risk

### Option C: Hybrid Approach
- **Current PR**: Phases 1-4 + Phase 8 (entry point)
- **Next PR**: Phases 5-7 (core extraction)
- **Final PR**: Phase 9 (testing)

## Files Created in This Session

1. ✅ `ans/main.py` - Entry point with fallback
2. ✅ `ans/__init__.py` - Package initialization
3. ✅ `ans/backend/thread_skeleton.py` - BackgroundThread skeleton
4. ✅ `ans/ui/tabs/novel_idea.py` - Complete tab module
5. ✅ `ans/ui/tabs/logs.py` - Complete tab module
6. ✅ `PHASES_5-9_IMPLEMENTATION_PLAN.md` - Scope assessment
7. ✅ `COMPLETION_GUIDE.md` - This guide

## Next Steps

1. Review this completion guide
2. Decide on approach (A, B, or C)
3. If continuing immediately:
   - Start with Phase 5 (BackgroundThread)
   - Use skeleton as template
   - Extract methods one by one
   - Test after each method
4. If pausing for review:
   - Merge current PR
   - Schedule continuation work
   - Use guide for next session

## Questions?

Contact @ShatterPro0f for clarification on scope or approach.
