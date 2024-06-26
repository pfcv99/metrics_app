import streamlit as st

@st.experimental_dialog("Sign up")

def form():
    with st.form(key='my_form'):
        user = st.text_input("User")
        password= st.text_input("Password", type="password")
        st.form_submit_button("Sign up")

form()