import pandas as pd
import streamlit as st
from components import logo

logo.add_logo()

# Criar o DataFrame
data = {
    'Date': ['06/03/2024'] * 4,
    'BED_File': ['Oncorisk_96genes.bed'] * 4,
    'BAM_File': ['1106179.bam'] * 4,
    'Gene': ['AIP', 'ALK', 'APC', 'ATM'],
    'Average_Read_Depth': [1, 1, 1, 1],
    'Coverage_500x(%)': [3, 3, 3, 3],
    'Coverage_100x(%)': [8, 8, 8, 8],
    'Coverage_50x(%)': [7, 7, 7, 7],
    'Coverage_30x(%)': [9, 9, 9, 9],
    'Coverage_20x(%)': [6, 6, 6, 6],
    'Coverage_15x(%)': [5, 5, 5, 5],
    'Coverage_10x(%)': [2, 2, 2, 2],
    'Coverage_1x(%)': [4, 4, 4, 4]
}

df = pd.DataFrame(data)

# Criar um MultiIndex
df.set_index(['Date', 'BED_File', 'BAM_File', 'Gene'], inplace=True)

# Adicionar a linha total
total_row = df.groupby(['Date', 'BED_File', 'BAM_File']).sum().mean().round().astype(int)
total_df = pd.DataFrame([total_row], index=pd.MultiIndex.from_tuples([('Total', '', '', '')], names=['Date', 'BED_File', 'BAM_File', 'Gene']))

df = pd.concat([df, total_df])

# Resetar o índice para criar um DataFrame plano
df.reset_index(inplace=True)

# Streamlit App
st.title('DataFrame Consolidado')

# Mostrar DataFrame
st.write(df)





import subprocess
from pathlib import Path

def run_samtools_depth_v3(bam_path, bed_path, depth_dir, gene_list):
    for gene_name in gene_list:
        # Comando para executar samtools depth com filtro diretamente no comando awk
        depth_command = f"awk -v gene={gene_name} '{{if ($4 == gene) {{sub(/^chr/, \"\", $1); print}}}}' {bed_path} | samtools depth -b - {bam_path} > {depth_dir}/{gene_name}.depth"

        # Executa o comando samtools depth com o filtro aplicado diretamente no comando awk
        subprocess.run(depth_command, shell=True)

# Exemplo de uso:
bam_path = Path("data/mapped/1106179.bam")
bed_path = Path("data/regions/gene_exons/UCSC_hg19_exons_modif_canonical.bed")
depth_output_dir = Path("data")  # Diretório para os arquivos de saída de profundidade
gene_list = ["DICER1","ATM","AXIN2"]  # Lista de genes a serem processados

run_samtools_depth_v3(bam_path, bed_path, depth_output_dir, gene_list)
