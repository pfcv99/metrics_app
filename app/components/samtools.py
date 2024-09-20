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

    # Build awk command to filter BED file
    gene_filter = gene_selection or ''
    exon_filter = '|'.join(map(str, exon_selection)) if exon_selection else ''
    command = (
        f'awk -v gene_filter="{gene_filter}" -v exon_filter="{exon_filter}" '
        "'{if ((gene_filter == \"\" || $4 == gene_filter) && (exon_filter == \"\" || $5 ~ exon_filter)) "
        "{sub(/^chr/, \"\", $1); print}}' "
        f'{bed_path}'
    )

    # Run awk command and capture output
    awk_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, text=True)
    awk_output, _ = awk_process.communicate()

    if not awk_output.strip():
        print("No matching regions found.")
        return

    # Store filtered BED content in Streamlit session state
    st.session_state.filtered_bed = awk_output

    # Run samtools depth using filtered BED content from session state
    samtools_command = ['samtools', 'depth', '-b', '-', cram_path]
    samtools_process = subprocess.Popen(samtools_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    samtools_output, _ = samtools_process.communicate(input=st.session_state.filtered_bed)

    # Store samtools output (.depth content) in Streamlit session state
    st.session_state.depth_output = samtools_output

    if depth_dir:
        depth_path = os.path.join(depth_dir, f"{os.path.splitext(os.path.basename(cram_path))[0]}.depth")
        with open(depth_path, 'w') as output_file:
            output_file.write(samtools_output)
        print(f"Output also saved to {depth_path}")

    print("Depth data stored in session state.")

