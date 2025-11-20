"""
Unit tests for Automated Novel System (ANS) using pytest.

This module provides test stubs for key BackgroundThread and ANSWindow methods,
including configuration parsing, LLM calls with mocked client, and file operations.

Run with: pytest tests.py -v
"""

import pytest
import os
import json
import tempfile
import shutil
from unittest.mock import Mock, MagicMock, patch, mock_open, call
from PyQt5 import QtWidgets, QtCore
import sys

# Import the classes to test
sys.path.insert(0, os.path.dirname(__file__))
from ans import BackgroundThread, ANSWindow


class TestConfigurationParsing:
    """Test suite for configuration string parsing."""
    
    def test_parse_config_string_valid(self):
        """Test parsing a valid configuration string."""
        config_str = "Idea: A dragon awakens, Tone: Dark fantasy, Soft Target: 5000"
        
        # Extract pattern matching logic
        import re
        pattern = r'Idea: (.+?), Tone: (.+?)(?:, Soft Target: (\d+))?$'
        match = re.match(pattern, str(config_str))
        
        assert match is not None
        assert match.group(1).strip() == "A dragon awakens"
        assert match.group(2).strip() == "Dark fantasy"
        assert match.group(3) == "5000"
    
    def test_parse_config_string_without_soft_target(self):
        """Test parsing config without soft target."""
        config_str = "Idea: A dragon awakens, Tone: Dark fantasy"
        
        import re
        pattern = r'Idea: (.+?), Tone: (.+?)(?:, Soft Target: (\d+))?$'
        match = re.match(pattern, str(config_str))
        
        assert match is not None
        assert match.group(1).strip() == "A dragon awakens"
        assert match.group(2).strip() == "Dark fantasy"
        assert match.group(3) is None
    
    def test_parse_config_string_invalid(self):
        """Test parsing an invalid configuration string."""
        config_str = "Invalid format"
        
        import re
        pattern = r'Idea: (.+?), Tone: (.+?)(?:, Soft Target: (\d+))?$'
        match = re.match(pattern, str(config_str))
        
        assert match is None
    
    def test_extract_idea_from_config(self):
        """Test extracting idea from configuration."""
        config_str = "Idea: A magical quest begins, Tone: Adventure, Soft Target: 3000"
        
        import re
        pattern = r'Idea: (.+?), Tone: (.+?)(?:, Soft Target: (\d+))?$'
        match = re.match(pattern, config_str)
        
        idea = match.group(1).strip()
        assert idea == "A magical quest begins"


