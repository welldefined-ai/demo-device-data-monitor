# Testing Specification

## Test Organization

### Directory Structure
```
backend/tests/
├── unit/              # Fast, isolated tests
├── integration/       # Database, external services
└── conftest.py        # Shared fixtures
```

### Naming Conventions
- Test files: `test_<module_name>.py`
- Test functions: `test_<function_name>_<scenario>()`

## Test Categories

### Unit Tests
- **Location**: `tests/unit/`
- **Characteristics**: Fast (< 1s), no external dependencies, use mocks
- **Examples**: Configuration, schemas, business logic, utilities

### Integration Tests
- **Location**: `tests/integration/`
- **Characteristics**: Real dependencies (test database), verify persistence
- **Examples**: Migrations, repositories, API endpoints, WebSocket, Modbus

## Tools

- **pytest**: Test framework
- **pytest-asyncio**: Async support
- **pytest-cov**: Coverage reporting
- **unittest.mock**: Mocking

## Coverage Requirements

- **Overall**: ≥ 80%
- **Core modules** (`ddms/core/`, `ddms/services/`, `ddms/db/repositories/`): ≥ 90%
- **API routes**: ≥ 85%
- **Excluded**: Type stubs, abstract classes, migrations, config files

## Test Structure (AAA Pattern)

```python
def test_create_device():
    # Arrange - Setup test data
    device_data = {"name": "Sensor 1"}

    # Act - Execute code under test
    result = create_device(device_data)

    # Assert - Verify outcome
    assert result.name == "Sensor 1"
```

## Best Practices

- Test behavior, not implementation
- Use descriptive test names: `test_create_device_with_valid_data_returns_device()`
- Mock external dependencies (database, network), not internal logic
- Keep tests isolated and independent
- Use fixtures for common setup/teardown
