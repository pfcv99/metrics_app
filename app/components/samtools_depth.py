import subprocess
import numpy as np


def run_samtools_depth_v0(bam_path, bed_path, depth_path):
    command = f"samtools depth -b {bed_path} {bam_path} > {depth_path}"
    subprocess.run(command, shell=True)
    
    
    
    
def run_samtools_depth_v1(bam_path, bed_path, depth_path, filter_value):
    # Comando para executar samtools depth com filtro diretamente no comando awk
    depth_command = f"awk '{{if ($4 == \"{filter_value}\"){{sub(/^chr/, \"\", $1); print}}}}' '{bed_path}' | samtools depth -b - '{bam_path}' > '{depth_path}'"
    
    # Executa o comando samtools depth com o filtro aplicado diretamente no comando awk
    subprocess.run(depth_command, shell=True)



def run_samtools_depth_v2(bam_path, bed_path, depth_path, gene_name):

    # Comando para executar samtools depth com filtro diretamente no comando awk
    depth_command = f"awk -v gene={gene_name} '{{if ($4 == gene) {{sub(/^chr/, \"\", $1); print}}}}' {bed_path} | samtools depth -b - {bam_path} > {depth_path}"

    # Executa o comando samtools depth com o filtro aplicado diretamente no comando awk
    subprocess.run(depth_command, shell=True)
    
def run_samtools_depth_v2_exon(bam_path, bed_path, depth_path, gene_name, exon_selection):
    exon_filter = ','.join(map(str, exon_selection))
    depth_command = f"awk -v gene={gene_name} -v exon_filter=\"{exon_filter}\" '{{split(exon_filter, arr, \",\"); if ($4 == gene && (\"\" in arr || $5 == arr[1])) {{sub(/^chr/, \"\", $1); print}}}}' {bed_path} | samtools depth -b - {bam_path} > {depth_path}"

    
    # Executa o comando samtools depth com o filtro aplicado diretamente no comando awk
    subprocess.run(depth_command, shell=True)



def run_samtools_depth_v3(bam_path, bed_path, depth_path, gene_list):
    # Construir o comando awk para filtrar o BED com os genes da lista
    gene_list = gene_list.split(", ")
    awk_command = "awk '{if ($4 == \"" + "\" || $4 == \"".join(gene_list) + "\") print}' " + bed_path
    # Combinar o comando awk com o comando samtools depth e redirecionar a saída para o arquivo de profundidade
    depth_command = f"{awk_command} | samtools depth -b - {bam_path} > {depth_path}"
    
    # Executar o comando combinado
    subprocess.run(depth_command, shell=True)
    
def run_samtools_depth_v4(bam_path, bed_path, depth_path, gene_list):
    # Construir o comando awk para filtrar o BED com os genes da lista
    gene_list = gene_list.split(", ")
    awk_command = (
        'awk \'BEGIN { genes="' +
        ' '.join(gene_list) +
        '" } ' +
        '{split(genes, genes_array, " "); ' +
        'for (i in genes_array) { ' +
        'if ($4 == genes_array[i]) {print; next}}}' +
        '\' ' +
        bed_path
    )
    
    # Combinar o comando awk com o comando samtools depth e redirecionar a saída para o arquivo de profundidade
    depth_command = f"{awk_command} | samtools depth -b - {bam_path} > {depth_path}"
    
    # Executar o comando combinado
    subprocess.run(depth_command, shell=True)


# Function to calculate average depth, min, and max
def calculate_depth_statistics(depth_path):
    depths = []

    with open(depth_path, 'r') as file:
        for line in file:
            depth = float(line.strip().split()[2])
            depths.append(depth)

    if depths:
        average_depth = sum(depths) / len(depths)
        min_depth = min(depths)
        max_depth = max(depths)
        return round(average_depth, 2), min_depth, max_depth
    else:
        return None, None, None



# Function to count coverage at different levels
def count_coverage_singlegene(depth_path):
    bases_with_coverage = {500: 0, 100: 0, 50: 0, 30: 0, 20: 0, 15: 0, 10: 0, 1: 0}

    with open(depth_path) as file:
        lines = file.readlines()
        total_bases = len(lines)

        if total_bases == 0:
            return {f'Coverage_{cov}x(%)': None for cov in bases_with_coverage}

        for line in lines:
            fields = line.strip().split()
            depth = float(fields[2])

            for coverage, count in bases_with_coverage.items():
                if depth >= coverage:
                    bases_with_coverage[coverage] += 1

    percentage_with_coverage = {cov: (count / total_bases) * 100.0 for cov, count in bases_with_coverage.items()}
    return {f'Coverage_{cov}x(%)': percentage for cov, percentage in percentage_with_coverage.items()}


