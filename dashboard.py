import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh

BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Store Intelligence Dashboard",
    layout="wide"
)

st_autorefresh(
    interval=3000,
    key="refresh"
)

st.title("🏪 Store Intelligence Dashboard")

store_id = st.sidebar.selectbox(
    "Select Store",
    [
        "STORE_001",
        "STORE_002"
    ]
)

try:

    metrics = requests.get(
        f"{BASE_URL}/stores/{store_id}/metrics"
    ).json()

    # st.write(metrics)

    funnel = requests.get(
        f"{BASE_URL}/stores/{store_id}/funnel"
    ).json()

    heatmap = requests.get(
        f"{BASE_URL}/stores/{store_id}/heatmap"
    ).json()

    anomalies = requests.get(
        f"{BASE_URL}/stores/{store_id}/anomalies"
    ).json()

except Exception as e:

    st.error(
        f"API not reachable: {e}"
    )

    st.stop()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Unique Visitors",
    metrics["unique_visitors"]
)

col2.metric(
    "Conversion Rate",
    metrics["conversion_rate"]
)

col3.metric(
    "Abandonment Rate",
    metrics["abandonment_rate"]
)

col4.metric(
    "Queue Depth",
    metrics["queue_depth"]
)

st.divider()

st.subheader("Funnel")

f1, f2, f3, f4 = st.columns(4)

f1.metric(
    "Store Visitors",
    funnel["store_visitors"]
)

f2.metric(
    "Zone Visitors",
    funnel["zone_visitors"]
)

f3.metric(
    "Queue Visitors",
    funnel["queue_visitors"]
)

f4.metric(
    "Purchases",
    funnel["purchases"]
)

st.divider()

st.subheader("Heatmap")

import pandas as pd

heatmap_df = pd.DataFrame(
    heatmap["zones"]
)

if not heatmap_df.empty:

    st.bar_chart(
        heatmap_df.set_index("zone")[
            "heat_score"
        ]
    )

    st.dataframe(
        heatmap_df,
        use_container_width=True
    )

st.divider()

st.subheader("Anomalies")

if len(anomalies["anomalies"]) == 0:

    st.success(
        "No anomalies detected"
    )

else:

    for anomaly in anomalies["anomalies"]:

        severity = anomaly["severity"]

        text = (
            f"{anomaly['type']} | "
            f"{severity} | "
            f"{anomaly['message']}"
        )

        if severity == "CRITICAL":
            st.error(text)

        elif severity == "WARN":
            st.warning(text)

        else:
            st.info(text)