"""
Silent Chart Screenshot Capture Service
Captures TradingView charts without user interaction using Playwright
"""

import asyncio
import base64
import os
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

from open_webui.utils import logger

log = logger.logger

# Global browser instance cache for performance
_cached_browser: Optional[Browser] = None
_cached_context: Optional[BrowserContext] = None


async def get_cached_browser() -> tuple[Browser, BrowserContext]:
    """
    Gets or creates a cached browser instance for faster screenshots.
    Reuses browser across requests to improve performance.
    """
    global _cached_browser, _cached_context
    
    try:
        if _cached_browser and _cached_browser.is_connected():
            return _cached_browser, _cached_context
    except Exception:
        # Browser disconnected, need to recreate
        _cached_browser = None
        _cached_context = None
    
    try:
        playwright = await async_playwright().start()
        
        browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-software-rasterizer',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        _cached_browser = browser
        _cached_context = context
        
        log.info("📸 Created new browser instance for chart capture")
        return browser, context
        
    except Exception as e:
        log.error(f"❌ Failed to create browser instance: {e}")
        # If Playwright browsers aren't installed, provide helpful error
        if "Executable doesn't exist" in str(e) or "playwright" in str(e).lower():
            log.error("💡 SOLUTION: Run 'python -m playwright install chromium' to install browser")
        raise


