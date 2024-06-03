import streamlit as st
from components import streamlit_page_config
from components import logo

# Set Streamlit page configuration
streamlit_page_config.set_page_configuration()

sidebar_logo = "data/img/unilabs_logo.png"
main_body_logo = "data/img/thumbnail_image001.png"
st.logo(sidebar_logo, icon_image=main_body_logo)

st.write("# Authors")
st.write("- Pedro Filipe Carneiro Venâncio | pedrofcvenancio@ua.pt")
st.divider()

st.write("# Changelog")
st.divider()

st.write("# Resources")
