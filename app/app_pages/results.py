import streamlit as st
import pandas as pd
from components import dataframe, metrics

sidebar_logo = "data/img/unilabs_logo.png"
main_body_logo = "data/img/thumbnail_image001.png"
st.logo(sidebar_logo, icon_image=main_body_logo)

st.title("Results")
tab1, tab2, tab3 = st.tabs(["Overview", "Gene Detail", "Exon Detail"])

with tab1:
    df = pd.DataFrame(columns=["command", "rating", "is_widget"])
    df = pd.DataFrame(
    [
        {"command": "st.selectbox", "rating": 4, "is_widget": True},
        {"command": "st.balloons", "rating": 5, "is_widget": False},
        {"command": "st.time_input", "rating": 3, "is_widget": True},
    ]
    )
    edited_df = st.data_editor(
        df,
        column_config={
            "command": "Streamlit Command",
            "rating": st.column_config.NumberColumn(
                "Your rating",
                help="How much do you like this command (1-5)?",
                min_value=1,
                max_value=5,
                step=1,
                format="%d ⭐",
            ),
            "is_widget": "Widget ?",
        },
        disabled=["command", "is_widget"],
        hide_index=True,
    )

    favorite_command = edited_df.loc[edited_df["rating"].idxmax()]["command"]
    st.markdown(f"Your favorite command is **{favorite_command}** 🎈")
    st.session_state.assembly
    st.session_state.region
    st.session_state.bam
with tab2:
    st.write("Gene Detail")
    
    df = dataframe.dataframe()
    st.dataframe(df)
    
with tab3:
    st.write("Exon Detail")