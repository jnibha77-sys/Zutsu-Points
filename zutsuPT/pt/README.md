# Points Table — Live Scoreboard

A Flask-based scoreboard server that fetches team data from Google Sheets and renders a live-updating scoreboard image.

---

## Deploy to Vercel

### Prerequisites

- A [Vercel](https://vercel.com) account (free tier works)
- Your code pushed to a **GitHub** repository

### Step-by-step

1. **Push your repo to GitHub** (if not already done)
   ```bash
   git add .
   git commit -m "ready for vercel"
   git push origin main
   ```

2. **Go to [vercel.com/new](https://vercel.com/new)** and click **"Import Project"**

3. **Select your GitHub repo** — Vercel will detect the `vercel.json` config automatically

4. **Click Deploy** — no environment variables or build settings needed, everything is configured via `vercel.json`

5. **Done!** Your scoreboard will be live at the URL Vercel gives you (e.g. `https://your-project.vercel.app`)

### How it works on Vercel

| Feature | Local (`python main_web.py`) | Vercel (serverless) |
|---|---|---|
| Image generation | Background thread, every 5s | On-demand per request |
| File storage | Saves `output_stream.png` to disk | Generates in-memory, no disk writes |
| Server | Flask dev server on port 5000 | Vercel's serverless Python runtime |

> **Note:** On Vercel, each request to `/scoreboard.png` generates a fresh image from Google Sheets. The free tier allows plenty of requests for a live scoreboard.

### Useful routes

| Route | Description |
|---|---|
| `/` | Live scoreboard page (auto-refreshes every 2s) |
| `/scoreboard.png` | Raw scoreboard image |
| `/debug` | JSON diagnostic info for troubleshooting |

---

## Run Locally

```bash
pip install -r requirements.txt
python main_web.py
```

Open `http://localhost:5000/` in your browser.
