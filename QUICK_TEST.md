# Quick Test Guide

## Quick Start - Run Tests

### Backend Tests (Recommended First)

```bash
cd backend

# Install test dependencies (if not already installed)
pip install pytest pytest-asyncio

# Run all tests
pytest tests/ -v

# Or use the batch script (Windows)
tests\run_tests.bat
```

### Expected Output

You should see tests passing for:
- ✅ Chat routes (create, get, list, messages, streaming)
- ✅ Trading routes (history, zones)
- ✅ Database models (Chat, Message, User)
- ✅ Chat service (streaming, fallback)
- ✅ Integration tests (full chat flow)

## Test Files Created

### Backend Tests
- `backend/tests/test_chat_routes.py` - 15+ chat API tests
- `backend/tests/test_trading_routes.py` - 7 trading API tests
- `backend/tests/test_database.py` - 5 database model tests
- `backend/tests/test_chat_service.py` - 5 chat service tests
- `backend/tests/test_integration.py` - 3 integration tests

### Frontend Tests
- `frontend/tests/api.test.ts` - API integration tests

## Common Issues

### Issue: Import errors
**Solution**: Make sure you're in the `backend` directory when running tests

### Issue: Database errors
**Solution**: Tests use in-memory SQLite, should work automatically. Check `conftest.py`

### Issue: pytest not found
**Solution**: 
```bash
pip install pytest pytest-asyncio
```

### Issue: Module import errors
**Solution**: Tests automatically add backend to path. If issues persist, run from backend directory:
```bash
cd backend
pytest tests/ -v
```

## Test Coverage

✅ **35+ tests** covering:
- All chat endpoints
- Trading endpoints
- Database operations
- Service layer
- Integration flows

## Next Steps After Tests Pass

1. ✅ Verify all tests pass
2. ✅ Start backend: `cd backend && python app.py`
3. ✅ Start frontend: `cd frontend && npm run dev`
4. ✅ Test manually in browser at `http://localhost:3000`

