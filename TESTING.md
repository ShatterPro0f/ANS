# Testing the Refactored ANS Application

## Prerequisites

Install required dependencies:

```bash
pip install PyQt5 ollama
```

Optional dependencies for full functionality:

```bash
pip install qframelesswindow python-docx reportlab
```

## Running Integration Tests

The refactored codebase includes comprehensive integration tests:

```bash
python3 test_integration.py
```

This will test:
1. Module imports (all 19 modules)
2. SignalBroker functionality
3. ProjectManager singleton
4. Tab creation functions (all 7 tabs)
5. Constants module

## Running the Application

### Using the Refactored Modules

```bash
python3 -m ans.main
```

Or:

```bash
python3 ans/main.py
```

### Using the Original (Compatibility)

```bash
python3 ans.py
```

## Manual Testing Checklist

### Smoke Tests
- [ ] Application starts without errors
- [ ] All 7 tabs are visible (Initialization, Novel Idea, Planning, Writing, Logs, Dashboard, Settings)
- [ ] Window controls work (minimize, maximize, close)
- [ ] Window dragging works
- [ ] Dark mode toggle works

### Functional Tests
- [ ] **Initialization Tab**
  - [ ] Create new project
  - [ ] Load existing project
  - [ ] Project list refreshes
- [ ] **Novel Idea Tab**
  - [ ] Enter idea, tone, word count
  - [ ] Click "Start" button
  - [ ] Validates inputs
- [ ] **Planning Tab**
  - [ ] Synopsis displays
  - [ ] Approve/Adjust buttons work
  - [ ] Outline generates
  - [ ] Characters display
  - [ ] World-building shows
  - [ ] Timeline appears
- [ ] **Writing Tab**
  - [ ] Draft displays
  - [ ] Approve section works
  - [ ] Adjust section works
  - [ ] Pause/Resume works
- [ ] **Logs Tab**
  - [ ] Shows project logs
  - [ ] Updates in real-time
- [ ] **Dashboard Tab**
  - [ ] Shows project status
  - [ ] Progress bar updates
  - [ ] Export DOCX works
  - [ ] Export PDF works
- [ ] **Settings Tab**
  - [ ] Dark mode toggles
  - [ ] LLM model selection
  - [ ] Temperature slider
  - [ ] Settings persist

### Integration Tests
- [ ] **Signal Flow**
  - [ ] start_signal triggers generation
  - [ ] approve_signal moves to next phase
  - [ ] adjust_signal triggers refinement
  - [ ] log_update updates logs
  - [ ] error_signal shows errors
- [ ] **File Operations**
  - [ ] Projects created with all files
  - [ ] Project files written correctly
  - [ ] Progress tracked accurately
  - [ ] Thread-safe file access
- [ ] **BackgroundThread**
  - [ ] run() method executes
  - [ ] generate_* methods work
  - [ ] refine_* methods work
  - [ ] approve_section() works
  - [ ] All 25 methods functional

## Known Limitations

The refactored code maintains backward compatibility with the original ans.py, which remains functional. Both versions can coexist:

- **Original**: `python3 ans.py`
- **Refactored**: `python3 -m ans.main`

If the refactored version has import issues, it will automatically fall back to the original.

## Test Environment

Tests were run without PyQt5 installed to verify module structure and Python syntax. For full testing, install all dependencies.

To verify module structure without running the GUI:

```bash
# Check Python syntax of all modules
for file in ans/**/*.py; do python3 -m py_compile "$file" && echo "✓ $file"; done

# Test imports (requires PyQt5)
python3 -c "from ans.ui.main_window import ANSWindow; print('SUCCESS')"
```

## CI/CD Integration

For automated testing in CI/CD:

```yaml
# Example GitHub Actions
- name: Install dependencies
  run: pip install -r requirements.txt
  
- name: Run integration tests
  run: python3 test_integration.py
  
- name: Check syntax
  run: |
    for file in ans/**/*.py; do
      python3 -m py_compile "$file"
    done
```
