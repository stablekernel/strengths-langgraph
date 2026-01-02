# Testing Guide for CliftonStrengths Agent

This guide explains how tests are organized and how to run them in this project.

## Test Structure

The tests are organized in the following directory structure:

```
tests/
├── README.md                 # This file - testing documentation
├── conftest.py              # Shared test configuration and fixtures
├── unit_tests/              # Unit tests - test individual components in isolation
│   ├── __init__.py
│   ├── test_configuration.py  # Tests for Context configuration
│   ├── test_db.py            # Tests for DynamoDB client
│   └── test_tools.py         # Tests for store/get profile tools
└── integration_tests/       # Integration tests - test components working together
    ├── __init__.py
    └── test_graph.py         # Tests for the complete agent graph

```

## Types of Tests

### Unit Tests (`tests/unit_tests/`)
These test individual functions and classes in **isolation**. They use "mocks" (fake objects) instead of real databases or APIs.

**What we test:**
- `test_db.py` - DynamoDB client methods (store, retrieve)
- `test_tools.py` - Tool functions that the agent calls
- `test_configuration.py` - Configuration setup

**Why unit tests?**
- Fast to run (no real AWS calls)
- Don't need AWS credentials
- Test each piece independently

### Integration Tests (`tests/integration_tests/`)
These test multiple components working together. They may use real services or comprehensive mocks.

**What we test:**
- `test_graph.py` - The complete agent workflow

## How to Run Tests

### Prerequisites

First, make sure you have the test dependencies installed:

```bash
# Activate your virtual environment
source /Users/arthur.torres/go/src/strengths-langgraph/.venv/bin/activate

# Navigate to the project directory
cd /Users/arthur.torres/go/src/strengths-langgraph/strengths-agent

# Install test dependencies
pip install pytest pytest-mock moto[dynamodb]
```

### Running All Tests

```bash
pytest
```

This will:
- Discover all test files (files starting with `test_`)
- Run all test functions (functions starting with `test_`)
- Show a summary of passed/failed tests

### Running Specific Test Files

```bash
# Run only unit tests
pytest tests/unit_tests/

# Run only integration tests
pytest tests/integration_tests/

# Run a specific test file
pytest tests/unit_tests/test_db.py

# Run a specific test file with verbose output
pytest tests/unit_tests/test_tools.py -v
```

### Running Specific Tests

```bash
# Run a specific test function
pytest tests/unit_tests/test_db.py::TestDynamoDBClient::test_store_profile_success

# Run all tests in a class
pytest tests/unit_tests/test_db.py::TestDynamoDBClient
```

### Useful Pytest Options

```bash
# Show more detailed output
pytest -v

# Show print statements (useful for debugging)
pytest -s

# Stop at first failure
pytest -x

# Show which tests will run without running them
pytest --collect-only

# Run tests and show coverage report
pytest --cov=src/strengths_agent --cov-report=term-missing
```

## Understanding Test Output

When you run `pytest`, you'll see output like:

```
tests/unit_tests/test_db.py ........          [50%]
tests/unit_tests/test_tools.py ......         [100%]

===================== 14 passed in 0.12s =====================
```

- Each `.` represents a passed test
- `F` means a test failed
- `E` means there was an error
- Numbers like `[50%]` show progress

If a test fails, pytest shows:
- The test name that failed
- The line where it failed
- What was expected vs. what was actual

## Writing Your Own Tests

Here's a simple example:

```python
def test_my_function():
    """Test description - what this test checks."""
    # Arrange: Set up test data
    input_value = "test"
    
    # Act: Call the function being tested
    result = my_function(input_value)
    
    # Assert: Check the result is what we expect
    assert result == "expected_output"
```

### Using Fixtures

Fixtures are reusable test setup code:

```python
import pytest

@pytest.fixture
def sample_strengths():
    """Provide a list of 34 strengths for testing."""
    return [f"Strength{i}" for i in range(1, 35)]

def test_with_fixture(sample_strengths):
    """Test uses the fixture as a parameter."""
    assert len(sample_strengths) == 34
```

### Using Mocks

Mocks let you fake external dependencies:

```python
from unittest.mock import MagicMock, patch

def test_with_mock():
    """Test using a mock to avoid real AWS calls."""
    with patch("strengths_agent.tools.get_db_client") as mock_client:
        # Set up what the mock should return
        mock_client.return_value.store_profile.return_value = {
            "success": True
        }
        
        # Call the real function (which uses the mock)
        result = store_profile(...)
        
        # Verify it worked
        assert result["success"] is True
```

## Common Issues

### Import Errors
If you see `ModuleNotFoundError`:
```bash
# Make sure the package is installed in editable mode
pip install -e .
```

### Fixture Not Found
Make sure `conftest.py` is in the right place and contains your fixture.

### Tests Can't Find AWS
Unit tests shouldn't need AWS - check that you're using mocks properly.

## Running Tests in CI/CD

Tests are automatically run when you push code (if CI/CD is configured). Make sure all tests pass before pushing!

## Tips for Beginners

1. **Start small**: Run one test file at a time
2. **Read test names**: They describe what's being tested
3. **Use `-v` flag**: Shows more detail about what's happening
4. **Don't be afraid of failures**: They help you find bugs!
5. **Look at existing tests**: Copy their pattern for new tests

## Getting Help

- Read the [pytest documentation](https://docs.pytest.org/)
- Look at existing test files for examples
- Run `pytest --help` to see all options
