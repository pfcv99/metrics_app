import streamlit as st
import os
from pathlib import Path

def bam_working_directory():
    """Function to set the working directory for BAM files"""
    bam_folder = st.text_input('BAM files directory', value="data/mapped")
    if bam_folder:
        st.info("The selected folder is: " + bam_folder)
    return bam_folder

def bed_working_directory():
    """Function to set the working directory for BED files"""
    bed_folder = st.text_input('BED files directory', value="data/regions")
    if bed_folder:
        st.info("The selected folder is: " + bed_folder)
    return bed_folder
