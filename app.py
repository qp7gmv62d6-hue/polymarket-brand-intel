import streamlit as st
import requests
import json
import re
import csv
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# ── Page config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Polymarket Brand Intelligence",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Syne:wght@400;600;700;800&display=swap');

/* Root */
:root {
    --bg:       #080c14;
    --surface:  #0e1520;
    --border:   #1c2333;
    --text:     #cdd6f4;
    --muted:    #6e7d9f;
    --accent:   #7c3aed;
    --cyan:     #06b6d4;
    --green:    #22c55e;
    --red:      #ef4444;
    --amber:    #f59e0b;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    font-family: 'JetBrains Mono', monospace;
    color: var(--text);
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { background: var(--surface) !important; }

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* Hero */
.hero {
    text-align: center;
    padding: 3rem 0 2rem;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #7c3aed, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    letter-spacing: -0.02em;
}
.hero p {
    color: var(--muted);
    font-size: 0.875rem;
    margin-top: 0.5rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* Metric cards */
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
}
.metric-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    margin-bottom: 0.4rem;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--text);
    line-height: 1;
}
.metric-sub {
    font-size: 0.72rem;
    color: var(--muted);
    margin-top: 0.3rem;
}

/* Tags */
.tag {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-right: 0.3rem;
}
.tag-open   { background: rgba(34,197,94,0.15);  color: #22c55e; border: 1px solid rgba(34,197,94,0.3); }
.tag-closed { background: rgba(110,125,159,0.15); color: #6e7d9f; border: 1px solid rgba(110,125,159,0.3); }
.tag-risk   { background: rgba(239,68,68,0.15);  color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }

/* Section headers */
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--muted);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.5rem;
    margin: 1.5rem 0 1rem;
}

/* Risk meter */
.risk-bar-container {
    background: var(--border);
    border-radius: 4px;
    height: 8px;
    margin: 0.5rem 0;
    overflow: hidden;
}
.risk-bar {
    height: 100%;
    border-radius: 4px;
    transition: width 0.8s ease;
}

/* Market row */
.market-row {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.market-q {
    font-size: 0.82rem;
    color: var(--text);
    flex: 1;
    margin-right: 1rem;
}
.market-meta {
    font-size: 0.72rem;
    color: var(--muted);
    white-space: nowrap;
}

/* Input styling override */
.stTextInput input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.95rem !important;
    padding: 0.75rem 1rem !important;
}
.stTextInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent) !important;
}
.stButton button {
    background: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 0.6rem 1.5rem !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    width: 100%;
}
.stButton button:hover {
    background: #6d28d9 !important;
}

/* Divider */
hr { border-color: var(--border) !important; }

/* Plotly charts background */
.js-plotly-plot .plotly { background: transparent !important; }

/* Alert / info boxes */
.stAlert { background: var(--surface) !important; border-color: var(--border) !important; }

