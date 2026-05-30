# Test Suite Documentation

## Overview

This test suite provides comprehensive coverage for the Background Screenshot Capture application. It uses `pytest` with mocking to test business logic without requiring external dependencies like Google Drive API or GUI interaction.

## Test Coverage: 69%

- **config_manager.py**: 97% coverage
- **screenshot_tray.py**: 66% coverage
- **region_selector.py**: 62% coverage
- **error_handling**: 100% coverage
- **circuit_breaker**: 98% coverage

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures
├── test_config_manager.py         # Config loading/saving tests
├── test_circuit_breaker.py        # Circuit Breaker pattern tests
├── test_error_handling.py         # Error classification & retry tests
├── test_region_selector.py        # Region selection logic tests
└── test_screenshot_capture.py     # Screenshot capture tests
```

## Running Tests

### Run all tests

```bash
uv run pytest tests/ -v
```

### Run with coverage report

```bash
uv run pytest tests/ --cov=. --cov-report=html --cov-report=term
```

### Run specific test file

```bash
uv run pytest tests/test_config_manager.py -v
```

### Run specific test

```bash
uv run pytest tests/test_circuit_breaker.py::TestCircuitBreaker::test_initial_state -v
```

### View HTML coverage report

```bash
# After running with --cov-report=html
start htmlcov/index.html  # Windows
```

## Test Categories

### 1. Configuration Tests (`test_config_manager.py`)

Tests for YAML configuration management:

- Loading default config
- Loading existing config
- Saving configuration changes
- Property getters/setters
- Region handling (tuple/list/None)
- Error handling configuration
- Corrupted config fallback

### 2. Circuit Breaker Tests (`test_circuit_breaker.py`)

Tests for the Circuit Breaker pattern used in Google Drive uploads:

- State transitions (CLOSED → OPEN → HALF_OPEN → CLOSED)
- Failure threshold detection
- Timeout and retry logic
- Success threshold in HALF_OPEN state
- Manual reset functionality
- Status reporting

### 3. Error Handling Tests (`test_error_handling.py`)

Tests for error classification and retry logic:

- Network error detection
- Authentication error detection
- HTTP status code classification (401, 403, 500+)
- Quota exceeded detection
- Exponential backoff timing
- Non-retryable error detection (auth, quota)

### 4. Region Selector Tests (`test_region_selector.py`)

Tests for screen region selection logic:

- Initialization
- Cancel/fullscreen methods
- Coordinate handling
- Minimum size validation
- Inverted drag handling
- GUI integration test (skipped - requires manual testing)

### 5. Screenshot Capture Tests (`test_screenshot_capture.py`)

Tests for screenshot capture functionality:

- Initialization
- Screenshot with/without region
- Error handling
- Start/stop/pause/resume
- Status reporting
- Configuration reload
- Google Drive upload (mocked)

## Fixtures

### `temp_dir`

Creates a temporary directory for test files, automatically cleaned up after test.

### `mock_config_file`

Creates a test YAML config file with sample values.

### `test_config`

Provides a Config instance loaded from the mock config file.

### `mock_drive_service`

Mocked Google Drive API service for upload tests.

### `mock_screenshot`

Mocked PIL Image for screenshot tests.

### `mock_pyautogui`

Mocked pyautogui module to avoid actual screenshots.

## Mocking Strategy

### Why Mock?

- **Speed**: Tests run in seconds, not minutes
- **Reliability**: No network, filesystem, or GUI dependencies
- **Isolation**: Each test is independent
- **CI/CD**: Can run in automated environments

### What's Mocked?

- Google Drive API (`mock_drive_service`)
- Screenshot capture (`mock_pyautogui`)
- File system operations (using `temp_dir`)
- GUI components (tkinter) - when testable

### What's NOT Mocked?

- Core business logic (Circuit Breaker, Config Manager)
- Error classification logic
- YAML parsing (uses real PyYAML)
- Retry with backoff logic

## Best Practices Used

1. **AAA Pattern**: Arrange, Act, Assert in each test
2. **Descriptive Names**: Test names explain what they test
3. **Fixtures**: Shared setup code in conftest.py
4. **Isolation**: Each test is independent
5. **Mocking**: External dependencies are mocked
6. **Coverage**: Aim for >80% coverage on business logic
7. **Fast**: Full suite runs in < 5 seconds

## Known Limitations

### Not Tested (Excluded from Coverage)

- `config_dialog.py` - GUI dialog (requires manual testing)
- `region_selector.py` select_region() - Full GUI flow (requires manual testing)
- `screenshot_capture.py` - Old CLI version (deprecated)

### Integration Testing

Some scenarios require manual testing:

- Full OAuth 2.0 flow with Google Drive
- Actual screenshot capture and upload
- System tray GUI interaction
- Region selection with mouse interaction

## Adding New Tests

### 1. Create test file

```python
# tests/test_new_feature.py
import pytest
from my_module import MyClass

class TestMyClass:
    def test_something(self):
        # Arrange
        obj = MyClass()

        # Act
        result = obj.do_something()

        # Assert
        assert result == expected_value
```

### 2. Add fixtures if needed

```python
# tests/conftest.py
@pytest.fixture
def my_fixture():
    return "test data"
```

### 3. Run tests

```bash
uv run pytest tests/test_new_feature.py -v
```

## Dependencies

Test dependencies (already in requirements.txt):

- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities
- `freezegun` - Time mocking for Circuit Breaker tests

## Continuous Integration

To run tests in CI/CD:

```yaml
# .github/workflows/test.yml example
- name: Run tests
  run: |
    uv pip install -r requirements.txt
    uv run pytest tests/ --cov=. --cov-report=xml
```

## Troubleshooting

### Tests fail with "ModuleNotFoundError"

```bash
# Install dependencies
uv pip install -r requirements.txt
```

### Coverage report not generated

```bash
# Ensure pytest-cov is installed
uv pip install pytest-cov
```

### Tests hang or fail with GUI errors

The GUI tests (tkinter) should be skipped automatically. If not:

```bash
# Run with -k to skip GUI tests
uv run pytest tests/ -k "not integration"
```

## Future Improvements

- [ ] Add integration tests for Google Drive uploads
- [ ] Add performance/load tests
- [ ] Test screenshot_capture.py (CLI version)
- [ ] Add mutation testing with `mutmut`
- [ ] Increase coverage to >80%
