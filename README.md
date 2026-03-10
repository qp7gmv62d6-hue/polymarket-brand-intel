# 🔮 Polymarket Brand Intelligence

A Streamlit app that mines Polymarket prediction markets for brand discovery insights — crowd-priced signals on risk, leadership, competition, product, and regulation.

## What it does

Enter any brand name → get:
- Total markets tracked + volume wagered
- 24hr betting velocity  
- Volume-weighted risk score
- YES probability on all open markets
- Probability history charts (how crowd sentiment shifted over time)
- CSV export

## Stack

- **Frontend/backend:** Streamlit (Python)
- **Data:** Polymarket Gamma API + CLOB API (no API key needed)
- **Charts:** Plotly

## Local setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Cloud (free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app**
4. Connect your GitHub repo
5. Set **Main file path** to `app.py`
6. Click **Deploy**

Done — you'll get a public URL like `https://yourname-polymarket-brand-intel.streamlit.app`

## How it fetches data

Uses a two-pronged approach per Polymarket's [agent-skills](https://github.com/Polymarket/agent-skills) documentation:

1. **Tag-based search** — finds Polymarket tag IDs matching the brand, fetches all markets under those tags
2. **Events sweep** — hits `/events?q=` to catch markets not tagged but mentioned in event titles

All data is cached for 5 minutes to avoid hammering the API.

## File structure

```
app.py              ← entire app (single file)
requirements.txt    ← dependencies
README.md           ← this file
```
