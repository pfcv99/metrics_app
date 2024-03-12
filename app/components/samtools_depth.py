import subprocess

def run_samtools_depth(bam_path, bed_path, depth_path, filter_value):
    # Comando para executar samtools depth com filtro diretamente no comando awk
    depth_command = f"awk '{{if ($4 == \"{filter_value}\"){{sub(/^chr/, \"\", $1); print}}}}' '{bed_path}' | samtools depth -b - '{bam_path}' > '{depth_path}'"
    
    # Executa o comando samtools depth com o filtro aplicado diretamente no comando awk
    subprocess.run(depth_command, shell=True)





def run_samtools_depth2(bam_path, bed_path, depth_path):
    command = f"samtools depth -b {bed_path} {bam_path} > {depth_path}"
    subprocess.run(command, shell=True)