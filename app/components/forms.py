import streamlit as st
from pathlib import Path
import time
from components import genome



# Initialize session state variables with valid default values
if 'analysis' not in st.session_state:
    st.session_state.analysis = 'Single Gene'  # Initialize with the first valid option
    
if 'assembly' not in st.session_state:
    st.session_state.assembly = "GRCh38/hg38"  # Initialize with the first valid option

if 'region' not in st.session_state:
    st.session_state.region = None
    
if 'bam' not in st.session_state:
    st.session_state.bam = []

def session_state_update():
    st.session_state.assembly = st.session_state.assembly_value
    st.session_state.region = st.session_state.region_value
    st.session_state.bam = st.session_state.bam_value

def single_gene():

    with st.container():
                
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
                key="assembly_value",
                label_visibility="visible",
                disabled=False,
                horizontal=True,
                index = None
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
        # Convert all elements to strings before sorting
        genes = genome.assembly(st.session_state.assembly, st.session_state.analysis)[1][3].unique().tolist() #ISTO NÃO ESTÁ A FUNCIONAR CORRETAMENTE
        genes_list = sorted([str(gene) for gene in genes]) #NEM ISTO. NÃO ATUALIZA DE FORMA DINÂMICA. ESTÁ SEMPRE A MOSTRAR O GRCh37/hg19
        # Now use the sorted list in the selectbox
        st.selectbox('Select a Gene of Interest', genes_list, key="region_value", index=None, label_visibility="collapsed", placeholder="Select a Gene of Interest")
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
        st.multiselect('Select a BAM file', bam_files, key="bam_value", label_visibility="collapsed",placeholder="Select a BAM file")
        # Every form must have a submit button.
        submitted = st.button("Submit", on_click=session_state_update)
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

def gene_panel(panel_list):
    st.write(panel_list)