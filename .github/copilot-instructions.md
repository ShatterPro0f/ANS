<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Automated Novel System (ANS) Project

This workspace contains a PyQt5-based desktop application for automated novel generation and management.

### CRITICAL: Update Instructions After Every Response
**IMPORTANT**: After completing any task or implementing any feature, you MUST update this copilot-instructions.md file to reflect the changes. This ensures that subsequent responses have accurate context about the current state of the project. Update the following sections as needed:
- Feature/component descriptions
- Signal definitions
- Backend thread methods
- Frontend implementations
- Project statistics
- Future development areas

### Project Overview
- **Language**: Python 3.7+
- **GUI Framework**: PyQt5
- **Main Entry Point**: `ans.py`
- **Architecture**: Tab-based interface with signal-driven communication

### Key Components

#### ANSWindow Class (UPDATED - November 21, 2025)
The main application window now uses **FramelessMainWindow** from qframelesswindow library:
- **Base Class**: `FramelessMainWindow` (when library available) or `QMainWindow` (fallback)
- Window title: "Automated Novel System"
- Window icon: Logo from `assets/logo.png` (set via `self.setWindowIcon()`)
- Default geometry: 1200x800 pixels
- Tab widget with 7 tabs: Initialization, Novel Idea, Planning, Writing, Logs, Dashboard, Settings
- Custom signals for inter-component communication
- **Professional Frameless Window**:
  - Custom title bar installed via `setTitleBar()` method
  - Automatic Windows Aero snap support (left/right 50%, corners 25%, top maximize)
  - All window controls work through library's native event handler
  - Seamless multi-monitor snap transitions
  - Dark/light mode switching updates title bar in real-time
- **Logo Display in Initialization Tab**:
  - Logo image displayed at top center (80px height) with title and subtitle
  - Logo file: `assets/logo.png` (256x256px, 1471 bytes)
  - Title: "Automated Novel System" (18pt bold, dark blue)
  - Subtitle: "AI-Powered Creative Writing Assistant" (11pt gray)
  - Separator line below logo header
  - Creates professional branding appearance

