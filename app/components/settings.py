# metrics_app/app/components/settings.py

import streamlit as st
import os
from pathlib import Path

def bam_working_directory():
    """Function to set the working directory for BAM files"""
    bam_folder = st.text_input('BAM files directory', value="/mnt/DADOS/Biologia Molecular/15-NGS/PCRMultiplex/3-Analise/2024/Casos Somático/BAM", label_visibility="collapsed",placeholder="Paste the path for BAM directory")

    return bam_folder

def bed_working_directory():
    """Function to set the working directory for BED files"""
    bed_folder = st.text_input('BED files directory', value="/mnt/DADOS/Biologia Molecular/15-NGS/PCRMultiplex/3-Analise/2024/Casos Somático/BED", label_visibility="collapsed",placeholder="Paste the path for BED directory")

    return bed_folder

def bed_bam_map_file():
    """Function to set the working directory for BED files"""
    bed_bam_map_file = st.text_input('BED files directory', value="/mnt/DADOS/Biologia Molecular/15-NGS/PCRMultiplex/3-Analise/2024/Casos Somático/Casos2.csv", label_visibility="collapsed",placeholder="Paste the path for BED_BAM_Map file")

    return bed_bam_map_file
