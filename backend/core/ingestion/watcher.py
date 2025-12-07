import asyncio
import aiohttp
import feedparser
from datetime import datetime
from typing import List, Dict
from core.ingestion.queue_manager import queue_manager
import re

class SecWatcher:
    """
    Polls SEC RSS feeds for new filings and pushes events to the queue.
    """
    
    RSS_URL = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&CIK=&type=10-K&company=&dateb=&owner=include&start=0&count=40&output=atom"
    
    def __init__(self):
        self.seen_ids = set()
        self.cik_map = {} # Cache for CIK -> Ticker
        
    async def _ensure_cik_map(self):
        if not self.cik_map:
            print("🔄 Loading CIK map...")
            from services.sec_client import sec_client
            # sec_client.get_ticker_map returns {ticker: cik}
            # We need {cik: ticker}
            mapping = await sec_client.get_ticker_map()
            self.cik_map = {str(v).zfill(10): k for k, v in mapping.items()}
            print(f"✅ Loaded {len(self.cik_map)} CIK mappings")

    async def start(self, poll_interval: int = 60):
        """Start the polling loop"""
        await self._ensure_cik_map()
        print(f"👀 SEC Watcher started. Polling {self.RSS_URL} every {poll_interval}s...")
        
        while True:
            try:
                await self._poll()
            except Exception as e:
                print(f"❌ Watcher Error: {e}")
            
            await asyncio.sleep(poll_interval)
            
    async def _poll(self):
        """Fetch and parse RSS feed"""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.RSS_URL, headers={'User-Agent': 'Tradeberg/1.0 (anmol@example.com)'}) as response:
                if response.status != 200:
                    print(f"⚠️ RSS Fetch Failed: {response.status}")
                    return
                
                content = await response.text()
                feed = feedparser.parse(content)
                
                new_count = 0
                for entry in feed.entries:
                    # Entry ID is unique (e.g. accession number URL)
                    if entry.id in self.seen_ids:
                        continue
                        
                    self.seen_ids.add(entry.id)
                    
                    # Parse Title: "10-K - Apple Inc. (0000320193) (Filer)"
                    title = entry.title
                    
                    # Extract CIK
                    match = re.search(r'\((\d{10})\)', title)
                    cik = match.group(1) if match else None
                    
                    if not cik:
                        continue

                    # Resolve Ticker
                    ticker = self.cik_map.get(cik)
                    if not ticker:
                        # Try to find it in the title if map fails? 
                        # Or just skip for now to avoid junk data.
                        # print(f"⚠️ Unknown CIK {cik} for {title}")
                        continue
                    
                    # Extract Form Type
                    form_type = "10-K" # We filtered RSS for 10-K
                    
                    # URL - Need to get primary document, not index
                    # RSS gives us index page like: .../0001048695-25-000157-index.htm
                    # We need the actual document, which requires fetching the index first
                    # For now, we'll use sec_client.get_recent_filings which already does this
                    # But since we're in a watcher loop, let's just pass the index URL
                    # and let the pipeline handle fetching the primary doc
                    url = entry.link
                    
                    # Date
                    filed_at = datetime.strptime(entry.updated, "%Y-%m-%dT%H:%M:%S%z").replace(tzinfo=None)
                    
                    # Push event
                    try:
                        success = queue_manager.push_event(
                            ticker=ticker, 
                            cik=cik, 
                            url=url, 
                            form_type=form_type, 
                            filed_at=filed_at
                        )
                        if success:
                            print(f"📥 Queued: {ticker} ({form_type})")
                            new_count += 1
                    except Exception as e:
                        print(f"❌ Queue Push Error: {e}")
                
                if new_count > 0:
                    print(f"✅ Watcher: Pushed {new_count} new filings to queue.")

watcher = SecWatcher()