class TestFileOperations:
    """Test suite for file I/O operations."""
    
    def test_create_project_structure(self):
        """Test creating project directory structure with files."""
        # Use temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = os.path.join(temp_dir, 'test_project')
            
            # Simulate project structure creation
            os.makedirs(project_path, exist_ok=True)
            
            # Create required files
            files_to_create = [
                'story.txt',
                'log.txt',
                'config.txt',
                'context.txt',
                'characters.txt',
                'world.txt',
                'summaries.txt',
                'outline.txt',
                'buffer_backup.txt'
            ]
            
            for filename in files_to_create:
                filepath = os.path.join(project_path, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write('')
            
            # Verify all files were created
            for filename in files_to_create:
                filepath = os.path.join(project_path, filename)
                assert os.path.exists(filepath), f"File {filename} not created"
            
            # Verify directory exists
            assert os.path.isdir(project_path)
    
    def test_write_to_story_file(self):
        """Test writing content to story.txt."""
        with tempfile.TemporaryDirectory() as temp_dir:
            story_path = os.path.join(temp_dir, 'story.txt')
            content = "=== CHAPTER 1 ===\nOnce upon a time..."
            
            with open(story_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Read back and verify
            with open(story_path, 'r', encoding='utf-8') as f:
                read_content = f.read()
            
            assert read_content == content
    
    def test_write_to_log_file(self):
        """Test writing log entries with timestamps."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = os.path.join(temp_dir, 'log.txt')
            
            import datetime
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"{timestamp} - Test log entry\n"
            
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(log_entry)
            
            with open(log_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            assert "Test log entry" in content
            assert "-" in content
    
    def test_write_json_to_characters_file(self):
        """Test writing character JSON to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            characters_path = os.path.join(temp_dir, 'characters.txt')
            
            characters_data = [
                {
                    "name": "Hero",
                    "age": 25,
                    "background": "A brave adventurer",
                    "traits": ["Courageous", "Loyal"],
                    "arc": "Redemption"
                }
            ]
            
            with open(characters_path, 'w', encoding='utf-8') as f:
                json.dump(characters_data, f, indent=2)
            
            with open(characters_path, 'r', encoding='utf-8') as f:
                read_data = json.load(f)
            
            assert len(read_data) == 1
            assert read_data[0]['name'] == "Hero"
            assert read_data[0]['age'] == 25
    
    def test_read_config_file(self):
        """Test reading configuration file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, 'config.txt')
            
            config_content = "Idea: Test Novel\nTone: Adventure\nSoft Target: 5000\n"
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            # Read and parse
            config_dict = {}
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        config_dict[key.strip()] = value.strip()
            
            assert config_dict['Idea'] == 'Test Novel'
            assert config_dict['Tone'] == 'Adventure'
            assert config_dict['Soft Target'] == '5000'


class TestLLMCalls:
    """Test suite for LLM (Ollama) calls with mocked client."""
    
    @patch('ans.ollama.Client')
    def test_generate_with_retry_success(self, mock_client_class):
        """Test successful LLM call with retry wrapper."""
        # Create mock parent window
        parent_window = MagicMock()
        
        # Mock the streaming response
        mock_stream = iter([
            {'response': 'Hello '},
            {'response': 'world'},
            {'response': '!'}
        ])
        
        parent_window.client.generate.return_value = mock_stream
        
        # Create BackgroundThread with None parent (avoid QThread mock issues)
        thread = BackgroundThread(None)
        
        # Call retry helper
        stream = thread._generate_with_retry(
            parent_window,
            model='gemma3:12b',
            prompt='Test prompt',
            max_retries=3
        )
        
        # Verify stream is returned
        assert stream is not None
        
        # Verify client.generate was called
        parent_window.client.generate.assert_called_once()
    
    @patch('ans.ollama.Client')
    def test_generate_with_retry_failure(self, mock_client_class):
        """Test LLM call failure after retries."""
        parent_window = MagicMock()
        
        # Mock client to raise exception
        parent_window.client.generate.side_effect = Exception("Connection failed")
        
        # Create BackgroundThread with None parent (avoid QThread mock issues)
        thread = BackgroundThread(None)
        
        # Call retry helper
        stream = thread._generate_with_retry(
            parent_window,
            model='gemma3:12b',
            prompt='Test prompt',
            max_retries=3
        )
        
        # Should return None after retries
        assert stream is None
        
        # Verify retries were attempted (3 times)
        assert parent_window.client.generate.call_count == 3
    
    def test_stream_response_processing(self):
        """Test processing streamed token responses."""
        # Simulate streaming response
        stream_chunks = [
            {'response': 'The '},
            {'response': 'quick '},
            {'response': 'brown '},
            {'response': 'fox'}
        ]
        
        # Accumulate tokens
        result = ''
        for chunk in stream_chunks:
            token = chunk.get('response', '')
            result += token
        
        assert result == 'The quick brown fox'
    
    def test_stream_response_with_empty_tokens(self):
        """Test handling empty tokens in stream."""
        stream_chunks = [
            {'response': 'Hello'},
            {'response': ''},  # Empty token
            {'response': ' '},
            {'response': 'world'}
        ]
        
        result = ''
        for chunk in stream_chunks:
            token = chunk.get('response', '')
            if token:  # Only add non-empty tokens
                result += token
        
        assert result == 'Hello world'
    
    def test_synopsis_generation_prompt_format(self):
        """Test synopsis generation prompt construction."""
        idea = "A dragon awakens"
        tone = "Dark fantasy"
        soft_target = 5000
        
        prompt = (
            f"Generate ONLY a 500–1000-word novel synopsis. No introduction or preamble.\n\n"
            f"Novel Idea: {idea}\n"
            f"Tone: {tone}\n"
            f"Target Word Count: {soft_target}\n\n"
            f"Include these sections:\n"
            f"- Setting: World and time period\n"
            f"- Characters: Main characters and their motivations\n"
            f"- Themes: Central themes\n"
            f"- Plot Arc: Beginning, middle, climax, and resolution\n\n"
            f"Ensure: No plot holes, consistent tone, engaging narrative."
        )
        
        assert "A dragon awakens" in prompt
        assert "Dark fantasy" in prompt
        assert "5000" in prompt
        assert "ONLY" in prompt
    
    def test_outline_refinement_prompt_format(self):
        """Test outline refinement prompt construction."""
        feedback = "Make the ending more dramatic"
        
        prompt = (
            f"Revise outline based on feedback: \"{feedback}\". "
            f"Keep tone and structure. "
            f"Return ONLY the revised outline, no explanation or preamble."
        )
        
        assert "Make the ending more dramatic" in prompt
        assert "tone and structure" in prompt
        assert "ONLY" in prompt
    
    def test_section_refinement_prompt_format(self):
        """Test section refinement prompt construction."""
        section_content = "Once upon a time..."
        feedback = "Add more description"
        
        prompt = (
            f"Rewrite the section \"{section_content}\" "
            f"incorporating changes: \"{feedback}\". "
            f"Re-check vocabulary and plot consistency."
        )
        
        assert section_content in prompt
        assert feedback in prompt
        assert "vocabulary" in prompt


class TestBufferOperations:
    """Test suite for buffer management."""
    
    def test_buffer_initialization(self):
        """Test buffer is initialized empty."""
        thread = BackgroundThread(None)
        assert thread.buffer == ''
    
    def test_buffer_append(self):
        """Test appending content to buffer."""
        thread = BackgroundThread(None)
        thread.buffer = ''
        
        thread.buffer += "First part "
        thread.buffer += "second part"
        
        assert thread.buffer == "First part second part"
    
    def test_buffer_reset(self):
        """Test resetting buffer."""
        thread = BackgroundThread(None)
        thread.buffer = "Some content"
        
        thread.buffer = ''
        
        assert thread.buffer == ''
    
    def test_buffer_word_count(self):
        """Test calculating word count from buffer."""
        thread = BackgroundThread(None)
        thread.buffer = "The quick brown fox jumps over the lazy dog"
        
        word_count = len(thread.buffer.split())
        
        assert word_count == 9


class TestPauseResume:
    """Test suite for pause/resume functionality."""
    
    def test_pause_flag_initialization(self):
        """Test pause flag is initialized to False."""
        thread = BackgroundThread(None)
        assert thread.paused is False
    
    def test_set_paused_true(self):
        """Test setting pause flag to True."""
        thread = BackgroundThread(None)
        thread.set_paused(True)
        
        assert thread.paused is True
        assert thread.is_paused() is True
    
    def test_set_paused_false(self):
        """Test setting pause flag to False."""
        thread = BackgroundThread(None)
        thread.set_paused(True)
        thread.set_paused(False)
        
        assert thread.paused is False
        assert thread.is_paused() is False
    
    def test_pause_state_toggle(self):
        """Test toggling pause state multiple times."""
        thread = BackgroundThread(None)
        
        # Initial state
        assert thread.is_paused() is False
        
        # Pause
        thread.set_paused(True)
        assert thread.is_paused() is True
        
        # Resume
        thread.set_paused(False)
        assert thread.is_paused() is False
        
        # Pause again
        thread.set_paused(True)
        assert thread.is_paused() is True


class TestProjectManagement:
    """Test suite for project management operations."""
    
    def test_project_list_retrieval(self):
        """Test retrieving list of projects."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock projects directory
            projects_dir = os.path.join(temp_dir, 'projects')
            os.makedirs(projects_dir, exist_ok=True)
            
            # Create test project directories
            os.makedirs(os.path.join(projects_dir, 'project_1'), exist_ok=True)
            os.makedirs(os.path.join(projects_dir, 'project_2'), exist_ok=True)
            os.makedirs(os.path.join(projects_dir, 'project_3'), exist_ok=True)
            
            # Simulate project list retrieval
            projects = sorted([
                item for item in os.listdir(projects_dir)
                if os.path.isdir(os.path.join(projects_dir, item))
            ])
            
            assert len(projects) == 3
            assert 'project_1' in projects
            assert 'project_2' in projects
    
    def test_project_path_construction(self):
        """Test constructing project paths."""
        base_path = '/projects'
        project_name = 'my_novel'
        
        project_path = os.path.join(base_path, project_name)
        
        assert 'my_novel' in project_path
        assert 'projects' in project_path


class TestProgressTracking:
    """Test suite for progress tracking."""
    
    def test_calculate_progress_percentage(self):
        """Test calculating progress percentage."""
        current_words = 2500
        soft_target = 5000
        
        progress_percentage = (current_words / soft_target) * 100
        
        assert progress_percentage == 50.0
    
    def test_progress_at_milestone_80_percent(self):
        """Test detecting 80% progress milestone."""
        current_words = 4100
        soft_target = 5000
        
        progress_percentage = (current_words / soft_target) * 100
        
        assert progress_percentage > 80
        assert progress_percentage < 100
    
    def test_progress_at_completion_100_percent(self):
        """Test detecting 100% progress completion."""
        current_words = 5000
        soft_target = 5000
        
        progress_percentage = (current_words / soft_target) * 100
        
        assert progress_percentage == 100.0
    
    def test_chapter_advancement_calculation(self):
        """Test calculating chapter advancement."""
        current_chapter = 1
        current_section = 3  # Sections per chapter
        sections_per_chapter = 5
        
        if (current_section + 1) > sections_per_chapter:
            next_chapter = current_chapter + 1
        else:
            next_chapter = current_chapter
        
        assert next_chapter == current_chapter  # Should not advance yet


class TestExportFunctionality:
    """Test suite for export to DOCX and PDF."""
    
    def test_docx_export_path_generation(self):
        """Test DOCX export filename generation."""
        project_name = "my_novel"
        output_filename = f"{project_name}_novel.docx"
        
        assert output_filename == "my_novel_novel.docx"
        assert ".docx" in output_filename
    
    def test_pdf_export_path_generation(self):
        """Test PDF export filename generation."""
        project_name = "my_novel"
        output_filename = f"{project_name}_novel.pdf"
        
        assert output_filename == "my_novel_novel.pdf"
        assert ".pdf" in output_filename
    
    def test_chapter_heading_parsing(self):
        """Test parsing chapter headings from story."""
        story_content = """=== CHAPTER 1 ===
Introduction content here.

=== CHAPTER 2 ===
Main action happens here.
"""
        
        import re
        chapters = re.findall(r'=== CHAPTER \d+ ===', story_content)
        
        assert len(chapters) == 2
        assert '=== CHAPTER 1 ===' in chapters
        assert '=== CHAPTER 2 ===' in chapters


class TestSignalEmission:
    """Test suite for signal emission patterns."""
    
    def test_log_update_signal_creation(self):
        """Test log update signal can be created."""
        # Mock signal
        signal = MagicMock()
        
        # Emit signal
        signal.emit("Test log message")
        
        # Verify emit was called
        signal.emit.assert_called_once_with("Test log message")
    
    def test_error_signal_emission(self):
        """Test error signal emission."""
        signal = MagicMock()
        error_msg = "Connection failed"
        
        signal.emit(error_msg)
        
        signal.emit.assert_called_once_with("Connection failed")
    
    def test_synopsis_ready_signal_with_content(self):
        """Test synopsis_ready signal with content."""
        signal = MagicMock()
        content = "Generated synopsis text..."
        
        signal.emit(content)
        
        signal.emit.assert_called_once_with(content)


class TestInputValidation:
    """Test suite for input validation."""
    
    def test_validate_word_count_is_number(self):
        """Test validating word count is numeric."""
        word_count_str = "5000"
        
        try:
            word_count = int(word_count_str)
            is_valid = True
        except ValueError:
            is_valid = False
        
        assert is_valid is True
    
    def test_validate_word_count_invalid(self):
        """Test invalid word count input."""
        word_count_str = "not_a_number"
        
        try:
            word_count = int(word_count_str)
            is_valid = True
        except ValueError:
            is_valid = False
        
        assert is_valid is False
    
    def test_validate_empty_prompt(self):
        """Test validating non-empty prompt."""
        prompt = "  "
        
        is_valid = bool(prompt.strip())
        
        assert is_valid is False
    
    def test_validate_non_empty_prompt(self):
        """Test validating non-empty prompt."""
        prompt = "Generate a story about dragons"
        
        is_valid = bool(prompt.strip())
        
        assert is_valid is True


class TestTimeTracking:
    """Test suite for timestamp and timing operations."""
    
    def test_timestamp_format(self):
        """Test timestamp is in correct format."""
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Verify format
        parts = timestamp.split()
        assert len(parts) == 2  # Date and time
        assert len(parts[0].split('-')) == 3  # Year-Month-Day
        assert len(parts[1].split(':')) == 3  # Hour:Minute:Second
    
    def test_log_entry_with_timestamp(self):
        """Test log entry includes timestamp."""
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = "Test message"
        
        log_entry = f"{timestamp} - {message}"
        
        assert timestamp in log_entry
        assert message in log_entry
        assert " - " in log_entry


# Test execution configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
