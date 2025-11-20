# Automated Novel System (ANS)

A PyQt5-based desktop application for automated novel generation using local Ollama LLM models. Generate complete novels from simple ideas with AI-powered content creation across all stages: synopsis, outline, character development, world-building, and section writing.

## Features

### Core Functionality
- **AI-Powered Synopsis Generation** - Generate and refine novel synopses with user feedback
- **25-Chapter Outline Generation** - Automatic outline creation with chapter summaries
- **Character Development** - Auto-generate detailed character profiles from outline
- **World Building** - Create comprehensive world details and settings
- **Timeline Generation** - Generate timelines with dates, locations, and events
- **Section-by-Section Writing** - Generate novel sections with 2-pass polish system
- **Real-time Streaming** - Token-by-token display of LLM responses
- **Auto-Approval Mode** - Automatically approve content at each generation stage

### User Interface
- **Tab-Based Interface** - 7 organized tabs for complete workflow
- **Dark Mode Support** - Full dark theme with custom stylesheet
- **Scrollable Content** - All tabs support scrolling for large content
- **Expandable Windows** - Pop-out dialogs for detailed viewing

### Advanced Features
- **Automatic Retry Logic** - 3-attempt retry with exponential backoff
- **Pause/Resume Control** - Pause generation and resume later
- **Progress Tracking** - Real-time word count and chapter progress
- **Milestone Notifications** - User prompts at 80% completion
- **Consistency Checking** - Final validation for plot holes
- **Export Options** - Generate DOCX and PDF documents

## Project Structure

```
ANS/
├── ans.py                 # Main application (4500+ lines)
├── tests.py              # Unit test suite (42 tests)
├── README.md             # This file
├── TESTING.md            # Testing documentation
├── Config/               # App-wide settings
│   └── app_settings.txt
├── projects/             # Novel projects directory
│   └── <project_name>/
│       ├── story.txt
│       ├── log.txt
│       ├── config.txt
│       ├── outline.txt
│       ├── characters.txt
│       ├── world.txt
│       ├── timeline.txt
│       └── ...
└── .github/
    └── copilot-instructions.md
```

## Prerequisites

- Python 3.7+
- PyQt5
- Ollama (local service)
- python-docx (optional, for DOCX export)
- reportlab (optional, for PDF export)

## Installation

1. **Clone Repository**
   ```bash
   git clone https://github.com/ShatterPro0f/ANS.git
   cd ANS
   ```

2. **Install Dependencies**
   ```bash
   pip install PyQt5 ollama python-docx reportlab
   ```

3. **Install Ollama**
   - Download from [ollama.ai](https://ollama.ai)
   - Run Ollama service

4. **Pull LLM Model**
   ```bash
   ollama pull gemma3:12b
   ```

## Running the Application

```bash
python ans.py
```

## Tabs Overview

| Tab | Purpose |
|-----|---------|
| **Initialization** | Create/load projects, test LLM connection |
| **Novel Idea** | Input novel concept, tone, target word count |
| **Planning** | Review and approve synopsis, outline, characters, world, timeline |
| **Writing** | Generate and approve individual sections |
| **Logs** | View project activity logs |
| **Dashboard** | Track progress, export to DOCX/PDF |
| **Settings** | Configure app-wide options and theme |

## Usage Workflow

1. **Create Project** → Initialization Tab
2. **Define Idea** → Novel Idea Tab
3. **Generate Content** → Planning Tab (synopsis → outline → characters → world → timeline)
4. **Write Sections** → Writing Tab
5. **Export** → Dashboard Tab

## Signals

The application uses PyQt5 signals for component communication:
- `start_signal` - Initiate novel generation
- `approve_signal` - Approve content
- `adjust_signal` - Request adjustments
- `pause_signal` - Pause generation
- `new_synopsis`, `new_outline`, `new_characters`, `new_world`, `new_timeline`, `new_draft` - Content updates
- `log_update` - Log events
- `error_signal` - Error notifications

## Settings

Located at: `Config/app_settings.txt`

- **Dark Mode** - Toggle dark theme
- **Model Selection** - Choose LLM model
- **Temperature** - Control response creativity (0.0-1.0)
- **Auto-save Interval** - Save frequency (1-60 minutes)
- **Notifications** - Enable/disable alerts
- **Auto-approval** - Automatically approve content

## Testing

Run comprehensive test suite:
```bash
pytest tests.py -v
```

**42 tests passing** covering:
- Configuration parsing
- File operations
- LLM calls with mocking
- Buffer management
- Pause/resume functionality
- Project management
- Progress tracking
- Export functionality
- Signal emission
- Input validation

## Development

This is a skeleton project. Additional functionality will be added to each tab and signal handler as development continues.
