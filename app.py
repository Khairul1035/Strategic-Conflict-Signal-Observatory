import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Strategic Signal Observatory v2.1",
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
        padding-top: 2rem;
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
        font-size: 0.85rem;
        color: #6b7280;
        margin-bottom: 0.3rem;
    }

    .brief-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #111827;
    }

    .section-note {
        color: #6b7280;
        font-size: 0.95rem;
    }

    .researcher-line {
        font-size: 0.95rem;
        color: #374151;
        margin-top: -0.4rem;
        margin-bottom: 1rem;
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
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("data/events_sample.csv")

df = load_data()

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
        return "Monitor diplomatic signalling, economic sensitivity, and narrative amplification over the next cycle."
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

def build_scenario(high_risk_count, contested_count, verified_count):
    scenario_a = "Scenario A — Controlled Diplomatic Containment"
    scenario_b = "Scenario B — Narrative Escalation Without Major Structural Shift"
    scenario_c = "Scenario C — Business-Risk Spillover"

    if high_risk_count >= 1 and verified_count >= 1:
        likely = scenario_c
    elif contested_count > verified_count:
        likely = scenario_b
    else:
        likely = scenario_a

    return scenario_a, scenario_b, scenario_c, likely

def dominant_narrative(country_df):
    if country_df.empty:
        return "Insufficient evidence"
    mode_series = country_df["narrative_type"].mode()
    if len(mode_series) == 0:
        return "Insufficient evidence"
    return str(mode_series.iloc[0])

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("Strategic Signal Observatory v2.1")
st.markdown(
    '<div class="researcher-line"><strong>Lead Researcher:</strong> MOHD KHAIRUL RIDHUAN BIN MOHD FADZIL</div>',
    unsafe_allow_html=True
)
st.caption("Conflict interpretation interface for educational and analytical purposes only.")

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:
    st.header("Control Panel")

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
# FILTER DATA
# --------------------------------------------------
filtered = df[
    (df["category"].isin(categories)) &
    (df["signal_level"].isin(signals))
].copy()

country_df = filtered[filtered["country"] == selected_country].copy()

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
scenario_a, scenario_b, scenario_c, likely_scenario = build_scenario(
    high_risk_count, contested_count, verified_count
)

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
# COUNTRY INTELLIGENCE CARD
# --------------------------------------------------
st.subheader("Country Intelligence Card")

c1, c2 = st.columns([1.2, 1])

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
        <div class="small-label">What to watch next</div>
        <div class="value-box">{watch_next}</div>
        <br>
        <div class="small-label">Most likely scenario</div>
        <div class="value-box">{likely_scenario}</div>
        <br>
        <div class="small-label">Analytical caution</div>
        <div class="value-box">Interpret visible patterns only. Do not infer hidden intent, classified action, or tactical certainty.</div>
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

with right_panel:
    st.subheader("Scenario Panel")
    st.write(f"**{scenario_a}**")
    st.write("Trigger: verified diplomatic or official signalling begins to stabilise perception.")
    st.write("")
    st.write(f"**{scenario_b}**")
    st.write("Trigger: contested claims circulate faster than corroborated evidence.")
    st.write("")
    st.write(f"**{scenario_c}**")
    st.write("Trigger: business, energy, or policy sensitivity becomes more visible than the narrative surface.")
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

**Risk interpretation:** {selected_country} shows {high_risk_count} high-risk indicator(s). This may imply sensitivity in business conditions, policy positioning, diplomatic signalling, or regional confidence.

**Dominant narrative form:** {dom_narrative}

**ASEAN outlook:** {asean_text}

**Watch next:** {watch_next}

**Analytical caution:** This dashboard does not infer hidden intent, operational planning, or classified realities. It supports interpretation of visible patterns only.

**Epistemic note:** Users should distinguish between verified reporting, repeated claims, and narrative amplification. Contested reporting should not be treated as established fact without corroboration.

**Lead researcher:** MOHD KHAIRUL RIDHUAN BIN MOHD FADZIL

**For educational and analytical purposes only.**
"""
st.markdown(memo)
