# OpsMind AI — Production Deployment Architecture Guide

> **Phase 7–8 documentation:** End-to-end integration testing status, environment
> configuration, and full deployment runbook for Render (backend) and Vercel (frontend).

---

## Table of Contents

1. [Integration Health Checks](#1-integration-health-checks)
2. [Environment Variables Reference](#2-environment-variables-reference)
3. [Backend Deployment — Render / Railway](#3-backend-deployment--render--railway)
4. [Frontend Deployment — Vercel / Netlify](#4-frontend-deployment--vercel--netlify)
5. [CORS & Network Configuration](#5-cors--network-configuration)
6. [Post-Deployment Verification Checklist](#6-post-deployment-verification-checklist)
7. [Architecture Diagram](#7-architecture-diagram)

---

## 1. Integration Health Checks

### ✅ React Dev Server (Phase 6 Verified)

| Check | Status | Detail |
|-------|--------|--------|
| Vite dev server | 🟢 **RUNNING** | `http://localhost:5173/` — VITE v8.1.4, ready in 789 ms |
| `App.jsx` routing | 🟢 **HEALTHY** | 6 routes wired: `/`, `/ledger`, `/forecasts`, `/logs`, `/settings`, `/profile` |
| Axios base URL | 🟢 **HEALTHY** | `VITE_API_URL \|\| 'http://localhost:8000'` — env-driven, zero hardcoding |
| `/api/inventory` endpoint | 🟢 **DUAL-MOUNTED** | Backend exposes both `/inventory` and `/api/inventory` via `@app.get` decoration |
| Dashboard data flow | 🟢 **VERIFIED** | `fetchInventory()` → GET `/inventory` → `InventoryOut[]` schema → Recharts render |
| Decision Center | 🟢 **VERIFIED** | GET `/decision` with POST `/decision` fallback — priority flags rendered |
| CORS middleware | 🟢 **OPEN** | `allow_origins=["*"]` for dev — restrict to domain in production (see §5) |

### Backend Endpoint Map

```
GET  /health              → DB connectivity ping
GET  /inventory           → All products + stock levels  ← Dashboard KPIs + Charts
GET  /api/inventory       → Alias (same handler)
GET  /predict             → Latest ML predictions
GET  /decision            → Stored decision log entries  ← Decision Center (GET)
POST /decision            → Generate new decisions from predictions ← Decision Center (POST)
GET  /forecast?sku=&horizon= → Time-series forecast data
POST /ingest              → Trigger data ingestion pipeline
```

---

## 2. Environment Variables Reference

### Backend (FastAPI) — `.env`

```bash
# ── Supabase / PostgreSQL ──────────────────────────────────────────
DATABASE_URL=postgresql://user:password@host:5432/dbname
# Full Supabase connection string (Session Pooler, port 5432):
# postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres

# ── Optional Supabase Keys ─────────────────────────────────────────
SUPABASE_URL=https://[project-ref].supabase.co
SUPABASE_KEY=your-anon-or-service-role-key

# ── FastAPI Settings ───────────────────────────────────────────────
ENVIRONMENT=production
PORT=8000
```

### Frontend (React/Vite) — `.env` or Vercel Environment Variables

```bash
# ── Backend API URL ────────────────────────────────────────────────
# Point to your live Render/Railway backend URL in production:
VITE_API_URL=https://opsmind-ai-backend.onrender.com

# In development (default fallback in api.js if not set):
# VITE_API_URL=http://localhost:8000
```

> **⚠️ Important:** All Vite environment variables MUST be prefixed with `VITE_` to be
> exposed to client-side code via `import.meta.env`.

---

## 3. Backend Deployment — Render / Railway

### 3a. Render Deployment

#### Step 1 — Create a New Web Service

1. Go to [https://dashboard.render.com](https://dashboard.render.com) → **New → Web Service**
2. Connect your GitHub repository: `Ragavimurugesh/opsmindai`
3. Set the **Root Directory** to: `backend`

#### Step 2 — Configure Build & Start Commands

| Setting | Value |
|---------|-------|
| **Runtime** | `Python 3.11` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Health Check Path** | `/health` |
| **Auto-Deploy** | ✅ Enabled (on push to `main`) |

#### Step 3 — Set Environment Variables on Render

Navigate to your service → **Environment** tab → Add:

```
DATABASE_URL   = postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres
SUPABASE_URL   = https://[project-ref].supabase.co
SUPABASE_KEY   = your-service-role-key
ENVIRONMENT    = production
```

> **💡 Supabase Connection Pooler:** Use the **Session Pooler** (port 5432) URL from
> Supabase → Project Settings → Database → Connection string. The Transaction Pooler
> (port 6543) may cause issues with SQLAlchemy's session management.

#### Step 4 — `render.yaml` (Auto-configuration)

The repository already contains `backend/render.yaml`. Render will detect this and
pre-populate service settings automatically during the first deploy.

```yaml
# backend/render.yaml (reference)
services:
  - type: web
    name: opsmind-ai-backend
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: DATABASE_URL
        sync: false          # Set manually in Render dashboard
      - key: ENVIRONMENT
        value: production
```

#### Step 5 — Python Environment Notes

```
Python Version : 3.11+ recommended
Key packages   : fastapi, uvicorn[standard], sqlalchemy, psycopg2-binary,
                 pandas, scikit-learn, prophet, xgboost, python-dotenv
requirements   : backend/requirements.txt (auto-installed on build)
```

### 3b. Railway Deployment (Alternative)

1. Railway → **New Project → Deploy from GitHub Repo**
2. Set **Root Directory**: `backend`
3. Railway auto-detects Python; configure via `railway.json` or Dashboard:
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables in Railway's **Variables** panel (same as §3 Step 3)

---

## 4. Frontend Deployment — Vercel / Netlify

### 4a. Vercel Deployment (Recommended)

#### Step 1 — Import Project

1. Go to [https://vercel.com/new](https://vercel.com/new) → **Import Git Repository**
2. Select `Ragavimurugesh/opsmindai`
3. Set **Root Directory** to: `frontend`

#### Step 2 — Configure Build Settings

| Setting | Value |
|---------|-------|
| **Framework Preset** | `Vite` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |
| **Install Command** | `npm install` |
| **Node.js Version** | `20.x` (LTS) |

#### Step 3 — Set Environment Variables on Vercel

Navigate to your project → **Settings → Environment Variables** → Add:

```
VITE_API_URL = https://opsmind-ai-backend.onrender.com
```

> **🔑 Critical:** This single variable switches the Axios base URL from `localhost:8000`
> to your live backend. No code changes required — `api.js` already reads:
> ```js
> baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000'
> ```

#### Step 4 — SPA Routing (Vite + React Router)

Create `frontend/public/vercel.json` to handle client-side routing:

```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

Or add `vercel.json` at the frontend root level (Vercel auto-detects).

#### Step 5 — Update CORS in Production

Once the live Vercel URL is known (e.g., `https://opsmind-ai.vercel.app`), update
`backend/main.py` CORS to restrict origins:

```python
# Production CORS — replace wildcard with your actual Vercel domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://opsmind-ai.vercel.app",
        "https://opsmindai.vercel.app",
        # Add custom domain if configured
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4b. Netlify Deployment (Alternative)

1. Netlify → **Sites → Add new site → Import an existing project**
2. Set **Base directory**: `frontend`, **Build command**: `npm run build`, **Publish directory**: `dist`
3. Add environment variable `VITE_API_URL` under **Site settings → Environment variables**
4. Create `frontend/public/_redirects` for SPA routing:
   ```
   /*  /index.html  200
   ```

---

## 5. CORS & Network Configuration

### Development (Current)
```python
allow_origins=["*"]   # Open — safe for local dev only
```

### Production (Required Change)
```python
allow_origins=[
    "https://your-app.vercel.app",
    "https://yourcustomdomain.com",
]
```

### API URL Switch Summary

| Environment | `VITE_API_URL` value | Where set |
|-------------|---------------------|-----------|
| Local dev | *(not set — fallback to `localhost:8000`)* | `.env` file (gitignored) |
| Vercel Preview | `https://opsmind-ai-backend.onrender.com` | Vercel env vars |
| Vercel Production | `https://opsmind-ai-backend.onrender.com` | Vercel env vars |

---

## 6. Post-Deployment Verification Checklist

Run these checks after deploying both services:

### Backend Health
- [ ] `GET https://opsmind-ai-backend.onrender.com/health` → `{"status":"ok","database":"connected"}`
- [ ] `GET https://opsmind-ai-backend.onrender.com/inventory` → Returns array of products
- [ ] `GET https://opsmind-ai-backend.onrender.com/decision` → Returns decision log
- [ ] `POST https://opsmind-ai-backend.onrender.com/ingest` → Returns ingestion status
- [ ] Supabase dashboard → Confirm rows present in `products` and `inventory` tables

### Frontend Health
- [ ] Vercel deployment URL loads the React dashboard
- [ ] KPI cards show real data (not `—` skeleton state)
- [ ] AreaChart "Demand Forecasting Trend" renders with data
- [ ] BarChart "Stock vs Sales Comparison" renders correctly
- [ ] Decision Center shows entries with 🔴/🟡/🟢 priority flags
- [ ] Layout sidebar navigation works for all 6 routes
- [ ] Browser DevTools Network tab: `/inventory` returns `200 OK` (not `404` or CORS error)

### Integration End-to-End
- [ ] No CORS errors in browser console
- [ ] Supabase connection indicator in header shows **Connected** (green)
- [ ] "Run Ingestion" button triggers pipeline without 500 errors
- [ ] Dashboard auto-refreshes data correctly

---

## 7. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRODUCTION STACK                          │
└─────────────────────────────────────────────────────────────────┘

  Browser (User)
       │
       ▼
  ┌──────────────────────┐
  │   Vercel CDN          │  React 19 + Vite 8 + Tailwind CSS v4
  │   opsmind-ai.vercel   │  Recharts + Lucide + React Router v7
  │   .app                │
  └──────────┬───────────┘
             │  HTTPS API calls (Axios)
             │  VITE_API_URL → Render backend
             ▼
  ┌──────────────────────┐
  │   Render Web Service  │  FastAPI + Uvicorn
  │   opsmind-ai-backend  │  SQLAlchemy ORM
  │   .onrender.com       │  Prophet + XGBoost ML
  └──────────┬───────────┘
             │  PostgreSQL connection (DATABASE_URL)
             │  psycopg2-binary driver
             ▼
  ┌──────────────────────┐
  │   Supabase            │  PostgreSQL 15
  │   (Managed DB)        │  Tables: products, inventory,
  │                       │          predictions, decision_log,
  │                       │          forecasts, sales_history
  └──────────────────────┘

  ┌──────────────────────┐
  │   GitHub              │  Source of truth
  │   Ragavimurugesh/     │  CI/CD: Auto-deploy on push to main
  │   opsmindai           │  Render + Vercel watch this repo
  └──────────────────────┘
```

---

## Quick Reference Commands

```bash
# ── Local Development ──────────────────────────────────────────────
# Backend
cd backend && uvicorn main:app --reload --port 8000

# Frontend
cd frontend && npm run dev          # → http://localhost:5173

# ── Production Build Test ──────────────────────────────────────────
cd frontend && npm run build        # Outputs to frontend/dist/
cd frontend && npm run preview      # Preview production build locally

# ── Database Seed ─────────────────────────────────────────────────
cd backend && python seed_data.py

# ── Git Workflow ───────────────────────────────────────────────────
git add .
git commit -m "your message"
git push origin main                # Triggers auto-deploy on Render + Vercel
```

---

*Generated: Phase 7–8 · OpsMind AI v1.0.0 · Repository: `Ragavimurugesh/opsmindai`*
