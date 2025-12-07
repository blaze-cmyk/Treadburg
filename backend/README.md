# TradeBerg Backend (FastAPI)

FastAPI backend for the TradeBerg trading / AI assistant.  
This powers the chat, history, billing hooks and future integrations.

---

## 1. Prerequisites

- **Python**: 3.11+ (you are using 3.12 in `.runvenv`, which is fine)
- **pip** (or pipx)
- **Virtual env** (recommended)
- **Perplexity API key** for AI responses

---

## 2. Environment setup

From the `backend/` folder:

```bash
cd backend

# 1) Create and activate venv (if you don't already have one)
python -m venv .runvenv
source .runvenv/bin/activate        # macOS / Linux
# .runvenv\Scripts\activate.bat     # Windows

# 2) Install dependencies
pip install -r requirements.txt

# 3) Env file
cp .env.example .env
```

Edit `.env` and set at minimum:

```env
PERPLEXITY_API_KEY=your_key_here
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8080
```

You normally do **not** need Supabase/Stripe keys just to run chat.

---

## 3. Running the backend

From `backend/` with your venv active:

```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

The server will start on:

- API root: `http://localhost:8080/api`
- Docs (Swagger): `http://localhost:8080/docs`
- Health check: `http://localhost:8080/health`

The frontend expects the backend on **`http://localhost:8080/api`** by default.

---

## 4. Main modules

- `app.py` – FastAPI app, CORS, router wiring.
- `routes/chat.py` – **core chat API**:
  - `POST /api/chat/create` – create chat and first message.
  - `POST /api/chat/{chat_id}/stream` – streaming AI response.
  - CRUD for chats + messages.
- `services/intent_service.py` – rule‑based intent classifier.
- `services/tradeberg_prompt_service.py` – builds immutable TradeBerg prompt.
- `services/perplexity_service.py` – wrapper over Perplexity API.
- `services/formatter_service.py` – cleans markdown chunks.
- `core/constants.py` – **immutable TradeBerg doctrine / system prompt**.
- `database.py`, `models/chat.py`, `models/user.py` – SQLite storage.

---

## 5. CORS and frontend connection

Backend CORS is configured to allow the Next.js app:

- `http://localhost:3000`
- `http://127.0.0.1:3000`

If you change ports or domains, update `.env`:

```env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

The frontend does **not** call FastAPI directly from the browser; it hits
Next.js API routes (`/api/chat/...`), which proxy to this backend.

---

## 6. Running tests

From `backend/` with venv active:

```bash
pytest
```

---

## 7. Useful tips

- If imports for Supabase/Stripe complain but you’re not using billing,
  you can leave those envs empty – chat will still work.
- If you change anything under `services/` or `routes/chat.py` while
  running `uvicorn --reload`, the server will auto‑restart.

Backend and frontend run independently – just keep this server on
`localhost:8080` while running the Next.js app on `localhost:3000`.

