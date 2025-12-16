"""
Tests for trading routes
"""
import pytest
from fastapi.testclient import TestClient

class TestTradingRoutes:
    """Test trading API endpoints"""
    
    def test_get_trading_history(self, client: TestClient):
        """Test getting trading history"""
        response = client.get("/api/trading/history")
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        assert "total" in data
        assert isinstance(data["history"], list)
    
    def test_get_trading_history_with_symbol_filter(self, client: TestClient):
        """Test getting trading history filtered by symbol"""
        response = client.get("/api/trading/history?symbol=AAPL")
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        # All items should have the filtered symbol
        for item in data["history"]:
            assert item["symbol"] == "AAPL"
    
    def test_get_trading_history_with_date_filters(self, client: TestClient):
        """Test getting trading history with date filters"""
        response = client.get(
            "/api/trading/history",
            params={
                "startDate": "2024-01-01T00:00:00Z",
                "endDate": "2024-12-31T23:59:59Z"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
    
    def test_get_zone_history(self, client: TestClient):
        """Test getting zone history"""
        response = client.get("/api/trading/zones?symbol=AAPL")
        assert response.status_code == 200
        data = response.json()
        assert "zones" in data
        assert "symbol" in data
        assert data["symbol"] == "AAPL"
        assert isinstance(data["zones"], list)
    
    def test_get_zone_history_with_timeframe(self, client: TestClient):
        """Test getting zone history with timeframe"""
        response = client.get(
            "/api/trading/zones",
            params={"symbol": "BTC", "timeframe": "1h"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "zones" in data
        assert "timeframe" in data
        assert data["timeframe"] == "1h"
    
    def test_add_trading_history(self, client: TestClient):
        """Test adding trading history entry"""
        history_item = {
            "id": "test-1",
            "symbol": "AAPL",
            "action": "buy",
            "quantity": 10,
            "price": 175.50,
            "timestamp": "2024-01-01T00:00:00Z",
            "profit_loss": 25.00
        }
        response = client.post("/api/trading/history", json=history_item)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert data["success"] is True
    
    def test_add_zone(self, client: TestClient):
        """Test adding zone entry"""
        zone_item = {
            "id": "zone-1",
            "symbol": "AAPL",
            "zone_type": "support",
            "price_level": 170.00,
            "strength": 0.85,
            "timeframe": "1h",
            "created_at": "2024-01-01T00:00:00Z",
            "touched_count": 3
        }
        response = client.post("/api/trading/zones", json=zone_item)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert data["success"] is True

