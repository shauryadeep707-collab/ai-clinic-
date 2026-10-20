# Deploying AI Health Clinic to Render

This guide outlines how to deploy **AI Health Clinic** to [Render](https://render.com) in less than 2 minutes.

---

## Method 1: Automatic Blueprint Deployment (Recommended)

1. Log in to your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** in the top navigation bar and select **Blueprint**.
3. Connect your GitHub account and select your repository:
   - **Repository:** `shauryadeep707-collab/ai-clinic-`
4. Render will automatically detect [`render.yaml`](../render.yaml) at the root of the repository.
5. Review the configuration:
   - **Service Name:** `ai-health-clinic`
   - **Environment:** `python`
   - **Region:** Oregon (or closest to your users)
   - **Plan:** Free
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
6. Click **Apply**.
7. Render will build and deploy your application. Once finished, you will receive a public HTTPS URL (e.g. `https://ai-health-clinic.onrender.com`).

---

## Method 2: Manual Web Service Setup

If you prefer to configure manually without a Blueprint:

1. On [dashboard.render.com](https://dashboard.render.com/), click **New +** > **Web Service**.
2. Select **Build and deploy from a Git repository** > **Next**.
3. Choose `shauryadeep707-collab/ai-clinic-` (or paste `https://github.com/shauryadeep707-collab/ai-clinic-`).
4. Fill in the settings:
   - **Name:** `ai-health-clinic`
   - **Region:** Any (e.g. Oregon or Frankfurt)
   - **Branch:** `main`
   - **Root Directory:** *(leave blank)*
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan Type:** `Free`
5. In **Advanced** > **Environment Variables**, add:
   - `PYTHON_VERSION`: `3.12.0`
   - `APP_NAME`: `AI Health Clinic`
   - `DB_ENGINE`: `sqlite`
   - `PYTHONPATH`: `.`
   - `SECRET_KEY`: *(any random string for JWT encryption)*
6. Click **Create Web Service**.

---

## Live Endpoints on Render
Once deployed:
- **Web Application:** `https://<your-subdomain>.onrender.com/`
- **Health Check:** `https://<your-subdomain>.onrender.com/health`
- **Interactive Swagger Docs:** `https://<your-subdomain>.onrender.com/docs`
