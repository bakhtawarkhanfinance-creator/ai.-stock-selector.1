
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# Sample dataset
companies_data = [
    {"Company": "Alpha Energy", "Industry": "Energy", "Region": "Europe", "MarketCap": 2000, "RevenueGrowth": 12.5, "ProfitMargin": 8.2, "ROE": 16.3, "ESGScore": 75},
    {"Company": "Beta Power", "Industry": "Energy", "Region": "Europe", "MarketCap": 1500, "RevenueGrowth": 10.1, "ProfitMargin": 7.5, "ROE": 14.8, "ESGScore": 80},
    {"Company": "Gamma Oil", "Industry": "Energy", "Region": "Europe", "MarketCap": 1800, "RevenueGrowth": 15.0, "ProfitMargin": 9.0, "ROE": 17.5, "ESGScore": 70},
    {"Company": "Delta Renewables", "Industry": "Energy", "Region": "Europe", "MarketCap": 1600, "RevenueGrowth": 18.2, "ProfitMargin": 10.5, "ROE": 19.0, "ESGScore": 85},
    {"Company": "Epsilon Gas", "Industry": "Energy", "Region": "Europe", "MarketCap": 1400, "RevenueGrowth": 9.8, "ProfitMargin": 6.9, "ROE": 13.2, "ESGScore": 65},
    {"Company": "Zeta Solar", "Industry": "Energy", "Region": "Europe", "MarketCap": 1700, "RevenueGrowth": 16.0, "ProfitMargin": 11.0, "ROE": 20.1, "ESGScore": 90}
]

# Convert to DataFrame
df = pd.DataFrame(companies_data)

st.set_page_config(page_title="AI Stock Selector", layout="wide")
st.title("📈 AI-Powered Stock Selector")

# Sidebar filters
st.sidebar.header("🔍 Filter Criteria")
industry = st.sidebar.selectbox("Select Industry", df["Industry"].unique())
region = st.sidebar.selectbox("Select Region", df["Region"].unique())
market_cap_min = st.sidebar.slider("Minimum Market Cap", 1000, 3000, 1000)
market_cap_max = st.sidebar.slider("Maximum Market Cap", 1000, 3000, 2000)
roe_min = st.sidebar.slider("Minimum ROE", 10.0, 25.0, 15.0)
esg_min = st.sidebar.slider("Minimum ESG Score", 50, 100, 70)

# Apply filters
filtered_df = df[
    (df["Industry"] == industry) &
    (df["Region"] == region) &
    (df["MarketCap"] >= market_cap_min) &
    (df["MarketCap"] <= market_cap_max) &
    (df["ROE"] >= roe_min) &
    (df["ESGScore"] >= esg_min)
]

# Scoring mechanism
weights = {
    "RevenueGrowth": 0.25,
    "ProfitMargin": 0.25,
    "ROE": 0.25,
    "ESGScore": 0.25
}

for metric in weights:
    filtered_df[metric + "_Norm"] = (filtered_df[metric] - filtered_df[metric].min()) / (filtered_df[metric].max() - filtered_df[metric].min())

filtered_df["Score"] = sum(filtered_df[metric + "_Norm"] * weight for metric, weight in weights.items())

ranked_df = filtered_df.sort_values(by="Score", ascending=False)[["Company", "MarketCap", "RevenueGrowth", "ProfitMargin", "ROE", "ESGScore", "Score"]]

st.subheader("🏆 Top Ranked Companies")
st.dataframe(ranked_df)

# Score breakdown chart
st.subheader("📊 Score Breakdown by Company")
if not ranked_df.empty:
    score_components = [metric + "_Norm" for metric in weights]
    score_df = filtered_df[["Company"] + score_components].set_index("Company")
    score_df = score_df.reset_index().melt(id_vars="Company", var_name="Metric", value_name="Normalized Score")

    chart = alt.Chart(score_df).mark_bar().encode(
        x=alt.X("Company:N", title="Company"),
        y=alt.Y("Normalized Score:Q", title="Score"),
        color="Metric:N",
        tooltip=["Company", "Metric", "Normalized Score"]
    ).properties(width=800)

    st.altair_chart(chart, use_container_width=True)

# Company profile cards
st.subheader("📋 Company Profiles")
for _, row in ranked_df.iterrows():
    with st.expander(row["Company"]):
        st.write(f"**Market Cap:** {row['MarketCap']} M")
        st.write(f"**Revenue Growth:** {row['RevenueGrowth']}%")
        st.write(f"**Profit Margin:** {row['ProfitMargin']}%")
        st.write(f"**ROE:** {row['ROE']}%")
        st.write(f"**ESG Score:** {row['ESGScore']}")
        st.write(f"**Composite Score:** {round(row['Score'], 2)}")

# Download button
st.subheader("📥 Export Results")
csv = ranked_df.to_csv(index=False)
st.download_button("Download Ranked Companies as CSV", csv, "ranked_companies.csv", "text/csv")

st.markdown("---")
st.markdown("**Note:** Scores are calculated using a weighted average of normalized performance metrics.")
