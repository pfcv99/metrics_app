import subprocess

def depth(cram_path, bed_path, depth_path, gene_selection=None, exon_selection=None):
    """
    Calculate the depth of coverage for specific exons of genes in a cram file using samtools.

    Args:
        cram_path (str): Path to the cram file.
        bed_path (str): Path to the Universal BED file containing exon coordinates.
        depth_path (str): Path to save the depth output.
        gene_selection (list or None): List of gene names to include in the depth calculation. If None, all genes will be included.
        exon_selection (list or None): List of exon numbers to include in the depth calculation. If None, all exons will be included.

    Returns:
        None
    """
    #gene_filter = ','.join(map(str, gene_selection)) if gene_selection else ''
    gene_filter = gene_selection if gene_selection else ''
    print(gene_filter)
    exon_filter = ','.join(map(str, exon_selection)) if exon_selection else ''
    print(exon_filter)
    
    awk_command = f'awk -v gene_filter={gene_filter} -v exon_filter={exon_filter} \'{{split(exon_filter, arr, ","); if (($4 == gene_filter || gene_filter == "") && ("" in arr || $5 == arr[1])) {{sub(/^chr/, "", $1); print}}}}\' {bed_path}'
    samtools_command = f'samtools depth -b - {cram_path} > {depth_path}'
    
    print(subprocess.run(f'{awk_command} | {samtools_command}', shell=True))


