# TradeBerg Testing Guide

This guide explains how to run tests for both frontend and backend.

## Backend Tests

### Setup

1. Install test dependencies:
```bash
cd backend
pip install pytest pytest-asyncio httpx
```

Or add to `requirements.txt`:
```
pytest==8.0.0
pytest-asyncio==0.23.0
httpx==0.27.0
```

2. Run tests:
```bash
# Windows
python -m pytest tests/ -v

# Or use the batch script
tests\run_tests.bat

# Linux/Mac
pytest tests/ -v

# Or use the shell script
chmod +x tests/run_tests.sh
./tests/run_tests.sh
```

### Test Structure

- `tests/test_chat_routes.py` - Chat API endpoint tests
- `tests/test_trading_routes.py` - Trading API endpoint tests
- `tests/test_database.py` - Database model tests
- `tests/test_chat_service.py` - Chat service tests
- `tests/test_integration.py` - End-to-end integration tests
- `tests/conftest.py` - Pytest fixtures and configuration

### Running Specific Tests

```bash
# Run only chat route tests
pytest tests/test_chat_routes.py -v

# Run only integration tests
pytest tests/test_integration.py -v

# Run a specific test
pytest tests/test_chat_routes.py::TestChatRoutes::test_create_chat -v
```

## Frontend Tests

### Setup

1. Install test dependencies:
```bash
cd frontend
npm install --save-dev jest @testing-library/react @testing-library/jest-dom jest-environment-jsdom
```

2. Update `package.json` scripts:
```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  }
}
```

3. Run tests:
```bash
npm test
```

### Test Structure

- `tests/api.test.ts` - API integration tests

## Test Coverage

### Backend Test Coverage

✅ **Chat Routes**
- Create chat
- Get all chats
- Get chat by ID
- Get messages
- Stream responses
- Token limits

✅ **Trading Routes**
- Get trading history
- Get zone history
- Filter by symbol
- Filter by date

✅ **Database Models**
- Chat creation
- Message creation
- Relationships
- Cascade deletes

✅ **Chat Service**
- Streaming responses
- Fallback responses
- Conversation history

✅ **Integration**
- Complete chat flow
- Multiple chat isolation
- Message ordering

### Frontend Test Coverage

✅ **API Integration**
- Chat endpoints
- Trading endpoints
- Streaming responses

## Running All Tests

### Quick Test Script

Create a script to run all tests:

**`run_all_tests.sh` (Linux/Mac):**
```bash
#!/bin/bash
echo "🧪 Running all tests..."

echo "📦 Backend tests..."
cd backend
pytest tests/ -v
cd ..

echo "🌐 Frontend tests..."
cd frontend
npm test
cd ..

echo "✅ All tests completed!"
```

**`run_all_tests.bat` (Windows):**
```batch
@echo off
echo 🧪 Running all tests...

echo 📦 Backend tests...
cd backend
pytest tests\ -v
cd ..

echo 🌐 Frontend tests...
cd frontend
npm test
cd ..

echo ✅ All tests completed!
pause
```

## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-asyncio
      - name: Run tests
        run: |
          cd backend
          pytest tests/ -v

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '20'
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      - name: Run tests
        run: |
          cd frontend
          npm test
```

## Troubleshooting

### Backend Tests

**Issue: Import errors**
- Ensure you're in the backend directory
- Check that all dependencies are installed
- Verify Python path includes backend directory

**Issue: Database errors**
- Tests use in-memory SQLite, should work automatically
- Check `conftest.py` for database setup

**Issue: Async test errors**
- Ensure `pytest-asyncio` is installed
- Check `pytest.ini` for `asyncio_mode = auto`

### Frontend Tests

**Issue: Module not found**
- Run `npm install` in frontend directory
- Check `jest.config.js` for path mappings

**Issue: API connection errors**
- Tests use `NEXT_PUBLIC_API_URL` or default to localhost:8080
- Ensure backend is running or mock API calls

## Test Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Tests should clean up after themselves
3. **Fixtures**: Use pytest fixtures for common setup
4. **Naming**: Use descriptive test names
5. **Assertions**: Be specific about what you're testing
6. **Coverage**: Aim for high test coverage of critical paths

## Next Steps

- Add more edge case tests
- Add performance tests
- Add E2E tests with Playwright/Cypress
- Set up test coverage reporting
- Add pre-commit hooks to run tests

