def coverage(depth_file, genes=None, exons=None):
    """
    Calculate the coverage at different levels from a samtools depth file.

    Args:
        depth_file (str): Path to the samtools depth file.
        genes (str or list): Optional. Gene(s) to calculate coverage for.
        exons (str or list): Optional. Exon(s) to calculate coverage for.

    Returns:
        dict: A dictionary containing the coverage at different levels.
    """
    coverage_levels = [500, 100, 50, 30, 20, 15, 10, 1]
    coverage_dict = {f'Coverage_{cov}x(%)': 0 for cov in coverage_levels}
    gene_coverage_dict = {}
    exon_coverage_dict = {}

    with open(depth_file) as file:
        lines = file.readlines()
        total_bases = len(lines)

        if total_bases == 0:
            return coverage_dict, gene_coverage_dict, exon_coverage_dict

        for line in lines:
            fields = line.strip().split()
            depth = float(fields[2])

            if genes is not None:
                gene_name = fields[0]
                if isinstance(genes, str):
                    genes = [genes]
                if gene_name not in genes:
                    continue

                if gene_name not in gene_coverage_dict:
                    gene_coverage_dict[gene_name] = coverage_dict.copy()

            if exons is not None:
                exon_name = fields[1]
                if isinstance(exons, str):
                    exons = [exons]
                if exon_name not in exons:
                    continue

                if exon_name not in exon_coverage_dict:
                    exon_coverage_dict[exon_name] = coverage_dict.copy()

            for coverage in coverage_levels:
                if depth >= coverage:
                    coverage_dict[f'Coverage_{coverage}x(%)'] += 1
                    if gene_name in gene_coverage_dict:
                        gene_coverage_dict[gene_name][f'Coverage_{coverage}x(%)'] += 1
                    if exon_name in exon_coverage_dict:
                        exon_coverage_dict[exon_name][f'Coverage_{coverage}x(%)'] += 1

        coverage_dict = {key: (value / total_bases) * 100.0 for key, value in coverage_dict.items()}
        gene_coverage_dict = {gene: {key: (value / total_bases) * 100.0 for key, value in cov_dict.items()} for gene, cov_dict in gene_coverage_dict.items()}
        exon_coverage_dict = {exon: {key: (value / total_bases) * 100.0 for key, value in cov_dict.items()} for exon, cov_dict in exon_coverage_dict.items()}

    return coverage_dict, gene_coverage_dict, exon_coverage_dict


def average_read_depth(depth_file, genes=None, exons=None):
    depths = []
    with open(depth_file, 'r') as file:
        for line in file:
            fields = line.strip().split()
            depth = float(fields[2])
            gene_name = fields[0]
            exon_name = fields[1]

            if genes is not None:
                if isinstance(genes, str):
                    genes = [genes]
                if gene_name not in genes:
                    continue

            if exons is not None:
                if isinstance(exons, str):
                    exons = [exons]
                if exon_name not in exons:
                    continue

            depths.append(depth)

    if depths:
        average_depth = sum(depths) / len(depths)
        min_depth = min(depths)
        max_depth = max(depths)
        return round(average_depth, 2), min_depth, max_depth

def coverage_nucleotide(depth_file, genes=None, exons=None):
    """
    Calculate the coverage at different levels from a samtools depth file.

    Args:
        depth_file (str): Path to the samtools depth file.
        genes (str or list): Optional. Gene(s) to calculate coverage for.
        exons (str or list): Optional. Exon(s) to calculate coverage for.

    Returns:
        dict: A dictionary containing the coverage at different levels.
    """
    coverage_dict = {}
    gene_coverage_dict = {}
    exon_coverage_dict = {}

    with open(depth_file) as file:
        lines = file.readlines()
        total_bases = len(lines)

        if total_bases == 0:
            return coverage_dict, gene_coverage_dict, exon_coverage_dict

        for line in lines:
            fields = line.strip().split()
            gene_name = fields[0]
            exon_name = fields[1]

            if genes is not None:
                if isinstance(genes, str):
                    genes = [genes]
                if gene_name not in genes:
                    continue

                if gene_name not in gene_coverage_dict:
                    gene_coverage_dict[gene_name] = 0

            if exons is not None:
                if isinstance(exons, str):
                    exons = [exons]
                if exon_name not in exons:
                    continue

                if exon_name not in exon_coverage_dict:
                    exon_coverage_dict[exon_name] = 0

            if gene_name in gene_coverage_dict:
                gene_coverage_dict[gene_name] += 1
            if exon_name in exon_coverage_dict:
                exon_coverage_dict[exon_name] += 1

        coverage_dict['Total_Nucleotides'] = total_bases
        coverage_dict['Gene_Coverage'] = gene_coverage_dict
        coverage_dict['Exon_Coverage'] = exon_coverage_dict

    return coverage_dict