/* Dataframe */
.stDataFrame { border: 1px solid var(--border) !important; border-radius: 6px !important; }
</style>
""", unsafe_allow_html=True)

# ── API helpers ───────────────────────────────────────────────────
GAMMA = "https://gamma-api.polymarket.com"
CLOB  = "https://clob.polymarket.com"
REQUEST_TIMEOUT = 8
MAX_TAGS = 5
MAX_MARKET_PAGES = 3
MAX_EVENT_PAGES = 2
TAXONOMY_FILE = "Content Taxonomy 3.1 (1).tsv"
BRAND_METADATA_FILE = "brand_metadata.csv"
TAXONOMY_ALIAS_RULES = {
    "Artificial Intelligence": [
        "ai", "artificial intelligence", "llm", "gpt", "chatgpt", "openai",
        "anthropic", "claude", "gemini", "sora", "model", "inference",
    ],
    "Computer Software and Applications": [
        "software", "app", "application", "saas", "platform", "tool",
        "assistant", "api",
    ],
    "Cloud Computing": ["cloud", "azure", "aws", "gcp", "compute"],
    "Social Networking": ["social network", "social media", "x", "twitter"],
    "Programming Languages": ["python", "javascript", "typescript", "coding"],
    "Consumer Electronics": ["device", "hardware", "wearable", "smartphone"],
    "Business I.T.": ["enterprise software", "it spending", "it budget"],
    "Executive Leadership & Management": [
        "ceo", "founder", "board", "chairman", "executive", "leadership",
        "sam altman", "resign", "fired", "step down",
    ],
    "Venture Capital": ["venture capital", "funding", "raise", "series a", "series b"],
    "Private Equity": ["private equity", "buyout"],
    "Mergers and Acquisitions": ["m&a", "merger", "acquisition", "acquire"],
    "Stocks and Bonds": ["stock", "shares", "equity", "market cap", "valuation", "ipo"],
    "Financial Regulation": ["regulation", "regulatory", "sec", "ftc", "doj", "eu"],
    "Legal Services Industry": ["lawsuit", "legal", "court", "sue", "antitrust"],
    "Political Issues & Policy": ["policy", "bill", "law", "ban", "tariff"],
    "Elections": ["election", "vote", "ballot", "primary"],
    "Cryptocurrency": ["crypto", "bitcoin", "ethereum", "solana", "dogecoin", "xrp"],
    "Movies": ["movie", "film", "box office"],
    "Television": ["tv", "television", "series", "season finale"],
    "Music": ["album", "song", "tour", "single"],
    "eSports": ["esports", "esport"],
    "Sports": ["game", "match", "season", "tournament", "championship"],
}
RISK_DETAILS = {
    "Executive Leadership & Management",
    "Financial Regulation",
    "Legal Services Industry",
    "Political Issues & Policy",
    "Elections",
    "Mergers and Acquisitions",
    "Stocks and Bonds",
    "Venture Capital",
    "Private Equity",
}
DOWNSIDE_TERMS = [
    "not ", "won't", "willnt", "lose", "less than", "under", "below", "delay",
    "miss", "ban", "fine", "sue", "lawsuit", "investigation", "fired",
    "resign", "step down", "fail", "drop", "fall", "down", "denied",
]
BRAND_ALIASES = {
    "chatgpt": ["chatgpt", "openai", "gpt-4", "gpt 4", "gpt-5", "gpt 5", "sam altman", "sora"],
    "openai": ["openai", "chatgpt", "gpt-4", "gpt 4", "gpt-5", "gpt 5", "sam altman", "sora"],
    "google": ["google", "gemini", "alphabet"],
    "x": ["x", "twitter", "elon"],
    "twitter": ["twitter", "x", "elon"],
    "facebook": ["facebook", "meta", "instagram", "zuckerberg"],
    "meta": ["meta", "facebook", "instagram", "zuckerberg"],
}


def normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()


def has_term(text: str, term: str) -> bool:
    normalized_term = normalize_text(term)
    if not normalized_term:
        return False
    return normalized_term in text


def normalize_path(parts: list[str]) -> list[str]:
    return [part.strip() for part in parts if part and part.strip()]


def build_aliases(name: str, path_parts: list[str]) -> set[str]:
    aliases = {normalize_text(name)}
    for part in path_parts:
        aliases.add(normalize_text(part))
        if "&" in part:
            aliases.update(normalize_text(piece) for piece in part.split("&"))

    for part in path_parts + [name]:
        for alias in TAXONOMY_ALIAS_RULES.get(part, []):
            aliases.add(normalize_text(alias))

    return {alias for alias in aliases if alias}


def parse_csv_list(value: str) -> list[str]:
    return [item.strip() for item in (value or "").split("|") if item and item.strip()]


def parse_facet_values(value: str) -> list[str]:
    return [item.strip() for item in (value or "").split(",") if item and item.strip()]


def extract_facet_options(series: pd.Series) -> list[str]:
    options = set()
    for value in series.fillna(""):
        options.update(parse_facet_values(value))
    return sorted(options)


def row_has_any_facet_value(value: str, selected: list[str]) -> bool:
    if not selected:
        return True
    row_values = set(parse_facet_values(value))
    return any(item in row_values for item in selected)


@st.cache_data(show_spinner=False)
def load_taxonomy() -> list[dict]:
    path = Path(TAXONOMY_FILE)
    if not path.exists():
        return []

    with path.open() as handle:
        rows = list(csv.reader(handle, delimiter="\t"))

    taxonomy = []
    for row in rows[2:]:
        if len(row) < 7:
            continue
        name = row[2].strip()
        if not name:
            continue
        path_parts = normalize_path(row[3:7])
        if not path_parts:
            continue
        taxonomy.append({
            "name": name,
            "path": path_parts,
            "aliases": sorted(build_aliases(name, path_parts)),
            "depth": len(path_parts),
        })
    return taxonomy


@st.cache_data(show_spinner=False)
def load_brand_metadata() -> list[dict]:
    path = Path(BRAND_METADATA_FILE)
    if not path.exists():
        return []

    entries = []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            term = (row.get("term") or "").strip()
            if not term:
                continue
            aliases = {normalize_text(term)}
            aliases.update(normalize_text(alias) for alias in parse_csv_list(row.get("aliases", "")))
            entries.append({
                "term": term,
                "industry": (row.get("industry") or "").strip(),
                "product_type": (row.get("product_type") or "").strip(),
                "parent_brand": (row.get("parent_brand") or "").strip(),
                "aliases": sorted(alias for alias in aliases if alias),
            })
    return entries


def collect_market_facets(text: str) -> dict[str, list[str]]:
    facets = {
        "industry": set(),
        "product_type": set(),
        "parent_brand": set(),
        "entity": set(),
    }
    normalized = normalize_text(text)
    if not normalized:
        return {key: [] for key in facets}

    for entry in load_brand_metadata():
        if not any(alias in normalized for alias in entry["aliases"]):
            continue
        facets["entity"].add(entry["term"])
        if entry["industry"]:
            facets["industry"].add(entry["industry"])
        if entry["product_type"]:
            facets["product_type"].add(entry["product_type"])
        if entry["parent_brand"]:
            facets["parent_brand"].add(entry["parent_brand"])

    return {key: sorted(values) for key, values in facets.items()}


def build_search_terms(brand: str) -> list[str]:
    brand = " ".join(brand.split()).strip()
    if not brand:
        return []

    terms = [brand]
    parts = [part for part in brand.split() if len(part) >= 4]

    if len(parts) > 1:
        terms.extend(parts[:2])
        acronym = "".join(part[0] for part in parts if part[0].isalnum())
        if len(acronym) >= 3:
            terms.append(acronym.upper())

    seen = set()
    deduped = []
    for term in terms:
        key = term.lower()
        if key not in seen:
            deduped.append(term)
            seen.add(key)
    return deduped


def get_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": "polymarket-brand-intel/1.0"})
    return session


def build_match_terms(brand: str) -> list[str]:
    normalized_brand = normalize_text(brand)
    if not normalized_brand:
        return []

    terms = [normalized_brand]
    words = [word for word in normalized_brand.split() if len(word) >= 4]
    terms.extend(words)
    terms.extend(BRAND_ALIASES.get(normalized_brand, []))

    seen = set()
    deduped = []
    for term in terms:
        normalized_term = normalize_text(term)
        if normalized_term and normalized_term not in seen:
            deduped.append(normalized_term)
            seen.add(normalized_term)
    return deduped


def market_search_text(market: dict) -> str:
    chunks = [
        market.get("question", ""),
        market.get("description", ""),
        market.get("slug", ""),
    ]
    tags = market.get("tags") or []
    chunks.extend(tag.get("label", "") for tag in tags if isinstance(tag, dict))
    events = market.get("events") or []
    for event in events:
        if isinstance(event, dict):
            chunks.extend([
                event.get("title", ""),
                event.get("slug", ""),
                event.get("subtitle", ""),
            ])
    return normalize_text(" ".join(chunks))


def classify_market_taxonomy(question: str) -> tuple[str, str]:
    text = normalize_text(question)
    best_entry = None
    best_score = 0

    for entry in load_taxonomy():
        score = 0
        for alias in entry["aliases"]:
            if has_term(text, alias):
                score += 2 + min(len(alias.split()), 3)

        exact_name = normalize_text(entry["name"])
        if exact_name and has_term(text, exact_name):
            score += 4

        if score == 0:
            continue

        score += entry["depth"]
        if best_entry is None or score > best_score or (
            score == best_score and entry["depth"] > best_entry["depth"]
        ):
            best_entry = entry
            best_score = score

    if best_entry is None:
        return "Other", "Other"

    path = best_entry["path"]
    topic_group = path[1] if len(path) > 1 else path[0]
    topic_detail = path[-1]
    return topic_group, topic_detail


def is_downside_market(question: str, topic_detail: str) -> bool:
    text = normalize_text(question)
    if topic_detail not in RISK_DETAILS:
        return False

    if any(has_term(text, term) for term in DOWNSIDE_TERMS):
        return True

    finance_downside = [
        "less than", "under", "below", "down round", "not ipo", "delay ipo",
    ]
    leadership_downside = ["resign", "fired", "step down", "replace"]
    competition_downside = ["lose to", "surpass", "beat", "before"]

    if topic_detail in {"Stocks and Bonds", "Venture Capital", "Private Equity", "Mergers and Acquisitions"} and any(has_term(text, term) for term in finance_downside):
        return True
    if topic_detail == "Executive Leadership & Management" and any(has_term(text, term) for term in leadership_downside):
        return True
    if topic_detail in {"Political Issues & Policy", "Elections"} and any(has_term(text, term) for term in competition_downside):
        return True

    return False


def is_relevant_market(market: dict, brand: str) -> bool:
    text = market_search_text(market)
    if not text:
        return False

    brand_text = normalize_text(brand)
    match_terms = build_match_terms(brand)

    if brand_text and brand_text in text:
        return True

    brand_words = [word for word in brand_text.split() if len(word) >= 4]
    if len(brand_words) > 1 and all(word in text for word in brand_words):
        return True

    strong_aliases = [term for term in match_terms if " " in term or len(term) >= 5]
    if any(term in text for term in strong_aliases):
        return True

    return False

@st.cache_data(ttl=300, show_spinner=False)
def search_brand(brand: str) -> list:
    """Fetch all markets for a brand using tags + events sweep."""
    raw, seen = [], set()
    session = get_session()
    search_terms = build_search_terms(brand)

    def add(m):
        mid = m.get("id") or m.get("conditionId", "")
        if mid and mid not in seen:
            raw.append(m); seen.add(mid); return True
        return False

    if not search_terms:
        return raw

    # Tag lookup
    try:
        r = session.get(
            f"{GAMMA}/tags",
            params={"q": search_terms[0], "limit": MAX_TAGS},
            timeout=REQUEST_TIMEOUT,
        )
        for tag in r.json()[:MAX_TAGS]:
            tid = tag.get("id")
            if not tid:
                continue
            for page in range(MAX_MARKET_PAGES):
                offset = page * 100
                mr = session.get(f"{GAMMA}/markets", params={
                    "tag_id": tid, "limit": 100, "offset": offset,
                    "order": "volume", "ascending": "false",
                    "active": "true", "closed": "false"
                }, timeout=REQUEST_TIMEOUT)
                items = mr.json()
                for m in items:
                    if is_relevant_market(m, brand):
                        add(m)
                if len(items) < 100:
                    break
    except Exception:
        pass

    # Events sweep
    for term in search_terms:
        if len(term) < 3: continue
        try:
            for page in range(MAX_EVENT_PAGES):
                offset = page * 100
                er = session.get(
                    f"{GAMMA}/events",
                    params={
                        "q": term,
                        "limit": 100,
                        "offset": offset,
                        "active": "true",
                        "closed": "false",
                    },
                    timeout=REQUEST_TIMEOUT,
                )
                events = er.json()
                if not events:
                    break
                for ev in events:
                    markets = ev.get("markets") or []
                    if isinstance(markets, str):
                        try:
                            markets = json.loads(markets)
                        except Exception:
                            markets = []
                    for m in markets:
                        if is_relevant_market(m, brand):
                            add(m)
                if len(events) < 100:
                    break
        except Exception:
            pass

    return raw

def parse_token_ids(raw_token_ids) -> list[str]:
    if isinstance(raw_token_ids, list):
        return [str(token).strip() for token in raw_token_ids if str(token).strip()]
    if isinstance(raw_token_ids, str):
        try:
            parsed = json.loads(raw_token_ids)
            if isinstance(parsed, list):
                return [str(token).strip() for token in parsed if str(token).strip()]
        except Exception:
            cleaned = raw_token_ids.strip().strip("[]")
            if cleaned:
                return [token.strip().strip('"') for token in cleaned.split(",") if token.strip()]
    return []


@st.cache_data(ttl=60, show_spinner=False)
def get_price_history(token_ids: tuple[str, ...], interval: str = "1d") -> list:
    for token_id in token_ids:
        try:
            r = get_session().get(f"{CLOB}/prices-history", params={
                "tokenID": token_id, "interval": interval, "fidelity": 60
            }, timeout=REQUEST_TIMEOUT)
            payload = r.json()
            history = payload.get("history", []) if isinstance(payload, dict) else []
            if history:
                return history
        except Exception:
            continue
    return []

def parse_yes_prob(m):
    try:
        prices = json.loads(m.get("outcomePrices", "[]"))
        return round(float(prices[0]) * 100, 1) if prices else None
    except: return None

def build_df(markets: list) -> pd.DataFrame:
    rows = []
    for m in markets:
        question = m.get("question", "")
        searchable_text = market_search_text(m)
        topic_group, topic_detail = classify_market_taxonomy(searchable_text)
        facets = collect_market_facets(searchable_text)
        rows.append({
            "question":    question,
            "status":      "Closed" if m.get("closed") else "Open",
            "yes_prob":    parse_yes_prob(m),
            "volume":      float(m.get("volume") or m.get("volumeNum") or 0),
            "liquidity":   float(m.get("liquidity") or m.get("liquidityNum") or 0),
            "volume_24hr": float(m.get("volume24hr") or 0),
            "end_date":    (m.get("endDate") or "")[:10],
            "tags":        ", ".join(t.get("label","") for t in (m.get("tags") or [])),
            "token_id":    (m.get("clobTokenIds") or "[]"),
            "topic":       topic_group,
            "topic_detail": topic_detail,
            "industry":    ", ".join(facets["industry"]),
            "product_type": ", ".join(facets["product_type"]),
            "parent_brand": ", ".join(facets["parent_brand"]),
            "matched_entity": ", ".join(facets["entity"]),
            "search_text": searchable_text,
            "_raw":        m,
        })
    df = pd.DataFrame(rows)
    if df.empty: return df
    df = df.sort_values("volume", ascending=False).reset_index(drop=True)
    df.index += 1
    return df

def risk_score(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    open_df = df[df["status"] == "Open"].copy()
    open_df["is_risk"] = open_df.apply(
        lambda row: is_downside_market(row["question"], row["topic_detail"]), axis=1
    )
    risk_df = open_df[open_df["is_risk"] & open_df["yes_prob"].notna()]
    if risk_df.empty:
        return 0.0
    tvol = risk_df["volume"].sum()
    if tvol == 0:
        return risk_df["yes_prob"].mean()
    return (risk_df["yes_prob"] * risk_df["volume"]).sum() / tvol

# ── Plotting helpers ──────────────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(14,21,32,0.8)",
    font=dict(family="JetBrains Mono", color="#6e7d9f", size=11),
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis=dict(gridcolor="#1c2333", showline=False, zeroline=False),
    yaxis=dict(gridcolor="#1c2333", showline=False, zeroline=False),
)

def plot_volume_by_type(df: pd.DataFrame):
    df = df.copy()
    vol = df.groupby("topic")["volume"].sum().sort_values() / 1e6
    colors = {
        "Product": "#06b6d4",
        "Finance": "#22c55e",
        "Leadership": "#7c3aed",
        "Policy/Legal": "#ef4444",
        "Competition": "#f59e0b",
        "Partnerships": "#ec4899",
        "Adoption": "#14b8a6",
        "Other": "#4b5563",
    }
    fig = go.Figure(go.Bar(
        x=vol.values, y=vol.index, orientation="h",
        marker_color=[colors.get(t,"#4b5563") for t in vol.index],
        text=[f"${v:.1f}M" for v in vol.values],
        textposition="outside", textfont=dict(color="#cdd6f4", size=10),
    ))
    fig.update_layout(**PLOT_LAYOUT, title=dict(text="Volume by Topic", font=dict(color="#cdd6f4", size=12)))
    fig.update_xaxes(title_text="$ Volume (M USDC)")
    return fig

def plot_open_probs(df: pd.DataFrame):
    open_df = df[(df["status"]=="Open") & df["yes_prob"].notna()].head(12)
    if open_df.empty: return None
    colors = ["#22c55e" if p>=60 else "#ef4444" if p<=30 else "#f59e0b"
              for p in open_df["yes_prob"]]
    labels = [q[:52]+"…" if len(q)>52 else q for q in open_df["question"]]
    fig = go.Figure(go.Bar(
        x=open_df["yes_prob"].values, y=labels, orientation="h",
        marker_color=colors,
        text=[f"{p}%" for p in open_df["yes_prob"]],
        textposition="outside", textfont=dict(color="#cdd6f4", size=10),
    ))
    fig.add_vline(x=50, line_dash="dash", line_color="rgba(255,255,255,0.2)")
    fig.update_layout(**PLOT_LAYOUT,
        title=dict(text="Open Market YES Probabilities", font=dict(color="#cdd6f4", size=12)),
        height=max(300, len(open_df)*42))
    fig.update_xaxes(range=[0,115], title_text="YES Probability (%)")
    return fig

def plot_price_history(history: list, question: str):
    if not history: return None
    ts = [h["t"] for h in history]
    ps = [h["p"] * 100 for h in history]
    fig = go.Figure(go.Scatter(
        x=pd.to_datetime(ts, unit="s"), y=ps,
        mode="lines", line=dict(color="#7c3aed", width=2),
        fill="tozeroy", fillcolor="rgba(124,58,237,0.08)",
    ))
    fig.update_layout(**PLOT_LAYOUT,
        title=dict(text=f"Probability History", font=dict(color="#cdd6f4", size=12)),
        height=280)
    fig.update_yaxes(title_text="YES Prob (%)", range=[0,100])
    return fig

# ── UI ────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🔮 Brand Intelligence</h1>
  <p>Powered by Polymarket prediction markets · Real-money crowd signals</p>
</div>
""", unsafe_allow_html=True)

