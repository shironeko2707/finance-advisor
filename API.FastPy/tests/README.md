# Testing Guide

## 🧪 Test Structure

The Lengkeng API uses a comprehensive pytest-based testing framework with the following structure:

```
tests/
├── __init__.py
├── conftest.py              # Test configuration & fixtures
├── test_config.py           # Test database configuration
├── test_user_management.py  # API endpoint tests
└── test_user_services.py    # Unit tests for services & repositories
```

## 🚀 Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install -r requirements.txt
```

### Basic Test Commands

1. **Run all tests:**
   ```bash
   python -m pytest tests/ -v
   ```

2. **Run specific test file:**
   ```bash
   python -m pytest tests/test_user_management.py -v
   ```

3. **Run specific test:**
   ```bash
   python -m pytest tests/test_user_management.py::TestUserCreation::test_create_user_minimal_fields -v
   ```

4. **Use the interactive test runner:**
   ```bash
   python run_tests.py
   ```

### Advanced Testing Options

1. **Run with coverage:**
   ```bash
   pip install pytest-cov
   python -m pytest tests/ --cov=user_mgmt --cov-report=html
   ```

2. **Run tests in parallel:**
   ```bash
   pip install pytest-xdist
   python -m pytest tests/ -n auto
   ```

3. **Run tests with detailed output:**
   ```bash
   python -m pytest tests/ -v --tb=long
   ```

## 📋 Test Categories

### 1. API Integration Tests (`test_user_management.py`)

Tests the HTTP endpoints with different scenarios:

- **TestUserCreation**: Tests user creation with various payloads
  - Minimal required fields only
  - Custom password scenarios
  - Complete user information
  - Role and status overrides

- **TestUserValidation**: Tests validation error scenarios
  - Missing required fields
  - Invalid username formats
  - Invalid email formats
  - Duplicate username/email handling

- **TestUserRetrieval**: Tests user retrieval operations
  - Get user by ID
  - User not found scenarios
  - List all users

### 2. Unit Tests (`test_user_services.py`)

Tests the business logic and data access layers:

- **TestUserService**: Tests the service layer
  - User creation through service
  - User retrieval by ID and username
  - User listing functionality

- **TestUserRepository**: Tests the repository layer
  - Direct database operations
  - User creation and retrieval
  - Email and username lookups

## 🔧 Test Configuration

### Database Setup

Tests use an isolated in-memory SQLite database that is:
- Created fresh for each test
- Automatically cleaned up after each test
- Completely separate from your development database

### Test Fixtures

The testing framework provides several fixtures:

- `test_client`: FastAPI TestClient with database override
- `test_db`: Direct database session for unit tests

### Environment Configuration

Tests can be configured through environment variables:

```bash
# Use a specific test database (optional)
export TEST_DATABASE_URL="sqlite:///./test.db"

# Run tests
python -m pytest tests/
```

## 🎯 Best Practices

1. **Isolation**: Each test runs in isolation with a fresh database
2. **Descriptive Names**: Test names clearly describe what is being tested
3. **Arrange-Act-Assert**: Tests follow the AAA pattern
4. **Fast Execution**: Using in-memory database for speed
5. **Comprehensive Coverage**: Both unit and integration tests

## 🚨 Migration from Old Tests

If you were using the old `test_create_user_examples.py`, it has been replaced by this new structure. The old scenarios have been converted to proper pytest tests:

- ✅ `test_create_user_scenarios()` → `TestUserCreation` class
- ✅ `test_validation_errors()` → `TestUserValidation` class
- ✅ Manual HTTP requests → FastAPI TestClient
- ✅ Server dependency → Isolated test database

## 📈 Continuous Integration

This test structure is CI/CD ready. Example GitHub Actions workflow:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.12
      - run: pip install -r requirements.txt
      - run: python -m pytest tests/ -v --cov=user_mgmt
```

## 🛠️ Extending Tests

To add new tests:

1. Add test functions to existing test classes
2. Create new test classes for new features
3. Use the provided fixtures for database access
4. Follow the existing naming conventions
5. Add both unit and integration tests for new features
