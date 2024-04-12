import streamlit as st
from components import streamlit_page_config
from components import logo

# Set Streamlit page configuration
streamlit_page_config.set_page_configuration()

logo.add_logo()

st.write("# Authors")
st.write("- Pedro Filipe Carneiro Venâncio | pedrofcvenancio@ua.pt")
st.divider()

st.write("# Changelog")
st.divider()

st.write("# Resources")
