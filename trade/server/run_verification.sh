#!/bin/bash
# TradeBerg V2 Verification Suite Runner

echo "🚀 Starting TradeBerg V2 Verification Suite"
echo "==========================================="
echo "📅 Date: $(date)"
echo ""

# Create logs directory
mkdir -p logs

# Function to run test
run_test() {
    script=$1
    name=$2
    echo "▶️  Running $name..."
    python scripts/tests/$script
    if [ $? -eq 0 ]; then
        echo "✅ $name Completed"
    else
        echo "❌ $name Failed"
        exit 1
    fi
    echo "-------------------------------------------"
}

# Run tests
run_test "test_database_integrity.py" "Database Integrity Check"
run_test "test_fundamental_agent.py" "Fundamental Agent Test"
run_test "test_market_agent.py" "Market Agent Test"
run_test "test_synthesizer.py" "Synthesizer Agent Test"

echo ""
echo "🎉 All verification tests completed successfully!"
echo "📄 Check logs/ directory for detailed JSON reports."
