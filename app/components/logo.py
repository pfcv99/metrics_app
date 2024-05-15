import streamlit as st

@st.cache_data
def add_logo():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url("https://cdn.worldvectorlogo.com/logos/unilabs-1.svg");
                background-repeat: no-repeat;
                background-size: 90%; /* or 'cover' or other values based on your preference */
                padding-top: 100px;
                margin-top: 60px;
                background-position: 20px 20px;
            }
            [data-testid="stSidebarNav"]::before {
                content: "";
                margin-left: 20px;
                margin-bottom: 10px;
                font-size: 35px;
                position: absolute;
                top: 140px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

