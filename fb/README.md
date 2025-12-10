# TradeBerg Frontend (Next.js)

Next.js 15 app for the TradeBerg UI – charts, AI chat, sidebar, billing pages, etc.

---

## 1. Prerequisites

- **Node.js**: 20.x recommended
- **npm**: 10+

---

## 2. Install dependencies

From the `frontend/` folder:

```bash
cd frontend
npm install
```

This uses `package.json` / `package-lock.json` to install all React/Next/Tailwind
and UI dependencies.

---

## 3. Environment config

Create a `.env.local` file in `frontend/` (if you don’t already have one):

```env
NEXT_PUBLIC_API_URL=http://localhost:8080/api
```

This is the URL of the FastAPI backend.  
If you keep uvicorn on port 8080 (recommended), you don’t need to change anything else.

---

## 4. Running the frontend

From `frontend/`:

```bash
npm run dev
```

Then open:

- App: `http://localhost:3000`

The app expects the backend at `http://localhost:8080/api` and talks to it through
Next.js API routes under `src/app/api`.

---

## 5. Important frontend pieces

- `src/components/chat/TradebergChat.tsx`
  - Core chat experience: message list, typing animation, prompt tray,
    screenshot capture, attachments, stop‑generation button, edit‑prompt overlay.
- `src/lib/api/backend.ts`
  - Thin client around `/api/chat/...` (Next.js routes) for chats, streaming
    responses, and token limits.
- `src/app/api/chat/**`
  - Next.js route handlers that proxy to FastAPI (`/api/chat/...`).
- `src/app/(main)/trade/page.tsx`
  - Trade view page with TradingView chart + AI side panel.

---

## 6. Typical dev flow

1. Start backend (from `backend/`):
   ```bash
   python -m uvicorn app:app --host 0.0.0.0 --port 8080 --reload
   ```
2. Start frontend (from `frontend/`):
   ```bash
   npm run dev
   ```
3. Visit `http://localhost:3000/trade` and use the chat + chart.

---

## 7. Build & production

To build for production:

```bash
npm run build
npm run start
```

You’ll still need the FastAPI backend running on a reachable URL
and `NEXT_PUBLIC_API_URL` pointing at it.
