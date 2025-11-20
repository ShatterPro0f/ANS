# ANS Unit Tests Documentation

This document describes the unit test suite for the Automated Novel System (ANS).

## Overview

The test suite uses **pytest** and provides comprehensive coverage of key ANS components:
- Configuration parsing
- File I/O operations
- LLM (Ollama) calls with mocked client
- Buffer management
- Pause/resume functionality
- Project management
- Progress tracking
- Export functionality
- Signal emission
- Input validation
- Timestamp operations

## Running Tests

### Run All Tests
```bash
pytest tests.py -v
```

### Run Specific Test Class
```bash
pytest tests.py::TestConfigurationParsing -v
```

### Run Single Test
```bash
pytest tests.py::TestConfigurationParsing::test_parse_config_string_valid -v
```

### Show Test Coverage Summary
```bash
pytest tests.py --collect-only -q
```

### Run with Detailed Output
```bash
pytest tests.py -vv --tb=short
```

## Test Suite Breakdown

### 1. TestConfigurationParsing (4 tests)
Tests configuration string parsing logic:
- ✓ Valid config with all parameters
- ✓ Config without soft target
- ✓ Invalid config format handling
- ✓ Extracting idea from config

### 2. TestFileOperations (5 tests)
Tests file I/O operations:
- ✓ Project directory structure creation
- ✓ Writing to story.txt
- ✓ Writing log entries with timestamps
- ✓ Writing JSON character data
- ✓ Reading configuration files

### 3. TestLLMCalls (7 tests)
Tests LLM calls with mocked Ollama client:
- ✓ Successful LLM call with retry wrapper
- ✓ LLM call failure after retries
- ✓ Stream response token processing
- ✓ Handling empty tokens in stream
- ✓ Synopsis generation prompt format
- ✓ Outline refinement prompt format
- ✓ Section refinement prompt format

### 4. TestBufferOperations (4 tests)
Tests buffer management:
- ✓ Buffer initialization (empty string)
- ✓ Appending content to buffer
- ✓ Resetting buffer
- ✓ Word count calculation from buffer

### 5. TestPauseResume (4 tests)
Tests pause/resume functionality:
- ✓ Pause flag initialization
- ✓ Setting pause to True
- ✓ Setting pause to False
- ✓ Multiple pause/resume toggles

### 6. TestProjectManagement (2 tests)
Tests project management operations:
- ✓ Retrieving project list
- ✓ Constructing project paths

### 7. TestProgressTracking (4 tests)
Tests progress calculation:
- ✓ Calculate progress percentage
- ✓ Detect 80% milestone
- ✓ Detect 100% completion
- ✓ Chapter advancement calculation

### 8. TestExportFunctionality (3 tests)
Tests export features:
- ✓ DOCX export filename generation
- ✓ PDF export filename generation
- ✓ Chapter heading parsing from story

### 9. TestSignalEmission (3 tests)
Tests signal emission:
- ✓ Log update signal creation
- ✓ Error signal emission
- ✓ Synopsis ready signal with content

### 10. TestInputValidation (4 tests)
Tests input validation:
- ✓ Valid word count (numeric)
- ✓ Invalid word count (non-numeric)
- ✓ Empty prompt rejection
- ✓ Non-empty prompt acceptance

### 11. TestTimeTracking (2 tests)
Tests timestamp operations:
- ✓ Timestamp format validation
- ✓ Log entry with timestamp

## Test Results Summary

**Total Tests**: 42  
**Passing**: 42 ✓  
**Failing**: 0  
**Execution Time**: ~4.3 seconds  

## Mocking Strategy

### LLM Client Mocking
Tests use `unittest.mock` to mock the Ollama client:

```python
from unittest.mock import MagicMock, patch

@patch('ans.ollama.Client')
def test_generate_with_retry_success(self, mock_client_class):
    parent_window = MagicMock()
    mock_stream = iter([
        {'response': 'Token 1 '},
        {'response': 'Token 2'}
    ])
    parent_window.client.generate.return_value = mock_stream
    # Test code...
```

### File Operations Testing
Tests use `tempfile.TemporaryDirectory()` for isolated file operations:

```python
with tempfile.TemporaryDirectory() as temp_dir:
    story_path = os.path.join(temp_dir, 'story.txt')
    # Write and test file operations
```

## Key Testing Patterns

### 1. Configuration Parsing
```python
import re
pattern = r'Idea: (.+?), Tone: (.+?)(?:, Soft Target: (\d+))?$'
match = re.match(pattern, config_str)
assert match is not None
```

### 2. File Operations
```python
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
# Verify file exists and content is correct
```

### 3. LLM Call Simulation
```python
stream = self._generate_with_retry(
    parent_window,
    model='gemma3:12b',
    prompt=prompt,
    max_retries=3
)
assert stream is not None
```

### 4. Progress Calculation
```python
progress_percentage = (current_words / soft_target) * 100
assert progress_percentage == 50.0  # 2500/5000
```

## Extending Tests

To add new tests:

1. Create a new test class inheriting from `object`
2. Name methods starting with `test_`
3. Use descriptive docstrings
4. Add assertions to validate behavior
5. Use mocking for external dependencies

Example:
```python
class TestNewFeature:
    """Test suite for new feature."""
    
    def test_feature_behavior(self):
        """Test that feature behaves correctly."""
        # Setup
        result = perform_operation()
        
        # Assert
        assert result == expected_value
```

## Dependencies

- pytest: `pip install pytest`
- PyQt5: `pip install PyQt5`
- ollama: `pip install ollama` (not required for tests, mocked)
- unittest.mock: Built-in (Python 3.3+)
- tempfile: Built-in

## Notes

- Tests do NOT run the main ANS application
- All LLM calls are mocked (no actual Ollama connection needed)
- File operations use temporary directories (no side effects)
- Tests are isolated and can run in any order
- All tests complete in under 5 seconds

## Continuous Integration

To run tests in a CI/CD pipeline:

```bash
pytest tests.py -v --tb=short --junit-xml=test-results.xml
```

This generates JUnit XML output compatible with CI systems (GitHub Actions, GitLab CI, Jenkins, etc.).

## Troubleshooting

### ImportError: No module named 'ans'
**Solution**: Run pytest from the ANS project directory:
```bash
cd c:\Users\samue\Documents\ANS
pytest tests.py -v
```

### ModuleNotFoundError: No module named 'pytest'
**Solution**: Install pytest:
```bash
pip install pytest
```

### PyQt5 not available
**Solution**: Install PyQt5:
```bash
pip install PyQt5
```

## Test Maintenance

When updating ANS code:
1. Run tests to ensure no regressions
2. Update mocks if public APIs change
3. Add new tests for new features
4. Keep tests focused and independent
5. Use descriptive test names

---

**Last Updated**: November 20, 2025  
**Total Test Coverage**: 42 comprehensive test cases
