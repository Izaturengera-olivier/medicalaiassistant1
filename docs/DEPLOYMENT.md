# Clinical Decision Support (CDS) — Production Deployment Guide

This guide provides end-to-end instructions for deploying the **Clinical Decision Support (CDS)** system to cloud Platform-as-a-Service (PaaS) providers such as **Render** or **Railway**.

---

## 1. Quick Turnkey Deployment with Render (Recommended)

The repository includes a ready-to-use [`render.yaml`](../render.yaml) blueprint that provisions the entire production stack with one click:
- **PostgreSQL 16** managed database
- **Backend API**: Django + Gunicorn + Tesseract OCR in a container
- **Frontend SPA**: Vite + React Static Site with automatic client-side routing

### Step-by-Step Instructions:

1. **Push your code to GitHub or GitLab**:
   ```bash
   git add .
   git commit -m "Configure production deployment for PaaS"
   git push origin main
   ```

2. **Connect to Render**:
   - Log in to your [Render Dashboard](https://dashboard.render.com).
   - Click **New +** in the top right corner and select **Blueprint**.
   - Connect your `clinical-cds` repository.

3. **Configure Environment Secrets**:
   Render automatically links the database connection string and cross-service URLs. You will only be prompted to supply your secret API keys:
   - `AI_API_KEY`: Your DeepSeek, OpenAI, or Gemini API key.
   - `WEB_SEARCH_API_KEY`: *(Optional)* Your Tavily search API key for live medical guidelines.

4. **Click "Apply"**:
   Render will build the Docker container for the backend, run database migrations, compile the React frontend, and deploy both with automatic HTTPS SSL certificates!

5. **Create your Admin Superuser**:
   - In the Render Dashboard, go to your **`clinical-cds-backend`** service.
   - Click the **Shell** tab on the left.
   - Run:
     ```bash
     python manage.py createsuperuser
     ```
   - Follow the prompts to create your system administrator account.

---

## 2. Alternative Deployment with Railway

Railway also provides first-class support for Dockerized Django and React:

1. **Create a New Project on Railway**:
   - Log in to [Railway.app](https://railway.app).
   - Click **New Project** -> **Deploy from GitHub repo**.
   - Select your `clinical-cds` repository.

2. **Add PostgreSQL Database**:
   - In the project canvas, click **+ New** -> **Database** -> **Add PostgreSQL**.
   - Railway will provide a `DATABASE_URL` environment variable.

3. **Configure Backend Service**:
   - Click on the repository service card -> **Settings**.
   - Set **Build Method** to `Dockerfile` pointing to `backend/Dockerfile`.
   - In **Variables**, add:
     - `DJANGO_SETTINGS_MODULE=config.settings.production`
     - `DJANGO_SECRET_KEY=generate-a-strong-random-key`
     - `DJANGO_DEBUG=false`
     - `DATABASE_URL=${{Postgres.DATABASE_URL}}`
     - `AI_PROVIDER=deepseek` (or `openai`)
     - `AI_API_KEY=your-api-key`
     - `AI_MODEL=deepseek-chat`
     - `CORS_ALLOWED_ORIGINS=https://your-frontend-domain.up.railway.app`
   - In **Networking**, click **Generate Domain** to get your backend public URL.

4. **Configure Frontend Service**:
   - Click **+ New** -> **GitHub Repo** -> select `clinical-cds`.
   - Set **Root Directory** to `/frontend`.
   - Set **Build Command** to `npm install && npm run build`.
   - Set **Install Command** to `npm install`.
   - Set Environment Variable:
     - `VITE_API_URL=https://your-backend-domain.up.railway.app/api`
   - Generate a public domain for the frontend.

---

## 3. Environment Variables Reference

| Variable | Description | Example / Default |
| :--- | :--- | :--- |
| `DJANGO_SETTINGS_MODULE` | Active Django settings file | `config.settings.production` |
| `DJANGO_SECRET_KEY` | Cryptographic secret key | *Random 50+ char string* |
| `DJANGO_DEBUG` | Debug mode (MUST be false in prod) | `false` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames | `.onrender.com,.up.railway.app` |
| `DATABASE_URL` | PostgreSQL connection string | `postgres://user:pass@host:5432/cds?sslmode=require` |
| `CORS_ALLOWED_ORIGINS` | Allowed frontend domains for API calls | `https://your-frontend.onrender.com` |
| `CSRF_TRUSTED_ORIGINS` | Trusted origins for CSRF protection | `https://your-frontend.onrender.com` |
| `AI_PROVIDER` | AI provider for clinical CDS reasoning | `deepseek`, `openai`, `gemini`, `groq` |
| `AI_API_KEY` | Secret API key for AI provider | `sk-...` |
| `AI_MODEL` | Model identifier | `deepseek-chat`, `gpt-4o-mini`, etc. |
| `WEB_SEARCH_PROVIDER` | Search provider for RAG grounding | `tavily` |
| `WEB_SEARCH_API_KEY` | API key for medical web search | `tvly-...` |
| `JWT_ACCESS_MINUTES` | Lifetime of user auth token | `60` |
| `JWT_REFRESH_DAYS` | Lifetime of refresh token | `7` |

---

## 4. Post-Deployment Verification Checklist

- [ ] **Health Check**: Visit `https://<your-backend-domain>/api/health/`. It should return `{"status": "ok", "service": "clinical-cds"}` with HTTP 200.
- [ ] **Admin Login**: Visit `https://<your-backend-domain>/admin/` and log in with your superuser.
- [ ] **Frontend Load**: Visit your frontend URL, confirm pages load and client-side routing works without 404s on page refresh.
- [ ] **AI Assistant Test**: Log into the web interface as a patient or doctor and send a test message (e.g. *"I have a fever and cough"*). Verify that the AI returns detailed pedagogical explanations with cited medical guidelines.
- [ ] **Document Analysis Test**: Upload a sample PDF or scanned report to verify Tesseract OCR and report parsing in the cloud environment.