async def capture_chart_silently(
    symbol: str = "BTCUSDT",
    timeframe: str = "15m",
    frontend_url: Optional[str] = None,
    timeout: int = 30000
) -> Optional[str]:
    """
    Captures TradingView chart screenshot WITHOUT user interaction.
    This runs entirely in backend - user never sees it happen.
    
    Args:
        symbol: Trading symbol (e.g., "BTCUSDT")
        timeframe: Chart timeframe (e.g., "15m", "1h", "1d")
        frontend_url: Base URL of frontend (defaults to env var or localhost)
        timeout: Timeout in milliseconds
        
    Returns:
        Base64-encoded PNG image string, or None if capture failed
    """
    browser = None
    page = None
    
    try:
        log.info(f"📸 Silently capturing chart for {symbol} ({timeframe})...")
        
        # Get frontend URL
        if not frontend_url:
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        
        # Get cached browser
        browser, context = await get_cached_browser()
        
        # Create new page
        page = await context.new_page()
        
        # Navigate to trading terminal/page with chart
        # Trade Terminal route: /?tt=1 or /terminal?symbol=...&interval=...
        # Try multiple URL formats to ensure we capture the chart
        chart_urls = [
            f"{frontend_url}/terminal?symbol={symbol}&interval={timeframe}",
            f"{frontend_url}/?tt=1&symbol={symbol}&interval={timeframe}",
            f"{frontend_url}/?symbol={symbol}&interval={timeframe}&tt=1"
        ]
        
        chart_url = chart_urls[0]  # Primary URL
        log.debug(f"Navigating to: {chart_url}")
        
        try:
            await page.goto(chart_url, wait_until="networkidle", timeout=timeout)
        except Exception as e:
            log.warning(f"Primary URL failed, trying alternatives: {e}")
            # Try alternative URLs
            for alt_url in chart_urls[1:]:
                try:
                    await page.goto(alt_url, wait_until="networkidle", timeout=timeout)
                    chart_url = alt_url
                    log.info(f"Successfully navigated to: {chart_url}")
                    break
                except Exception:
                    continue
        
        # Wait for TradingView iframe or chart element to load
        # Trade Terminal uses TradingView iframe, Historical uses canvas
        try:
            # Wait for TradingView iframe (primary for Trade Terminal)
            await page.wait_for_selector(
                'iframe[id*="tradingview"], iframe[src*="tradingview"], iframe[title*="TradingView"], .tradingview-widget-container iframe',
                timeout=15000
            )
            log.debug("TradingView iframe found")
            
            # Additional wait for chart to fully render
            await asyncio.sleep(3)
            
        except Exception as e:
            log.warning(f"TradingView iframe not found, trying chart container: {e}")
            # Fallback: try chart container or canvas
            try:
                await page.wait_for_selector(
                    '#tradeberg-chart, #historical-chart, canvas, .tradingview-widget-container',
                    timeout=10000
                )
                log.debug("Chart container found")
                await asyncio.sleep(2)
            except Exception as e2:
                log.warning(f"Chart container also not found: {e2}")
                await asyncio.sleep(3)  # Final fallback wait
        
        # Try to capture specific chart element first
        screenshot = None
        
        # Method 1: Try to capture TradingView iframe (Trade Terminal)
        try:
            # Multiple selectors for TradingView iframe
            iframe_selectors = [
                'iframe[id*="tradingview"]',
                'iframe[src*="tradingview"]',
                'iframe[title*="TradingView"]',
                '.tradingview-widget-container iframe',
                'iframe.tradingview-widget-container__widget'
            ]
            
            iframe_element = None
            for selector in iframe_selectors:
                try:
                    iframe_element = await page.query_selector(selector)
                    if iframe_element:
                        log.debug(f"Found TradingView iframe with selector: {selector}")
                        break
                except Exception:
                    continue
            
            if iframe_element:
                log.info("📸 Capturing TradingView iframe (Trade Terminal)")
                screenshot_bytes = await iframe_element.screenshot(type='png')
                screenshot = base64.b64encode(screenshot_bytes).decode('utf-8')
                log.info(f"✅ Screenshot captured: {len(screenshot)} chars")
        except Exception as e:
            log.debug(f"Could not capture TradingView iframe: {e}")
        
        # Method 2: Fallback to chart container
        if not screenshot:
            try:
                chart_selectors = [
                    '#tradeberg-chart',
                    '#historical-chart',
                    '.tradingview-widget-container',
                    'canvas'  # For lightweight charts
                ]
                
                for selector in chart_selectors:
                    try:
                        element = await page.query_selector(selector)
                        if element:
                            log.debug(f"Capturing element: {selector}")
                            screenshot_bytes = await element.screenshot(type='png')
                            screenshot = base64.b64encode(screenshot_bytes).decode('utf-8')
                            break
                    except Exception:
                        continue
            except Exception as e:
                log.debug(f"Could not capture chart container: {e}")
        
        # Method 3: Fallback to viewport screenshot (crop to chart area if possible)
        if not screenshot:
            try:
                log.debug("Capturing viewport (fallback)")
                screenshot_bytes = await page.screenshot(
                    type='png',
                    full_page=False,
                    clip={'x': 0, 'y': 0, 'width': 1920, 'height': 800}  # Approximate chart area
                )
                screenshot = base64.b64encode(screenshot_bytes).decode('utf-8')
            except Exception as e:
                log.error(f"Viewport screenshot failed: {e}")
                return None
        
        if screenshot:
            log.info(f"✅ Chart captured successfully (hidden from user) - {len(screenshot)} chars")
            return screenshot
        else:
            log.warning("⚠️ Screenshot capture returned None")
            return None
            
    except Exception as error:
        log.error(f"❌ Chart capture failed: {error}")
        return None
        
    finally:
        # Close page but keep browser for reuse
        if page:
            try:
                await page.close()
            except Exception:
                pass


async def capture_from_existing_session(
    page: Page,
    selector: str = "#tradeberg-chart, #historical-chart"
) -> Optional[str]:
    """
    Captures screenshot from an already-open browser page.
    Use this if you have a persistent browser session.
    
    Args:
        page: Playwright page object
        selector: CSS selector for chart element
        
    Returns:
        Base64-encoded PNG image string, or None if capture failed
    """
    try:
        element = await page.query_selector(selector)
        
        if element:
            screenshot_bytes = await element.screenshot(type='png')
            return base64.b64encode(screenshot_bytes).decode('utf-8')
        else:
            # Fallback to viewport
            screenshot_bytes = await page.screenshot(type='png', full_page=False)
            return base64.b64encode(screenshot_bytes).decode('utf-8')
            
    except Exception as error:
        log.error(f"Screenshot capture error: {error}")
        return None


async def cleanup_browser():
    """
    Cleanup browser instance. Call this on application shutdown.
    """
    global _cached_browser, _cached_context
    
    try:
        if _cached_context:
            await _cached_context.close()
            _cached_context = None
        
        if _cached_browser:
            await _cached_browser.close()
            _cached_browser = None
            
        log.info("🧹 Browser cleanup completed")
    except Exception as e:
        log.error(f"Browser cleanup error: {e}")