#### CustomTitleBar Class (UPDATED - November 21, 2025)
Custom title bar widget integrated with qframelesswindow library for Windows Aero snap support:
- **Purpose**: Provide styled title bar with logo branding and window controls
- **Integration**: Installed via `FramelessMainWindow.setTitleBar()` for automatic snap handling
- **Layout**: Horizontal layout with icon (24px), title label, spacer, and 3 control buttons
- **Size**: Fixed height 32px for proper window layout spacing
- **Key Features**:
  - Window icon display scaled from light/dark logo paths
  - Window title text left-aligned after icon
  - Spacer automatically pushes buttons to the right
  - Three control buttons: Minimize (−), Maximize (□/▢), Close (✕)
  - Dark mode support with real-time color updates
  - Windows 11 standard button sizing (40x32px)
  - Red close button on hover (#e81123 hover, #c41410 pressed)
- **Color Support** (`set_dark_mode(is_dark)`):
  - Light mode: White background, black text, light gray buttons
  - Dark mode: #1e1e1e background, #e0e0e0 text, darker buttons
  - Switches logo to appropriate theme variant
  - Real-time updates on dark mode toggle
- **Window Control Methods**:
  - `minimize_window()`: Calls `self.parent_window.showMinimized()`
  - `maximize_window()`: Toggles between maximize/restore states
  - `close_window()`: Calls `self.parent_window.close()`
- **Mouse Event Handlers**:
  - `mousePressEvent()`: Initiates window drag from title bar
  - `mouseMoveEvent()`: Moves window following cursor
  - `mouseDoubleClickEvent()`: Toggles maximize on double-click
- **Visual Design**: Hover effects, button state changes, smooth transitions, proper spacing

#### Synopsis System
The application uses a two-file system for synopsis management to maintain clear separation between initial and refined versions:

**Files:**
- `synopsis.txt` - Initial synopsis (written once during generation, never modified after initial writing)
- `refined_synopsis.txt` - Refined synopsis (overwritten with each refinement iteration until approved)
- `summaries.txt` - Section summaries (separate from synopsis, used for chapter/section summaries after approval)

**In-Memory State:**
- `BackgroundThread.synopsis` - Stores current synopsis in memory during processing
- Persists for entire session duration
- Automatically synced between files and memory

**Loading Behavior:**
- `BackgroundThread.load_synopsis_from_project(project_path)` - Loads synopsis when needed
  - Prioritizes `refined_synopsis.txt` (latest refined version)
  - Falls back to `synopsis.txt` (initial version)
  - Automatically called by: generate_outline, generate_characters when synopsis not in memory
  - Allows seamless continuation of work on saved projects

**Used By:**
- `run()` - Initial generation writes to synopsis.txt
- `run()` refinement phase - Writes refined version to refined_synopsis.txt
- `refine_synopsis_with_feedback()` - Updates refined_synopsis.txt on each feedback iteration
- `generate_outline()` - Uses synopsis for outline context
- `generate_characters()` - Uses synopsis for character consistency
- `_populate_planning_displays()` - Loads both files for display on project load
The application supports multiple independent novel projects organized in a `projects/` folder:

**App-Level Configuration (`Config/` folder, created on startup):**
- `Config/app_settings.txt` - Application-wide settings

**Project-Level Structure (created via `create_project_structure(project_name)`):**
- `projects/<project_name>/story.txt` - Main story content
- `projects/<project_name>/log.txt` - Project-specific logs with timestamps
- `projects/<project_name>/config.txt` - Project configuration (key-value pairs)
- `projects/<project_name>/context.txt` - Story context and background
- `projects/<project_name>/characters.txt` - Character data (JSON format)
- `projects/<project_name>/world.txt` - World-building data (JSON format)
- `projects/<project_name>/synopsis.txt` - Initial synopsis (written once, never modified)
- `projects/<project_name>/refined_synopsis.txt` - Refined synopsis (overwritten with each refinement iteration)
- `projects/<project_name>/summaries.txt` - Story summaries and section outlines (generated after sections are approved)
- `projects/<project_name>/outline.txt` - Generated 25-chapter novel outline with chapter summaries
- `projects/<project_name>/timeline.txt` - Timeline with dates, locations, and events
- `projects/<project_name>/buffer_backup.txt` - Temporary buffer backup
- `projects/<project_name>/drafts/` - Folder for draft versions
- Placeholders: `story_backup.txt`, `log_backup.txt` (not auto-created)

**Method: `create_project_structure(project_path)`**
- Creates project directory and all necessary files/folders
- Initializes log with timestamp and "Project initialized" message
- All files use UTF-8 encoding

**Assets Structure (`assets/` folder, created on startup):**
- `assets/logo.png` - ANS application logo (256x256px, PNG format)
  - Contains book and gear imagery representing automated creative writing
  - Used in window icon and Initialization tab header
  - Dark blue background (#1a2f4d) with darker blue accents (#001f3f)

#### Project Loading System
The application supports loading and managing existing projects with session persistence:

**Methods:**
- `load_project(project_name)` - Load existing project and store in `self.current_project` for runtime persistence
  - Validates all required project files exist
  - Loads all project data into memory as a dictionary
  - Logs the load action to `Config/app_settings.txt`
  - **NEW**: Automatically populates Planning tab displays with existing project data via `_populate_planning_displays()`
- `get_project_list()` - Returns sorted list of all existing projects in `projects/` folder
- `get_current_project()` - Returns the currently loaded project data (None if no project loaded)
- `_read_file(filepath)` - Utility to safely read file content
- `_populate_planning_displays()` - **NEW** - Populates Planning tab text displays with existing project data on project load
  - Loads outline from `outline.txt` if it exists
  - Loads characters, world, and timeline from project data
  - Displays data immediately so user sees where they left off
  - Handles JSON parsing and formatting for characters/world data
  - Logs completion to project log

**Session Persistence:**
- `self.current_project` stores loaded project data in memory for the duration of the app session
- Remains accessible across tabs and components while app is running
- Contains: name, path, story, log, config, context, characters, world, summaries, buffer_backup
- **NEW**: Planning displays automatically refreshed with existing data when project is loaded

#### Signals
Used for event communication between components:
- `start_signal(str)` - Initiate novel generation with config string
- `approve_signal(str)` - Approve content (emits content type, e.g., 'synopsis' or 'outline')
- `adjust_signal(str, str)` - Request adjustments (emits content type and feedback)
- `refinement_start()` - Signal that synopsis refinement phase is starting
- `outline_refinement_start()` - Signal that outline refinement phase is starting
- `pause_signal()` - Pause operations
- `new_synopsis(str)` - New refined synopsis available
- `new_outline(str)` - New outline available (initial or refined)
- `new_characters(str)` - New character JSON array available
- `new_draft(str)` - New draft available
- `log_update(str)` - Log updates (emitted with message, writes to project log.txt)
- `error_signal(str)` - Error notifications (shows QMessageBox and logs)
- `test_result_signal(str)` - Test results from background threads

#### CustomTitleBar Class (NEW - Lines 2594-2734)
Custom frameless window title bar for complete UI control and professional appearance:
- **Purpose**: Replace OS-level title bar with Qt-rendered widget
- **Parent Class**: Inherits from QWidget
- **Layout**: Horizontal layout with icon, title label, spacer, and control buttons
- **Key Features**:
  - Window icon display (24px height, scaled from logo)
  - Window title text (center-aligned)
  - Spacer to push buttons to right
  - Three control buttons: Minimize (−), Maximize (□/▢), Close (✕)
  - Dark mode support with real-time color updates
  - Windows 11 standard button sizing (36x24px)
  - Red close button on hover (#e81123 hover, #c41410 pressed, white text)
- **Initialization** (`__init__(parent_window, title, icon_path)`):
  - Creates vertical layout for title bar widget
  - Loads and scales window icon from `icon_path`
  - Creates buttons with QAction-like appearance
  - Sets initial colors based on theme
- **Color Support** (`set_dark_mode(is_dark)`):
  - Light mode: White background, black text, light gray buttons
  - Dark mode: #1e1e1e background, #e0e0e0 text, darker buttons
  - Updates all label and button colors instantly
  - Called on dark mode toggle for responsive UI
- **Mouse Event Handlers**:
  - `mousePressEvent()`: Detects left-click on title bar to initiate drag (stores cursor globalPos)
  - `mouseMoveEvent()`: Implements window movement when dragging (uses globalPos - startPos)
  - `mouseDoubleClickEvent()`: Double-click on title bar toggles maximize/restore
- **Window Control Methods**:
  - `minimize_window()`: Calls `self.parent_window.showMinimized()`
  - `maximize_window()`: Toggles between `showMaximized()` and `showNormal()`, updates icon (□ → ▢)
  - `close_window()`: Calls `self.parent_window.close()`
- **Button Connections**: All three buttons connected to respective control methods via clicked signal
- **Visual Design**:
  - Buttons have hover effects (color changes on hover)
  - Close button is red on hover (Windows 11 style)
  - Buttons have pressed effects (darker color when clicked)
  - Smooth color transitions for visual feedback
  - 4px button margins for spacing

#### BackgroundThread Class
Thread for long-running operations (novel generation, processing):
- Inherits from `QtCore.QThread`
- Stores input configuration in `self.inputs`
- **Stores generated/refined synopsis in memory**: `self.synopsis` attribute persists throughout session
- **Method to load synopsis from project**: `load_synopsis_from_project(project_path)` 
  - Attempts to load refined_synopsis.txt first (latest version)
  - Falls back to synopsis.txt if refined version doesn't exist
  - Handles both file loading scenarios for saved projects
- **Configurable Settings** (with defaults, synced from ANSWindow settings via `_sync_settings_to_thread()`):
  - `llm_model` - LLM model name (default: 'gemma3:12b', synced from Settings tab model selection) ✓ ALL 20+ LLM CALLS UPDATED
  - `temperature` - LLM temperature/creativity (default: 0.7, range 0.0-1.0, synced from Settings tab slider) ✓ APPLIED TO ALL CALLS
  - `max_retries` - Maximum retry attempts for LLM calls (default: 3, range 1-10)
  - `detail_level` - Generation detail level (default: 'balanced', options: 'concise', 'balanced', 'detailed')
  - `character_depth` - Character profile depth (default: 'standard', options: 'shallow', 'standard', 'deep')
  - `world_depth` - World-building depth (default: 'standard', options: 'minimal', 'standard', 'comprehensive')
  - `quality_check` - Quality check strictness (default: 'moderate', options: 'strict', 'moderate', 'lenient')
  - `sections_per_chapter` - Sections generated per chapter (default: 3, range 1-10)
  - **CRITICAL FIX**: All LLM calls now use `model=self.llm_model` instead of hardcoded `model='gemma3:12b'`
- **Signals emitted**: 
  - `processing_finished(str)` - Processing complete with result
  - `processing_error(str)` - Error during processing
  - `processing_progress(str)` - Progress updates
  - `log_update(str)` - Logging from thread
  - `init_complete()` - Initialization phase complete
  - `synopsis_ready(str)` - Initial synopsis generated (streamed tokens)
  - `new_synopsis(str)` - Refined synopsis ready (streamed tokens)
  - `new_outline(str)` - Generated or refined 25-chapter outline (streamed tokens)
  - `new_characters(str)` - Generated character JSON array (streamed tokens)
- **CRITICAL: Per-Token Streaming in Refinement Methods** (November 20, 2025 FIX):
  - **Issue**: All 5 refinement methods were collecting all tokens internally, then emitting ONE signal at the end with complete content
  - **Root Cause**: Handler `_on_new_synopsis()` relies on length comparison (`new_length > current_length`) to detect incremental updates. Single end-of-process emit only satisfied this once.
  - **Fix**: All refinement methods now emit signal for EVERY TOKEN collected:
    ```python
    for chunk in refinement_stream:
        if token:
            refined_content += token
            self.new_signal.emit(refined_content)  # Emit every token (was missing)
            
            if token_count % 100 == 0:
                self.log_update.emit(...)  # Log for tracking
    ```
  - **Methods Fixed** (all now stream per-token):
    1. `refine_synopsis_with_feedback()` - emits `new_synopsis` every token
    2. `refine_outline_with_feedback()` - emits `new_outline` every token
    3. `refine_characters_with_feedback()` - emits `new_characters` every token
    4. `refine_world_with_feedback()` - emits `new_world` every token
    5. `refine_timeline_with_feedback()` - emits `new_timeline` every token
    6. `refine_section_with_feedback()` - emits `new_draft` for all 3 streams (main refinement + 2 polish passes)
  - **Result**: Handler now sees incremental length growth and appends text live to display
  - **Pause Support**: All token loops now check `self.wait_while_paused()` for pause/resume control
- **Key Methods**:
  - `_generate_with_retry(parent_window, model, prompt, max_retries=None)` - Wrapper for all LLM calls with automatic retry logic using thread settings (returns stream iterator or None on failure after all retries, exponential backoff: 1s, 2s, 4s)
  - `start_processing(data)` - Sets inputs and starts thread execution with proper cleanup
  - `set_paused(paused)` - Sets pause flag for pause/resume control
  - `is_paused()` - Checks if thread is currently paused
  - `wait_while_paused()` - Blocks execution with 100ms sleep intervals until resumed
  - `run()` - Main thread execution: generates synopsis -> refines it -> emits signals
  - `refine_synopsis_with_feedback(content_type, feedback)` - Refines synopsis based on user feedback (recursive, unlimited iterations, only processes 'synopsis')
  - `generate_outline(content_type)` - Generates 25-chapter detailed outline when synopsis is approved (only processes 'synopsis' type)
  - `refine_outline_with_feedback(content_type, feedback)` - Refines outline based on user feedback (recursive, unlimited iterations, only processes 'outline')
  - `generate_characters(content_type)` - Generates character profiles from outline (only processes 'outline' type)
  - `refine_characters_with_feedback(content_type, feedback)` - Refines character profiles based on user feedback (only processes 'characters' type)
  - `generate_world(content_type)` - Generates world-building details from outline (only processes 'characters' type)
  - `refine_world_with_feedback(content_type, feedback)` - Refines world-building details based on user feedback (only processes 'world' type)
  - `generate_timeline(content_type)` - Generates timeline with dates, locations, events (only processes 'world' type)
  - `refine_timeline_with_feedback(content_type, feedback)` - Refines timeline based on user feedback (only processes 'timeline' type)
  - `start_chapter_research_loop()` - Starts chapter-by-chapter research notes generation loop
  - `generate_novel_section()` - Generates draft sections with 2-pass polish and optional vocabulary enhancement
  - `refine_section_with_feedback(content_type, feedback)` - Refines draft section with 2 polish passes (only processes 'section' type)
  - `approve_section(content_type)` - Approves section: appends to story.txt, generates summary, updates context.txt (only processes 'section' type)
  - `perform_final_consistency_check()` - Validates completed novel against characters/world/timeline for plot holes and vocabulary issues
  - `backup()` - Performs hourly backup of project files

**Retry Logic Implementation (_generate_with_retry)**:
- All streaming LLM calls in BackgroundThread now use the `_generate_with_retry()` wrapper
- Signature: `stream = self._generate_with_retry(parent_window, model=self.llm_model, prompt=prompt)`
- Uses `max_retries` from thread settings (default 3, configurable 1-10)
- Returns the stream iterator on success, or None if all retries fail
- Automatically logs retry attempts and failures with exponential backoff (1s, 2s, 4s delays)
- Emits error_signal to parent window on final failure after all retries
- Applies temperature setting from `self.temperature` to all LLM calls
- Usage pattern for all LLM generate calls:
  ```python
  stream = self._generate_with_retry(parent_window, model=self.llm_model, prompt=prompt)
  if stream is None:
      self.log_update.emit("Failed to generate content after retries")
      return
  
  try:
      for chunk in stream:
          # Process chunk tokens
  ```
- Applied to all 21 LLM generate calls across 15 methods in BackgroundThread:
  1. run() - synopsis generation and initial refinement (2 calls)
  2. refine_synopsis_with_feedback() (1 call)
  3. generate_outline() (1 call)
  4. refine_outline_with_feedback() (1 call)
  5. generate_characters() (1 call)
  6. refine_characters_with_feedback() (1 call)
  7. generate_world() (1 call)
  8. refine_world_with_feedback() (1 call)
  9. generate_timeline() (1 call)
  10. refine_timeline_with_feedback() (1 call)
  11. refine_section_with_feedback() (3 calls: refinement, polish_stream_1, polish_stream_2)
  12. approve_section() (2 calls: summary_stream, context_stream)
  13. perform_final_consistency_check() (1 call)
  14. start_chapter_research_loop() (1 call)
  15. generate_novel_section() (3 calls: draft_stream, polish_stream, enhance_stream)

**BackgroundThread.run() Method (line 124-172):**
- **Purpose**: Main execution entry point for novel generation pipeline
- **Key Fix (November 2025)**: Config string parsing rewritten to handle multi-line idea/tone text
  - **OLD Method**: Used regex pattern `r'Idea: (.+?), Tone: (.+?)(?:, Soft Target: (\d+))?$'` with `re.search(pattern, str(self.inputs), re.DOTALL)`
  - **Issue**: Failed when idea or tone contained newlines - regex `.+?` and `$` anchor incompatible with multiline text, caused silent return with no error logs
  - **NEW Method**: String position-based parsing (more robust):
    ```python
    soft_target = 250000
    inputs_str = str(self.inputs)
    
    # Extract soft target from end using regex on last line only
    soft_target_match = re.search(r', Soft Target: (\d+)$', inputs_str)
    if soft_target_match:
        soft_target = int(soft_target_match.group(1))
        inputs_str = inputs_str[:soft_target_match.start()]
    
    # Find separators using string methods
    idea_start = inputs_str.find('Idea: ')
    tone_start = inputs_str.rfind(', Tone: ')  # rfind finds LAST occurrence
    
    # Validate separators found
    if idea_start == -1 or tone_start == -1:
        self.processing_error.emit(f"Invalid config format: {self.inputs}")
        return
    
    # Extract substrings between separators
    idea = inputs_str[idea_start + 6:tone_start].strip()
    tone = inputs_str[tone_start + 8:].strip()
    ```
  - **Why This Works**: Handles arbitrary text in idea/tone (including newlines, commas) because we:
    1. Find soft target from the END (not corrupted by multiline separators)
    2. Use `rfind()` for tone separator to find the LAST `, Tone:` in case idea contains `, Tone:`
    3. No regex anchors or greedy/non-greedy quantifiers that fail on newlines
- **Logging**: Emits comprehensive logs at each step for debugging:
  - `"Parsed config - Idea: {idea[:50]}... | Tone: {tone[:30]}... | Target: {soft_target}"`
  - `"Generating initial synopsis (streaming tokens)..."`
  - And subsequent progress logs from refinement and outline generation

**Config String Format** (from ANSWindow._on_start_signal):
- Format: `f"Idea: {idea_text}, Tone: {tone_text}, Soft Target: {word_count}"`
- Example with multiline: `"Idea: A dragon awakens in the valley,\nfilled with ancient magic.\nTone: Dark fantasy with\ntones of mystery, Soft Target: 5000"`
- Note: Idea and tone can contain newlines from QTextEdit widgets, commas, and other characters
- All three components used to configure initial synopsis generation
1. Synopsis Phase:
   - Parse config string (Idea, Tone, Soft Target)
   - Generate initial synopsis with streaming (emits `synopsis_ready` every token)
   - Automatically start refinement pass
   - Refine synopsis for depth/coherence/tone alignment (emits `new_synopsis` every token)
2. Outline Phase (triggered by approve_signal with 'synopsis'):
   - Generate 25-chapter outline from approved synopsis (emits `new_outline` every token)
   - Save to outline.txt
3. Outline Refinement Loop (triggered by adjust_signal with 'outline'):
   - Refine outline based on user feedback
   - Re-emit `new_outline` signal to loop back to approval/adjustment
4. Character Phase (triggered by approve_signal with 'outline'):
   - Generate detailed character profiles from approved outline
   - Includes: Name, Age, Background, Traits, Arc, Relationships
   - Format: JSON array of character objects
   - Ensures consistency with synopsis
   - Emits `new_characters` with streamed JSON tokens
   - Save to characters.txt

### Development Guidelines

#### Architecture & Design
- Use PyQt5's signal/slot mechanism for all inter-component communication
- Keep tab implementations modular and independent
- All long-running operations must run in `BackgroundThread`, never block UI
- Project data is stored in `self.current_project` for session persistence
- Emit `log_update` signal for all user-initiated actions when project is active

#### Code Style & Standards
- Follow PEP 8 naming conventions
- Add docstrings to all classes and methods
- Use UTF-8 encoding for all file operations
- Use `os.path.join()` for cross-platform path handling
- Use `datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')` for all timestamps

#### Threading & Async Operations
- **CRITICAL**: Never update UI widgets directly from background threads
- Always emit signals from background threads to update UI in main thread
- Example pattern:
  ```python
  # In background thread:
  self.processing_finished.emit(result_data)
  
  # In main window:
  self.thread.processing_finished.connect(self._on_processing_finished)
  ```
- Background threads should be QThread objects, not daemon threads for long operations
- Use `threading.Event().wait(seconds)` for delays in background threads

#### Event Logging
- Emit `log_update.emit("message")` for all user actions when `self.current_project` is active
- Actions to log: project load/create, LLM connection status, test prompts, novel generation start
- Logs automatically write to project's `log.txt` with timestamp
- Format: `"2025-11-20 12:34:56 - message"`
- App-level events (startup, LLM tests during init) go to `Config/app_settings.txt`

#### Project Management
- Always verify `self.current_project` is not None before logging or accessing project data
- Update in-memory `self.current_project` when modifying project files
- Call `_refresh_logs_tab()` after loading a project to update UI
- Use `load_project(project_name)` to load existing projects (includes validation)
- Use `create_project_structure(project_path)` to create new projects

#### Error Handling
- Emit `error_signal.emit(error_message)` for user-facing errors
- This automatically shows QMessageBox.critical() and logs to app settings
- Use try/except blocks in background threads to catch errors and emit `processing_error` signal
- Always provide user-friendly error messages, not raw exception traces

#### Planning Tab & Synopsis/Outline Workflow
The Planning tab manages the synopsis generation, refinement, outline generation, and outline refinement workflow:
- **Displays**:
  - `synopsis_display` - Shows initial synopsis as it streams from Ollama (with Expand button)
  - `planning_synopsis_display` - Shows refined synopsis after refinement completes (with Expand button)
  - `outline_display` - Shows 25-chapter novel outline after synopsis approval (with Expand button)
  - `characters_display` - Shows character profiles in JSON format (with Expand button)
  - `world_display` - Shows world-building details (with Expand button)
  - `timeline_display` - Shows timeline with dates, locations, and events (with Expand button)
- **Expand Functionality** (UPDATED):
  - Each text display has an "Expand" button that opens a fullscreen dialog (1000x800px)
  - Dialog shows the complete text with dedicated close button
  - **NEW**: Expanded window continues to receive streaming updates in real-time
  - **Implementation**: `expanded_text_widgets` dictionary stores references to all open expanded windows
  - **Streaming Updates**: All signal handlers (`_on_synopsis_ready`, `_on_new_synopsis`, `_on_new_outline`) check for open expanded windows and append new tokens
  - Preserves original text and scroll positions
  - Method: `_expand_text_window(window_name)` - Opens expanded dialog for any text widget
  - Method: `_on_expanded_window_close(window_name, dialog)` - Removes reference when dialog closes
- **Planning Tab Buttons** (context-aware - emit signals during generation, log guidance for loaded content):
  - **Context Detection Pattern** (UPDATED):
    - All approve/adjust buttons now check `if self.thread.isRunning()` to determine context:
      - **IF TRUE** (active generation): Emit `approve_signal(section)` or `adjust_signal(section, feedback)` to trigger refinement loops
      - **IF FALSE** (loaded project content): Log helpful message guiding user to manual edit or start new generation
    - Loaded content identified by: existing project data displayed in text widgets when project loads
  - Synopsis Section:
    - `approve_button` - `_on_approve_synopsis()` → Checks for content, updates current_project['synopsis'], then emits `approve_signal('synopsis')` only if thread running
    - `adjust_button` - `_on_adjust_synopsis()` → Gets feedback, conditionally emits `adjust_signal('synopsis', feedback)` if thread running; logs guidance for loaded content
    - **NEW - Initial Synopsis Buttons**:
      - `initial_approve_button` - `_on_approve_initial_synopsis()` → Checks for content, routes to normal approve flow
      - `initial_adjust_button` - `_on_adjust_initial_synopsis()` → Gets feedback, conditionally emits based on thread state
      - Both enabled when initial synopsis finishes streaming (in `_on_synopsis_ready()`)
      - Both disabled when user clicks approve/adjust (streams initial refinement)
  - Outline Section:
    - `approve_outline_button` - `_on_approve_outline()` → Checks outline_display for content, updates current_project['outline'], emits signal
    - `adjust_outline_button` - `_on_adjust_outline()` → Gets feedback, conditionally emits `adjust_signal('outline', feedback)` if thread running; logs guidance for loaded content
  - Characters Section:
    - `approve_characters_button` - `_on_approve_characters()` → Checks characters_display for content, updates current_project['characters'], emits signal
    - `adjust_characters_button` - `_on_adjust_characters()` → Gets feedback, conditionally emits `adjust_signal('characters', feedback)` if thread running; logs guidance for loaded content
  - World Section:
    - `approve_world_button` - `_on_approve_world()` → Checks world_display for content, updates current_project['world'], emits signal
    - `adjust_world_button` - `_on_adjust_world()` → Gets feedback, conditionally emits `adjust_signal('world', feedback)` if thread running; logs guidance for loaded content
  - Timeline Section:
    - `approve_timeline_button` - `_on_approve_timeline()` → Checks timeline_display for content, updates current_project['timeline'], emits signal, disables buttons
    - `adjust_timeline_button` - `_on_adjust_timeline()` → Gets feedback, conditionally emits `adjust_signal('timeline', feedback)` if thread running; disables buttons during refinement; logs guidance for loaded content
- **Multi-Phase Workflow**:
  1. **Synopsis Generation Phase**: User enters idea/tone in Novel Idea tab and clicks "Start"
     - BackgroundThread generates initial synopsis (streams to `synopsis_display`)
     - Both button sets disabled
  2. **Synopsis Refinement Phase**: `refinement_start` signal automatically begins refinement
     - BackgroundThread refines synopsis (streams to `planning_synopsis_display`)
     - Synopsis buttons remain disabled
  3. **Synopsis Approval Phase**: Refined synopsis complete
     - Synopsis Approve/Adjust buttons become enabled
     - User can approve (triggers outline generation) or adjust (loops back to refinement)
  4. **Outline Generation Phase**: After `approve_signal('synopsis')`
     - BackgroundThread generates 25-chapter outline (streams to `outline_display`)
     - Outline saved to `outline.txt`
     - Outline buttons disabled during generation
  5. **Outline Approval Phase**: Outline generation complete
     - Outline Approve/Adjust buttons become enabled
     - User can approve (completes workflow) or adjust (triggers outline refinement)
  6. **Outline Refinement Phase** (optional): After `adjust_signal('outline', feedback)`
     - `outline_refinement_start` signal clears outline display
     - BackgroundThread refines outline (streams to `outline_display`)
     - Outline buttons remain disabled
     - Returns to Outline Approval Phase
- **Button State Machine**:
  - Initial: All disabled
  - After initial synopsis: All disabled (waiting for synopsis refinement)
  - After refined synopsis: Synopsis buttons enabled (user can approve/adjust)
  - During synopsis refinement: All disabled
  - After outline generation: Outline buttons enabled (user can approve/adjust)
  - During outline refinement: Outline buttons disabled
- **Text Update Strategy**: All displays use `insertPlainText()` to append new content while maintaining scroll position. Smart scroll checks if user is at bottom before auto-scrolling.
- **Outline Generation Details**:
  - Prompt includes: soft target word count, tone, synopsis content
  - Output: 25 chapters with titles, 100-200 word summaries per chapter, key events, character developments, dynamic chapter lengths (5000-15000 words)
  - Automatically saved to `projects/<project_name>/outline.txt`
  - Emits `new_outline` signal streamed every token
- **Outline Refinement Details**:
  - Prompt: "Revise outline based on feedback: \"{feedback}\". Keep tone and structure. Return ONLY the revised outline, no explanation or preamble."
  - Can be refined unlimited times based on user feedback
  - Each refinement overwrites `outline.txt` with updated version
  - Emits `new_outline` signal streamed every token to loop back to approval

#### Writing Tab & Section Approval Workflow
The Writing tab manages chapter-by-chapter draft generation and refinement:
- **Displays**:
  - `draft_display` - Shows current section draft as it streams from Ollama (with Expand button)
- **Writing Tab Buttons** (context-aware - emit signals during generation, log guidance for inactive):
  - `approve_section_button` - `_on_approve_section()` → Checks draft_display for content, updates buffer and current_project, emits `approve_signal('section')`; validates thread context
  - `adjust_section_button` - `_on_adjust_section()` → Validates draft exists, gets feedback, conditionally emits `adjust_signal('section', feedback)` if thread running; logs guidance for inactive context
  - `pause_button` - `_on_pause_generation()` → Sets `thread.paused = True`, calls `wait_while_paused()` in streaming loops, hides Pause button, shows Resume button
  - `resume_button` - `_on_resume_generation()` → Sets `thread.paused = False`, resumes execution in streaming loops, hides Resume button, shows Pause button
- **Pause/Resume Workflow**:
  1. **Pause Triggered**: User clicks Pause button during generation
     - `_on_pause_generation()` sets `thread.paused = True`
     - Logs: `"Generation paused. Click resume to continue."`
     - Pause button hidden, Resume button shown
     - Streaming loops check `self.wait_while_paused()` at each token iteration
     - Execution halts until resume is clicked (non-blocking 100ms sleep loop)
  2. **Resume Triggered**: User clicks Resume button
     - `_on_resume_generation()` sets `thread.paused = False`
     - Logs: `"Generation resumed."`
     - Resume button hidden, Pause button shown
     - Streaming loops exit `wait_while_paused()` and continue processing
  3. **Pause Flag Implementation**:
     - `BackgroundThread.paused` flag controls pause state
     - `BackgroundThread.set_paused(paused)` - Sets pause flag
     - `BackgroundThread.is_paused()` - Checks current pause state
     - `BackgroundThread.wait_while_paused()` - Blocks with 100ms sleep intervals until resumed
     - Called at start of each token loop iteration
- **Section Refinement Workflow** (triggered by adjust_signal('section', feedback)):
  1. **Refinement Phase**: `refine_section_with_feedback(content_type, feedback)`
     - Uses buffer storage: Prompt = `Rewrite the section "{self.buffer}" incorporating changes: "{feedback}". Re-check vocabulary and plot consistency.`
     - Streams refined section tokens from Ollama
     - Applies 2 polish passes:
       - **Polish Pass 1**: Flow and transitions check - `Polish this section for flow and transitions: "{refined_section}". Enhance narrative flow, improve transitions, maintain consistency.`
       - **Polish Pass 2**: Vocabulary and style check - `Refine vocabulary and style: "{refined_section}". Check for overused words, improve sentence variety, enhance prose quality.`
     - Updates buffer with final refined section
     - Logs: `"Starting section refinement with user feedback..."` → Polish pass tokens → `"Section refinement complete: X words (Y tokens) + 2 polish passes"`
     - Emits `new_draft` signal with refined section (streams to `draft_display`)
  2. **Loop Back to Review Phase**: Draft buttons become enabled
     - User can approve (accept and move to next section)
     - User can adjust again (re-loops with new feedback)
- **Section Approval Workflow** (triggered by approve_signal('section')):
  1. **Store Section**: `approve_section(content_type)`
     - Appends buffer to `story.txt` with chapter heading if new chapter: `=== CHAPTER {N} ===`
     - Reads current chapter/section from config.txt
     - Detects new chapter when `CurrentSection == 1`
  2. **Generate Summary**:
     - Prompt: `{section_content}\n\nSummarize this section in 100 words.`
     - Streams summary tokens from Ollama
     - Appends to `summaries.txt` with format: `Chapter {N}, Section {M}:\n{summary}\n\n`
  3. **Extract Context**:
     - Prompt: `Extract key events and mood from this section: "{section_content[:500]}..." Format as: Events: [list], Mood: [description]. Return ONLY the formatted output.`
     - Streams context tokens from Ollama
     - Appends to `context.txt`: `Chapter {N}, Section {M}: {context_update}\n`
  4. **Update Progress**:
     - Increments `CurrentSection` in config.txt
     - Tracks `SectionWords` for each section
  5. **Update Progress**:
     - Reads total story.txt word count after section append
     - Calculates progress: `(story_word_count / soft_target) * 100`
     - Updates `Progress` in config.txt with percentage
     - Determines chapter completion: `(CurrentSection + 1) > 3` (3 sections per chapter)
     - Increments `CurrentChapter` if chapter complete
     - Resets `CurrentSection` to 1 for new chapter
     - Logs: `"Progress: {int(progress_percentage)}% ({story_word_count} / {soft_target} words)"`
     - Logs chapter completion: `"Chapter {N} complete! Moving to Chapter {N+1}"`
  6. **Milestone Handling (80% Progress)**:
     - Triggers when `progress_percentage > 80 and < 100`
     - Shows QMessageBox dialog: `"Novel Progress Update"` with two options
     - Message shows: Current progress%, word count, current/total chapters
     - **Yes (Extend)**: Adds 5 chapters to `TotalChapters`, logs extension
     - **No (Wrap Up)**: Sets `TotalChapters` to `CurrentChapter + 2`, logs wrap-up
     - User response updates config.txt with new TotalChapters value
  7. **Completion Check**:
     - Checks if `CurrentChapter > TotalChapters`
     - Shows completion logs: `"=== NOVEL COMPLETE ==="`
     - Logs: Total chapters completed, final word count, final progress%
  8. **Logging Chain**:
     - `"Section {M} of Chapter {N} appended to story.txt"`
     - `"Generating summary for Section {M}..."`
     - `"Section summary generated and saved (X tokens)"`
     - `"Extracting context (key events/mood) for Section {M}..."`
     - `"Context updated with events/mood (X tokens)"`
     - `"Progress: {%}% ({words} / {target} words)"`
     - `"Chapter {N} complete! Moving to Chapter {N+1}"` (if applicable)
     - `"Milestone reached: {%}% complete. Prompting user for chapter extension..."` (if >80%)
     - `"Novel extended: Total chapters increased from {N} to {M}"` (if user extends)
     - `"Novel wrapping up: Total chapters set to {M} for conclusion"` (if user wraps)
     - `"Starting final consistency check on completed novel..."` (novel complete)
     - `"Consistency check complete ({X} tokens)"`
     - `"Consistency Check Results: {results}"`
     - `"Issues detected. Prompting user for auto-fix option..."` (if issues found)
     - `"User selected auto-fix. Initiating section refinement process..."` (if user chooses auto-fix)
     - `"User declined auto-fix. Novel remains as-is with noted issues."` (if user declines)
     - `"No consistency issues detected! Novel is ready for publication."` (if no issues)
     - `"=== NOVEL COMPLETE ==="` (completion marker)
     - `"Section {M} of Chapter {N} approved and processed (X words)"`
- **Section Workflow**:
  - Draft displays as it's generated (streams to `draft_display`)
  - User can approve to accept and move to next section
  - User can adjust to request refinements (loops back to refinement with feedback)
  - Pause button enables when draft is ready for review
  - All buttons disabled during generation and refinement

#### Final Consistency Check & Auto-Fix Workflow
The final consistency check validates completed novels against characters/world/timeline data for plot holes and vocabulary issues:
- **Method**: `perform_final_consistency_check()` in BackgroundThread
- **Trigger**: Automatically called when `CurrentChapter > TotalChapters` (novel completion)
- **Process**:
  1. **Validation Setup**:
     - Reads story.txt (full content, limited to first 5000 chars for analysis)
     - Reads characters.txt, world.txt, timeline.txt (limited to 2000 chars each)
  2. **Consistency Prompt**:
     - Constructs comprehensive prompt: `Check full story for consistency with characters, world, and timeline. List any plot holes or vocabulary issues.`
     - Includes story excerpt, character list, world details, and timeline
     - Instructs LLM to return ONLY issues list or "No issues found."
  3. **Issue Detection**:
     - Streams response tokens from Ollama (gemma3:12b)
     - Collects full response (token count tracked)
     - Logs: `"Consistency check complete ({X} tokens)"`
     - Logs: `"Consistency Check Results: {results}"`
  4. **Issue Analysis**:
     - Checks if response contains "no issues" (case-insensitive)
     - If NO issues: Logs `"No consistency issues detected! Novel is ready for publication."`
     - If issues FOUND: Proceeds to user prompt (Step 5)
  5. **User Auto-Fix Prompt**:
     - Shows QMessageBox dialog: `"Novel Consistency Issues Detected"`
     - Message displays detected issues and offers two options
     - **"Yes (Auto-fix)"**: Logs `"User selected auto-fix. Initiating section refinement process..."` and `"Auto-fix: Refining story sections to address consistency issues..."`
     - **"No (Skip)"**: Logs `"User declined auto-fix. Novel remains as-is with noted issues."`
  6. **Future Auto-Fix Logic** (placeholder for future implementation):
     - Parse issues to identify affected sections/chapters
     - Generate targeted refinement prompts
     - Stream refinements and update story.txt incrementally
     - Update summaries/context/config accordingly
- **Logging**:
  - `"Starting final consistency check on completed novel..."`
  - `"Consistency check complete ({X} tokens)"`
  - `"Consistency Check Results: {results}"`
  - `"Issues detected. Prompting user for auto-fix option..."` (if issues found)
  - `"User selected auto-fix. Initiating section refinement process..."` (if user chooses auto-fix)
  - `"Auto-fix: Refining story sections to address consistency issues..."`
  - `"Note: Manual review recommended after auto-fix completion"`
  - `"User declined auto-fix. Novel remains as-is with noted issues."` (if user declines)
  - `"No consistency issues detected! Novel is ready for publication."` (if no issues)

#### Frontend Implementation
- All frontend components should connect to backend signals
- Use QGroupBox for organizing related UI controls
- Use QTextEdit for displaying logs, read-only when displaying content
- Use QLineEdit/QSpinBox for user inputs with validation
- Every user action should emit appropriate signal when active

#### Dashboard Tab & Export Functionality
The Dashboard tab provides project overview and novel export options:
- **Displays**:
  - `dashboard_status_label` - Current project status indicator
  - `dashboard_progress_label` - Current progress percentage
  - `dashboard_progress_bar` - Visual progress indicator (0-100%)
  - `export_status_label` - Status of export operations
- **Export Buttons**:
  - `export_docx_button` - Export to Word document (.docx) using python-docx
  - `export_pdf_button` - Export to PDF using reportlab
- **Export Features**:
  - **DOCX Export** (`export_story_to_docx(project_path, output_filename)`):
    - Reads story.txt and config.txt (for project title)
    - Creates formatted Word document with:
      - Large bold title (24pt, centered) from project Idea
      - Project metadata (name, generation timestamp)
      - Chapter headings (parsed from `=== CHAPTER N ===` markers, formatted as Heading 1)
      - Body paragraphs with justified alignment
      - Blank lines preserved for spacing
    - Saves as `{project_name}_novel.docx` in project folder
    - Returns True on success, False otherwise
    - Dependencies: `python-docx` (optional, graceful degradation if missing)
  - **PDF Export** (`export_story_to_pdf(project_path, output_filename)`):
    - Reads story.txt and config.txt (for project title)
    - Creates formatted PDF with:
      - Large bold title (24pt, centered) from project Idea
      - Project metadata (name, generation timestamp)
      - Chapter headings parsed from `=== CHAPTER N ===` markers (14pt, Heading 2 style)
      - Body paragraphs with justified alignment, proper leading
      - Proper spacing between chapters
    - Saves as `{project_name}_novel.pdf` in project folder
    - Returns True on success, False otherwise
    - Dependencies: `reportlab` (optional, graceful degradation if missing)
- **Export Button Handlers**:
  - `_on_export_docx()` - Validates project loaded, checks python-docx installed, calls export function, logs export, updates status label
  - `_on_export_pdf()` - Validates project loaded, checks reportlab installed, calls export function, logs export, updates status label
- **Logging**: All exports logged with format `"Novel exported to {FORMAT}: {filepath}"`
- **Status Updates**: Export status displayed in `export_status_label` with checkmark (✓) for success or X (✗) for failure

#### Settings Tab & Configuration Management
The Settings tab provides comprehensive application configuration options:
- **Theme Settings Group**:
  - `dark_mode_checkbox` - Toggle dark/light mode UI theme
  - `_apply_dark_mode()` - Apply dark theme stylesheet
  - `_apply_light_mode()` - Apply light theme stylesheet (default)
- **LLM Configuration Group**:
  - `model_combo` - Select LLM model from installed Ollama models (default: 'gemma3:12b')
  - `temperature_slider` - Adjust LLM temperature (0-100, maps to 0.0-1.0, default: 0.70)
  - `temperature_value_label` - Display current temperature value
  - `refresh_models_btn` - Re-scan Ollama for installed models
  - `_populate_ollama_models()` - Auto-detect models from Ollama
  - `_refresh_ollama_models()` - User-triggered model refresh
  - `_get_available_models()` - Retrieve available models from Ollama client
- **Application Settings Group**:
  - `autosave_spinbox` - Auto-save interval in minutes (1-60, default: 15)
  - `notifications_checkbox` - Enable/disable notifications (default: True)
  - `autoapproval_checkbox` - Auto-approve content without user review (default: False)
- **Generation Parameters Group**:
  - `max_retries_spinbox` - Maximum LLM retry attempts (1-10, default: 3)
  - `detail_combo` - Generation detail level (options: Concise, Balanced, Detailed; default: Balanced)
  - `char_depth_combo` - Character profile depth (options: Shallow, Standard, Deep; default: Standard)
  - `world_depth_combo` - World-building depth (options: Minimal, Standard, Comprehensive; default: Standard)
  - `quality_combo` - Quality check strictness (options: Strict, Moderate, Lenient; default: Moderate)
  - `sections_spinbox` - Sections per chapter (1-10, default: 3)
- **Application Info Group**:
  - `version_label` - Display application version (1.0.0)
  - `about_button` - Show detailed about dialog with features
  - `_on_about_clicked()` - Display application information dialog
- **Settings Persistence**:
  - `_load_settings()` - Load app settings from `Config/app_settings.txt` on startup
  - `_save_settings()` - Save all settings to `Config/app_settings.txt` when changed
  - Settings automatically saved on every control change (connected to valueChanged/stateChanged/currentTextChanged signals)
  - `_sync_settings_to_thread()` - Sync UI settings to BackgroundThread before generation starts
  - All settings synced to thread in `_on_start_signal()` before novel generation begins
- **Settings File Format** (`Config/app_settings.txt`):
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

### Running the Application
```bash
python ans.py
```

### Dependencies
- PyQt5: `pip install PyQt5`
- ollama: `pip install ollama` (requires local Ollama service running)
- python-docx: `pip install python-docx` (optional, for DOCX export)
- reportlab: `pip install reportlab` (optional, for PDF export)

### Project Statistics
- **Tabs**: 7 (Initialization, Novel Idea, Planning, Writing, Logs, Dashboard, Settings)
- **Signals**: 14 total (inter-component communication, includes new_outline, outline_refinement_start, new_characters)
- **Project Files**: 9 per project (story, log, config, context, characters, world, summaries, outline, buffer_backup)
- **LLM Model**: Configurable (default: gemma3:12b, local via Ollama)
- **Configurable Parameters**: 8 total (model, temperature, max_retries, detail_level, character_depth, world_depth, quality_check, sections_per_chapter)
- **App-Level Settings**: Dark mode, model selection, temperature, auto-save, notifications, auto-approval
- **Streaming**: Real-time token streaming for synopsis generation, refinement, outline generation, outline refinement, character generation, section refinement, and consistency checking
- **Outline Refinement**: Unlimited iterations with user feedback, keeps tone and structure
- **Outline Generation**: 25 chapters with 100-200 word summaries per chapter, dynamic chapter lengths (5000-15000 words)
- **Character Generation**: Detailed profiles in JSON array format with Name, Age, Background, Traits, Arc, Relationships
- **Section Refinement**: 2-pass polish system (flow/transitions, vocabulary/style) with user feedback incorporation
- **Section Approval**: Automatic summary generation (100 words), context extraction (key events/mood), progress tracking (word count %, chapter advancement)
- **Progress Milestones**: 80% threshold triggers user dialog for novel extension (+5 chapters) or wrap-up (+2 chapters)
- **Pause/Resume**: Non-blocking pause control with 100ms sleep intervals, button toggling, thread-safe flag system
- **Final Validation**: Consistency checking against characters/world/timeline with plot hole and vocabulary issue detection, QMessageBox auto-fix prompt
- **Settings Persistence**: All settings persisted to `Config/app_settings.txt`, synced to BackgroundThread before each generation
- **Context-Aware Buttons** (NEW): All approve/adjust buttons now distinguish between active generation and loaded content:
  - **Active Generation** (thread.isRunning()): Emit signals to trigger refinement loops
  - **Loaded Content** (!thread.isRunning()): Log helpful guidance directing user to manual edit or start new generation
  - Enables editing both newly generated and previously saved project content

### Common Tasks Reference

**Creating a new feature with logging:**
```python
def _on_user_action(self):
    # Validate inputs
    if not user_input:
        self.error_signal.emit("Input required")
        return
    
    # Log if project active
    if self.current_project:
        self.log_update.emit("User action performed")
    
    # Emit main signal
    self.main_signal.emit(data)
```

**Adding a background operation:**
```python
# In BackgroundThread.run():
try:
    result = perform_operation(self.inputs)
    self.processing_finished.emit(result)
except Exception as e:
    self.processing_error.emit(str(e))
finally:
    self.processing_progress.emit("Complete")
```

**Loading project logs:**
```python
# Logs tab automatically shows current project logs
# Call _refresh_logs_tab() after loading project
# All future log_update signals write to project log.txt
```

### Future Development Areas
- ✅ Implement `BackgroundThread.run()` with novel generation logic (synopsis generation/refinement complete)
- ✅ Add Planning tab UI and backend integration (synopsis approval/adjustment complete)
- ✅ Add outline generation with 25-chapter structure (outline generation complete)
- ✅ Add Writing tab with section approval/refinement workflow (pause/resume complete)
- ✅ Add progress tracking with milestone notifications (80% threshold complete)
- ✅ Add final consistency check validation (basic implementation complete)
- ✅ Implement custom frameless window with professional title bar (complete)
- ✅ Integrate qframelesswindow library for Windows Aero snap support (complete - November 21, 2025)
- Add auto-fix logic for consistency issues (parse issues, target refinement, section updates)
- Add Dashboard with project statistics and completion metrics
- Implement save/restore of project data
- Add AI-powered generation prompts for additional content types
- Add user preferences and settings UI
- Add timeline.txt generation for completed novels

### Best Practices Reference

#### Best Practice 1: Project File I/O
**Rule**: All file operations must use context-aware paths and UTF-8 encoding.

**✓ Correct Pattern:**
```python
import os
# Always use os.path.join() for cross-platform compatibility
file_path = os.path.join(self.current_project['path'], 'story.txt')
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
```

**✗ Incorrect Pattern:**
```python
# Don't hardcode paths or forget encoding
with open(f"projects/{project}/story.txt") as f:  # Wrong: platform-specific, no encoding
    content = f.read()
```

#### Best Practice 2: Background Thread Operations
**Rule**: All long-running operations (>100ms) must run in BackgroundThread. Never block UI thread.

**✓ Correct Pattern:**
```python
# In main window, when user initiates operation:
config_str = f"Idea: {idea}, Tone: {tone}, Soft Target: {word_count}"
self.thread.start_processing(config_str)
self.log_update.emit("Novel generation started")

# BackgroundThread.run():
try:
    result = self.ollama_client.generate(self.inputs)
    self.processing_finished.emit(result)
except Exception as e:
    self.processing_error.emit(str(e))
```

**✗ Incorrect Pattern:**
```python
# Don't block UI with long operations
def _on_button_click(self):
    result = very_slow_operation()  # WRONG: Freezes UI
    self.text_edit.setText(result)
```

#### Best Practice 3: Event Logging (Project-Aware)
**Rule**: Emit `log_update` for all significant user actions when project is active. Logs auto-write to `log.txt`.

**✓ Correct Pattern:**
```python
def _on_generate_novel(self):
    if not self.current_project:
        self.error_signal.emit("Load a project first")
        return
    
    # Log the action
    self.log_update.emit("Novel generation started")
    
    # Process
    self.thread.start_processing(config)
```

**✗ Incorrect Pattern:**
```python
def _on_generate_novel(self):
    # Don't: Skip logging, no project check
    self.thread.start_processing(config)
```

**Events to Always Log:**
- Project created: `"Project created: {project_name}"`
- Project loaded: `"Project loaded: {project_name}"`
- LLM connection status: `"LLM connection {status} (attempt {n}/3)"`
- Novel generation start: `"Novel generation started with config: {config}"`
- Test prompt run: `"Test prompt: {prompt[:50]}..."`
- Generation complete: `"Novel generation complete"`

#### Best Practice 4: Signal/Slot Architecture
**Rule**: All inter-component communication uses signals/slots. No direct function calls between components.

**✓ Correct Pattern:**
```python
# Define signal in source class
class MyTab(QtWidgets.QWidget):
    my_signal = QtCore.pyqtSignal(str)
    
    def do_something(self):
        self.my_signal.emit("data")

# Connect in main window
tab = MyTab()
tab.my_signal.connect(self._on_tab_signal)

def _on_tab_signal(self, data):
    self.log_update.emit(f"Received: {data}")
```

**✗ Incorrect Pattern:**
```python
# Don't: Direct coupling between components
tab.process_data()
tab.update_main_window()  # Wrong: tab shouldn't know about main window
```

#### Best Practice 5: Error Handling
**Rule**: Always emit `error_signal` for user-facing errors. Never show raw exceptions.

**✓ Correct Pattern:**
```python
try:
    project_path = os.path.join('projects', project_name)
    if not os.path.exists(project_path):
        self.error_signal.emit(f"Project '{project_name}' not found")
        return
    # ... load project
except Exception as e:
    self.error_signal.emit(f"Failed to load project: {str(e)}")
```

**✗ Incorrect Pattern:**
```python
# Don't: Show raw exceptions
try:
    load_project(project_name)
except Exception as e:
    QMessageBox.critical(self, "Error", str(e))  # Wrong: raw exception, no logging
```

#### Best Practice 6: Tab Implementation Pattern
**Rule**: Each tab should follow a consistent structure with dedicated creation method.

**✓ Correct Pattern:**
```python
def _create_my_tab(self):
    """Create My Tab with widgets and connections."""
    tab = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout()
    
    # Add widgets
    button = QtWidgets.QPushButton("Do Something")
    button.clicked.connect(self._on_button_click)
    layout.addWidget(button)
    
    tab.setLayout(layout)
    return tab

def _on_button_click(self):
    if not self.current_project:
        self.error_signal.emit("Load a project first")
        return
    
    self.log_update.emit("User clicked button")
    # ... process
```

#### Best Practice 7: Project Data Access
**Rule**: Always check `self.current_project` before accessing, validate structure, update in-memory copy when modifying.

**✓ Correct Pattern:**
```python
def update_story(self, new_content):
    """Update story content in current project."""
    if not self.current_project:
        self.error_signal.emit("No project loaded")
        return
    
    try:
        # Update in-memory cache
        self.current_project['story'] = new_content
        
        # Write to file
        story_path = os.path.join(self.current_project['path'], 'story.txt')
        with open(story_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        self.log_update.emit("Story updated")
    except Exception as e:
        self.error_signal.emit(f"Failed to update story: {str(e)}")
```

#### Best Practice 8: Thread-Safe UI Updates
**Rule**: Never update UI from background threads. Always use signals to marshal updates to main thread.

**✓ Correct Pattern:**
```python
# In BackgroundThread subclass:
class MyThread(QtCore.QThread):
    finished = QtCore.pyqtSignal(str)
    
    def run(self):
        try:
            result = do_work()
            self.finished.emit(result)  # Signal to main thread
        except Exception as e:
            self.error.emit(str(e))

# In main window:
thread = MyThread()
thread.finished.connect(self._on_thread_finished)

def _on_thread_finished(self, result):
    self.text_edit.setText(result)  # Safe: runs in main thread via slot
```

**✗ Incorrect Pattern:**
```python
# Don't: Update UI directly from thread
def run(self):
    result = do_work()
    self.parent().text_edit.setText(result)  # ERROR: Wrong thread!
```

#### Best Practice 9: Configuration String Format
**Rule**: Config strings follow consistent format: `"Key: Value, Key: Value, ..."`

**✓ Correct Format:**
```python
config_str = f"Idea: {idea}, Tone: {tone}, Soft Target: {word_count}"
# Example: "Idea: A dragon awakens, Tone: Dark fantasy, Soft Target: 5000"
```

#### Best Practice 10: Timestamp and Logging Format
**Rule**: All timestamps use ISO format. Logs include timestamp, separator, message.

**✓ Correct Pattern:**
```python
import datetime

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
log_entry = f"{timestamp} - Action completed"
# Example: "2025-11-20 14:32:17 - Novel generation started"
```

Very important: Always refer to this file for Copilot instructions when contributing to the project.
- All functions implemented on backend must be documented here for Copilot to understand context.
- All functions and classes must have docstrings explaining their purpose and usage.
- All new features or changes must be reflected in this instruction file to keep Copilot updated.
- All features implemented on backend should have a front end component to interact with.
- When implementing a feature, follow the exact patterns shown in Best Practices sections 1-10.
- Use grep_search to find similar patterns in existing code before implementing new features.
- Always validate that your implementation follows all 10 best practices before marking as complete.Very important : Always refer to this file for Copilot instructions when contributing to the project.
-All functions implemented on backend must be documented here for Copilot to understand context.
-all functions and classes must have docstrings explaining their purpose and usage.
-all new features or changes must be reflected in this instruction file to keep Copilot updated.
-all features implemented on backend should have a front end component to interact with.