import streamlit as st
import duckdb

st.set_page_config(page_title="User Signups Dashboard", layout="wide")

st.title("User Signups Dashboard")
st.write("Visualizing the clean output of the DuckDB data pipeline.")


try:
    conn = duckdb.connect(":memory:")

    parquet_file = "data_live/analytics.parquet"

    # Total Validated Signups - count
    total_signups = conn.execute(f"SELECT COUNT(*) FROM read_parquet('{parquet_file}')").fetchone()[0]
    st.metric("Total Signups", total_signups)

    st.subheader("Signups by Plan Type")

    # Signups grouped by plan_type - bar
    plan_df = conn.execute(
        f"SELECT plan_type, COUNT(*) as signup_count FROM read_parquet('{parquet_file}') GROUP BY plan_type ORDER BY signup_count DESC"
    ).fetchdf()
    
    st.bar_chart(plan_df, x="plan_type", y="signup_count")

    st.subheader("Recent Signups")

    # Recent signups - table
    recent_df = conn.execute(
        f"SELECT * FROM read_parquet('{parquet_file}') ORDER BY timestamp DESC LIMIT 100"
    ).fetchdf()
    

    st.dataframe(recent_df, width="stretch")
    
except duckdb.IOException:
    st.error("Parquet file not found. Please run `python pipeline.py` first to generate the data.")
finally:
    if 'conn' in locals():
        conn.close()