# Function to count coverage at different levels
def count_coverage_genepanel(depth_path, normalization_factors_output):
    bases_with_coverage = {500: {}, 100: {}, 50: {}, 30: {}, 20: {}, 15: {}, 10: {}, 1: {}}

    # Inicializar contadores para cada gene
    for cov_threshold in bases_with_coverage:
        for gene in normalization_factors_output:
            bases_with_coverage[cov_threshold][gene] = 0

    with open(depth_path) as file:
        lines = file.readlines()
        total_bases = len(lines)

        if total_bases == 0:
            return {f'Coverage_{cov}x(%)': {gene: None for gene in normalization_factors_output} for cov in bases_with_coverage}

        for line in lines:
            fields = line.strip().split()
            depth = float(fields[2])

            for coverage, gene_counts in bases_with_coverage.items():
                for gene, factor in normalization_factors_output.items():
                    if depth >= coverage:
                        gene_counts[gene] += 1

    coverage_results = {}

    # Calcular cobertura percentual para cada gene em cada limiar de cobertura
    for cov_threshold, gene_counts in bases_with_coverage.items():
        coverage_results[f'Coverage_{cov_threshold}x(%)'] = {}
        for gene, count in gene_counts.items():
            coverage_results[f'Coverage_{cov_threshold}x(%)'][gene] = (count / total_bases) * 100.0 * normalization_factors_output[gene]

    # Calcular cobertura total para cada gene com fator de normalização
    total_coverage = {}
    for gene, factor in normalization_factors_output.items():
        total_coverage[gene] = sum(gene_counts[gene] for gene_counts in bases_with_coverage.values()) * factor

    coverage_results['Total_Coverage(%)'] = total_coverage

    return coverage_results



def normalization_factor(assembly_file, region):
    
    max_gene_size = 0
    size_coding_global = 0
    size_coding_per_gene = {}
    normalization_factor_per_gene = {}
    region = region.split(", ")
    with open(assembly_file, 'r') as file:
        for gene in region:
            size_coding = 0
            file.seek(0)  # Reseta o ponteiro do arquivo para o início
            for line in file:
                fields = line.strip().split('\t')
                # Supondo que o nome do gene esteja na primeira coluna
                if fields[3] == gene:
                    size = int(fields[6])
                    size_coding += size
                    if size > max_gene_size:
                        max_gene_size = size
            size_coding_global += size_coding
            size_coding_per_gene[gene] = size_coding

    for gene, size in size_coding_per_gene.items():
        normalization_factor_per_gene[gene] = size / max_gene_size

    return max_gene_size, size_coding_per_gene, normalization_factor_per_gene, size_coding_global

def size_gene(assembly_file, region):
    
    max_gene_size = 0
    size_coding_per_gene = {}
    region = region.split(", ")
    with open(assembly_file, 'r') as file:
        for gene in region:
            size_coding = 0
            file.seek(0)  # Reseta o ponteiro do arquivo para o início
            for line in file:
                fields = line.strip().split('\t')
                # Supondo que o nome do gene esteja na primeira coluna
                if fields[3] == gene:
                    size = int(fields[6])
                    size_coding += size
                    if size > max_gene_size:
                        max_gene_size = size
            size_coding_per_gene[gene] = size_coding

    per_gene_size_output = {gene: size for gene, size in size_coding_per_gene.items()}
    
    return per_gene_size_output


def get_size_coding_per_gene(assembly_file, region):
    size_coding_per_gene = {}
    region = region.split(", ")
    with open(assembly_file, 'r') as file:
        for gene in region:
            size_coding = 0
            file.seek(0)  # Reseta o ponteiro do arquivo para o início
            for line in file:
                fields = line.strip().split('\t')
                # Supondo que o nome do gene esteja na primeira coluna
                if fields[3] == gene:
                    size = int(fields[6])
                    size_coding += size
            size_coding_per_gene[gene] = size_coding

    return size_coding_per_gene

print(get_size_coding_per_gene("data/regions/genome_exons/MANE_hg38_exons_modif_MANE_with_difference_chr.bed", "PKD1,BRCA1"))



def rpkm(counts, lengths):
    #https://www.oreilly.com/library/view/elegant-scipy/9781491922927/ch01.html
    """Calculate reads per kilobase transcript per million reads.

    RPKM = (10^9 * C) / (N * L)

    Where:
    C = Number of reads mapped to a gene
    N = Total mapped reads in the experiment
    L = Exon length in base pairs for a gene

    Parameters
    ----------
    counts: array, shape (N_genes, N_samples)
        RNAseq (or similar) count data where columns are individual samples
        and rows are genes.
    lengths: array, shape (N_genes,)
        Gene lengths in base pairs in the same order
        as the rows in counts.

    Returns
    -------
    normed : array, shape (N_genes, N_samples)
        The RPKM normalized counts matrix.
    """
    N = np.sum(counts, axis=0)  # sum each column to get total reads per sample
    L = lengths
    C = counts

    normed = 1e9 * C / (N[np.newaxis, :] * L[:, np.newaxis])

    return(normed)

