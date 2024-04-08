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
    
    
    
def run_samtools_depth_v3(bam_path, bed_path, depth_path, gene_list):
    # Comando para executar samtools depth com filtro diretamente no comando awk
    depth_command = f"samtools depth -b {bed_path} {bam_path} > {depth_path}"
    
    for gene_name in gene_list:
        # Acrescentar ao comando awk para filtrar o gene atual, adicionar o nome do gene como uma coluna e anexar ao arquivo de profundidade
        depth_command += f" && awk -v gene={gene_name} '{{if ($4 == gene) {{print $0, gene}}}}' {bed_path} | samtools depth -b - {bam_path} | awk -v gene={gene_name} '{{print $0, gene}}' >> {depth_path}"
    
    # Executa o comando samtools depth com o filtro aplicado diretamente no comando awk
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
def count_coverage(depth_path):
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