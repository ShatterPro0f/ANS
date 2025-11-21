# ANS Architecture Documentation

## System Overview

The Automated Novel System (ANS) is now organized into a modular architecture with clear separation of concerns across 4 main packages.

## Package Structure

```
ans/
├── main.py              # Application entry point
├── signals.py           # Central signal broker
│
├── backend/             # Business logic & processing
│   ├── llm.py          # LLM communication with retry logic
│   ├── project.py      # File I/O and project management
│   └── thread.py       # Background processing thread
│
├── ui/                  # User interface components
│   ├── main_window.py  # Main application window
│   ├── title_bar.py    # Custom frameless window title bar
│   └── tabs/           # Tab modules (7 tabs)
│       ├── initialization.py
│       ├── novel_idea.py
│       ├── planning.py
│       ├── writing.py
│       ├── logs.py
│       ├── dashboard.py
│       └── settings.py
│
└── utils/               # Shared utilities
    ├── constants.py    # Application constants
    ├── config.py       # Configuration management
    └── export.py       # Export functionality (DOCX/PDF)
```

## Component Relationships

```
┌─────────────────────────────────────────────────────────┐
│                     Application                          │
│                                                          │
│  ┌────────────┐                                         │
│  │  main.py   │  Entry Point                            │
│  └─────┬──────┘                                         │
│        │                                                 │
│        v                                                 │
│  ┌────────────────────────────────────────────┐        │
│  │           ANSWindow (main_window.py)        │        │
│  │  ┌──────────────────────────────────────┐  │        │
│  │  │  Title Bar  │  7 Tabs  │  Menu Bar  │  │        │
│  │  └──────────────────────────────────────┘  │        │
│  └─────┬──────────────────┬───────────────────┘        │
│        │                  │                             │
│  ┌─────v──────┐    ┌──────v──────┐                     │
│  │  SignalBroker  │  BackgroundThread │                │
│  │  (signals.py)  │  (thread.py)      │                │
│  └─────┬──────┘    └──────┬──────┘                     │
│        │                  │                             │
│        │  ┌───────────────v────────────┐               │
│        │  │   ProjectManager (I/O)     │               │
│        │  │   ConfigManager (Settings) │               │
│        │  │   LLM Client (Ollama)      │               │
│        │  └────────────────────────────┘               │
│        │                                                │
│  ┌─────v───────────────────────────────────┐          │
│  │            File System                   │          │
│  │  projects/     Config/     assets/       │          │
│  └──────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────┘
```

## Signal Flow

The SignalBroker decouples components through event-driven architecture:

```
User Action → ANSWindow → SignalBroker → BackgroundThread
                             ↓
                          Logs Tab
                          Planning Tab
                          Writing Tab
                          etc.

BackgroundThread → SignalBroker → ANSWindow → Update UI
                      ↓
                   Logs Tab
                   Planning Tab
```

### Key Signals

| Signal | Direction | Purpose |
|--------|-----------|---------|
| `start_signal` | UI → Thread | Start novel generation |
| `approve_signal` | UI → Thread | Approve content, move to next phase |
| `adjust_signal` | UI → Thread | Request content refinement |
| `log_update` | Thread → UI | Log messages |
| `error_signal` | Thread → UI | Error notifications |
| `new_synopsis` | Thread → UI | Updated synopsis content |
| `new_outline` | Thread → UI | Generated outline |
| `new_characters` | Thread → UI | Character profiles |
| `new_draft` | Thread → UI | Draft section content |

## Data Flow

### Project Creation Flow

```
1. User Input (Initialization Tab)
   └─> ANSWindow.create_project_structure()
       └─> ProjectManager.create_project()
           └─> File System: projects/<name>/
               ├─ story.txt
               ├─ log.txt
               ├─ config.txt
               ├─ context.txt
               ├─ characters.txt
               ├─ world.txt
               ├─ synopsis.txt
               ├─ outline.txt
               └─ timeline.txt
```

### Novel Generation Flow

```
1. User Input (Novel Idea Tab)
   ├─ Idea text
   ├─ Tone
   └─ Word count target

2. SignalBroker.start_signal.emit(config)

3. BackgroundThread.run()
   ├─ Generate initial synopsis
   │  └─> SignalBroker.synopsis_ready.emit(text)
   │      └─> Planning Tab updates
   │
   ├─ Refine synopsis
   │  └─> SignalBroker.new_synopsis.emit(text)
   │      └─> Planning Tab updates
   │
   ├─ Generate outline (25 chapters)
   │  └─> SignalBroker.new_outline.emit(text)
   │      └─> Planning Tab updates
   │
   ├─ Generate characters
   │  └─> SignalBroker.new_characters.emit(json)
   │      └─> Planning Tab updates
   │
   ├─ Generate world-building
   │  └─> SignalBroker.new_world.emit(json)
   │      └─> Planning Tab updates
   │
   └─ Generate timeline
      └─> SignalBroker.new_timeline.emit(text)
          └─> Planning Tab updates
```

