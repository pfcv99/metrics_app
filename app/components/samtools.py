import subprocess
import streamlit as st
import os

def depth(cram_path, bed_path, depth_dir='data/depth', gene_selection=None, exon_selection=None):
    """
    Calculate the depth of coverage for specific exons of genes in a CRAM/BAM file using samtools.

    Args:
        cram_path (str): Path to the CRAM/BAM file.
        bed_path (str): Path to the Universal BED file containing exon coordinates.
        depth_dir (str, optional): Directory to save the depth output file (optional if storing in session state).
        gene_selection (list or None): List of gene names to include in the depth calculation.
        exon_selection (list or None): List of exon numbers to include in the depth calculation.

    Returns:
        None
    """
    if not os.path.isfile(cram_path) or not os.path.isfile(bed_path):
        raise FileNotFoundError("Invalid file path.")

    # Convert gene_selection to a list if it's a string
    if isinstance(gene_selection, str):
        gene_selection = [gene_selection]

    # Convert exon_selection to a list of strings if it's a list of numbers
    if exon_selection is not None:
        exon_selection = list(map(str, exon_selection))  # Convert exon numbers to strings

    # Read the BED file and filter it using Python logic
    filtered_bed_lines = []
    
    with open(bed_path, 'r') as bed_file:
        for line in bed_file:
            columns = line.strip().split('\t')
            
            # Ensure the BED file has at least 6 columns (chr, start, end, gene, exon, size)
            if len(columns) < 6:
                continue
            
            chrom, start, end, gene, exon, size = columns[0], columns[1], columns[2], columns[3], columns[4], columns[5]

            # Apply gene and exon filters (exact match)
            if (gene_selection is None or gene in gene_selection) and (exon_selection is None or exon in exon_selection):
                filtered_bed_lines.append(f"{chrom}\t{start}\t{end}\t{gene}\t{exon}\t{size}\n")

    # Check if any filtered BED content was found
    if not filtered_bed_lines:
        raise ValueError("No matching regions found for the provided gene or exon selection.")

    # Store filtered BED content in Streamlit session state
    st.session_state.filtered_bed = ''.join(filtered_bed_lines)

    # Run samtools depth using filtered BED content from session state
    samtools_command = ['samtools', 'depth', '-b', '-', cram_path]
    samtools_process = subprocess.Popen(samtools_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    samtools_output, _ = samtools_process.communicate(input=st.session_state.filtered_bed)

    # Store samtools output (.depth content) in Streamlit session state
    st.session_state.depth_output = samtools_output

    if depth_dir:
        # Define the output depth file path based on the CRAM/BAM file name
        depth_path = os.path.join(depth_dir, f"{os.path.splitext(os.path.basename(cram_path))[0]}.depth")
        with open(depth_path, 'w') as output_file:
            output_file.write(samtools_output)
