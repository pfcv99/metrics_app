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
    
    
    

def run_samtools_depth_v3(bam_path, bed_path, depth_dir, gene_list):
    for gene_name in gene_list:
        # Comando para executar samtools depth com filtro diretamente no comando awk
        depth_command = f"awk -v gene={gene_name} '{{if ($4 == gene) {{sub(/^chr/, \"\", $1); print}}}}' {bed_path} | samtools depth -b - {bam_path} > {depth_dir}"

        # Executa o comando samtools depth com o filtro aplicado diretamente no comando awk
        subprocess.run(depth_command, shell=True)




