from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from open_webui.env import SRC_LOG_LEVELS
from open_webui.utils import logger

# Initialize logger
logger.start_logger()
log = logger.logger

router = APIRouter(prefix="/nansen", tags=["nansen"])

# Nansen API configuration
NANSEN_API_KEY = os.getenv("NANSEN_API_KEY", "")
NANSEN_API_BASE_URL = os.getenv("NANSEN_API_BASE_URL", "https://api.nansen.ai/api/v1")


class DeFiHoldingsRequest(BaseModel):
    wallet_address: str


class DeFiHoldingsResponse(BaseModel):
    wallet_address: str
    holdings: List[Dict[str, Any]]
    total_value_usd: float
    chains: List[str]
    timestamp: str


class SmartMoneyRequest(BaseModel):
    chains: List[str] = ["ethereum", "solana", "base"]
    page: int = 1
    per_page: int = 50
    order_by: str = "value_usd"


@router.post("/defi-holdings")
async def get_defi_holdings(request: DeFiHoldingsRequest) -> Dict[str, Any]:
    """
    Get DeFi holdings for a specific wallet address.
    
    Args:
        request: DeFiHoldingsRequest with wallet_address
        
    Returns:
        Dict containing wallet holdings, balances, and token details
    """
    if not NANSEN_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Nansen API key not configured. Please set NANSEN_API_KEY in .env"
        )
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{NANSEN_API_BASE_URL}/portfolio/defi-holdings",
                headers={
                    "apiKey": NANSEN_API_KEY,
                    "Content-Type": "application/json"
                },
                json={"wallet_address": request.wallet_address}
            )
            
            if response.status_code != 200:
                log.error(f"Nansen API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Nansen API error: {response.text}"
                )
            
            data = response.json()
            log.info(f"Retrieved DeFi holdings for wallet: {request.wallet_address}")
            
            return {
                "success": True,
                "wallet_address": request.wallet_address,
                "data": data
            }
            
    except httpx.TimeoutException:
        log.error("Nansen API request timeout")
        raise HTTPException(status_code=504, detail="Request timeout")
    except Exception as e:
        log.exception(f"Error fetching DeFi holdings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/smart-money/holdings")
async def get_smart_money_holdings(request: SmartMoneyRequest) -> Dict[str, Any]:
    """
    Get smart money holdings across multiple chains.
    
    Args:
        request: SmartMoneyRequest with chains, pagination, and ordering
        
    Returns:
        Dict containing smart money holdings and portfolio data
    """
    if not NANSEN_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Nansen API key not configured. Please set NANSEN_API_KEY in .env"
        )
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{NANSEN_API_BASE_URL}/smart-money/holdings",
                headers={
                    "apiKey": NANSEN_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "chains": request.chains,
                    "pagination": {
                        "page": request.page,
                        "per_page": request.per_page
                    },
                    "order_by": [
                        {
                            "field": request.order_by,
                            "direction": "DESC"
                        }
                    ]
                }
            )
            
            if response.status_code != 200:
                log.error(f"Nansen API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Nansen API error: {response.text}"
                )
            
            data = response.json()
            log.info(f"Retrieved smart money holdings for chains: {request.chains}")
            
            return {
                "success": True,
                "data": data
            }
            
    except httpx.TimeoutException:
        log.error("Nansen API request timeout")
        raise HTTPException(status_code=504, detail="Request timeout")
    except Exception as e:
        log.exception(f"Error fetching smart money holdings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def nansen_health_check() -> Dict[str, Any]:
    """Check if Nansen API is configured and accessible."""
    return {
        "status": "ok",
        "configured": bool(NANSEN_API_KEY),
        "api_base_url": NANSEN_API_BASE_URL,
        "api_key_present": "***" + NANSEN_API_KEY[-4:] if NANSEN_API_KEY else "missing"
    }

@router.get("/test")
async def test_endpoint():
    """Simple test endpoint to verify router is working."""
    return {"message": "Nansen router is working!", "timestamp": "2025-11-05"}
