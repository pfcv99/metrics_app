import streamlit as st
from components import genome, streamlit_page_config, forms


# Set Streamlit page configuration
streamlit_page_config.set_page_configuration()

sidebar_logo = "data/img/unilabs_logo.png"
main_body_logo = "data/img/thumbnail_image001.png"
st.logo(sidebar_logo, icon_image=main_body_logo)


st.title("Metrics calculator\n")



font_css = """
<style>
button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
  font-size: 24px;
  margin-right: 70px;
  align: left;
}
</style>
"""

st.write(font_css, unsafe_allow_html=True) 
tab1, tab2, tab3 = st.tabs(["Single Gene", "Gene Panel", "Exome"], )


panel = genome.panel()
panel_list = sorted([str(panel) for panel in panel])

with tab1:
    forms.single_gene()

with tab2:
    forms.gene_panel()

with tab3:
    st.header("Exome")
    #exome(genes_list)