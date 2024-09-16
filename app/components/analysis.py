import streamlit as st
from components import samtools, genome, s3, samtools_depth_obsolete, bam_cram

def run_single_gene():
    bed_path = genome.assembly(st.session_state.assembly, st.session_state.analysis)
    if isinstance(bed_path, tuple):
        bed_path = bed_path[0]
    samtools.depth('data/mapped/1110366_PKD1.bam', bed_path, 'data/depth', st.session_state.region, st.session_state.exon)
    print(st.session_state.bam_cram_value)
    print(genome.assembly(st.session_state.assembly, st.session_state.analysis))
    print(st.session_state.region)
    print(st.session_state.exon)
    #samtools_depth_obsolete.run_samtools_depth_v0(s3.cram(), 'data/regions/single_gene/BRAF_15.bed', 'data/depth')