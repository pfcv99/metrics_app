import subprocess


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
    exon_filter = exon_selection.split(", ")
    depth_command = f"awk -v gene={gene_name} -v exon='{exon_filter}' '{{if ($4 == gene && ($5 in exon || exon == \"\")) {{sub(/^chr/, \"\", $1); print}}}}' {bed_path} | samtools depth -b - {bam_path} > {depth_path}"
    
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
def count_coverage(depth_path, normalization_factors_output):
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

    # Multiplicar el coverage de cada gen por su respectivo factor de normalización
    percentage_with_coverage = {cov: (count / total_bases) * 100.0 * 100* normalization_factors_output[gene] for cov, count in bases_with_coverage.items() for gene in normalization_factors_output}
    
    return {f'Coverage_{cov}x(%)': percentage for cov, percentage in percentage_with_coverage.items()}



def normalization_factor(assembly_file, region):
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
                    size_coding += int(fields[6])
            size_coding_global += size_coding
            size_coding_per_gene[gene] = size_coding

    for gene, size in size_coding_per_gene.items():
        normalization_factor_per_gene[gene] = size / size_coding_global

    return size_coding_global, size_coding_per_gene, normalization_factor_per_gene

