import os
import glob
import pandas as pd
import streamlit as st

@st.cache_data
def find_equivalent_file(directory, pattern):
    """
    This function searches for files in a directory that match a specific pattern.
    For example, '*.BED' will find any BED file in the directory.
    """
    files = glob.glob(os.path.join(directory, pattern))
    if files:
        return files[0]  # Return the first matching file
    else:
        raise FileNotFoundError(f"No files matching pattern {pattern} found in {directory}")

@st.cache_data
def assembly(assembly, analysis):
    directories = {
        "GRCh38/hg38": 'data/regions/universal_bed/GRCh38_hg38/',
        "GRCh37/hg19": 'data/regions/universal_bed/GRCh37_hg19/'
    }

    # Define patterns for searching files
    patterns = {
        "Single Gene": "*_nochr.BED",
        "Gene Panel": "*_modif.BED",
        "Exome": "*_nochr.BED"
    }

    # Get the appropriate directory and pattern
    directory = directories.get(assembly)
    pattern = patterns.get(analysis)

    if directory and pattern:
        # Find the first matching file in the directory
        path = find_equivalent_file(directory, pattern)
        return path, pd.read_csv(path, sep='\t', header=None)
    else:
        raise ValueError("Invalid assembly or analysis type")


@st.cache_data
def panel():
    directory = 'data/regions/gene_panels/'
    pattern = "*.xlsx"

    # Find the first matching Excel file in the directory
    path = find_equivalent_file(directory, pattern)
    return pd.read_excel(path, header=0)
