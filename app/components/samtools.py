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
        exon_selection (list or None): List of exon numbers to include in the depth calculation for each gene.

    Returns:
        None
    """
    # Initialize session state attributes if they don't exist
    if 'depth_output' not in st.session_state:
        st.session_state.depth_output = {}
    
    if 'filtered_bed' not in st.session_state:
        st.session_state.filtered_bed = ""

    # Check if paths to the CRAM/BAM and BED files are valid
    if not os.path.isfile(cram_path) or not os.path.isfile(bed_path):
        st.error("Invalid file path provided for CRAM/BAM or BED file.")
        return  # Stop execution if the paths are invalid

    # Convert gene_selection to a list if it's a string
    if isinstance(gene_selection, str):
        gene_selection = [gene_selection]

    # Convert exon_selection to a list of strings if it's a list of numbers
    if exon_selection is not None:
        exon_selection = list(map(str, exon_selection))  # Convert exon numbers to strings

    # If no gene or exon selection is provided, use the original BED file
    if gene_selection is None and exon_selection is None:
        try:
            # Load the original BED content directly
            with open(bed_path, 'r') as bed_file:
                st.session_state.filtered_bed = bed_file.read()  # Store original BED content in session state
        except Exception as e:
            st.error(f"Error loading BED file: {e}")
            return  # Stop execution in case of file read error
    else:
        # Otherwise, filter the BED file based on the gene and exon selection
        filtered_bed_lines = []
        try:
            with open(bed_path, 'r') as bed_file:
                for line in bed_file:
                    columns = line.strip().split('\t')

                    # Ensure the BED file has at least 6 columns (chr, start, end, gene, exon, size)
                    if len(columns) < 6:
                        continue

                    chrom, start, end, gene, exon, size = columns[0], columns[1], columns[2], columns[3], columns[4], columns[5]

                    # Apply gene filter (multiple genes allowed)
                    if gene_selection is None or gene in gene_selection:
                        # Apply exon filter: if exon_selection is None, include all exons for the gene
                        if exon_selection is None or exon in exon_selection:
                            filtered_bed_lines.append(f"{chrom}\t{start}\t{end}\t{gene}\t{exon}\t{size}\n")

            # Check if any filtered BED content was found
            if not filtered_bed_lines:
                st.info("No matching regions found for the provided gene or exon selection.")
                return  # Stop execution if no matching regions found

            # Store filtered BED content in Streamlit session state
            st.session_state.filtered_bed = ''.join(filtered_bed_lines)

        except Exception as e:
            st.error(f"Error filtering BED file: {e}")
            return  # Stop execution in case of file processing error

    # Create a unique key for the output based on the CRAM/BAM file name
    output_key = os.path.splitext(os.path.basename(cram_path))[0]

    # Run samtools depth using the BED content (either original or filtered) from session state
    try:
        samtools_command = ['samtools', 'depth', '-b', '-', cram_path]
        samtools_process = subprocess.Popen(samtools_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        samtools_output, _ = samtools_process.communicate(input=st.session_state.filtered_bed)

        # Check if samtools_output is empty
        if not samtools_output.strip():  # If no output is found
            
            # Remove "chr" prefix from the chromosome names in the original BED content
            modified_bed_lines = []
            for line in st.session_state.filtered_bed.splitlines():
                if line.strip():  # Only process non-empty lines
                    columns = line.strip().split('\t')
                    # Replace "chr" in the chromosome name, if present
                    if columns[0].startswith("chr"):
                        columns[0] = columns[0][3:]  # Remove "chr" prefix
                    modified_bed_lines.append('\t'.join(columns))

            # Prepare the modified BED content for samtools
            modified_bed_content = '\n'.join(modified_bed_lines)

            samtools_process = subprocess.Popen(samtools_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            samtools_output, _ = samtools_process.communicate(input=modified_bed_content)

        # Check if samtools_output is still empty
        if not samtools_output.strip():  # If still no output
            return  # Stop execution if no data is returned

        # Store samtools output (.depth content) in Streamlit session state as a dictionary
        st.session_state.depth_output[output_key] = samtools_output

        # Optionally, save the depth data to a file
        if depth_dir:
            # Ensure the directory exists
            os.makedirs(depth_dir, exist_ok=True)
            
            # Define the output depth file path based on the CRAM/BAM file name
            depth_path = os.path.join(depth_dir, f"{output_key}.depth")
            with open(depth_path, 'w') as output_file:
                output_file.write(samtools_output)

    except Exception as e:
        st.error(f"Error running samtools depth: {e}")
        return  # Stop execution in case of samtools error
