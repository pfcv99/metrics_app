import streamlit as st
from components import samtools, genome
def run_single_gene():
    bed_path = genome.assembly(st.session_state.assembly, st.session_state.analysis)
    if isinstance(bed_path, tuple):
        bed_path = bed_path[0]
    samtools.depth(st.session_state.bam_cram[st.session_state.bam_cram_value[0]], bed_path, 'data/depth', st.session_state.region, st.session_state.exon)

def run_gene_panel():
    bed_path = genome.assembly(st.session_state.assembly, st.session_state.analysis)
    if isinstance(bed_path, tuple):
        bed_path = bed_path[0]
    samtools.depth(st.session_state.bam_cram[st.session_state.bam_cram_panel[0]], bed_path, 'data/depth', st.session_state.region, st.session_state.exon)

def run_exome():
    bed_path = genome.assembly(st.session_state.assembly, st.session_state.analysis)
    if isinstance(bed_path, tuple):
        bed_path = bed_path[0]
    samtools.depth(st.session_state.bam_cram[st.session_state.bam_cram_value_exome[0]], bed_path, 'data/depth', "", "")