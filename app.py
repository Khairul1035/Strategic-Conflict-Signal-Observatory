import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timezone

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Strategic Signal Observatory v3.0",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM STYLE
# --------------------------------------------------
st.markdown("""
<style>
    .main {
        background-color: #f6f7fb;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3 {
        color: #1f2a44;
        font-weight: 700;
    }

    .custom-card {
        background: white;
        padding: 1rem 1.2rem;
        border-radius: 14px;
        border: 1px solid #e6e8ef;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        margin-bottom: 1rem;
    }

    .brief-title {
        font-size: 0.83rem;
        color: #6b7280;
        margin-bottom: 0.25rem;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        font-weight: 600;
    }

    .brief-value {
        font-size: 1.35rem;
        font-weight: 700;
        color: #111827;
    }

    .researcher-line {
        font-size: 0.95rem;
        color: #374151;
        margin-top: -0.4rem;
        margin-bottom: 0.8rem;
    }

    .small-label {
        font-size: 0.82rem;
        color: #6b7280;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .value-box {
        font-size: 1rem;
        color: #111827;
        font-weight: 600;
        margin-top: 0.25rem;
    }

    .meta-line {
        font-size: 0.9rem;
        color: #4b5563;
        margin-bottom: 0.35rem;
    }

    .tag-ok {
        display: inline-block;
        padding: 0.2rem 0.55rem;
        border-radius: 999px;
        background: #e8f5e9;
        color: #1b5e20;
        font-size: 0.8rem;
        font-weight: 700;
        margin-right: 0.4rem;
    }

    .tag-warn {
        display: inline-block;
        padding: 0.2rem 0.55rem;
        border-radius: 999px;
        background: #fff8e1;
        color: #8d6e00;
        font-size: 0.8rem;
        font-weight: 700;
        margin-right: 0.4rem;
    }

    .tag-risk {
        display: inline-block;
        padding: 0.2rem 0.55rem;
        border-radius: 999px;
        background: #ffebee;
        color: #b71c1c;
        font-size: 0.8rem;
        font-weight: 700;
        margin-right: 0.4rem;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------
LOCAL_DATA_PATH = "data/events_sample.csv"

def safe_ratio(num, den):
    return round(num / den, 2) if den else 0.0

@st.cache_data(ttl=300)
def load_data(remote_csv_url: str | None = None):
    """
    Try remote CSV first for near-real-time refresh.
    Fall back to local CSV if remote source fails.
    """
    source_used = "Local backup CSV"
    if remote_csv_url:
        try:
            remote_df = pd.read_csv(remote_csv_url)
            source_used = "Remote CSV feed"
            return remote_df, source_used
        except Exception:
            pass

    local_df = pd.read_csv(LOCAL_DATA_PATH)
    return local_df, source_used

# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------
def classify_pattern(verified_count, contested_count):
    if verified_count > contested_count:
        return "Verified signals dominate. The environment appears more structured and visible than speculative."
    elif contested_count > verified_count:
        return "Contested signals dominate. The environment appears more ambiguous and vulnerable to narrative distortion."
    return "Verified and contested signals are balanced. Interpretation should remain cautious and non-final."

def get_risk_label(high_risk_count, contested_count):
    if high_risk_count >= 1 and contested_count >= 1:
        return "Elevated"
    elif high_risk_count >= 1:
        return "Guarded"
    elif contested_count >= 1:
        return "Cautious"
    return "Low"

def watch_next_message(high_risk_count, contested_count, verified_count):
    if high_risk_count >= 1 and contested_count >= 1:
        return "Monitor diplomatic signalling, market-sensitive movements, and narrative amplification over the next cycle."
    elif high_risk_count >= 1 and verified_count >= 1:
        return "Monitor market-sensitive developments, official signalling, and possible spillover implications."
    elif contested_count >= 1:
        return "Monitor repeated contested claims and whether they begin to shape broader perception or policy rhetoric."
    return "No immediate escalation pattern is visible within the current filtered dataset."

def asean_projection(country):
    if country in ["Iran", "Israel", "USA"]:
        return "Likely ASEAN posture: diplomatic balancing, rhetorical restraint, and limited strategic overcommitment."
    elif country in ["Saudi Arabia", "Qatar"]:
        return "Likely ASEAN posture: pragmatic monitoring of energy, trade, and diplomatic exposure."
    elif country == "Lebanon":
        return "Likely ASEAN posture: low direct involvement, with concern focused on regional spillover and stability."
    return "Likely ASEAN posture: limited direct response under current conditions."

def dominant_narrative(country_df):
    if country_df.empty:
        return "Insufficient evidence"
    mode_series = country_df["narrative_type"].mode()
    if len(mode_series) == 0:
        return "Insufficient evidence"
    return str(mode_series.iloc[0])

def actor_dominance(country_df):
    if country_df.empty:
        return "Insufficient evidence"
    counts = country_df["actor"].value_counts()
    return str(counts.idxmax())

def signal_quality_index(verified_count, contested_count):
    total = verified_count + contested_count
    score = safe_ratio(verified_count, total)
    if score >= 0.8:
        label = "High confidence environment"
    elif score >= 0.4:
        label = "Mixed confidence environment"
    else:
        label = "Low trust environment"
    return score, label

def narrative_pressure_index(contested_count, total_events):
    score = safe_ratio(contested_count, total_events)
    if score >= 0.8:
        label = "High narrative pressure"
    elif score >= 0.4:
        label = "Moderate narrative pressure"
    else:
        label = "Low narrative pressure"
    return score, label

def possible_hidden_intent(verified_count, contested_count, high_risk_count, actor_dom, dominant_narr):
    """
    Analytical reading only. Not a factual claim about concealed intent.
    """
    if contested_count > verified_count and dominant_narr in ["Media Claim", "Social Media"]:
        return "Possible analytical reading: perception management, narrative shaping, or ambiguity maintenance."
    if high_risk_count >= 1 and verified_count >= contested_count:
        return "Possible analytical reading: strategic signalling tied to market, policy, or reputational sensitivity."
    if actor_dom == "State" and verified_count > contested_count:
        return "Possible analytical reading: structured signalling rather than diffuse narrative contestation."
    return "Possible analytical reading: routine signalling environment with no strong hidden-intent indicator in the visible data."

def missing_but_expected(country_df, verified_count, contested_count):
    actors_present = set(country_df["actor"].astype(str).tolist())
    narratives_present = set(country_df["narrative_type"].astype(str).tolist())

    if contested_count > verified_count and "Official Statement" not in narratives_present:
        return "Missing but expected: official clarification is absent despite contested reporting. This may indicate intentional silence, delay, or incomplete verification."
    if "State" not in actors_present and len(country_df) > 0:
        return "Missing but expected: direct state-level signalling is limited in the visible dataset."
    return "No major missing-but-expected signal stands out under the current filtered view."

def build_scenario_probabilities(high_risk_count, contested_count, verified_count):
    a = 0.34
    b = 0.33
    c = 0.33

    if contested_count > verified_count:
        b += 0.20
        a -= 0.10
        c -= 0.10
    if high_risk_count >= 1:
        c += 0.20
        a -= 0.05
        b -= 0.15
    if verified_count > contested_count:
        a += 0.15
        b -= 0.10
        c -= 0.05

    values = [max(a, 0.05), max(b, 0.05), max(c, 0.05)]
    total = sum(values)
    probs = [round(v / total * 100, 1) for v in values]

    scenarios = {
        "Scenario A — Controlled Diplomatic Containment": probs[0],
        "Scenario B — Narrative Escalation Without Major Structural Shift": probs[1],
        "Scenario C — Business-Risk Spillover": probs[2]
    }

    likely = max(scenarios, key=scenarios.get)
    return scenarios, likely

def decision_implication(high_risk_count, contested_count, verified_count):
    business = "Elevated market or reputational sensitivity." if high_risk_count >= 1 else "No immediate business-risk spike visible."
    policy = "Policy rhetoric may become more cautious and verification-driven." if contested_count >= 1 else "Policy posture may remain relatively stable."
    regional = "Regional actors may hedge verbally while avoiding deep commitment." if (contested_count >= 1 or high_risk_count >= 1) else "Limited regional spillover is visible under current conditions."
    return business, policy, regional

# --------------------------------------------------
# SIDEBAR / CONTROLS
# --------------------------------------------------
with st.sidebar:
    st.header("Control Panel")

    remote_csv_url = st.text_input(
        "Optional remote CSV URL",
        value="",
        help="Paste a public CSV URL (e.g., GitHub raw CSV or published Google Sheet CSV). If unavailable, the app will automatically use the local backup CSV."
    )

    if st.button("Refresh data"):
        st.cache_data.clear()

    df, source_used = load_data(remote_csv_url)

    selected_country = st.selectbox(
        "Select one country for deep analysis",
        sorted(df["country"].unique())
    )

    categories = st.multiselect(
        "Filter category",
        sorted(df["category"].unique()),
        default=sorted(df["category"].unique())
    )

    signals = st.multiselect(
        "Filter signal level",
        sorted(df["signal_level"].unique()),
        default=sorted(df["signal_level"].unique())
    )

# --------------------------------------------------
# TIMESTAMP
# --------------------------------------------------
utc_now = datetime.now(timezone.utc)
local_now = datetime.now().astimezone()

# --------------------------------------------------
# FILTER DATA
# --------------------------------------------------
filtered = df[
    (df["category"].isin(categories)) &
    (df["signal_level"].isin(signals))
].copy()

country_df = filtered[filtered["country"] == selected_country].copy()

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("Strategic Signal Observatory v3.0")
st.markdown(
    '<div class="researcher-line"><strong>Lead Researcher:</strong> MOHD KHAIRUL RIDHUAN BIN MOHD FADZIL</div>',
    unsafe_allow_html=True
)
st.caption("Conflict interpretation interface for educational and analytical purposes only.")

st.markdown(
    f"""
<div class="meta-line"><strong>Data source:</strong> {source_used}</div>
<div class="meta-line"><strong>UTC fetch time:</strong> {utc_now.strftime("%Y-%m-%d %H:%M:%S %Z")}</div>
<div class="meta-line"><strong>Local fetch time:</strong> {local_now.strftime("%Y-%m-%d %H:%M:%S %Z")}</div>
""",
    unsafe_allow_html=True
)

if country_df.empty:
    st.warning("No data available for the selected country under the current filters.")
    st.stop()

# --------------------------------------------------
# METRICS
# --------------------------------------------------
verified_count = int((country_df["signal_level"] == "Verified").sum())
contested_count = int((country_df["signal_level"] == "Contested").sum())
high_risk_count = int((country_df["business_risk"] == "High").sum())
medium_risk_count = int((country_df["business_risk"] == "Medium").sum())
event_count = int(len(country_df))

risk_label = get_risk_label(high_risk_count, contested_count)
pattern_text = classify_pattern(verified_count, contested_count)
watch_next = watch_next_message(high_risk_count, contested_count, verified_count)
asean_text = asean_projection(selected_country)
dom_narrative = dominant_narrative(country_df)
actor_dom = actor_dominance(country_df)
sq_score, sq_label = signal_quality_index(verified_count, contested_count)
np_score, np_label = narrative_pressure_index(contested_count, event_count)
hidden_intent_text = possible_hidden_intent(
    verified_count, contested_count, high_risk_count, actor_dom, dom_narrative
)
missing_expected_text = missing_but_expected(country_df, verified_count, contested_count)
scenarios, likely_scenario = build_scenario_probabilities(high_risk_count, contested_count, verified_count)
business_imp, policy_imp, regional_imp = decision_implication(high_risk_count, contested_count, verified_count)

# --------------------------------------------------
# EXECUTIVE BRIEF
# --------------------------------------------------
st.subheader("Executive Brief")

b1, b2, b3, b4 = st.columns(4)

with b1:
    st.markdown(f"""
    <div class="custom-card">
        <div class="brief-title">Country Assessed</div>
        <div class="brief-value">{selected_country}</div>
    </div>
    """, unsafe_allow_html=True)

with b2:
    st.markdown(f"""
    <div class="custom-card">
        <div class="brief-title">Filtered Events</div>
        <div class="brief-value">{event_count}</div>
    </div>
    """, unsafe_allow_html=True)

with b3:
    st.markdown(f"""
    <div class="custom-card">
        <div class="brief-title">High-Risk Signals</div>
        <div class="brief-value">{high_risk_count}</div>
    </div>
    """, unsafe_allow_html=True)

with b4:
    st.markdown(f"""
    <div class="custom-card">
        <div class="brief-title">Assessment Level</div>
        <div class="brief-value">{risk_label}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(
    f"""
**Current assessment:** {selected_country} registers **{event_count} filtered event(s)**, comprising **{verified_count} verified signal(s)** and **{contested_count} contested signal(s)**.

**Primary interpretation:** {pattern_text}

**Immediate watchpoint:** {watch_next}
"""
)

# --------------------------------------------------
# ANALYTICAL INDICES
# --------------------------------------------------
st.subheader("Analytical Indices")

i1, i2, i3 = st.columns(3)
with i1:
    st.metric("Signal Quality Index", sq_score)
    st.caption(sq_label)

with i2:
    st.metric("Narrative Pressure Index", np_score)
    st.caption(np_label)

with i3:
    st.metric("Dominant Actor Weight", actor_dom)

# --------------------------------------------------
# COUNTRY INTELLIGENCE CARD
# --------------------------------------------------
st.subheader("Country Intelligence Card")

c1, c2 = st.columns(2)

with c1:
    st.markdown(f"""
    <div class="custom-card">
        <div class="small-label">Dominant narrative</div>
        <div class="value-box">{dom_narrative}</div>
        <br>
        <div class="small-label">Signal posture</div>
        <div class="value-box">{'Verified-led' if verified_count > contested_count else 'Contested-led' if contested_count > verified_count else 'Balanced'}</div>
        <br>
        <div class="small-label">Primary risk reading</div>
        <div class="value-box">{risk_label}</div>
        <br>
        <div class="small-label">ASEAN projection</div>
        <div class="value-box">{asean_text}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="custom-card">
        <div class="small-label">Possible hidden intent</div>
        <div class="value-box">{hidden_intent_text}</div>
        <br>
        <div class="small-label">Missing but expected</div>
        <div class="value-box">{missing_expected_text}</div>
        <br>
        <div class="small-label">Analytical caution</div>
        <div class="value-box">Interpret visible patterns only. Do not infer hidden intent, classified action, or tactical certainty as fact.</div>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# STRATEGIC INTERPRETATION + SCENARIOS
# --------------------------------------------------
left_panel, right_panel = st.columns(2)

with left_panel:
    st.subheader("Strategic Interpretation")
    st.info(pattern_text)

    if high_risk_count > 0:
        st.error(
            f"{selected_country} shows {high_risk_count} high-risk indicator(s). "
            "This may imply elevated business, policy, reputational, or regional sensitivity."
        )
    elif medium_risk_count > 0:
        st.warning(
            f"{selected_country} shows {medium_risk_count} medium-risk indicator(s). "
            "This suggests caution, but not a fully escalatory reading."
        )
    else:
        st.success("No high-risk structure is visible in the current filtered view.")

    st.markdown("**Decision implications**")
    st.write(f"- **Business:** {business_imp}")
    st.write(f"- **Policy:** {policy_imp}")
    st.write(f"- **Regional:** {regional_imp}")

with right_panel:
    st.subheader("Scenario Panel")
    for scenario_name, prob in scenarios.items():
        st.write(f"**{scenario_name} — {prob}%**")

    st.write("")
    st.write(f"**Most likely under current data:** {likely_scenario}")

# --------------------------------------------------
# EVENT TABLE
# --------------------------------------------------
st.subheader("Country Event Table")
display_cols = [
    "date", "country", "actor", "category",
    "signal_level", "narrative_type", "business_risk", "summary"
]
st.dataframe(country_df[display_cols], use_container_width=True)

# --------------------------------------------------
# CHARTS
# --------------------------------------------------
chart1, chart2 = st.columns(2)

with chart1:
    st.subheader("Signal vs Noise")
    signal_counts = country_df.groupby("signal_level").size().reset_index(name="count")
    fig1 = px.bar(signal_counts, x="signal_level", y="count")
    st.plotly_chart(fig1, use_container_width=True)

with chart2:
    st.subheader("Narrative Mix")
    narrative_counts = country_df.groupby("narrative_type").size().reset_index(name="count")
    fig2 = px.bar(narrative_counts, x="narrative_type", y="count")
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Regional Comparison")
comparison_df = filtered.groupby("country").size().reset_index(name="event_count")
fig3 = px.bar(comparison_df, x="country", y="event_count")
st.plotly_chart(fig3, use_container_width=True)

# --------------------------------------------------
# WHAT MOST PEOPLE MISS
# --------------------------------------------------
st.subheader("What Most People Miss")

if verified_count > contested_count and high_risk_count > 0:
    missed_point = (
        "The most important signal may not be the visible rhetoric itself, but the way verified reporting intersects with business-risk exposure."
    )
elif contested_count > verified_count:
    missed_point = (
        "The central issue may be ambiguity rather than volume. Contested claims can shape perception even when evidence remains incomplete."
    )
else:
    missed_point = (
        "The key analytical issue lies in the balance between credible signalling and narrative amplification, not in raw event count alone."
    )

st.write(missed_point)

# --------------------------------------------------
# ANALYST MEMO
# --------------------------------------------------
st.subheader("Analyst Memo")

memo = f"""
**Country assessed:** {selected_country}

**Situation overview:** The filtered dataset records {event_count} event(s) associated with {selected_country}. Within this subset, {verified_count} signal(s) are classified as verified and {contested_count} as contested.

**Signal interpretation:** {pattern_text}

**Signal quality:** {sq_score} ({sq_label})

**Narrative pressure:** {np_score} ({np_label})

**Risk interpretation:** {selected_country} shows {high_risk_count} high-risk indicator(s). This may imply sensitivity in business conditions, policy positioning, diplomatic signalling, or regional confidence.

**Dominant actor:** {actor_dom}

**Dominant narrative form:** {dom_narrative}

**Possible hidden intent (analytical reading only):** {hidden_intent_text}

**Missing but expected:** {missing_expected_text}

**ASEAN outlook:** {asean_text}

**Watch next:** {watch_next}

**Most likely scenario:** {likely_scenario}

**Decision implications:** Business — {business_imp} Policy — {policy_imp} Regional — {regional_imp}

**Analytical caution:** This dashboard does not infer hidden intent, operational planning, or classified realities as facts. It supports interpretation of visible patterns only.

**Epistemic note:** Users should distinguish between verified reporting, repeated claims, and narrative amplification. Contested reporting should not be treated as established fact without corroboration.

**Lead researcher:** MOHD KHAIRUL RIDHUAN BIN MOHD FADZIL

**UTC fetch time:** {utc_now.strftime("%Y-%m-%d %H:%M:%S %Z")}
**Local fetch time:** {local_now.strftime("%Y-%m-%d %H:%M:%S %Z")}
**Data source used:** {source_used}

**For educational and analytical purposes only.**
"""
st.markdown(memo)
