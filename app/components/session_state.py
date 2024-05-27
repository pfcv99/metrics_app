import streamlit as st

# Initialize session state variables
if 'analysis' not in st.session_state:
    st.session_state['analysis'] = 'Single Gene'
    
if 'assembly' not in st.session_state:
    st.session_state['assembly'] = "GRCh38/hg38"

if 'gene' not in st.session_state:
    st.session_state['gene'] = "x"

if 'bam' not in st.session_state:
    st.session_state['bam'] = ["x"]