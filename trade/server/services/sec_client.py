"""
SEC Client for fetching data from SEC EDGAR API.
Python port of the TypeScript SEC client.
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional
import time


class SECClient:
    """Client for interacting with SEC EDGAR API"""
    
    BASE_URL = "https://data.sec.gov"
    
    def __init__(self):
        self.last_request_time = 0
        self.min_request_interval = 0.15  # 150ms between requests (safe limit)
        self._ticker_map = None  # Cache for ticker-to-CIK mappings
        
    async def get_ticker_map(self) -> Dict[str, str]:
        """
        Fetch ticker-to-CIK mapping from SEC API
        Returns: Dict mapping ticker symbols to CIK numbers
        """
        if self._ticker_map is not None:
            return self._ticker_map
            
        await self._rate_limit()
        
        url = "https://www.sec.gov/files/company_tickers.json"
        headers = {
            'User-Agent': 'Tradeberg/1.0 (anmol@example.com)',
            'Accept': 'application/json'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Transform {"0": {"cik_str": 320193, "ticker": "AAPL", ...}, ...}
                        # Into {"AAPL": "0000320193", ...}
                        ticker_map = {}
                        for entry in data.values():
                            ticker = entry.get('ticker', '').upper()
                            cik = str(entry.get('cik_str', ''))
                            if ticker and cik:
                                # Pad CIK to 10 digits
                                ticker_map[ticker] = cik.zfill(10)
                        
                        self._ticker_map = ticker_map
                        print(f"✅ Loaded {len(ticker_map)} ticker-to-CIK mappings")
                        return ticker_map
                    else:
                        print(f"Failed to fetch ticker map: {response.status}")
                        return {}
        except Exception as e:
            print(f"Error fetching ticker map: {e}")
            return {}
    
    async def _get_cik(self, ticker: str) -> Optional[str]:
        """Get CIK for a ticker symbol"""
        ticker_map = await self.get_ticker_map()
        return ticker_map.get(ticker.upper())
    
    async def _rate_limit(self):
        """Ensure we don't exceed SEC rate limits"""
        now = time.time()
        time_since_last = now - self.last_request_time
        if time_since_last < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    async def get_company_facts(self, ticker: str) -> Optional[Dict]:
        """
        Fetch company facts from SEC EDGAR API
        
        Args:
            ticker: Stock ticker symbol (e.g., 'TSLA')
            
        Returns:
            Company facts data or None if not found
        """
        cik = await self._get_cik(ticker)
        if not cik:
            print(f"CIK not found for ticker: {ticker}")
            return None
        
        await self._rate_limit()
        
        url = f"{self.BASE_URL}/api/xbrl/companyfacts/CIK{cik}.json"
        headers = {
            'User-Agent': 'Tradeberg/1.0 (anmol@example.com)',
            'Accept': 'application/json'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"SEC API error: {response.status}")
                        return None
        except Exception as e:
            print(f"Error fetching SEC data: {e}")
            return None
    async def get_recent_filings(self, ticker: str, form_type: str = "10-K") -> Optional[Dict]:
        """
        Fetch recent filings for a ticker to find a specific form type.
        """
        cik = await self._get_cik(ticker)
        if not cik:
            print(f"CIK not found for ticker: {ticker}")
            return None
            
        await self._rate_limit()
        
        # SEC Submissions API
        url = f"{self.BASE_URL}/submissions/CIK{cik}.json"
        headers = {
            'User-Agent': 'Tradeberg/1.0 (anmol@example.com)',
            'Accept': 'application/json'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        filings = data.get("filings", {}).get("recent", {})
                        
                        if not filings:
                            return None
                            
                        # Iterate to find the latest form_type
                        forms = filings.get("form", [])
                        accession_numbers = filings.get("accessionNumber", [])
                        primary_documents = filings.get("primaryDocument", [])
                        filing_dates = filings.get("filingDate", [])
                        
                        for i, form in enumerate(forms):
                            if form == form_type:
                                # Found it!
                                acc_num = accession_numbers[i]
                                primary_doc = primary_documents[i]
                                filed_date = filing_dates[i]
                                
                                # Construct URL
                                # URL format: https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number_no_dashes}/{primary_document}
                                acc_num_clean = acc_num.replace("-", "")
                                filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_num_clean}/{primary_doc}"
                                
                                return {
                                    "ticker": ticker,
                                    "cik": cik,
                                    "form_type": form_type,
                                    "filed_at": filed_date,
                                    "url": filing_url,
                                    "accession_number": acc_num
                                }
                        return None
                    else:
                        print(f"SEC API error: {response.status}")
                        return None
        except Exception as e:
            print(f"Error fetching filings: {e}")
            return None

# Singleton instance
sec_client = SECClient()
