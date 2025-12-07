#!/bin/bash
# Script to run backend tests

echo "🧪 Running TradeBerg Backend Tests..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run pytest
pytest tests/ -v --tb=short

echo ""
echo "✅ Tests completed!"

