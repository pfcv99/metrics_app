import pandas as pd
import streamlit as st
import io

# Estrutura reutilizável para as métricas
def initialize_metrics():
    return {
        'Size Coding': 0,
        'Size Covered': 0,
        'Average Read Depth': 0,
        'Min Read Depth': float('inf'),
        'Max Read Depth': 0,
        "Coverage (0-1x)": 0,
        "Coverage (2-10x)": 0,
        "Coverage (11-15x)": 0,
        "Coverage (16-20x)": 0,
        "Coverage (21-30x)": 0,
        "Coverage (31-50x)": 0,
        "Coverage (51-100x)": 0,
        "Coverage (101-500x)": 0,
        "Coverage % (1x)": 0,
        "Coverage % (10x)": 0,
        "Coverage % (15x)": 0,
        "Coverage % (20x)": 0,
        "Coverage % (30x)": 0,
        "Coverage % (50x)": 0,
        "Coverage % (100x)": 0,
        "Coverage % (500x)": 0
    }

def calculate_metrics():
    # Acessar o conteúdo filtrado do .bed a partir do session_state do Streamlit
    bed_content = st.session_state.get('filtered_bed', '')
    
    depth_content = st.session_state.get('depth_output', '')
    
    if not bed_content:
        raise ValueError("No filtered BED content found in session state.")
    
    if not depth_content:
        raise ValueError("No DEPTH content found in session state.")
    
    # Ler o ficheiro .bed filtrado a partir do conteúdo no session_state
    bed_df = pd.read_csv(io.StringIO(bed_content), sep='\t', header=None, names=['CHROM', 'START', 'END', 'GENE', 'EXON', 'SIZE'])

    # Ler o ficheiro .depth
    depth_df = pd.read_csv(io.StringIO(depth_content), sep='\t', header=None, names=['CHROM', 'POS', 'DEPTH'])

    # Dicionário para armazenar os resultados globais, por gene e por exão
    results = {
        'All Genes': initialize_metrics()
    }

    # Obter todos os genes únicos
    genes = bed_df['GENE'].unique()
    
    gene_metrics = {}
    exon_metrics = {}

    for gene in genes:
        # Filtrar os exões para o gene específico
        gene_bed_df = bed_df[bed_df['GENE'] == gene]
        
        # Inicializar as métricas para o gene
        gene_metrics[gene] = initialize_metrics()
        gene_metrics[gene]['Size Coding'] = gene_bed_df['SIZE'].sum()

        for _, exon in gene_bed_df.iterrows():
            # Filtrar as linhas do depth file que estão dentro das coordenadas do exão
            exon_depth_df = depth_df[(depth_df['POS'] >= exon['START']) & (depth_df['POS'] <= exon['END'])]
            
            # Size Covered do exão
            size_covered_exon = exon_depth_df['POS'].max() - exon_depth_df['POS'].min() if not exon_depth_df.empty else 0
            
            # Inicializar as métricas do exão
            exon_metrics[(gene, exon['EXON'])] = initialize_metrics()
            exon_metrics[(gene, exon['EXON'])]['Size Coding'] = exon['SIZE']
            exon_metrics[(gene, exon['EXON'])]['Size Covered'] = size_covered_exon
            exon_metrics[(gene, exon['EXON'])]['Average Read Depth'] = exon_depth_df['DEPTH'].mean() if not exon_depth_df.empty else 0
            exon_metrics[(gene, exon['EXON'])]['Min Read Depth'] = exon_depth_df['DEPTH'].min() if not exon_depth_df.empty else 0
            exon_metrics[(gene, exon['EXON'])]['Max Read Depth'] = exon_depth_df['DEPTH'].max() if not exon_depth_df.empty else 0
            
            # Calcular cobertura por intervalos e percentagens para o exão
            for depth in exon_depth_df['DEPTH']:
                # Atualizar Coverage por intervalos
                if 0 <= depth <= 1:
                    exon_metrics[(gene, exon['EXON'])]["Coverage (0-1x)"] += depth
                elif 2 <= depth <= 10:
                    exon_metrics[(gene, exon['EXON'])]["Coverage (2-10x)"] += depth
                elif 11 <= depth <= 15:
                    exon_metrics[(gene, exon['EXON'])]["Coverage (11-15x)"] += depth
                elif 16 <= depth <= 20:
                    exon_metrics[(gene, exon['EXON'])]["Coverage (16-20x)"] += depth
                elif 21 <= depth <= 30:
                    exon_metrics[(gene, exon['EXON'])]["Coverage (21-30x)"] += depth
                elif 31 <= depth <= 50:
                    exon_metrics[(gene, exon['EXON'])]["Coverage (31-50x)"] += depth
                elif 51 <= depth <= 100:
                    exon_metrics[(gene, exon['EXON'])]["Coverage (51-100x)"] += depth
                elif 101 <= depth <= 500:
                    exon_metrics[(gene, exon['EXON'])]["Coverage (101-500x)"] += depth
                
                # Atualizar Coverage Percentage
                if depth >= 1:
                    exon_metrics[(gene, exon['EXON'])]["Coverage % (1x)"] += 1
                if depth >= 10:
                    exon_metrics[(gene, exon['EXON'])]["Coverage % (10x)"] += 1
                if depth >= 15:
                    exon_metrics[(gene, exon['EXON'])]["Coverage % (15x)"] += 1
                if depth >= 20:
                    exon_metrics[(gene, exon['EXON'])]["Coverage % (20x)"] += 1
                if depth >= 30:
                    exon_metrics[(gene, exon['EXON'])]["Coverage % (30x)"] += 1
                if depth >= 50:
                    exon_metrics[(gene, exon['EXON'])]["Coverage % (50x)"] += 1
                if depth >= 100:
                    exon_metrics[(gene, exon['EXON'])]["Coverage % (100x)"] += 1
                if depth >= 500:
                    exon_metrics[(gene, exon['EXON'])]["Coverage % (500x)"] += 1

            # Converter as contagens em percentagens
            for key in exon_metrics[(gene, exon['EXON'])]:
                if "Coverage %" in key and exon_metrics[(gene, exon['EXON'])]['Size Coding'] > 0:
                    exon_metrics[(gene, exon['EXON'])][key] = (exon_metrics[(gene, exon['EXON'])][key] / exon_metrics[(gene, exon['EXON'])]['Size Coding']) * 100

            # Atualizar métricas do gene com as métricas do exão
            for key in gene_metrics[gene]:
                if key != 'Size Coding':
                    gene_metrics[gene][key] += exon_metrics[(gene, exon['EXON'])][key]

            # Adicionar as métricas do exão ao dicionário de resultados
            results[f"{gene}_Exon_{exon['EXON']}"] = exon_metrics[(gene, exon['EXON'])]

        # Adicionar as métricas gerais do gene ao dicionário de resultados
        results[gene] = gene_metrics[gene]

        # Atualizar as métricas globais com as do gene
        for key in results['All Genes']:
            if key != 'Size Coding':
                results['All Genes'][key] += gene_metrics[gene][key]

    # Converter os resultados para DataFrame
    all_genes_df = pd.DataFrame([results['All Genes']])
    genes_data_df = pd.DataFrame(gene_metrics).T
    exons_data_df = pd.DataFrame(exon_metrics).T

    return all_genes_df, genes_data_df, exons_data_df
