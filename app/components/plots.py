# metrics_app/app/components/plots.py

import streamlit as st
import plotly.express as px
import pandas as pd
from pathlib import Path

def plot_depth_pos(output_folder):
    for file_path in Path(output_folder).glob("output_1110366_PKD1.depth"):
        data = pd.read_csv(file_path, sep="\t")
        df = pd.DataFrame(data)
        
        # Create a scatter plot using Plotly Express
        fig = px.scatter(df, x=df.columns[1], y=df.columns[2], marginal_x="histogram", marginal_y="rug")
        
        # Add a new x-axis
        fig.update_layout(xaxis2=dict(title=df.columns[0]))
        
        # Display the plot using Streamlit
        with st.container():
            st.plotly_chart(fig, use_container_width=True, theme="streamlit")

