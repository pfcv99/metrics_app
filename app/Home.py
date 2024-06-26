import streamlit as st
from components import logo

sidebar_logo = "data/img/unilabs_logo.png"
main_body_logo = "data/img/thumbnail_image001.png"
st.logo(sidebar_logo, icon_image=main_body_logo)

page = {
    "Your account" : [
        st.Page("app_pages/logout.py", title="Log out", icon=":material/logout:"),
        st.Page("app_pages/login.py", title="Log in", icon=":material/login:"),
        st.Page("app_pages/settings.py", title="Settings", icon=":material/settings:")
    ],
    "Tools" : [
        st.Page("app_pages/query.py", title="Metrics calculator", icon=":material/analytics:"),
        st.Page("app_pages/gene_panel_creator.py", title="Gene panel creator", icon=":material/edit_note:"),
        st.Page("app_pages/form.py", title="Form", icon=":material/edit_note:"),
    ],
    "About" : [
        st.Page("app_pages/3_About.py", title="About", icon=":material/info:")
    ]
}

pg = st.navigation(page)
pg.run()