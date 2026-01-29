import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.set_page_config(page_title="LEO Visibility Viewer", layout="wide")
st.title("🌌 LEO Satellite Visibility (Interactive)")

# =========================
# Parse TXT
# =========================
def parse_visibility_txt(txt_file):
    records = []
    lines = [line.decode("utf-8") if isinstance(line, bytes) else line for line in txt_file.readlines()]

    current_observer = None
    in_table = False

    for line in lines:
        line = line.strip()
        obs_match = re.match(r"Observer:\s*(.+)", line)
        if obs_match:
            current_observer = obs_match.group(1)
            in_table = False
            continue
        if line.startswith("Start Time (UTC)"):
            in_table = True
            continue
        if line.startswith("Number of events"):
            in_table = False
            continue
        if in_table and current_observer and line:
            parts = re.split(r"\s{2,}", line)
            if len(parts) == 3:
                start, stop, duration = parts
                records.append({
                    "Observer": current_observer,
                    "Start Time (UTC)": pd.to_datetime(start, format="%d %b %Y %H:%M:%S.%f"),
                    "Stop Time (UTC)": pd.to_datetime(stop, format="%d %b %Y %H:%M:%S.%f"),
                    "Duration (s)": float(duration)
                })
    return pd.DataFrame(records)

# =========================
# File Upload
# =========================
uploaded_file = st.file_uploader("Drag & Drop your visibility TXT file", type="txt")

if uploaded_file:
    df = parse_visibility_txt(uploaded_file)

    if df.empty:
        st.warning("No visibility events found in this file.")
    else:
        st.subheader("Interactive Visibility Timeline")

        df_plot = df.copy()
        df_plot['y'] = df_plot['Observer']

        fig = px.timeline(
            df_plot,
            x_start="Start Time (UTC)",
            x_end="Stop Time (UTC)",
            y="y",
            color="Observer",
            height=400 + 40*len(df['Observer'].unique()),
            title="Visibility Windows (Interactive)"
        )
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(xaxis_title="Time (UTC)", yaxis_title="Ground Station")
        st.plotly_chart(fig, use_container_width=True)

