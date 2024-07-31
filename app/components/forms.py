import streamlit as st
from pathlib import Path
import time
from components import genome


def session_state_initialize():
    # Initialize session state variables with valid default values
    defaults = {
        'analysis': 'Single Gene',
        'assembly': "GRCh38/hg38",
        'region': None,
        'bam': [],
        'success': None,
        'exon_value': [],
        'all_exons': True
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
        

def single_gene():
    session_state_initialize()
    with st.container(border=True):
                
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
                horizontal=True
                )
        
        st.session_state.assembly = st.session_state.assembly_value
        
        # Dynamically update the genes list when assembly changes
        genes_list = sorted([str(gene) for gene in genome.assembly(st.session_state.assembly, st.session_state.analysis)[1][3].unique().tolist()]) #NEM ISTO. NÃO ATUALIZA DE FORMA DINÂMICA. ESTÁ SEMPRE A MOSTRAR O GRCh37/hg19
        # Now use the sorted list in the selectbox
        col1, col2, col3 = st.columns(3)
        with col1:
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
            st.selectbox('Select a Gene of Interest', genes_list, key="region_value", index=None,  label_visibility="collapsed", placeholder="Select a Gene of Interest")
            st.session_state.region = st.session_state.region_value
        with col2:
            st.markdown(
                    "#### Exons",
                    help=(
                        "**Please select a BAM file.**\n"
                        "- The selection of a :red[BAM file] is essential for   analyzing the sequencing data.\n"
                        "- A :red[BAM file] contains aligned sequencing reads on    the reference genome.\n"
                        "- Ensure that the selected :red[BAM file] corresponds to   the sequencing data you want to analyze."
                    )
                )
            st.multiselect("Select exons", genome.assembly(st.session_state.assembly, st.session_state.analysis)[1][4].unique().tolist(), key="exon_value", label_visibility="collapsed", placeholder="Select exons", disabled=st.session_state.all_exons)
            st.checkbox("All exons", key="all_exons")
        st.markdown(
                    "#### BAM file(s)",
                    help=(
                        "**Please select a BAM file.**\n"
                        "- The selection of a :red[BAM file] is essential for   analyzing the sequencing data.\n"
                        "- A :red[BAM file] contains aligned sequencing reads on    the reference genome.\n"
                        "- Ensure that the selected :red[BAM file] corresponds to   the sequencing data you want to analyze."
                    )
                )
        bam_files = st.session_state.cram_files
        st.multiselect('Select a BAM file', bam_files, key="bam_value", label_visibility="collapsed",placeholder="Select a BAM file")
        
        st.session_state.bam = st.session_state.bam_value
        
        # Every form must have a submit button.
        submitted = st.button("Submit", key="submit")
        if submitted:
            if st.session_state.analysis and st.session_state.assembly and st.session_state.region and st.session_state.bam:
                progress_text = "Operation in progress. Please wait."
                my_bar = st.progress(0, text=progress_text)
                for percent_complete in range(100):
                    time.sleep(0.01)
                    my_bar.progress(percent_complete + 1, text=progress_text)
                time.sleep(1)
                my_bar.empty()
                
                st.success("Form submitted")
                st.session_state.sucess = True
                time.sleep(2)
            
                st.switch_page("app_pages/results.py")
            else:
                st.warning("Form not submitted. Please fill in all fields.")

def gene_panel():
    session_state_initialize()
    with st.container(border=True):
                
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
                key="panel_assembly_value",
                label_visibility="visible",
                disabled=False,
                horizontal=True,
                index = 1
                )       
        st.markdown(
                        "#### Gene Panel of Interest",
                        help=(
                            "**Please select a Gene Panel of Interest.**\n"
                            "- The selection of a :red[Gene of Interest] is     crucial for calculating the :red[average read depth].   \n"
                            "- A :red[Gene of Interest] defines the genomic     region of interest.\n"
                            "- The :red[read depth] will be calculated  specifically for these region.\n"
                            "- Ensure that the selected :red[Gene of Interest]  corresponds to the genomic region you want to analyze.   "
                        )
                    )
        st.session_state.assembly = st.session_state.panel_assembly_value
        # Convert all elements to strings before sorting
        panels = genome.panel()['Panel Name PT (Klims)'].unique().tolist() #ISTO NÃO ESTÁ A FUNCIONAR CORRETAMENTE
        panel_list = sorted([str(panel) for panel in panels]) #NEM ISTO. NÃO ATUALIZA DE FORMA DINÂMICA. ESTÁ SEMPRE A MOSTRAR O GRCh37/hg19
        # Now use the sorted list in the selectbox
        st.selectbox('Select a Gene Panel of Interest', panel_list, key="panel_region_value", index=None, label_visibility="collapsed", placeholder="Select a Gene Panel of Interest")
        
        st.session_state.region = st.session_state.panel_region_value
        
        st.markdown(
                    "#### BAM file",
                    help=(
                        "**Please select a BAM file.**\n"
                        "- The selection of a :red[BAM file] is essential for   analyzing the sequencing data.\n"
                        "- A :red[BAM file] contains aligned sequencing reads on    the reference genome.\n"
                        "- Ensure that the selected :red[BAM file] corresponds to   the sequencing data you want to analyze."
                    )
                )
        bam_files = st.session_state.cram_files
        st.multiselect('Select a BAM file', bam_files, key="panel_bam_value", label_visibility="collapsed",placeholder="Select a BAM file")
        
        st.session_state.bam = st.session_state.panel_bam_value
        
        # Every form must have a submit button.
        panel_submitted = st.button("Submit", key="panel_submit")
        if panel_submitted:
            if st.session_state.analysis and st.session_state.assembly and st.session_state.region and st.session_state.bam:
                progress_text = "Operation in progress. Please wait."
                my_bar = st.progress(0, text=progress_text)
                for percent_complete in range(100):
                    time.sleep(0.01)
                    my_bar.progress(percent_complete + 1, text=progress_text)
                time.sleep(1)
                my_bar.empty()
                
                st.success("Form submitted")
                st.session_state.sucess = True
                time.sleep(2)
            
                st.switch_page("app_pages/results.py")
            else:
                st.warning("Form not submitted. Please fill in all fields.")