### Writing Flow

```
1. BackgroundThread.generate_novel_section()
   ├─ Read outline, characters, world, timeline
   ├─ Generate draft section
   ├─ Polish (2 passes)
   └─> SignalBroker.new_draft.emit(text)
       └─> Writing Tab displays draft

2. User Review
   ├─ Approve → BackgroundThread.approve_section()
   │   ├─ Append to story.txt
   │   ├─ Generate summary
   │   ├─ Update context
   │   ├─ Update progress
   │   └─> Generate next section
   │
   └─ Adjust → BackgroundThread.refine_section()
       ├─ Refine with feedback
       ├─ Polish (2 passes)
       └─> SignalBroker.new_draft.emit(refined_text)
           └─> Loop back to review
```

## Thread Safety

### File Locking Mechanism

```python
# ProjectManager implements per-file locking
class ProjectManager:
    def __init__(self):
        self._file_locks = {}  # Per-file locks
    
    def write_file(self, filepath, content):
        lock = self._get_file_lock(filepath)
        with lock:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
```

This prevents race conditions when:
- BackgroundThread writes to files
- UI reads project files
- Multiple operations happen concurrently

## Extensibility Points

### Adding a New Tab

1. Create `ans/ui/tabs/new_tab.py`:
```python
def create_new_tab(main_window, signal_broker):
    tab = QtWidgets.QWidget()
    # ... create UI ...
    
    references = {'key': widget}
    return tab, references
```

2. Update `ans/ui/tabs/__init__.py`:
```python
from ans.ui.tabs.new_tab import create_new_tab
__all__ = [..., 'create_new_tab']
```

3. Update `main_window.py` `__init__`:
```python
from ans.ui.tabs import create_new_tab
new_tab, refs = create_new_tab(self, self.signal_broker)
self.tabs.addTab(new_tab, "New Tab")
```

### Adding a New Export Format

1. Add function to `ans/utils/export.py`:
```python
def export_story_to_epub(project_path, output_filename):
    # Implementation
    pass
```

2. Add button to Dashboard tab
3. Connect to export function

### Adding a New Signal

1. Add signal to `ans/signals.py`:
```python
class SignalBroker(QtCore.QObject):
    new_signal = QtCore.pyqtSignal(str)
```

2. Emit from sender:
```python
signal_broker.new_signal.emit(data)
```

3. Connect to receiver:
```python
signal_broker.new_signal.connect(handler)
```

## Performance Considerations

### Memory Management
- **Streaming**: LLM responses streamed token-by-token
- **Lazy Loading**: Project files loaded on demand
- **Garbage Collection**: Qt objects properly parented

### CPU Usage
- **Background Thread**: Long operations don't block UI
- **Pause/Resume**: User can pause generation
- **Progressive Rendering**: UI updates incrementally

### Disk I/O
- **Buffered Writes**: Content buffered before writing
- **Append Operations**: Story sections appended incrementally
- **Lock Management**: Minimal lock hold time

## Error Handling

### Retry Mechanism
```python
# LLM calls have automatic retry with exponential backoff
stream = generate_with_retry(
    client, model, prompt,
    max_retries=3  # 1s, 2s, 4s delays
)
```

### Error Propagation
```
Thread Error → SignalBroker.error_signal → ANSWindow → QMessageBox
                    ↓
                Log File
```

### Graceful Degradation
- Optional dependencies (qframelesswindow, python-docx, reportlab)
- Fallback to QMainWindow if frameless unavailable
- Fallback to original ans.py if imports fail

## Configuration

### Application Settings
Stored in `Config/app_settings.txt`:
- Dark mode preference
- LLM model selection
- Temperature setting
- Max retries
- Detail level
- And more...

### Project Settings
Stored in `projects/<name>/config.txt`:
- Current chapter/section
- Progress percentage
- Total chapters
- Section word counts
- And more...

## Testing Strategy

### Unit Testing
- Each module can be tested independently
- Mock SignalBroker for component tests
- Mock ProjectManager for thread tests

### Integration Testing
- `test_integration.py` tests module interactions
- Verifies signal flow
- Checks file operations

### Manual Testing
- See `TESTING.md` for checklist
- Covers all 7 tabs
- Validates signal flow
- Confirms file operations

## Future Enhancements

### Short-term
1. Refactor BackgroundThread to use SignalBroker
2. Add comprehensive unit tests
3. Implement CI/CD pipeline

### Long-term
1. Plugin architecture for tabs
2. Database backend for projects
3. REST API for external integrations
4. Multi-language support
5. Cloud synchronization

## References

- `REFACTORING_COMPLETE.md` - Complete refactoring summary
- `TESTING.md` - Testing procedures
- `requirements.txt` - Dependencies
- Individual module docstrings - Implementation details
