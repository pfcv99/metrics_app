# metrics_app/app/components/streamlit_page_config.py

import streamlit as st

def set_page_configuration():
    """
    Set Streamlit page configuration.
    """
    st.set_page_config(
        page_title="UNILABS analysis tools",
        page_icon="data/img/thumbnail_image001.png",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
        'Get Help': 'mailto:pedrofcvenancio@ua.pt',
        'Report a bug': "https://forms.office.com/e/GCS50LBUms",
        'About': "**v1.0.0**"
    }
    )
