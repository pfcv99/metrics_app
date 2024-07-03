import streamlit as st
from components import genome
from components import streamlit_page_config
from pathlib import Path

# Set Streamlit page configuration
streamlit_page_config.set_page_configuration()

sidebar_logo = "data/img/unilabs_logo.png"
main_body_logo = "data/img/thumbnail_image001.png"
st.logo(sidebar_logo, icon_image=main_body_logo)


# Initialize session state variables with valid default values
if 'analysis' not in st.session_state:
    st.session_state['analysis'] = 'Single Gene'  # Initialize with the first valid option
    
if 'assembly' not in st.session_state:
    st.session_state['assembly'] = "GRCh37/hg19"  # Initialize with the first valid option

    
st.title("Metrics calculator\n")


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
        st.selectbox('Select a Gene of Interest', genes_list, key="gene", index=None, label_visibility="collapsed", placeholder="Select a Gene of Interest")
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
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.success("Form submitted")
            st.write(st.session_state.assembly)
            st.write(st.session_state.gene)
            st.write(st.session_state.bam)
            st.page_link("app_pages/results.py", label="Results", icon=":material/table_chart_view:")


def gene_panel(panel_list):
    with st.form("gene_panel", clear_on_submit=True):
                
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
                        "#### Gene Panel",
                        help=(
                            "**Please select a Gene Panel.**\n"
                            "- The selection of a :red[Gene Panel] is crucial for calculating the :red[average read depth].\n"
                            "- A :red[Gene Panel] defines the genomic region of interest.\n"
                            "- The :red[read depth] will be calculated  specifically for these region.\n"
                            "- Ensure that the selected :red[Gene Panel]  corresponds to the genomic region you want to analyze.   "
                        )
                    )

        # Now use the sorted list in the selectbox
        st.selectbox('Select a Gene Panel', panel_list, key="gene", index=None, label_visibility="collapsed", placeholder="Select a Gene of Interest")
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
        st.multiselect('Select a BAM file', bam_files, key="bam2", label_visibility="collapsed",placeholder="Select a BAM file")
        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.success("Form submitted")
            st.write(st.session_state.assembly)
            st.write(st.session_state.gene)
            st.write(st.session_state.bam)

def exome(genes_list):
    with st.form("gene_panel", clear_on_submit=True):
                
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
                        "#### Gene Panel",
                        help=(
                            "**Please select a Gene Panel.**\n"
                            "- The selection of a :red[Gene Panel] is crucial for calculating the :red[average read depth].\n"
                            "- A :red[Gene Panel] defines the genomic region of interest.\n"
                            "- The :red[read depth] will be calculated  specifically for these region.\n"
                            "- Ensure that the selected :red[Gene Panel]  corresponds to the genomic region you want to analyze.   "
                        )
                    )

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
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.success("Form submitted")
            st.write(st.session_state.assembly)
            st.write(st.session_state.gene)
            st.write(st.session_state.bam)
            


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
tab1, tab2, tab3 = st.tabs(["Single Gene", "Gene Panel", "Exome"])



# Convert all elements to strings before sorting
genes = genome.assembly(st.session_state.assembly, st.session_state.analysis)[1][3].unique().tolist()
genes_list = sorted([str(gene) for gene in genes])

panel = genome.panel()
panel_list = sorted([str(panel) for panel in panel])
print(panel_list)
with tab1:
    st.header("Single Gene")
    single_gene(genes_list)

with tab2:
    st.header("Gene Panel")
    #gene_panel(panel_list)

with tab3:
    st.header("Exome")
    #exome(genes_list)