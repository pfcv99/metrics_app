import subprocess
import os

def depth(cram_path, bed_path, depth_dir, gene_selection=None, exon_selection=None):
    """
    Calculate the depth of coverage for specific exons of genes in a CRAM/BAM file using samtools.

    Args:
        cram_path (str): Path to the CRAM/BAM file.
        bed_path (str): Path to the Universal BED file containing exon coordinates.
        depth_dir (str): Directory to save the depth output file.
        gene_selection (list or None): List of gene names to include in the depth calculation.
        exon_selection (list or None): List of exon numbers to include in the depth calculation.

    Returns:
        None
    """
    if not os.path.isdir(depth_dir) or not os.path.isfile(cram_path) or not os.path.isfile(bed_path):
        raise FileNotFoundError("Invalid directory or file path.")

    # Output file path
    depth_path = os.path.join(depth_dir, f"{os.path.splitext(os.path.basename(cram_path))[0]}.depth")

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

    # Run samtools depth using filtered BED output
    samtools_command = ['samtools', 'depth', '-b', '-', cram_path]
    samtools_process = subprocess.Popen(samtools_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    samtools_output, _ = samtools_process.communicate(input=awk_output)

    # Write samtools output to file
    with open(depth_path, 'w') as output_file:
        output_file.write(samtools_output)

    print(f"Output saved to {depth_path}")
