# Fundamental Agent Architecture: End-to-End Visualization

## Overview
This diagram captures the complete lifecycle of the **Fundamental Agent**, from the continuous ingestion of SEC filings to the generation of structured, cited financial analysis.

## Architecture Diagram

```mermaid
graph TD
    %% --- Ingestion Pipeline (The "Librarian") ---
    subgraph Ingestion ["Ingestion Pipeline (Continuous Background Process)"]
        direction TB
        SEC["SEC EDGAR (RSS/API)"]
        Watcher["Ingestion Watcher (Celery/Kafka)"]
        Downloader["Downloader (S3)"]
        Extractor["Text Extractor & Cleaner"]
        Chunker["Chunker (Token-based)"]
        Embedder["Embedding Model"]
        VectorDB[("Vector DB (pgvector)")]
        MetaDB[("Metadata DB (Postgres)")]

        SEC -->|"New Filing Event"| Watcher
        Watcher -->|"Trigger Task"| Downloader
        Downloader -->|"Raw HTML/XBRL"| Extractor
        Extractor -->|"Clean Text (No Tables)"| Chunker
        Chunker -->|"Text Chunks + Metadata"| Embedder
        Embedder -->|"Vectors"| VectorDB
        Downloader -->|"Filing Metadata"| MetaDB
    end

    %% --- User Request Flow ---
    subgraph RequestFlow ["User Request Flow"]
        User["User"]
        Router["Intent Router"]
        
        User -->|"Explain AAPL revenue & margins..."| Router
        Router -->|"Intent: FUNDAMENTAL_QUERY"| FundAgent
    end

    %% --- Agent Execution Core ---
    subgraph AgentCore ["Fundamental Agent Core"]
        FundAgent["Fundamental Agent Class"]
        
        subgraph ParallelFetch ["Async Data Gathering (asyncio.gather)"]
            Retriever["Retrieval Service"]
            MarketData["Market Data Service"]
            Redis["Redis Cache"]
            GoogleSearch["Google Search Grounding"]
        end
        
        ContextBuilder["Context Builder"]
        LLM["LLM (Gemini 1.5)"]
        OutputEngine["Output Engine"]
        
        FundAgent -->|"Run()"| ParallelFetch
        
        %% Retrieval Path
        Retriever -->|"Hybrid Search (BM25 + Vector)"| VectorDB
        VectorDB -->|"Top K Chunks + Source Meta"| Retriever
        
        %% Market Data Path
        MarketData -->|"Check Cache"| Redis
        Redis -.->|"Miss"| GoogleSearch
        GoogleSearch -->|"Web Grounded Data"| MarketData
        
        %% Synthesis
        Retriever -->|"Filings Context"| ContextBuilder
        MarketData -->|"Live Data"| ContextBuilder
        ContextBuilder -->|"Construct Prompt"| LLM
        
        %% System Prompt Logic
        note1[/"System Prompt:
        - Persona: TradeBerg Analyst
        - Rules: Cited facts only
        - Output: Sections + Visual Schema"/]
        note1 -.-> LLM
        
        LLM -->|"Raw Markdown Response"| OutputEngine
    end

    %% --- Output Processing ---
    subgraph OutputLayer ["Output Processing & Formatting"]
        OutputEngine -->|"Parse & Extract"| Tables["JSON Tables"]
        OutputEngine -->|"Parse & Extract"| Charts["JSON Charts"]
        OutputEngine -->|"Verify & Format"| Citations["Citations [Source]"]
        
        Tables & Charts & Citations --> FinalResponse["Structured Response Object"]
    end
    
    FinalResponse -->|"Stream (Markdown + JSON)"| User
```

## Key Components Explained

### 1. Ingestion Pipeline
*   **Watcher**: Polls SEC RSS feeds every few minutes.
*   **Extractor**: Strips HTML tags, identifies sections (MD&A, Risk Factors), and cleans text.
*   **Vector DB**: Stores embeddings with rich metadata (`ticker`, `form`, `filed_at`, `section`).

### 2. Agent Core
*   **Parallel Execution**: Fetches RAG data and Live Market data simultaneously for speed.
*   **Context Builder**: Merges "Past" (Filings) with "Present" (Live Price) into a single prompt.
*   **System Prompt**: Enforces the "TradeBerg Analyst" persona—concise, factual, and strictly cited.

### 3. Output Engine
*   **Role**: The "Formatter". It takes the raw text from the LLM and converts it into a structured format the frontend can render.
*   **Features**:
    *   Detects tables in text -> Converts to React-ready JSON.
    *   Detects time-series data -> Converts to Chart.js/Recharts JSON.
    *   Validates citations against the retrieved chunks.
