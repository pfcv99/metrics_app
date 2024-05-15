import pandas as pd
import streamlit as st
from components import logo
import subprocess

logo.add_logo()


#gene_list = ["PKD1", "DICER1", "ATM", "AXIN2"]
#bed_path = 'data/regions/genome_exons/MANE_hg38_exons_modif_MANE_with_difference.bed'
#awk_command = "awk '{if ($4 == \"" + "\" || $4 == \"".join(gene_list) + "\") print}' " + bed_path
#subprocess.run(awk_command, shell=True)
#
#
#
#
#def normalization_factor(assembly_file, region):
#    size_coding_global = 0
#    size_coding_per_gene = {}
#    normalization_factor_per_gene = {}
#
#    with open(assembly_file, 'r') as file:
#        for gene in region:
#            size_coding = 0
#            file.seek(0)  # Reseta o ponteiro do arquivo para o início
#            for line in file:
#                fields = line.strip().split('\t')
#                # Supondo que o nome do gene esteja na primeira coluna
#                if fields[3] == gene:
#                    size_coding += int(fields[6])
#            size_coding_global += size_coding
#            size_coding_per_gene[gene] = size_coding
#
#    for gene, size in size_coding_per_gene.items():
#        normalization_factor_per_gene[gene] = size / size_coding_global
#
#    return size_coding_global, size_coding_per_gene, normalization_factor_per_gene
#
#region = ["DICER1", "ATM", "AXIN2"]
#assembly_file = "data/regions/genome_exons/MANE_hg38_exons_modif_MANE_with_difference.bed"
#global_size, per_gene_size, normalization_factors = normalization_factor(assembly_file, region)
#
#print("Tamanho global de codificação:", global_size)
#print("Tamanho de codificação por gene:")
#for gene, size in per_gene_size.items():
#    print(gene + ":", size)
#
#print("\nFator de normalização por gene:")
#for gene, factor in normalization_factors.items():
#    print(gene + ":", factor)
#
#
#
## Criar o DataFrame
#data = {
#    'Date': ['06/03/2024'] * 4,
#    'BED_File': ['Oncorisk_96genes.bed'] * 4,
#    'BAM_File': ['1106179.bam'] * 4,
#    'Gene': ['AIP', 'ALK', 'APC', 'ATM'],
#    'Average_Read_Depth': [1, 1, 1, 1],
#    'Coverage_500x(%)': [3, 3, 3, 3],
#    'Coverage_100x(%)': [8, 8, 8, 8],
#    'Coverage_50x(%)': [7, 7, 7, 7],
#    'Coverage_30x(%)': [9, 9, 9, 9],
#    'Coverage_20x(%)': [6, 6, 6, 6],
#    'Coverage_15x(%)': [5, 5, 5, 5],
#    'Coverage_10x(%)': [2, 2, 2, 2],
#    'Coverage_1x(%)': [4, 4, 4, 4]
#}
#
#df = pd.DataFrame(data)
#
## Criar um MultiIndex
#df.set_index(['Date', 'BED_File', 'BAM_File', 'Gene'], inplace=True)
#
## Adicionar a linha total
#total_row = df.groupby(['Date', 'BED_File', 'BAM_File']).sum().mean().round().astype(int)
#total_df = pd.DataFrame([total_row], index=pd.MultiIndex.from_tuples([('Total', '', '', '')], names=['Date', 'BED_File', 'BAM_File', 'Gene']))
#
#df = pd.concat([df, total_df])
#
## Resetar o índice para criar um DataFrame plano
#df.reset_index(inplace=True)
#
## Streamlit App
#st.title('DataFrame Consolidado')
#
## Mostrar DataFrame
#st.write(df)





import subprocess
from pathlib import Path

