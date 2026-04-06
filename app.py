import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Tabayyun Intelligence Dashboard", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("data/events_sample.csv")

df = load_data()

st.title("Tabayyun Intelligence Dashboard")
st.caption("Strategic conflict interpretation dashboard for educational and analytical purposes only.")

with st.sidebar:
    st.header("Filter Panel")
    countries = st.multiselect("Select country", sorted(df["country"].unique()), default=sorted(df["country"].unique()))
    categories = st.multiselect("Select category", sorted(df["category"].unique()), default=sorted(df["category"].unique()))
    signals = st.multiselect("Select signal level", sorted(df["signal_level"].unique()), default=sorted(df["signal_level"].unique()))

filtered = df[
    df["country"].isin(countries) &
    df["category"].isin(categories) &
    df["signal_level"].isin(signals)
]

col1, col2, col3 = st.columns(3)
col1.metric("Events", len(filtered))
col2.metric("Countries", filtered["country"].nunique())
col3.metric("High Business Risk Events", (filtered["business_risk"] == "High").sum())

st.subheader("Event Table")
st.dataframe(filtered, use_container_width=True)

st.subheader("Signal Distribution")
fig1 = px.histogram(filtered, x="signal_level")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Country Comparison")
country_counts = filtered.groupby("country").size().reset_index(name="event_count")
fig2 = px.bar(country_counts, x="country", y="event_count")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Narrative Assessment")
narrative_counts = filtered.groupby(["country", "narrative_type"]).size().reset_index(name="count")
fig3 = px.bar(narrative_counts, x="country", y="count", color="narrative_type", barmode="group")
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Analyst Memo")
selected_country = st.selectbox("Choose one country for memo", sorted(filtered["country"].unique()))

country_df = filtered[filtered["country"] == selected_country]

if not country_df.empty:
    verified_count = (country_df["signal_level"] == "Verified").sum()
    contested_count = (country_df["signal_level"] == "Contested").sum()
    high_risk_count = (country_df["business_risk"] == "High").sum()

    memo = f"""
**Country assessed:** {selected_country}

**Initial assessment:** The current pattern suggests a mixed information environment with {verified_count} verified signals and {contested_count} contested signals.

**Risk interpretation:** {selected_country} shows {high_risk_count} high business-risk indicators in the present dataset. This may imply elevated sensitivity for market perception, policy signalling, or regional confidence.

**Analytical caution:** This dashboard does not infer operational intent. It distinguishes only between visible signals, contested reporting, and strategic relevance.

**Epistemic note:** Users should separate verified reporting from narrative amplification and avoid treating contested claims as established fact.

**For educational and analytical purposes only.**

# test commit
"""
    st.markdown(memo)
else:
    st.info("No data available for the selected country.")
