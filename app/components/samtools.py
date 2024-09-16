import subprocess
import os

def depth(cram_path, bed_path, depth_dir, gene_selection=None, exon_selection=None):
    """
    Calculate the depth of coverage for specific exons of genes in a CRAM/BAM file using samtools.

    Args:
        cram_path (str): Path to the CRAM/BAM file.
        bed_path (str): Path to the Universal BED file containing exon coordinates.
        depth_dir (str): Directory to save the depth output file.
        gene_selection (list or None): List of gene names to include in the depth calculation. If None, all genes will be included.
        exon_selection (list or None): List of exon numbers to include in the depth calculation. If None, all exons will be included.

    Returns:
        None
    """
    # Ensure depth_dir is a valid directory
    if not os.path.isdir(depth_dir):
        raise ValueError(f"depth_dir '{depth_dir}' is not a valid directory. Please provide a valid directory path.")

    # Ensure the CRAM/BAM file and BED file exist
    if not os.path.isfile(cram_path):
        raise FileNotFoundError(f"CRAM/BAM file '{cram_path}' not found.")
    if not os.path.isfile(bed_path):
        raise FileNotFoundError(f"BED file '{bed_path}' not found.")

    # Extract the prefix from the CRAM/BAM file name to create the output file name
    cram_filename = os.path.basename(cram_path)
    file_prefix = os.path.splitext(cram_filename)[0]
    depth_path = os.path.join(depth_dir, f"{file_prefix}.depth")

    # Create filters for gene and exon selection
    gene_filter = gene_selection if gene_selection else ''
    exon_filter = '|'.join(map(str, exon_selection)) if exon_selection else ''

    # Awk command to filter the BED file based on gene and exon selection
    command = (
        f'awk -v gene_filter="{gene_filter}" -v exon_filter="{exon_filter}" '
        "'{if ((gene_filter == \"\" || $4 == gene_filter) && (exon_filter == \"\" || $5 ~ exon_filter)) {sub(/^chr/, \"\", $1); print}}' "
        f'{bed_path}'
    )

    # Print the awk command output for debugging
    print(f"Running awk command: {command}")
    
    # Run the awk command using subprocess with shell=True
    awk_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, text=True)
    awk_output, _ = awk_process.communicate()

    # Output the awk results for debugging
    print("AWK output:")
    print(awk_output)

    # If the awk output is empty, return early and notify the user
    if not awk_output.strip():
        print("No matching regions found in the BED file based on gene and exon filters.")
        return

    # Samtools command to compute depth
    samtools_command = ['samtools', 'depth', '-b', '-', cram_path]

    # Run the samtools command with the awk output as input
    samtools_process = subprocess.Popen(samtools_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    samtools_output, _ = samtools_process.communicate(input=awk_output)

    # Write the samtools output to the depth file
    with open(depth_path, 'w') as output_file:
        output_file.write(samtools_output)

    # Check for errors
    if awk_process.returncode != 0:
        print(f"Error executing awk command")
    if samtools_process.returncode != 0:
        print(f"Error executing samtools command")
    else:
        print(f"Command executed successfully. Output saved to {depth_path}")