#def run_samtools_depth_v3(bam_path, bed_path, depth_dir, gene_list):
#    for gene_name in gene_list:
#        # Comando para executar samtools depth com filtro diretamente no comando awk
#        depth_command = f"awk -v gene={gene_name} '{{if ($4 == gene) {{sub(/^chr/, \"\", $1); print}}}}' {bed_path} | samtools depth -b - {bam_path} > {depth_dir}/{gene_name}#"
#
#        # Executa o comando samtools depth com o filtro aplicado diretamente no comando awk
#        subprocess.run(depth_command, shell=True)
#
## Exemplo de uso:
#bam_path = Path("data/mapped/1106179.bam")
#bed_path = Path("data/regions/gene_exons/UCSC_hg19_exons_modif_canonical.bed")
#depth_output_dir = Path("data")  # Diretório para os arquivos de saída de profundidade
#gene_list = ["DICER1","ATM","AXIN2"]  # Lista de genes a serem processados
#
#run_samtools_depth_v3(bam_path, bed_path, depth_output_dir, gene_list)
#
#
#
#def size_coding_for_gene(bed_file, gene_name):
#    gene_metrics = {"total_bases": 0, "num_exons": 0, "average_exon_size": 0}
#    with open(bed_file) as file:
#        lines = file.readlines()
#        for line in lines:
#            fields = line.strip().split()
#            if fields[3] == gene_name:  # Assumindo que o nome do gene está na quarta coluna
#                gene_size = int(fields[2]) - int(fields[1])
#                gene_metrics["total_bases"] += gene_size
#                gene_metrics["num_exons"] += 1
#    
#    # Calcular o tamanho médio dos exões para o gene
#    if gene_metrics["num_exons"] != 0:
#        gene_metrics["average_exon_size"] = gene_metrics["total_bases"] / gene_metrics["num_exons"]
#    
#    return gene_metrics
#
#gene_name = "PKD1"
#gene_metrics = size_coding_for_gene("data/regions/genome_exons/UCSC_hg19_exons_modif_canonical.bed", gene_name)
#
## Imprimir métricas para o gene PKD1
#print("Gene:", gene_name)
#print("Total de bases:", gene_metrics["total_bases"])
#print("Número de exões:", gene_metrics["num_exons"])
#print("Tamanho médio do exão:", gene_metrics["average_exon_size"])
#
#
#if st.button('Clique aqui'):
#    default_val = 'Texto de exemplo'
#    user_input = st.text_input("Digite algo aqui", value=default_val)
#
#
#
#
#import pandas as pd
#import pandas_profiling
#import streamlit as st
#
#from streamlit_pandas_profiling import st_profile_report
#
#
#df = pd.read_csv("data/bam_bed_map/bam_bed_map.csv")
#pr = df.profile_report()
#
#st_profile_report(pr)
#
#
#import numpy as np
#
#def rpkm(counts, lengths):
#    #https://www.oreilly.com/library/view/elegant-scipy/9781491922927/ch01.html
#    """Calculate reads per kilobase transcript per million reads.
#
#    RPKM = (10^9 * C) / (N * L)
#
#    Where:
#    C = Number of reads mapped to a gene
#    N = Total mapped reads in the experiment
#    L = Exon length in base pairs for a gene
#
#    Parameters
#    ----------
#    counts: array, shape (N_genes, N_samples)
#        RNAseq (or similar) count data where columns are individual samples
#        and rows are genes.
#    lengths: array, shape (N_genes,)
#        Gene lengths in base pairs in the same order
#        as the rows in counts.
#
#    Returns
#    -------
#    normed : array, shape (N_genes, N_samples)
#        The RPKM normalized counts matrix.
#    """
#    N = np.sum(counts, axis=0)  # sum each column to get total reads per sample
#    L = lengths
#    C = counts
#
#    normed = 1e9 * C / (N[np.newaxis, :] * L[:, np.newaxis])
#
#    return(normed)
#
#
#
## Example data
#counts = np.array([[100, 200, 150],   # Gene counts for three samples
#                   [50, 80, 60],
#                   [200, 300, 250]])
#lengths = np.array([1000, 1500, 800])  # Gene lengths in base pairs
#
## Calculate RPKM
#rpkm_values = rpkm(counts, lengths)
#
#print("RPKM normalized counts:")
#print(rpkm_values)





#import plotly.graph_objects as go
#
#headerColor = 'grey'
#rowEvenColor = 'lightgrey'
#rowOddColor = 'white'
#fig = go.Figure(data=[go.Table(
#  header=dict(
#    values=['<b>EXPENSES</b>','<b>Q1</b>','<b>Q2</b>','<b>Q3</b>','<b>Q4</b>'],
#    line_color='darkslategray',
#    fill_color=headerColor,
#    align=['left','center'],
#    font=dict(color='white', size=12)
#  ),
#  cells=dict(
#    values=[
#      ['Salaries', 'Office', 'Merchandise', 'Legal', '<b>TOTAL</b>'],
#      [1200000, 20000, 80000, 2000, 12120000],
#      [1300000, 20000, 70000, 2000, 130902000],
#      [1300000, 20000, 120000, 2000, 131222000],
#      [1400000, 20000, 90000, 2000, 14102000]],
#    line_color='darkslategray',
#    # 2-D list of colors for alternating rows
#    fill_color = [[rowOddColor,rowEvenColor,rowOddColor, rowEvenColor,rowOddColor]*5],
#    align = ['left', 'center'],
#    font = dict(color = 'darkslategray', size = 11)
#    ))
#])
#tab1, tab2 = st.tabs(["Streamlit theme (default)", "Plotly native theme"])
#with tab1:
#    st.plotly_chart(fig, theme="streamlit")
#with tab2:
#    st.plotly_chart(fig, theme=None)
    
    


import plotly.graph_objects as go

fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = 50,
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': "100x", 'font': {'size': 24}},
    gauge = {
        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "black"},
        'bar': {'color': "darkgrey"},
        'bgcolor': "white",
        'borderwidth': 2,
        'bordercolor': "gray",
        'steps': [
            {'range': [0, 94], 'color': 'red'},
            {'range': [94, 98], 'color': 'yellow'},
            {'range': [98, 100], 'color': 'green'}]}))

fig.update_layout(font = {'color': "darkgrey", 'family': "Arial"})

st.plotly_chart(fig, theme=None)
