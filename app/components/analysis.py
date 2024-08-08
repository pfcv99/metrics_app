import streamlit as st
from components import samtools, genome, s3, samtools_depth_obsolete

def run_single_gene():
    #samtools.depth(s3.cram(), genome.assembly(st.session_state.assembly, st.session_state.analysis), 'data/depth', st.session_state.region, st.session_state.exon)
    
    samtools_depth_obsolete.run_samtools_depth_v0(s3.cram(), 'data/regions/single_gene/BRAF_15.bed', 'data/depth')