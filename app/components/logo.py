import streamlit as st

def add_logo():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url("https://cdn.worldvectorlogo.com/logos/unilabs-1.svg");
                background-repeat: no-repeat;
                background-size: 90%; /* or 'cover' or other values based on your preference */
                padding-top: 100px;
                margin-top: 20px;
                background-position: 20px 20px;
            }
            [data-testid="stSidebarNav"]::before {
                content: "UniMetric Analyzer";
                margin-left: 20px;
                margin-bottom: 10px;
                font-size: 30px;
                position: relative;
                top: 45px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

