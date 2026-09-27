# Phase 6: Public Deployment & Submission Guide

## Objectives
1. Expose the running FastAPI bot service (`bot:app`) to a secure, public HTTPS endpoint.
2. Verify that the public endpoint responds correctly to the 5 challenge API routes.
3. Submit the public URL on the official challenge portal at [magicpin.com/vera/ai-challenge](https://magicpin.com/vera/ai-challenge).

---

## Deployment Options

### Option A: Local Tunnel via `ngrok` (Fastest for testing)
If running locally:
```bash
# 1. Start the bot server
uvicorn bot:app --host 0.0.0.0 --port 8000

# 2. Expose via ngrok
ngrok http 8000
```
This generates a public URL like:
`https://abcd-123-456.ngrok-free.app`

### Option B: Cloud Hosting (Render / Railway / Fly.io / GCP Cloud Run)
1. Push this repository to GitHub (`https://github.com/ggarvitbansal/Vera-ai`).
2. Deploy a new Web Service pointing to this repository.
3. Build command:
   ```bash
   pip install -r requirements.txt
   ```
4. Start command:
   ```bash
   uvicorn bot:app --host 0.0.0.0 --port $PORT
   ```

---

## Verified Live Deployment

- **Live URL**: `https://vera-ai-13c6.onrender.com`
- **Hosted on**: Render (Web Service)
- **Status**: Verified active and responding
- **Latency**: ~420ms `/healthz`, ~520ms `/tick`

### Verified Against Official Judge Simulator:
- `[PASS]` Warmup & Metadata probe
- `[PASS]` Category & Merchant context ingestion
- `[PASS]` Auto-reply loop breaking
- `[PASS]` Intent transition to action execution
- `[PASS]` Hostility & opt-out handling
- `[PASS]` Proactive trigger tick actions with 10/10 Specificity

---

## Final Submission Checklist
- [x] Code committed and pushed to GitHub: [https://github.com/ggarvitbansal/Vera-ai](https://github.com/ggarvitbansal/Vera-ai)
- [x] Static benchmark results generated in `submission.jsonl`
- [x] Public web service deployed on Render: `https://vera-ai-13c6.onrender.com`
- [x] Verified live deployment against `judge_simulator.py`
- [ ] Submit public base URL (`https://vera-ai-13c6.onrender.com`) on the magicpin challenge entry form

