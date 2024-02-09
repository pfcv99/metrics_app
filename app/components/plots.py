# metrics_app/app/components/plots.py

import streamlit as st
import plotly.express as px
import pandas as pd
from pathlib import Path

def plot_depth_pos(output_folder):
    tabs = st.tabs([file.stem for file in output_folder])
    
    for i, tab in enumerate(tabs):
        data = pd.read_csv(output_folder[i])
        df = pd.DataFrame(data)
        fig = px.scatter(df, x=df.columns[0], y=df.columns[1], marginal_x="histogram", marginal_y="rug")
        with st.container():
            st.write(f"### {tab}")  # Display the file name as a header
            st.plotly_chart(fig, use_container_width=True, theme="plotly")
