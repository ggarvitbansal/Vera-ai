# Deploying Vera Assistant on Render

This guide outlines the step-by-step process to deploy your Vera assistant on [Render](https://render.com) for public evaluation.

---

## 1. Quick Deploy via Render Dashboard

1. Log in to your [Render Dashboard](https://dashboard.render.com).
2. Click **New +** in the top right corner and select **Web Service**.
3. Under **Connect a repository**, choose **GitHub** and connect `ggarvitbansal/Vera-ai`.
4. Configure the service settings:
   - **Name**: `vera-ai` (or any name you like)
   - **Region**: Singapore or Frankfurt (closer to India has lower latency)
   - **Branch**: `main`
   - **Root Directory**: *(leave blank)*
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn bot:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free (or Starter if you want 0% spin-down latency)
5. Under **Advanced**:
   - **Health Check Path**: `/v1/healthz`
6. Click **Create Web Service**.

Render will automatically fetch the repository, install dependencies from `requirements.txt`, and deploy the FastAPI service.

---

## 2. Your Live Public URL

Once Render displays **Live**, your public URL will look like:
```
https://vera-ai-xxxx.onrender.com
```

### Verification Commands
Test your live URL directly from your terminal:
```bash
# 1. Health check
curl -sS https://<your-render-url>/v1/healthz

# 2. Metadata check
curl -sS https://<your-render-url>/v1/metadata
```

Run the local judge simulator against your Render deployment:
```bash
python -c "from judge_simulator import JudgeSimulator, OpenAIProvider; import os; os.environ['BOT_URL'] = 'https://<your-render-url>'; judge = JudgeSimulator(OpenAIProvider('fake-key')); judge.run('warmup')"
```

---

## 3. Important Tips for Evaluation Window

> [!TIP]
> **Free Tier Sleep Prevention**: Render Free tier services spin down after 15 minutes of inactivity. The magicpin challenge judge allows up to a **30-second timeout** per call, but cold starts can occasionally take longer.
> - **Before submitting**: Ping `https://<your-render-url>/v1/healthz` once to ensure the instance is awake and warm!
> - Alternatively, keep a free pinging service (like UptimeRobot) pinging `/v1/healthz` every 10 minutes during the evaluation window.

---

## 4. Final Portal Submission

Once your Render URL is verified:
1. Open the [magicpin AI Challenge Portal](https://magicpin.com/vera/ai-challenge).
2. Enter your live base URL (e.g. `https://vera-ai-xxxx.onrender.com`).
3. Submit your entry!
