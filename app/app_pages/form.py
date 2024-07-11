import streamlit as st
from components import genome
from components import streamlit_page_config
from pathlib import Path
import time

# Set Streamlit page configuration
streamlit_page_config.set_page_configuration()

sidebar_logo = "data/img/unilabs_logo.png"
main_body_logo = "data/img/thumbnail_image001.png"
st.logo(sidebar_logo, icon_image=main_body_logo)


# Initialize session state variables with valid default values
if 'analysis' not in st.session_state:
    st.session_state.analysis = 'Single Gene'  # Initialize with the first valid option
    
if 'assembly' not in st.session_state:
    st.session_state.assembly = "GRCh37/hg19"  # Initialize with the first valid option

if 'region' not in st.session_state:
    st.session_state.region = None
    
if 'bam' not in st.session_state:
    st.session_state.bam = []

st.title("Metrics calculator\n")

def session_state_update():
    st.session_state.assembly = st.session_state.assembly
    st.session_state.region = st.session_state.region
    st.session_state.bam = st.session_state.bam

def single_gene(genes_list):

    with st.form("form", clear_on_submit=True):
                
        st.markdown(
                    "#### Genome Assembly",
                    help=(
                        "**Please select the genome assembly.**\n"
                        "- The selection of a :red[genome assembly] is crucial for analyzing the sequencing data.\n"
                        "- A :red[genome assembly] defines the reference genome used for aligning the sequencing reads.\n"
                        "- Ensure that the selected :red[genome assembly] corresponds to the reference genome used for aligning the sequencing reads."
                    )
                )
        st.radio(
                "Select an option",
                ["GRCh37/hg19", "GRCh38/hg38"],
                key="assembly",
                label_visibility="visible",
                disabled=False,
                horizontal=True
                )       
        st.markdown(
                        "#### Gene of Interest",
                        help=(
                            "**Please select a Gene of Interest.**\n"
                            "- The selection of a :red[Gene of Interest] is     crucial for calculating the :red[average read depth].   \n"
                            "- A :red[Gene of Interest] defines the genomic     region of interest.\n"
                            "- The :red[read depth] will be calculated  specifically for these region.\n"
                            "- Ensure that the selected :red[Gene of Interest]  corresponds to the genomic region you want to analyze.   "
                        )
                    )

        # Now use the sorted list in the selectbox
        st.selectbox('Select a Gene of Interest', genes_list, key="region", index=None, label_visibility="collapsed", placeholder="Select a Gene of Interest")
        st.markdown(
                    "#### BAM file",
                    help=(
                        "**Please select a BAM file.**\n"
                        "- The selection of a :red[BAM file] is essential for   analyzing the sequencing data.\n"
                        "- A :red[BAM file] contains aligned sequencing reads on    the reference genome.\n"
                        "- Ensure that the selected :red[BAM file] corresponds to   the sequencing data you want to analyze."
                    )
                )
        bam_files = [f.name for f in Path("./data/mapped").iterdir() if f.suffix == ".bam" or f.suffix == ".cram"]
        st.multiselect('Select a BAM file', bam_files, key="bam", label_visibility="collapsed",placeholder="Select a BAM file")
        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit", on_click=session_state_update)
        if submitted:
            progress_text = "Operation in progress. Please wait."
            my_bar = st.progress(0, text=progress_text)
            for percent_complete in range(100):
                time.sleep(0.01)
                my_bar.progress(percent_complete + 1, text=progress_text)
            time.sleep(1)
            my_bar.empty()
            
            st.success("Form submitted")
            time.sleep(2)
            
            st.switch_page("app_pages/results.py")


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



# Convert all elements to strings before sorting
genes = genome.assembly(st.session_state.assembly, st.session_state.analysis)[1][3].unique().tolist()
genes_list = sorted([str(gene) for gene in genes])

panel = genome.panel()
panel_list = sorted([str(panel) for panel in panel])

with tab1:
    single_gene(genes_list)

with tab2:
    st.header("Gene Panel")
    #gene_panel(panel_list)

with tab3:
    st.header("Exome")
    #exome(genes_list)