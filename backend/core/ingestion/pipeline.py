import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Optional
from core.ingestion.queue_manager import queue_manager
from services.gemini_service import gemini_service
from database import SessionLocal
from models.document import DocumentChunk
from models.ingestion import IngestionEvent

class IngestionWorker:
    """
    Worker that consumes events from the queue and processes filings.
    Pipeline: Download -> Extract -> Chunk -> Embed -> Store.
    """
    
    def __init__(self):
        self.chunk_size = 2000
        self.chunk_overlap = 200

    async def start(self, poll_interval: int = 5):
        """Start the worker loop"""
        print(f"👷 Ingestion Worker started. Polling queue every {poll_interval}s...")
        
        while True:
            try:
                event = queue_manager.pop_event()
                if event:
                    print(f"⚙️ Processing {event.ticker} ({event.form_type})...")
                    success = await self._process_event(event)
                    
                    if success:
                        queue_manager.complete_event(event.id)
                        print(f"✅ Completed {event.ticker}")
                    else:
                        queue_manager.fail_event(event.id, "Processing failed")
                        print(f"❌ Failed {event.ticker}")
                else:
                    # Empty queue, sleep
                    await asyncio.sleep(poll_interval)
                    
            except Exception as e:
                print(f"❌ Worker Error: {e}")
                await asyncio.sleep(poll_interval)

    async def _process_event(self, event: IngestionEvent) -> bool:
        """Execute the pipeline for a single event"""
        try:
            # 1. Resolve Primary Document URL
            if not event.filing_url:
                print("No URL provided")
                return False
            
            # If URL is an index page, extract the primary document
            primary_url = event.filing_url
            if 'index.htm' in event.filing_url:
                print(f"   Resolving primary document from index...")
                primary_url = await self._get_primary_document_url(event.filing_url)
                if not primary_url:
                    print("   Failed to resolve primary document")
                    return False
                print(f"   Primary document: {primary_url}")
                
            # 2. Download
            print(f"   Downloading {primary_url}...")
            html = await self._download_text(primary_url)
            if not html:
                return False
                
            # 3. Extract
            print("   Extracting text...")
            text = self._clean_html(html)
            
            # 4. Chunk
            print("   Chunking...")
            chunks = self._chunk_text(text)
            
            # 5. Embed & Store
            print(f"   Embedding {len(chunks)} chunks...")
            await self._store_chunks(event.ticker, chunks, event.form_type)
            
            return True
            
        except Exception as e:
            print(f"   Pipeline Error: {e}")
            return False

    async def _get_primary_document_url(self, index_url: str) -> Optional[str]:
        """Parse index page to extract primary document URL"""
        try:
            html = await self._download_text(index_url)
            if not html:
                return None
                
            soup = BeautifulSoup(html, 'lxml')
            # Find the primary document link (usually first .htm or .html file that's not index)
            table = soup.find('table', {'summary': 'Document Format Files'})
            if table:
                for row in table.find_all('tr'):
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        doc_link = cells[2].find('a')
                        if doc_link and doc_link.get('href'):
                            href = doc_link['href']
                            # Skip index files
                            if 'index.htm' not in href.lower():
                                # Construct full URL
                                base_url = index_url.rsplit('/', 1)[0]
                                return f"{base_url}/{href}"
            
            # Fallback: look for any .htm file link
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.endswith('.htm') and 'index' not in href.lower():
                    base_url = index_url.rsplit('/', 1)[0]
                    return f"{base_url}/{href}"
                    
            return None
        except Exception as e:
            print(f"   Error parsing index: {e}")
            return None

    async def _download_text(self, url: str) -> Optional[str]:
        headers = {
            'User-Agent': 'Tradeberg/1.0 (anmol@example.com)',
            'Accept-Encoding': 'gzip, deflate',
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.text()
                return None

    def _clean_html(self, html: str) -> str:
        import warnings
        from bs4 import XMLParsedAsHTMLWarning
        warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
        
        soup = BeautifulSoup(html, 'lxml')
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text(separator=' ')
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        return text

    def _chunk_text(self, text: str) -> List[str]:
        chunks = []
        start = 0
        text_len = len(text)
        while start < text_len:
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += self.chunk_size - self.chunk_overlap
        return chunks

    async def _store_chunks(self, ticker: str, chunks: List[str], source: str):
        db = SessionLocal()
        try:
            # Clear old chunks for this ticker/source (Idempotency)
            db.query(DocumentChunk).filter(
                DocumentChunk.ticker == ticker,
                DocumentChunk.source == source
            ).delete()
            
            batch_size = 10
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i+batch_size]
                for j, content in enumerate(batch):
                    embedding = await gemini_service.embed_content(content)
                    if embedding:
                        chunk_obj = DocumentChunk(
                            ticker=ticker,
                            content=content,
                            embedding=embedding,
                            source=source,
                            chunk_index=i + j
                        )
                        db.add(chunk_obj)
                db.commit()
        finally:
            db.close()

pipeline = IngestionWorker()
