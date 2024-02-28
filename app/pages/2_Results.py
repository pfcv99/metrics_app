import streamlit as st

st.markdown(
    """
    <style>
        .stProgress > div > div > div > div {
            background-image: linear-gradient(to right, #15FF0D, yellow, #C10505);
        }
    </style>""",
    unsafe_allow_html=True,
)
progress = st.progress(100)
progress