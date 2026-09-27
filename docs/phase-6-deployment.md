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

## Verification Before Submitting
Once your public URL is live, run the judge simulator against it:
```bash
export BOT_URL=https://your-public-bot-url.com
python judge_simulator.py
```

Ensure:
- [x] `/v1/healthz` returns status `200` and loaded contexts count.
- [x] `/v1/metadata` returns team name and model information.
- [x] `/v1/context` responds with `accepted: true` on version push, and handles versioning idempotently.
- [x] `/v1/tick` returns proactive messages within the 30-second budget.
- [x] `/v1/reply` responds with `send`, `wait`, or `end` within 30 seconds.

---

## Final Submission Checklist
- [x] Code committed and pushed to GitHub: [https://github.com/ggarvitbansal/Vera-ai](https://github.com/ggarvitbansal/Vera-ai)
- [x] Static benchmark results generated in `submission.jsonl`
- [x] Server running and tested against `judge_simulator.py`
- [ ] Submit public base URL on the magicpin challenge entry form