# ── Search bar ────────────────────────────────────────────────────
if "active_brand" not in st.session_state:
    st.session_state.active_brand = ""
if "active_results" not in st.session_state:
    st.session_state.active_results = []

with st.form("brand_search_form"):
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        brand = st.text_input(
            "",
            value=st.session_state.active_brand,
            placeholder="Enter a brand, product, or person — e.g. Nike, Tesla, Sam Altman",
            label_visibility="collapsed",
            key="brand_input",
        )
    with col_btn:
        search = st.form_submit_button("Search", use_container_width=True)

st.markdown("---")

# ── Run search ────────────────────────────────────────────────────
if search and brand:
    with st.spinner(f"Fetching Polymarket data for **{brand}**…"):
        raw = search_brand(brand)
    st.session_state.active_brand = brand
    st.session_state.active_results = raw

brand = st.session_state.active_brand
raw = st.session_state.active_results

if brand and raw:
    df = build_df(raw)
    open_df   = df[df["status"] == "Open"]
    closed_df = df[df["status"] == "Closed"]
    score     = risk_score(df)

    st.markdown(f'<div class="section-header">Overview — {brand}</div>', unsafe_allow_html=True)

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Total Markets</div>
            <div class="metric-value">{len(df)}</div>
            <div class="metric-sub">{len(open_df)} open · {len(closed_df)} closed</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        total_vol = df["volume"].sum()
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Total Volume</div>
            <div class="metric-value">${total_vol/1e6:.1f}M</div>
            <div class="metric-sub">USDC wagered</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        vel = open_df["volume_24hr"].sum() if not open_df.empty else 0
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">24hr Velocity</div>
            <div class="metric-value">${vel/1e3:.0f}K</div>
            <div class="metric-sub">active betting today</div>
        </div>""", unsafe_allow_html=True)
    with m4:
        avg_yes = open_df["yes_prob"].dropna().mean() if not open_df.empty else 0
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Avg YES Prob</div>
            <div class="metric-value">{avg_yes:.1f}%</div>
            <div class="metric-sub">open markets</div>
        </div>""", unsafe_allow_html=True)
    with m5:
        risk_color = "#ef4444" if score>=40 else "#f59e0b" if score>=20 else "#22c55e"
        risk_label = "Elevated" if score>=40 else "Moderate" if score>=20 else "Low"
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Risk Score</div>
            <div class="metric-value" style="color:{risk_color}">{score:.1f}</div>
            <div class="metric-sub">{risk_label} risk level</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">Refine Results</div>', unsafe_allow_html=True)

    industry_options = extract_facet_options(df["industry"])
    product_options = extract_facet_options(df["product_type"])
    parent_options = extract_facet_options(df["parent_brand"])
    topic_options = sorted(value for value in df["topic_detail"].dropna().unique() if value and value != "Other")

    rf1, rf2 = st.columns([3, 2])
    with rf1:
        refine_text = st.text_input(
            "Refine within results",
            placeholder="Filter these results by term, tag, product, or brand alias",
            key="refine_text",
        )
    with rf2:
        status_filter = st.selectbox("Status", ["All", "Open", "Closed"],
                                     label_visibility="collapsed", key="status_filter")

    rf3, rf4, rf5, rf6 = st.columns(4)
    with rf3:
        selected_topics = st.multiselect("Topic", topic_options, key="topic_filter")
    with rf4:
        selected_industries = st.multiselect("Industry", industry_options, key="industry_filter")
    with rf5:
        selected_product_types = st.multiselect("Product Type", product_options, key="product_type_filter")
    with rf6:
        selected_parent_brands = st.multiselect("Parent Brand", parent_options, key="parent_brand_filter")

    filtered = df.copy()
    if status_filter != "All":
        filtered = filtered[filtered["status"] == status_filter]
    if selected_topics:
        filtered = filtered[filtered["topic_detail"].isin(selected_topics)]
    if selected_industries:
        filtered = filtered[filtered["industry"].apply(lambda value: row_has_any_facet_value(value, selected_industries))]
    if selected_product_types:
        filtered = filtered[filtered["product_type"].apply(lambda value: row_has_any_facet_value(value, selected_product_types))]
    if selected_parent_brands:
        filtered = filtered[filtered["parent_brand"].apply(lambda value: row_has_any_facet_value(value, selected_parent_brands))]
    if refine_text.strip():
        needle = normalize_text(refine_text)
        filtered = filtered[
            filtered["search_text"].fillna("").str.contains(needle, regex=False)
            | filtered["industry"].fillna("").str.lower().str.contains(needle, regex=False)
            | filtered["product_type"].fillna("").str.lower().str.contains(needle, regex=False)
            | filtered["parent_brand"].fillna("").str.lower().str.contains(needle, regex=False)
            | filtered["matched_entity"].fillna("").str.lower().str.contains(needle, regex=False)
        ]

    filtered_open_df = filtered[filtered["status"] == "Open"]
    st.caption(f"Showing {len(filtered)} of {len(df)} markets after refinement.")

    # ── Charts row ────────────────────────────────────────────────
    st.markdown('<div class="section-header">Market Intelligence</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        fig1 = plot_volume_by_type(filtered)
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
    with c2:
        fig2 = plot_open_probs(filtered)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No open markets with probability data found.")

    # ── Markets table ─────────────────────────────────────────────
    st.markdown('<div class="section-header">All Markets</div>', unsafe_allow_html=True)

    fc1, fc2 = st.columns([2, 4])
    with fc1:
        sort_by = st.selectbox("Sort by", ["Volume", "YES Probability", "24hr Volume"],
                               label_visibility="collapsed", key="sort_by")

    if sort_by == "YES Probability":
        filtered = filtered.sort_values("yes_prob", ascending=False)
    elif sort_by == "24hr Volume":
        filtered = filtered.sort_values("volume_24hr", ascending=False)

    # Render markets
    for _, row in filtered.iterrows():
        prob   = row["yes_prob"]
        vol    = row["volume"]
        status = row["status"]
        q      = row["question"]

        if prob is not None:
            bar_color = "#22c55e" if prob>=60 else "#ef4444" if prob<=30 else "#f59e0b"
            prob_display = f'<span style="color:{bar_color};font-weight:600">{prob}%</span>'
        else:
            prob_display = '<span style="color:#4b5563">N/A</span>'

        status_class = "tag-open" if status=="Open" else "tag-closed"
        vol_display = f"${vol/1e6:.2f}M" if vol >= 1e6 else f"${vol/1e3:.0f}K"

        st.markdown(f"""
        <div class="market-row">
            <div class="market-q">{q[:90]}{"…" if len(q)>90 else ""}</div>
            <div class="market-meta">
                <span class="tag {status_class}">{status}</span>
                &nbsp;YES {prob_display}
                &nbsp;&nbsp;Vol {vol_display}
                &nbsp;&nbsp;{row["end_date"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Probability history drilldown ─────────────────────────────
    st.markdown('<div class="section-header">Probability History</div>', unsafe_allow_html=True)
    st.caption("Select an open market to see how the crowd probability has shifted over time.")

    open_markets = filtered_open_df[filtered_open_df["yes_prob"].notna()]
    if not open_markets.empty:
        market_options = {row["question"][:80]: row for _, row in open_markets.iterrows()}
        selected_q = st.selectbox("Pick a market", list(market_options.keys()),
                                  label_visibility="collapsed", key="selected_market")
        selected = market_options[selected_q]

        interval = st.radio("Interval", ["1d", "1w", "1m", "3m", "all"],
                            horizontal=True, label_visibility="collapsed", key="history_interval")

        try:
            token_ids = parse_token_ids(selected["token_id"])
            if token_ids:
                with st.spinner("Loading price history…"):
                    history = get_price_history(tuple(token_ids), interval)
                if history:
                    fig3 = plot_price_history(history, selected_q)
                    if fig3:
                        st.plotly_chart(fig3, use_container_width=True,
                                        config={"displayModeBar": False})
                else:
                    st.info("No price history available for this market.")
        except Exception:
            st.info("Could not load price history for this market.")

    # ── Export ────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Export</div>', unsafe_allow_html=True)

    export_df = filtered[["question","status","yes_prob","volume","volume_24hr",
                          "liquidity","end_date","topic","topic_detail","industry",
                          "product_type","parent_brand","matched_entity","tags"]].copy()
    export_df.columns = ["Question","Status","YES%","Volume","24hr Vol",
                          "Liquidity","End Date","Topic","Topic Detail","Industry",
                          "Product Type","Parent Brand","Matched Entity","Tags"]

    csv = export_df.to_csv(index=False)
    filename = brand.lower().replace(" ", "_") + "_polymarket.csv"
    st.download_button(
        label=f"⬇ Download CSV ({len(filtered)} markets)",
        data=csv, file_name=filename, mime="text/csv",
    )

elif brand:
    st.warning(f"No markets found for **{brand}**. Try a different search term.")

elif not brand:
    st.markdown("""
    <div style="text-align:center; padding: 4rem 0; color: #4b5563;">
        <div style="font-size:3rem; margin-bottom:1rem">🔮</div>
        <div style="font-family:'Syne',sans-serif; font-size:1.1rem; color:#6e7d9f;">
            Enter a brand name above to begin
        </div>
        <div style="font-size:0.8rem; margin-top:0.5rem; color:#3d4a5f">
            Searches Polymarket's prediction markets for crowd-priced signals<br>
            on brand risk, leadership, competition, product, and regulation
        </div>
    </div>
    """, unsafe_allow_html=True)
