import streamlit as st
from components import logo

# Display logos
sidebar_logo = "data/img/unilabs_logo.png"
main_body_logo = "data/img/thumbnail_image001.png"
st.logo(sidebar_logo, icon_image=main_body_logo)

# Initialize session state
if "user" not in st.session_state:
    st.session_state.user = None
    
if "password" not in st.session_state:
    st.session_state.password = None


@st.experimental_dialog("Log in")
def login():
    user = st.text_input("User")
    password = st.text_input("Password", type="password")
    if st.button("Log in"):
        st.session_state.user = user
        st.session_state.password = password
        st.rerun()




def logout():
    st.session_state.user = None
    st.session_state.password = None
    st.rerun()


# Retrieve user credentials
user = st.session_state.user
password = st.session_state.password

# Define pages
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
settings = st.Page("app_pages/settings.py", title="Settings", icon=":material/settings:")
form = st.Page("app_pages/form.py", title="Query", icon=":material/analytics:",default=((user == "userA" and password == "userA") or (user == "admin" and password == "admin")))
results = st.Page("app_pages/results.py", title="Results", icon=":material/table_chart_view:")
gene_panel_creator = st.Page("app_pages/gene_panel_creator.py", title="Gene panel creator", icon=":material/edit_note:",default=(user == "userB" and password == "userB"))
about = st.Page("app_pages/3_About.py", title="About", icon=":material/info:")

# Group pages
account_pages = [logout_page, settings]
metrics_pages = [form, results]
panel_builder_pages = [gene_panel_creator]
about_pages = [about]

# Set up credentials
credentials = (user, password)

admin_credentials = (st.secrets.admin.user, st.secrets.admin.password)
userA_credentials = (st.secrets.userA.user, st.secrets.userA.password)
userB_credentials = (st.secrets.userB.user, st.secrets.userB.password)

# Build page dictionary based on user credentials
page_dict = {}
if credentials in [admin_credentials, userA_credentials]:
    page_dict["Metrics calculator"] = metrics_pages
if credentials in [admin_credentials, userB_credentials]:
    page_dict["Gene panels"] = panel_builder_pages
if credentials in [admin_credentials, userA_credentials, userB_credentials]:
    page_dict["About"] = about_pages


# Display navigation
if page_dict:
    pg = st.navigation({"Account": account_pages} | page_dict)
else:
    pg = st.navigation([st.Page(login)])
pg.run()