import streamlit as st


# Display logos
sidebar_logo = "data/img/unilabs_logo.png"
main_body_logo = "data/img/thumbnail_image001.png"
st.logo(sidebar_logo, size="large",link='http://localhost:8501/', icon_image=main_body_logo)

# Initialize session state
if "user" not in st.session_state:
    st.session_state.user = None

if "password" not in st.session_state:
    st.session_state.password = None

if 'bam_cram_files' not in st.session_state:
    st.session_state.bam_cram_files = []

if 'submit' not in st.session_state:
    st.session_state.submit = False

# Login feature flag (set to False to disable login, True to enable)
login_enabled = False

# Login dialog
@st.dialog(" ", width="large")
def login():
    col1, col2, col3 = st.columns(3)
    with col2:
        st.image(sidebar_logo, width=200)
    with st.container():
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
settings = st.Page("app_pages/settings.py", title="Settings", icon=":material/settings:")
form = st.Page("app_pages/query.py", title="Query", icon=":material/analytics:", default=True)
results = st.Page("app_pages/results.py", title="Results", icon=":material/table_chart_view:")
gene_panel_creator = st.Page("app_pages/gene_panel_creator.py", title="Gene panel creator", icon=":material/edit_note:")
about = st.Page("app_pages/about.py", title="About", icon=":material/info:")

# Group pages
metrics_pages = [form, results]
panel_builder_pages = [gene_panel_creator]
about_pages = [about]

# Set up credentials
credentials = (user, password)

admin_credentials = (st.secrets.admin.user, st.secrets.admin.password)
userA_credentials = (st.secrets.userA.user, st.secrets.userA.password)
userB_credentials = (st.secrets.userB.user, st.secrets.userB.password)
development = (None, None)

# Build page dictionary based on user credentials
page_dict = {}
if credentials in [admin_credentials, userA_credentials, development]:
    page_dict["Metrics calculator"] = metrics_pages
if credentials in [admin_credentials, userB_credentials, development]:
    page_dict["Gene panels"] = panel_builder_pages
if credentials in [admin_credentials, userA_credentials, userB_credentials, development]:
    page_dict["About"] = about_pages

# Show login dialog if login is enabled and no user is logged in
if login_enabled and (user is None or password is None):
    login()  # Call the login function to display the dialog
else:
    # Display navigation if logged in or if login is disabled
    if login_enabled:
        # Show Log out and navigation options if login is enabled
        logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
        account_pages = [logout_page, settings]
        pg = st.navigation({"Account": account_pages} | page_dict)
    else:
        # Skip login and hide Log out, show Query as default page
        pg = st.navigation(page_dict)

    # Run the selected page
    pg.run()
