import streamlit as st 

def clear_cache():
    keys = list(st.session_state.keys())
    for key in keys:
        st.session_state.pop(key)

#st.button('Clear Cache', on_click=clear_cache)