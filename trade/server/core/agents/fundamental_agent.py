import asyncio
import json
import logging
from typing import Dict, Any
from core.intent_router import IntentObject
from services.market_data_service import market_data_service
from services.vector_service import vector_service
from services.gemini_service import gemini_service
from core.output_engine import output_engine
from core.constants import TRADEBERG_GENERAL_IDENTITY

logger = logging.getLogger("fundamental_agent")
MAX_WAIT = 40  # seconds

class FundamentalAgent:
    """
    Analyzes company fundamentals using RAG (Filings) + Live Data.
    Enforces strict citation discipline.
    """
    
    SYSTEM_PROMPT = TRADEBERG_GENERAL_IDENTITY

    async def run(self, intent: IntentObject) -> Dict[str, Any]:
        ticker = intent.tickers[0] if intent.tickers else None
        query = intent.text.strip()
        
        try:
            # 🟦 1. General conversation — no ticker found
            if not ticker:
                prompt = f"{self.SYSTEM_PROMPT}\n\nUser query: {query}"
                # Guard Gemini call with timeout
                response_text, grounding_metadata = await asyncio.wait_for(
                    gemini_service.generate_content(
                        prompt=prompt,
                        use_search_grounding=True,           # web search always on for chat mode
                        system_instruction=self.SYSTEM_PROMPT
                    ),
                    timeout=MAX_WAIT
                )
                # Use OutputEngine to ensure charts are wrapped even in general chat
                formatted = output_engine.format_fundamental_response(
                    raw_text=response_text,
                    rag_docs=[],
                    market_data={}
                )
                
                if grounding_metadata:
                    formatted['grounding_metadata'] = grounding_metadata
                    
                return formatted

            # 🟩 2. Ticker present — normal filing workflow
            logger.info(f"[FA] Start analysis for {ticker}")
            
            # 2a. Parallel Data Fetching
            rag_docs, market_snapshot = await asyncio.gather(
                vector_service.search(intent.text, ticker=ticker, limit=5),
                market_data_service.get_snapshot(ticker)
            )
            
            # 2b. On-Demand Ingestion Fallback
            if not rag_docs:
                print(f"🔥 No data for {ticker}, triggering on-demand ingestion...")
                from services.ingest_service import ingest_service
                
                try:
                    # Try to ingest, but don't wait forever. 
                    # If it takes too long, we'll fall back to Search.
                    result = await asyncio.wait_for(
                        ingest_service.ingest_now(ticker),
                        timeout=4 # Wait up to 4s for SEC data
                    )
                    
                    if result["status"] == "completed":
                        rag_docs = await vector_service.search(intent.text, ticker=ticker, limit=5)
                        print(f"✅ Retry successful, found {len(rag_docs)} chunks")
                    else:
                        print(f"⚠️ On-demand ingestion status: {result['status']}")
                        
                except asyncio.TimeoutError:
                    print(f"⚠️ Ingestion timed out (4s) - falling back to Google Search")
                    # We proceed without rag_docs, relying on Search Grounding
                    pass
                except Exception as e:
                    print(f"⚠️ Ingestion failed: {e}")
                    pass

            # 2c. Build Context
            context = self._build_context(intent.text, rag_docs, market_snapshot)
            
            # 2c.1. Fallback Instruction
            if not rag_docs:
                context += "\n\nCRITICAL INSTRUCTION: No SEC filings were found for this query. You MUST use Google Search to find the answer. Do not refuse to answer. Provide the best available data from search results."
            
            # 2d. Generate Analysis
            # Enable search if we lack specific data or just want broader context
            # ALSO: If intent.meta['force_search'] is True (from Chat Page), always enable search.
            force_search = intent.meta.get('force_search', False)
            search_flag = (not rag_docs) or force_search
            
            response_text, grounding_metadata = await asyncio.wait_for(
                gemini_service.generate_content(
                    prompt=f"{self.SYSTEM_PROMPT}\n\n{context}",
                    use_search_grounding=search_flag,
                    system_instruction=self.SYSTEM_PROMPT
                ),
                timeout=MAX_WAIT
            )
            
            # 3. Format Output
            formatted = output_engine.format_fundamental_response(
                raw_text=response_text,
                rag_docs=rag_docs,
                market_data=market_snapshot
            )
            
            # Add grounding metadata if available
            if grounding_metadata:
                formatted['grounding_metadata'] = grounding_metadata
                
            logger.info(f"[FA] ✅ Finished {ticker}")
            return formatted

        except asyncio.TimeoutError:
            logger.warning(f"[FA] Timed out after {MAX_WAIT}s")
            return {
                "markdown": "Gemini timed out – please retry.",
                "agent": "fundamental",
            }

        except Exception as e:
            logger.exception(f"[FA] Internal error for {ticker or 'query'}: {e}")
            return {
                "markdown": f"Error processing {ticker or 'query'}: {e}",
                "agent": "fundamental",
            }

    def _build_context(self, query: str, docs: list, snapshot: dict) -> str:
        # Convert doc objects to text
        doc_text = ""
        for i, d in enumerate(docs):
            # d is a DocumentChunk object (SQLAlchemy model)
            text = d.content # The column is 'content', not 'text'
            source_name = d.source
            
            # Metadata access via property
            meta = d.meta if d.meta else {}
            page = meta.get('page', 'N/A')
            
            doc_text += f"--- Doc {i+1} (Source: {source_name}, Page: {page}) ---\n{text}\n\n"
        
        return f"""
        USER QUERY: {query}
        
        LIVE MARKET DATA:
        Price: {snapshot.get('price')}
        Volume: {snapshot.get('volume')}
        Source: {snapshot.get('source')}
        
        RETRIEVED FILINGS (RAG):
        {doc_text}
        """

fundamental_agent = FundamentalAgent()
