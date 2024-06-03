import streamlit as st
from components import genome_regions

sidebar_logo = "data/img/unilabs_logo.png"
main_body_logo = "data/img/thumbnail_image001.png"
st.logo(sidebar_logo, icon_image=main_body_logo)


# Initialize session state variables with valid default values
if 'analysis' not in st.session_state:
    st.session_state['analysis'] = 'Single Gene'  # Initialize with the first valid option
    
if 'assembly' not in st.session_state:
    st.session_state['assembly'] = "GRCh37/hg19"  # Initialize with the first valid option

    
st.markdown(
            "## **Average read depth and coverage calculator**\n"
        )

def form():

    with st.form("form", clear_on_submit=True):
                
        st.markdown(
                    "#### Genome Assembly",
                    help=(
                        "**Please select the genome assembly.**\n"
                        "- The selection of a :red[genome assembly] is crucial  for analyzing the sequencing data.\n"
                        "- A :red[genome assembly] defines the reference genome     used for aligning the sequencing reads.\n"
                        "- Ensure that the selected :red[genome assembly]   corresponds to the reference genome used for aligning the     sequencing reads."
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
        st.selectbox('Select a Gene of Interest', sorted(genome_regions.genome_assembly(st.session_state.assembly, st.session_state.analysis)[1][3].unique().tolist()), key="gene", index=None, label_visibility="collapsed",placeholder="Select a Gene of Interest")

        
        
        st.markdown(
                    "#### BAM file",
                    help=(
                        "**Please select a BAM file.**\n"
                        "- The selection of a :red[BAM file] is essential for   analyzing the sequencing data.\n"
                        "- A :red[BAM file] contains aligned sequencing reads on    the reference genome.\n"
                        "- Ensure that the selected :red[BAM file] corresponds to   the sequencing data you want to analyze."
                    )
                )
        st.multiselect('Select a BAM file', ["x","y","z"], key="bam", label_visibility="collapsed",placeholder="Select a BAM file")


    

       # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
    if submitted:
        st.write("Form submitted")
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

with tab1:
    form()
























