# Automated Novel System (ANS)

![ANS Logo](assets/logo.png)

A professional PyQt5-based desktop application for automated novel generation using local Ollama LLM models. Transform simple story ideas into complete, polished novels through an intelligent AI-powered pipeline that handles every stage of the creative process.

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green.svg)](https://pypi.org/project/PyQt5/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)](https://ollama.ai)

## ✨ Features Overview

### 🎯 Complete Novel Generation Pipeline

**From Concept to Completion** - ANS guides you through a structured workflow:

1. **📝 Synopsis Generation & Refinement**
   - Generate initial synopsis from your idea and tone
   - Automatic refinement for depth, coherence, and tone alignment
   - Unlimited user-guided adjustments with real-time streaming
   - Dual-file system: initial + refined versions

2. **📚 25-Chapter Outline Creation**
   - Intelligent chapter structure with dynamic lengths (5,000-15,000 words)
   - 100-200 word summaries per chapter
   - Key events and character development tracking
   - User-refinable with feedback loops

3. **👥 Character Development**
   - Auto-generate detailed character profiles (JSON format)
   - Name, Age, Background, Traits, Character Arc, Relationships
   - Consistency checks against synopsis
   - Configurable depth: Shallow, Standard, or Deep

4. **🌍 World Building**
   - Comprehensive world details and settings
   - Location descriptions, rules, magic systems
   - Configurable depth: Minimal, Standard, or Comprehensive
   - Automatic consistency with characters and timeline

5. **⏰ Timeline Generation**
   - Chronological event tracking with dates and locations
   - Key events mapped to story progression
   - Character appearances and plot points
   - Refinable with user feedback

6. **✍️ Section-by-Section Writing**
   - Generate novel sections with 2-pass polish system
   - Polish Pass 1: Flow and transitions
   - Polish Pass 2: Vocabulary and style
   - Optional vocabulary enhancement
   - Automatic summary generation (100 words)
   - Context extraction (key events/mood)

### 🎨 Professional User Interface

- **Frameless Window Design** - Custom title bar with Windows Aero snap support
  - Left/right snap (50% screen)
  - Corner snap (25% screen)
  - Top snap (maximize)
  - Seamless multi-monitor transitions
- **7 Organized Tabs** - Streamlined workflow navigation
- **Dark/Light Mode** - Real-time theme switching with custom stylesheets
- **Expandable Windows** - Full-screen dialogs for content review with live streaming updates
- **Context-Aware Buttons** - Smart behavior for active generation vs. loaded content
- **Logo Branding** - Professional appearance with themed logo variants

### 🚀 Advanced Capabilities

- **Real-Time Streaming** - Token-by-token display of LLM responses
- **Per-Token Signal Emission** - Live updates during generation and refinement
- **Automatic Retry Logic** - 3-attempt retry with exponential backoff (1s, 2s, 4s)
- **Pause/Resume Control** - Non-blocking pause with 100ms sleep intervals
- **Progress Tracking** - Real-time word count and completion percentage
- **Milestone Notifications** - Interactive prompts at 80% completion
  - Option to extend (+5 chapters)
  - Option to wrap up (+2 chapters for conclusion)
- **Consistency Checking** - Final validation against characters/world/timeline
  - Plot hole detection
  - Vocabulary issue identification
  - Optional auto-fix with user consent
- **Export Options** - Professional document generation
  - DOCX format with python-docx
  - PDF format with reportlab
  - Formatted chapters, metadata, and styling

### ⚙️ Comprehensive Configuration

- **LLM Settings**
  - Model selection from installed Ollama models
  - Temperature control (0.0-1.0 for creativity adjustment)
  - Auto-refresh model list
- **Generation Parameters**
  - Detail level: Concise, Balanced, Detailed
  - Character depth: Shallow, Standard, Deep
  - World depth: Minimal, Standard, Comprehensive
  - Quality check: Strict, Moderate, Lenient
  - Sections per chapter: 1-10 (default: 3)
  - Max retries: 1-10 (default: 3)
- **Application Settings**
  - Auto-save interval: 1-60 minutes
  - Notifications toggle
  - Auto-approval mode
- **Settings Persistence** - All configurations saved to `Config/app_settings.txt`

## 📂 Project Structure

```
ANS/
├── ans.py                          # Main application (5900+ lines)
├── README.md                       # This file
├── .gitignore                      # Git ignore patterns
│
├── Config/                         # Application-level configuration
│   └── app_settings.txt           # Persisted settings (dark mode, LLM, etc.)
│
├── assets/                         # UI assets and branding
│   ├── logo.png                   # Main logo (light theme)
│   ├── Logo_Dark.png              # Dark theme logo
│   ├── Header.png                 # Light header image
│   └── Header_Dark.png            # Dark header image
│
├── projects/                       # Novel projects (user-created)
│   └── <project_name>/
│       ├── story.txt              # Main novel content
│       ├── log.txt                # Project-specific activity logs
│       ├── config.txt             # Project configuration (key-value pairs)
│       ├── context.txt            # Story context and background info
│       ├── synopsis.txt           # Initial synopsis (never modified)
│       ├── refined_synopsis.txt   # Refined synopsis (updated until approved)
│       ├── outline.txt            # 25-chapter outline with summaries
│       ├── characters.txt         # Character profiles (JSON format)
│       ├── world.txt              # World-building details (JSON format)
│       ├── timeline.txt           # Timeline with dates/locations/events
│       ├── summaries.txt          # Section summaries (100 words each)
│       ├── buffer_backup.txt      # Temporary buffer backup
│       └── drafts/                # Draft versions folder
│
└── .github/
    └── copilot-instructions.md    # Development guidelines and architecture
```

### Project File Descriptions

| File | Purpose | Format |
|------|---------|--------|
| `story.txt` | Complete novel text with chapter markers | Plain text with `=== CHAPTER N ===` markers |
| `log.txt` | Timestamped activity log | ISO timestamp + message per line |
| `config.txt` | Project settings and progress | Key-value pairs (CurrentChapter, Progress, etc.) |
| `synopsis.txt` | Initial AI-generated synopsis | Plain text (immutable after creation) |
| `refined_synopsis.txt` | User-refined synopsis | Plain text (updated during refinement) |
| `outline.txt` | 25-chapter structure | Formatted text with chapter titles and summaries |
| `characters.txt` | Character profiles | JSON array of character objects |
| `world.txt` | World-building information | JSON dictionary |
| `timeline.txt` | Chronological events | Formatted text with dates and locations |
| `summaries.txt` | Section-by-section summaries | Structured text (Chapter X, Section Y format) |
| `context.txt` | Extracted key events and mood | Structured text per section |

## 🚀 Getting Started

### Prerequisites

| Requirement | Version | Purpose |
|------------|---------|---------|
| Python | 3.7+ | Application runtime |
| PyQt5 | Latest | GUI framework |
| Ollama | Latest | Local LLM service |
| python-docx | Latest (optional) | DOCX export functionality |
| reportlab | Latest (optional) | PDF export functionality |
| qframelesswindow | Latest (optional) | Professional frameless window with Aero snap |

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/ShatterPro0f/ANS.git
   cd ANS
   ```

2. **Install Required Python Packages**
   ```bash
   # Core dependencies (required)
   pip install PyQt5 ollama
   
   # Optional dependencies for enhanced features
   pip install python-docx reportlab qframelesswindow
   ```

3. **Install and Configure Ollama**
   - Download from [ollama.ai](https://ollama.ai)
   - Install for your operating system
   - Start the Ollama service (runs on `http://localhost:11434` by default)

4. **Pull an LLM Model**
   ```bash
   # Default recommended model
   ollama pull gemma3:12b
   
   # Alternative models (you can switch in Settings tab)
   ollama pull llama2
   ollama pull mistral
   ```

### Running the Application

```bash
python ans.py
```

The application window will open with 7 tabs. Start by creating or loading a project in the **Initialization** tab.

### First-Time Setup

1. **Test LLM Connection** (Initialization tab)
   - Click "Test Connection" to verify Ollama is running
   - Try a test prompt to confirm model availability

2. **Configure Settings** (Settings tab)
   - Choose your preferred LLM model
   - Adjust temperature for creativity level
   - Set dark/light theme preference
   - Configure generation parameters

3. **Create Your First Project** (Initialization tab)
   - Enter a project name
   - Click "Create Project"
   - Project folder created in `projects/` directory

## 📖 Application Tabs

### Tab-by-Tab Guide

#### 1️⃣ Initialization Tab
**Purpose**: Project management and LLM connection testing

**Features**:
- Create new novel projects
- Load existing projects with automatic data population
- Test Ollama connection and model availability
- Test prompts for model verification
- View project list
- Logo and branding display

**Actions**:
- Enter project name → Click "Create Project"
- Select project from dropdown → Click "Load Project"
- Click "Test Connection" to verify Ollama service
- Enter test prompt → Click "Test Prompt"

---

#### 2️⃣ Novel Idea Tab
**Purpose**: Define your novel concept

**Inputs**:
- **Novel Idea** (multi-line text): Your story concept, premise, plot
- **Tone** (multi-line text): Writing style, atmosphere, themes
- **Target Word Count** (numeric): Soft target for novel length (default: 250,000)

**Actions**:
- Fill in all fields with your novel concept
- Click "Start Generation" to begin the pipeline
- Config string format: `"Idea: {text}, Tone: {text}, Soft Target: {count}"`

---

#### 3️⃣ Planning Tab
**Purpose**: Generate and refine all pre-writing elements

**Displays** (all with Expand buttons for full-screen view):
- **Initial Synopsis**: First AI-generated synopsis (streaming display)
- **Refined Synopsis**: Automatically polished version
- **Outline**: 25-chapter structure with summaries
- **Characters**: Character profiles in JSON format
- **World**: World-building details and settings
- **Timeline**: Chronological events with dates

**Workflow**:
1. **Synopsis Phase**:
   - Initial synopsis streams → Automatic refinement streams
   - Review refined synopsis → Approve or Adjust with feedback
   - Unlimited refinement iterations

2. **Outline Phase** (after synopsis approval):
   - 25-chapter outline generates → Review → Approve or Adjust
   - Each chapter includes: title, summary, key events, character developments

3. **Characters Phase** (after outline approval):
   - Character profiles generate → Review → Approve or Adjust
   - Profiles include: Name, Age, Background, Traits, Arc, Relationships

4. **World Phase** (after characters approval):
   - World-building details generate → Review → Approve or Adjust

5. **Timeline Phase** (after world approval):
   - Timeline with dates/locations generates → Review → Approve or Adjust
   - Approval transitions to Writing tab

**Buttons**:
- **Approve**: Accept current content and proceed to next phase
- **Adjust**: Provide feedback for refinement (iterative)
- **Expand**: Open full-screen dialog with live streaming updates

**Context-Aware Behavior**:
- **Active Generation**: Buttons emit signals for refinement loops
- **Loaded Content**: Buttons log guidance for manual editing

---

#### 4️⃣ Writing Tab
**Purpose**: Generate novel sections chapter-by-chapter

**Display**:
- **Draft Display**: Current section with streaming updates
- **Expand Button**: Full-screen view with live updates

**Controls**:
- **Approve Section**: Accept section, append to story.txt, generate summary
- **Adjust Section**: Request refinement with feedback
- **Pause**: Stop generation (resume later)
- **Resume**: Continue paused generation

**Section Generation Process**:
1. Generate draft section (based on outline, characters, world, timeline, context)
2. Polish Pass 1: Flow and transitions
3. Polish Pass 2: Vocabulary and style
4. Optional: Vocabulary enhancement
5. Display for user review

**Section Approval Process**:
1. Append to `story.txt` with chapter heading (if new chapter)
2. Generate 100-word summary → Save to `summaries.txt`
3. Extract key events and mood → Update `context.txt`
4. Update progress tracking (word count, chapter, section)
5. Check for chapter completion
6. Check for milestone (80% completion)
7. Check for novel completion

**Progress Milestones**:
- **80% Completion**: Dialog prompts user
  - **Extend**: Add 5 chapters for more development
  - **Wrap Up**: Add 2 chapters for conclusion
- **100% Completion**: Final consistency check triggers

---

#### 5️⃣ Logs Tab
**Purpose**: View project activity history

**Features**:
- Read-only text display of `log.txt`
- Timestamped entries (ISO format: `YYYY-MM-DD HH:MM:SS`)
- Auto-refresh when project loads
- All user actions logged automatically

**Log Examples**:
```
2025-11-21 10:30:15 - Project loaded: MyNovel
2025-11-21 10:31:42 - Novel generation started
2025-11-21 10:32:18 - Synopsis approved
2025-11-21 10:35:04 - Outline generated (5843 tokens)
2025-11-21 10:40:22 - Section 1 of Chapter 1 approved and processed (2847 words)
```

---

#### 6️⃣ Dashboard Tab
**Purpose**: Track progress and export completed novels

**Progress Display**:
- Current project status
- Progress percentage (word count / target)
- Progress bar visualization (0-100%)

**Export Features**:
- **Export to DOCX**: Generate formatted Word document
  - Title page with project metadata
  - Chapter headings (Heading 1 style)
  - Body paragraphs (justified alignment)
  - Saved as `{project_name}_novel.docx`
  
- **Export to PDF**: Generate formatted PDF document
  - Title page with project metadata
  - Chapter headings (14pt)
  - Body paragraphs with proper leading
  - Saved as `{project_name}_novel.pdf`

**Export Status**: Visual feedback (✓ success, ✗ failure)

---

#### 7️⃣ Settings Tab
**Purpose**: Configure application behavior and appearance

**Theme Settings**:
- Dark Mode toggle (real-time switch)
- Custom stylesheets for light/dark themes
- Logo variants for theme consistency

**LLM Configuration**:
- Model selection dropdown (auto-populated from Ollama)
- Temperature slider (0.0 = deterministic, 1.0 = creative)
- Refresh Models button (re-scan Ollama)

**Application Settings**:
- Auto-save interval: 1-60 minutes
- Notifications: Enable/disable
- Auto-approval: Skip manual review (not recommended)

**Generation Parameters**:
- Max retries: 1-10 (default: 3)
- Detail level: Concise, Balanced, Detailed
- Character depth: Shallow, Standard, Deep
- World depth: Minimal, Standard, Comprehensive
- Quality check: Strict, Moderate, Lenient
- Sections per chapter: 1-10 (default: 3)

**Application Info**:
- Version display
- About dialog with feature list

**Settings Persistence**: All settings auto-save to `Config/app_settings.txt`

---

## 🔄 Complete Usage Workflow

### Step-by-Step Novel Generation

```
1. [Initialization] Create/Load Project
   └─> Project structure created in projects/ folder

2. [Novel Idea] Define Concept
   └─> Enter idea, tone, target word count
   └─> Click "Start Generation"

3. [Planning] Synopsis Generation & Refinement
   └─> Initial synopsis streams (auto)
   └─> Refined synopsis streams (auto)
   └─> User: Approve or Adjust
   └─> [If Adjust: Provide feedback → Refinement loop → Repeat]

4. [Planning] Outline Generation
   └─> 25-chapter outline streams
   └─> User: Approve or Adjust
   └─> [If Adjust: Provide feedback → Refinement loop → Repeat]

5. [Planning] Character Generation
   └─> Character profiles stream (JSON)
   └─> User: Approve or Adjust
   └─> [If Adjust: Provide feedback → Refinement loop → Repeat]

6. [Planning] World Building
   └─> World details stream (JSON)
   └─> User: Approve or Adjust
   └─> [If Adjust: Provide feedback → Refinement loop → Repeat]

7. [Planning] Timeline Generation
   └─> Timeline streams (dates/events)
   └─> User: Approve or Adjust
   └─> [If Adjust: Provide feedback → Refinement loop → Repeat]
   └─> Approval → Transition to Writing Tab

8. [Writing] Section-by-Section Generation
   └─> For each section (3 per chapter default):
       ├─> Generate draft section
       ├─> Polish Pass 1 (flow/transitions)
       ├─> Polish Pass 2 (vocabulary/style)
       ├─> Display for review
       ├─> User: Approve or Adjust
       ├─> [If Adjust: Refinement with feedback → Repeat]
       ├─> [If Approve:]
       │   ├─> Append to story.txt
       │   ├─> Generate summary
       │   ├─> Extract context
       │   ├─> Update progress
       │   └─> Check milestones
       └─> Proceed to next section

9. [Writing] Milestone Handling (80% Progress)
   └─> Dialog: Extend (+5 chapters) or Wrap Up (+2 chapters)
   └─> Continue section generation

10. [Writing] Completion
    └─> All chapters complete
    └─> Final consistency check runs
    └─> [If issues found:]
        ├─> Display issues to user
        ├─> User: Auto-fix or Skip
        └─> [If Auto-fix: Refinement process]
    └─> Novel complete message

11. [Dashboard] Export
    └─> Export to DOCX (formatted Word document)
    └─> Export to PDF (formatted PDF document)
```

### Workflow Controls

**Pause/Resume**:
- Click "Pause" during any generation
- Non-blocking pause (100ms sleep intervals)
- Click "Resume" to continue from pause point

**Feedback Refinement**:
- Any content can be adjusted with feedback
- Unlimited refinement iterations
- System maintains context for consistency

**Context-Aware Loading**:
- Load existing project at any stage
- Planning tab auto-populates with existing data
- Continue generation from last checkpoint

## 🔧 Technical Architecture

### Signal-Driven Communication

ANS uses PyQt5's signal/slot mechanism for component communication:

#### Window Signals (ANSWindow)
| Signal | Parameters | Purpose |
|--------|-----------|---------|
| `start_signal` | `str` (config) | Initiate novel generation with config string |
| `approve_signal` | `str` (content_type) | Approve content (synopsis, outline, characters, etc.) |
| `adjust_signal` | `str, str` (type, feedback) | Request adjustments with user feedback |
| `refinement_start` | None | Signal synopsis refinement phase starting |
| `outline_refinement_start` | None | Signal outline refinement phase starting |
| `timeline_refinement_start` | None | Signal timeline refinement phase starting |
| `pause_signal` | None | Pause current generation |
| `new_synopsis` | `str` | Emit refined synopsis text (streaming) |
| `new_outline` | `str` | Emit generated outline text (streaming) |
| `new_characters` | `str` | Emit character JSON array (streaming) |
| `new_world` | `str` | Emit world-building JSON dict (streaming) |
| `new_timeline` | `str` | Emit timeline text (streaming) |
| `new_draft` | `str` | Emit polished draft section (streaming) |
| `log_update` | `str` | Log event message (auto-writes to log.txt) |
| `error_signal` | `str` | Error notification (shows QMessageBox) |

#### Thread Signals (BackgroundThread)
| Signal | Parameters | Purpose |
|--------|-----------|---------|
| `processing_finished` | `str` | Processing complete with result |
| `processing_error` | `str` | Error during processing |
| `processing_progress` | `str` | Progress update messages |
| `init_complete` | None | Initialization phase complete |
| `synopsis_ready` | `str` | Initial synopsis generated (streaming) |

### Threading Model

- **Main Thread (UI)**: All Qt widgets, user interaction
- **BackgroundThread (QThread)**: All LLM calls, file I/O, long operations
- **Signal/Slot Communication**: Thread-safe UI updates
- **Non-Blocking Pause**: 100ms sleep intervals for responsive control

### Key Classes

#### ANSWindow
- **Base Class**: `FramelessMainWindow` (from qframelesswindow library, fallback to QMainWindow)
- **Window Properties**:
  - Size: 1200x800 pixels
  - Custom title bar with window controls
  - Windows Aero snap support (50% left/right, 25% corners, maximize top)
  - Dark/light mode with theme-aware logo switching
- **Tab Management**: 7 tabs with dedicated creation methods
- **Project Management**: In-memory `current_project` dictionary for session persistence
- **Settings Sync**: `_sync_settings_to_thread()` before each generation

#### CustomTitleBar
- **Base Class**: `QWidget`
- **Features**:
  - Logo display (24px, theme-aware)
  - Window title label
  - Minimize, Maximize/Restore, Close buttons
  - Windows 11 styling (red close button on hover)
  - Mouse event handlers for window dragging
  - Double-click to maximize/restore
- **Integration**: Installed via `setTitleBar()` for automatic snap handling

#### BackgroundThread
- **Base Class**: `QThread`
- **Responsibilities**:
  - All LLM API calls (21 calls across 15 methods)
  - File I/O operations
  - Content generation and refinement
  - Progress tracking and logging
- **Key Features**:
  - Automatic retry logic with exponential backoff
  - Per-token streaming with signal emission
  - Pause/resume support in all loops
  - Temperature and model configuration
  - In-memory synopsis persistence

### Retry Logic

**Implementation**: `_generate_with_retry(parent_window, model, prompt, max_retries=None)`

- **Default Retries**: 3 attempts (configurable 1-10)
- **Backoff**: Exponential (1s, 2s, 4s)
- **Return**: Stream iterator on success, None on failure
- **Error Handling**: Emits `error_signal` on final failure
- **Applied To**: All 21 LLM generate calls

### Per-Token Streaming

**Refinement Methods** (all emit signal for EVERY token):
1. `refine_synopsis_with_feedback()` → `new_synopsis`
2. `refine_outline_with_feedback()` → `new_outline`
3. `refine_characters_with_feedback()` → `new_characters`
4. `refine_world_with_feedback()` → `new_world`
5. `refine_timeline_with_feedback()` → `new_timeline`
6. `refine_section_with_feedback()` → `new_draft` (3 passes)

**Benefits**:
- Live UI updates during generation
- User sees incremental progress
- Responsive expanded windows
- Better UX for long-running operations

### File Management

**Synopsis System** (two-file approach):
- `synopsis.txt`: Initial version (immutable after creation)
- `refined_synopsis.txt`: Latest refined version (updated until approved)
- In-memory: `BackgroundThread.synopsis` persists throughout session
- Loading priority: `refined_synopsis.txt` → fallback to `synopsis.txt`

**Project Structure Creation**: `create_project_structure(project_path)`
- Creates all necessary files and folders
- UTF-8 encoding for all text files
- Initializes log with timestamp
- Creates `drafts/` folder for versioning

### Context-Aware Buttons

**Detection Pattern**: Check `if self.thread.isRunning()`

- **Active Generation** (`True`):
  - Emit signals to trigger refinement loops
  - Buttons control workflow progression
  
- **Loaded Content** (`False`):
  - Log helpful guidance messages
  - Direct user to manual editing or new generation
  - Support for editing previously saved projects

### Configuration Management

**Settings File**: `Config/app_settings.txt` (key-value format)

```
DarkMode: True/False
Model: gemma3:12b
Temperature: 0.7
AutoSave: 15
Notifications: True
AutoApproval: False
MaxRetries: 3
DetailLevel: balanced
CharacterDepth: standard
WorldDepth: standard
QualityCheck: moderate
SectionsPerChapter: 3
```

**Persistence**:
- Auto-save on every control change
- Load on application startup
- Sync to BackgroundThread before generation

### Export System

**DOCX Export**: `export_story_to_docx(project_path, output_filename)`
- Uses `python-docx` library
- Title page with metadata (24pt bold)
- Chapter headings (Heading 1 style)
- Body paragraphs (justified alignment)
- Blank line preservation

**PDF Export**: `export_story_to_pdf(project_path, output_filename)`
- Uses `reportlab` library
- Title page with metadata (24pt)
- Chapter headings (14pt)
- Body paragraphs with proper leading
- Chapter spacing

## 🎨 UI Features

### Frameless Window

**Library**: `qframelesswindow` (optional, graceful fallback to QMainWindow)

**Snap Behavior**:
- Drag to left edge → 50% width left half
- Drag to right edge → 50% width right half
- Drag to top edge → Maximize
- Drag to top-left corner → 25% top-left quadrant
- Drag to top-right corner → 25% top-right quadrant
- Drag to bottom-left corner → 25% bottom-left quadrant
- Drag to bottom-right corner → 25% bottom-right quadrant

**Multi-Monitor Support**: Seamless transitions between displays

### Expandable Windows

**Features**:
- Full-screen dialog (1000x800px)
- Live streaming updates during generation
- Preserved scroll position
- Dictionary tracking: `expanded_text_widgets`
- Close handler: `_on_expanded_window_close()`

### Dark/Light Mode

**Light Mode**:
- White background (#ffffff)
- Black text (#000000)
- Light gray buttons (#f0f0f0)
- Standard logo variant

**Dark Mode**:
- Dark background (#1e1e1e)
- Light text (#e0e0e0)
- Dark buttons (#2d2d2d)
- Dark logo variant

**Real-Time Switching**: Updates all UI elements immediately, including title bar

## 🧪 Testing & Development

### Code Statistics

- **Main Application**: 5,900+ lines (ans.py)
- **Classes**: 3 (ANSWindow, BackgroundThread, CustomTitleBar)
- **Tabs**: 7 with dedicated creation methods
- **Signals**: 14 total (window + thread)
- **LLM Methods**: 15 with 21 total API calls
- **Configurable Parameters**: 8 (model, temperature, retries, depth, quality, etc.)

### Development Guidelines

**Architecture Principles**:
- Signal/slot for all inter-component communication
- Background threads for long operations (>100ms)
- Never block UI thread
- Thread-safe UI updates via signals
- UTF-8 encoding for all file I/O
- Cross-platform path handling with `os.path.join()`

**Best Practices**:
1. Project file I/O with context-aware paths
2. Background thread operations (never block UI)
3. Event logging for all user actions
4. Signal/slot architecture (no direct coupling)
5. Error handling with `error_signal` emission
6. Tab implementation pattern (dedicated creation methods)
7. Project data access validation
8. Thread-safe UI updates (signals only)
9. Configuration string format consistency
10. Timestamp and logging format (ISO 8601)

**Code Style**:
- PEP 8 naming conventions
- Docstrings for all classes and methods
- Type hints where applicable
- Comprehensive inline comments for complex logic

## 📊 Feature Comparison

| Feature | ANS | Traditional Writing |
|---------|-----|-------------------|
| **Synopsis Generation** | AI-powered, auto-refined | Manual brainstorming |
| **Outline Structure** | 25 chapters, auto-generated | Manual plotting |
| **Character Development** | Detailed profiles, consistency checks | Manual character sheets |
| **World Building** | Comprehensive, structured | Manual wiki/notes |
| **Timeline Management** | Automatic chronology | Manual tracking |
| **Section Writing** | AI-assisted with polish | 100% manual |
| **Progress Tracking** | Real-time percentage | Manual word counts |
| **Consistency Checking** | Automated validation | Manual review |
| **Export Options** | DOCX/PDF with formatting | Copy-paste or export |
| **Streaming Feedback** | Live token display | N/A |
| **Pause/Resume** | Any time during generation | N/A |

## ❓ FAQ

### General Questions

**Q: How long does it take to generate a complete novel?**  
A: Depends on LLM model speed, target word count, and sections per chapter. For a 250,000-word novel with default settings (3 sections/chapter), expect 20-40 hours of generation time. Use pause/resume to work in sessions.

**Q: Can I use different LLM models?**  
A: Yes! Install any Ollama model (`ollama pull <model>`), then select it in Settings → LLM Configuration. Tested with gemma3:12b, llama2, mistral, and others.

**Q: What happens if generation fails or crashes?**  
A: All generated content is saved immediately. Reload your project to continue from the last saved section. Check logs tab for error details.

**Q: Can I edit generated content manually?**  
A: Absolutely! All content is stored in plain text/JSON files in your project folder. Edit with any text editor, then reload the project.

**Q: Does this require an internet connection?**  
A: No. Ollama runs locally on your machine. No data is sent to external servers.

### Technical Questions

**Q: Why is the window frameless?**  
A: Professional appearance with custom branding. The qframelesswindow library provides Windows Aero snap functionality. Falls back to standard window if library unavailable.

**Q: How does the two-file synopsis system work?**  
A: `synopsis.txt` preserves your original generated synopsis. `refined_synopsis.txt` is updated with each refinement iteration. Load either version when continuing work.

**Q: What's the purpose of context.txt?**  
A: Tracks key events and mood from each section. Used by the LLM to maintain story consistency in subsequent sections.

**Q: Can I change section length or chapter structure?**  
A: Sections per chapter is configurable (1-10) in Settings. Chapter length is dynamically determined by the LLM based on outline (5,000-15,000 words typical).

**Q: How accurate is the consistency checking?**  
A: Checks for character inconsistencies, plot holes, and vocabulary issues against characters.txt, world.txt, and timeline.txt. Not perfect—manual review recommended.

### Workflow Questions

**Q: Can I skip phases (e.g., go straight to writing)?**  
A: No. The pipeline ensures consistency. Each phase builds on previous phases. However, you can load existing project data and continue from any checkpoint.

**Q: What if I don't like the generated content?**  
A: Click "Adjust" and provide specific feedback. The system will refine unlimited times. For major changes, restart generation with different inputs.

**Q: Can I extend the novel after reaching 100%?**  
A: Yes! At 80% completion, you're prompted to extend (+5 chapters) or wrap up (+2 chapters). You can also manually modify config.txt → TotalChapters.

**Q: Does auto-approval skip refinement?**  
A: No. Auto-approval skips the manual review step. All content still goes through initial generation + automatic refinement before approval.

## 🐛 Troubleshooting

### Connection Issues

**Problem**: "Failed to connect to Ollama" error  
**Solution**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start Ollama service
# Windows: Start Ollama from Start Menu
# macOS: Open Ollama app
# Linux: ollama serve
```

**Problem**: "Model not found" error  
**Solution**:
```bash
# List installed models
ollama list

# Pull missing model
ollama pull gemma3:12b

# Refresh model list in ANS Settings tab
```

### Generation Issues

**Problem**: Generation is very slow  
**Solutions**:
- Use smaller model (e.g., llama2:7b instead of gemma3:12b)
- Increase temperature for faster, more creative responses
- Set detail level to "Concise" in Settings
- Close other resource-intensive applications

**Problem**: Generation stops mid-section  
**Solutions**:
- Check Ollama logs for errors
- Verify sufficient disk space for model
- Check system RAM (large models need 16GB+)
- Try clicking "Resume" button
- If persistent, restart Ollama service

**Problem**: "Retry failed after 3 attempts" errors  
**Solutions**:
- Increase max retries in Settings (up to 10)
- Check Ollama service is responsive: `curl http://localhost:11434/api/tags`
- Restart Ollama service
- Switch to different model

### Export Issues

**Problem**: DOCX export fails  
**Solution**:
```bash
pip install --upgrade python-docx
```

**Problem**: PDF export fails  
**Solution**:
```bash
pip install --upgrade reportlab
```

**Problem**: Export file is empty or corrupted  
**Solutions**:
- Ensure story.txt has content (check in project folder)
- Verify project is fully loaded in Initialization tab
- Check Dashboard tab shows progress > 0%
- Try exporting to different format

### UI Issues

**Problem**: Window controls don't work  
**Solution**:
```bash
# Install frameless window library
pip install qframelesswindow

# Or use standard window (automatic fallback)
```

**Problem**: Dark mode doesn't apply  
**Solutions**:
- Toggle dark mode checkbox in Settings tab
- Restart application
- Check Config/app_settings.txt for `DarkMode: True`

**Problem**: Expanded windows don't show streaming updates  
**Solution**: This is expected for loaded content. Streaming only works during active generation (thread.isRunning() == True).

### File System Issues

**Problem**: "Permission denied" when creating project  
**Solutions**:
- Run application with appropriate permissions
- Check projects/ folder is writable
- Move ANS to non-system directory (e.g., Documents)

**Problem**: Project files are corrupted  
**Solutions**:
- Check backups in project's drafts/ folder
- Look for buffer_backup.txt with recent content
- Check log.txt for error messages before corruption

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make changes following the Best Practices (see .github/copilot-instructions.md)
4. Test thoroughly with various scenarios
5. Commit with descriptive messages: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Guidelines

**See**: `.github/copilot-instructions.md` for comprehensive architecture documentation

**Key Principles**:
- All inter-component communication via signals/slots
- Long operations in BackgroundThread (never block UI)
- UTF-8 encoding for all file I/O
- Cross-platform path handling with `os.path.join()`
- PEP 8 naming conventions
- Docstrings for all classes and methods

**Before Submitting PR**:
- [ ] Code follows Best Practices (sections 1-10 in copilot-instructions.md)
- [ ] All new features have corresponding UI components
- [ ] Signals/slots used for component communication
- [ ] No direct UI updates from background threads
- [ ] All file operations use UTF-8 encoding
- [ ] Error handling with `error_signal` emission
- [ ] Logging for all user-initiated actions
- [ ] Settings persistence if new config added
- [ ] Update copilot-instructions.md with changes

### Areas for Contribution

**High Priority**:
- Auto-fix logic for consistency issues (parse and target refinements)
- Dashboard tab project statistics and completion metrics
- Automated testing suite expansion
- Multi-language support (i18n)
- Plugin system for custom generators

**Medium Priority**:
- Alternative export formats (EPUB, HTML)
- Template system for different genres
- Character relationship graph visualization
- Timeline visualization
- Undo/redo functionality

**Documentation**:
- Video tutorials for workflow
- Screenshot gallery of UI
- Example generated novels (anonymized)
- Performance optimization guide
- Model comparison benchmarks

## 📄 License

This project is open source. See LICENSE file for details.

## 🙏 Acknowledgments

- **Ollama**: Local LLM inference engine
- **PyQt5**: Powerful cross-platform GUI framework
- **qframelesswindow**: Professional frameless window implementation
- **python-docx**: Word document generation
- **reportlab**: PDF generation
- **Gemma/Llama/Mistral**: Open-source LLM models

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/ShatterPro0f/ANS/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ShatterPro0f/ANS/discussions)
- **Documentation**: See `.github/copilot-instructions.md` for technical details

---

**Built with ❤️ for writers who want AI as a creative partner, not a replacement.**
