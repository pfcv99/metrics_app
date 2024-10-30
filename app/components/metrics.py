import pandas as pd
import streamlit as st
import io

# Reusable structure for metrics
def initialize_metrics():
    return {
        'Size Coding': 0,
        'Size Covered': 0,
        'Breadth of Coverage %': 0,
        'Average Read Depth': 0,
        'Min Read Depth': 0,
        'Max Read Depth': 0,
        'Depth of Coverage % (1x)': 0,
        'Depth of Coverage % (10x)': 0,
        'Depth of Coverage % (15x)': 0,
        'Depth of Coverage % (20x)': 0,
        'Depth of Coverage % (30x)': 0,
        'Depth of Coverage % (50x)': 0,
        'Depth of Coverage % (100x)': 0,
        'Depth of Coverage % (500x)': 0,
        'Depth of Coverage (>500x)': 0,
        'Depth of Coverage (0-1x)': 0,
        'Depth of Coverage (2-10x)': 0,
        'Depth of Coverage (11-15x)': 0,
        'Depth of Coverage (16-20x)': 0,
        'Depth of Coverage (21-30x)': 0,
        'Depth of Coverage (31-50x)': 0,
        'Depth of Coverage (51-100x)': 0,
        'Depth of Coverage (101-500x)': 0
    }

def calculate_metrics():
    # Access the filtered BED content and depth data from session_state
    bed_content = st.session_state.get('filtered_bed', '')
    depth_dict = st.session_state.get('depth_output', {})

    if not bed_content:
        raise ValueError("No filtered BED content found in session state.")

    if not depth_dict:
        raise ValueError("No depth data found in session state.")

    # Read the filtered .bed file
    bed_df = pd.read_csv(io.StringIO(bed_content), sep='\t', header=None, names=['CHROM', 'START', 'END', 'GENE', 'EXON', 'SIZE'])

    results = {}
    desired_order = [
        'Size Coding',
        'Size Covered',
        'Breadth of Coverage %',
        'Average Read Depth',
        'Min Read Depth',
        'Max Read Depth',
        'Depth of Coverage % (1x)',
        'Depth of Coverage % (10x)',
        'Depth of Coverage % (15x)',
        'Depth of Coverage % (20x)',
        'Depth of Coverage % (30x)',
        'Depth of Coverage % (50x)',
        'Depth of Coverage % (100x)',
        'Depth of Coverage % (500x)',
        'Depth of Coverage (>500x)',
        'Depth of Coverage (0-1x)',
        'Depth of Coverage (2-10x)',
        'Depth of Coverage (11-15x)',
        'Depth of Coverage (16-20x)',
        'Depth of Coverage (21-30x)',
        'Depth of Coverage (31-50x)',
        'Depth of Coverage (51-100x)',
        'Depth of Coverage (101-500x)'
    ]

    for file_name, depth_content in depth_dict.items():
        # Read the depth file as a DataFrame
        depth_df = pd.read_csv(io.StringIO(depth_content), sep='\t', header=None, names=['CHROM', 'POS', 'DEPTH'])
        
        all_genes_metrics = initialize_metrics()
        total_positions = len(depth_df)

        if total_positions > 0:
            # Calculate metrics for all genes
            all_depths = depth_df['DEPTH']

            all_genes_metrics['Size Coding'] = bed_df['SIZE'].sum()
            all_genes_metrics['Average Read Depth'] = all_depths.mean()
            # Cálculo da média ponderada pela cobertura dos genes
            #weighted_sum = 0
            #total_size = 0
            #for _, row in bed_df.iterrows():
            #    start = row['START']
            #    end = row['END']
            #    size = row['SIZE']
            #    gene_depths = depth_df[(depth_df['POS'] >= start) & (depth_df['POS'] <= end)]['DEPTH']

            #    weighted_sum += gene_depths.sum() * size
            #    total_size += size

            all_genes_metrics['Min Read Depth'] = all_depths.min()
            all_genes_metrics['Max Read Depth'] = all_depths.max()
            all_genes_metrics['Size Covered'] = all_depths.count()
            all_genes_metrics['Breadth of Coverage %'] = (all_genes_metrics['Size Covered']/all_genes_metrics['Size Coding'])*100

            # Calculate coverage percentages and intervals
            coverage_thresholds = [1, 10, 15, 20, 30, 50, 100, 500]
            coverage_counts = {threshold: (all_depths >= threshold).sum() for threshold in coverage_thresholds}

            for threshold in coverage_thresholds:
                all_genes_metrics[f"Depth of Coverage % ({threshold}x)"] = (coverage_counts[threshold] / total_positions) * 100

            # Add depth intervals
            depth_intervals = {
                "Depth of Coverage (>500x)": (all_depths > 500).sum(),
                "Depth of Coverage (101-500x)": ((all_depths > 100) & (all_depths <= 500)).sum(),
                "Depth of Coverage (51-100x)": ((all_depths >= 51) & (all_depths <= 100)).sum(),
                "Depth of Coverage (31-50x)": ((all_depths >= 31) & (all_depths <= 50)).sum(),
                "Depth of Coverage (21-30x)": ((all_depths >= 21) & (all_depths <= 30)).sum(),
                "Depth of Coverage (16-20x)": ((all_depths >= 16) & (all_depths <= 20)).sum(),
                "Depth of Coverage (11-15x)": ((all_depths >= 11) & (all_depths <= 15)).sum(),
                "Depth of Coverage (2-10x)": ((all_depths >= 2) & (all_depths <= 10)).sum(),
                "Depth of Coverage (0-1x)": (all_depths <= 1).sum(),
            }

            all_genes_metrics.update(depth_intervals)

            # Store 'All Genes' metrics under the sample ID (file_name)
            results[file_name] = {}
            results[file_name]['All Genes'] = all_genes_metrics

            # Calculate metrics for each gene and exon
            genes_data = {}
            exons_data = {}
            genes = bed_df['GENE'].unique()

            for gene in genes:
                gene_metrics = initialize_metrics()
                gene_bed_df = bed_df[bed_df['GENE'] == gene]

                gene_metrics['Size Coding'] = gene_bed_df['SIZE'].sum()
                gene_depths = pd.Series(dtype=float)

                for _, row in gene_bed_df.iterrows():
                    start = row['START']
                    end = row['END']
                    exon_depths = depth_df[(depth_df['POS'] >= start) & (depth_df['POS'] <= end)]['DEPTH']
                    gene_depths = pd.concat([gene_depths, exon_depths], ignore_index=True)

                if len(gene_depths) > 0:
                    gene_metrics['Average Read Depth'] = gene_depths.mean()
                    gene_metrics['Min Read Depth'] = gene_depths.min()
                    gene_metrics['Max Read Depth'] = gene_depths.max()
                    gene_metrics['Size Covered'] = gene_depths.count()
                    gene_metrics['Breadth of Coverage %'] = (gene_metrics['Size Covered']/gene_metrics['Size Coding'])*100
                else:
                    gene_metrics['Average Read Depth'] = 0
                    gene_metrics['Min Read Depth'] = 0
                    gene_metrics['Max Read Depth'] = 0
                    gene_metrics['Size Covered'] = 0

                # Calculate coverage percentages
                coverage_counts_gene = {threshold: (gene_depths >= threshold).sum() for threshold in coverage_thresholds}
                for threshold in coverage_thresholds:
                    gene_metrics[f"Depth of Coverage % ({threshold}x)"] = (coverage_counts_gene[threshold] / gene_metrics['Size Covered']) * 100 if gene_metrics['Size Covered'] > 0 else 0

                # Add depth intervals for gene
                depth_intervals_gene = {
                    "Depth of Coverage (>500x)": (gene_depths > 500).sum(),
                    "Depth of Coverage (101-500x)": ((gene_depths > 100) & (gene_depths <= 500)).sum(),
                    "Depth of Coverage (51-100x)": ((gene_depths >= 51) & (gene_depths <= 100)).sum(),
                    "Depth of Coverage (31-50x)": ((gene_depths >= 31) & (gene_depths <= 50)).sum(),
                    "Depth of Coverage (21-30x)": ((gene_depths >= 21) & (gene_depths <= 30)).sum(),
                    "Depth of Coverage (16-20x)": ((gene_depths >= 16) & (gene_depths <= 20)).sum(),
                    "Depth of Coverage (11-15x)": ((gene_depths >= 11) & (gene_depths <= 15)).sum(),
                    "Depth of Coverage (2-10x)": ((gene_depths >= 2) & (gene_depths <= 10)).sum(),
                    "Depth of Coverage (0-1x)": (gene_depths <= 1).sum(),
                }

                gene_metrics.update(depth_intervals_gene)

                genes_data[gene] = gene_metrics

                # Exon-level metrics
                exon_data_for_gene = {}
                for exon_name in gene_bed_df['EXON'].unique():
                    exon_metrics = initialize_metrics()
                    exon_bed_df = gene_bed_df[gene_bed_df['EXON'] == exon_name]
                    exon_depths = pd.Series(dtype=float)
                    
                    exon_metrics['Size Coding'] = exon_bed_df['SIZE'].sum()

                    for _, row in exon_bed_df.iterrows():
                        start = row['START']
                        end = row['END']
                        exon_depths = pd.concat([exon_depths, depth_df[(depth_df['POS'] >= start) & (depth_df['POS'] <= end)]['DEPTH']], ignore_index=True)

                    if len(exon_depths) > 0:
                        exon_metrics['Average Read Depth'] = exon_depths.mean()
                        exon_metrics['Min Read Depth'] = exon_depths.min()
                        exon_metrics['Max Read Depth'] = exon_depths.max()
                        exon_metrics['Size Covered'] = exon_depths.count()
                        exon_metrics['Breadth of Coverage %'] = (exon_metrics['Size Covered']/exon_metrics['Size Coding'])*100
                    else:
                        exon_metrics['Average Read Depth'] = 0
                        exon_metrics['Min Read Depth'] = 0
                        exon_metrics['Max Read Depth'] = 0
                        exon_metrics['Size Covered'] = 0

                    # Calculate coverage percentages for exon
                    coverage_counts_exon = {threshold: (exon_depths >= threshold).sum() for threshold in coverage_thresholds}
                    for threshold in coverage_thresholds:
                        exon_metrics[f"Depth of Coverage % ({threshold}x)"] = (coverage_counts_exon[threshold] / exon_metrics['Size Covered']) * 100 if exon_metrics['Size Covered'] > 0 else 0

                    # Add depth intervals for exon
                    depth_intervals_exon = {
                        "Depth of Coverage (>500x)": (exon_depths > 500).sum(),
                        "Depth of Coverage (101-500x)": ((exon_depths > 100) & (exon_depths <= 500)).sum(),
                        "Depth of Coverage (51-100x)": ((exon_depths >= 51) & (exon_depths <= 100)).sum(),
                        "Depth of Coverage (31-50x)": ((exon_depths >= 31) & (exon_depths <= 50)).sum(),
                        "Depth of Coverage (21-30x)": ((exon_depths >= 21) & (exon_depths <= 30)).sum(),
                        "Depth of Coverage (16-20x)": ((exon_depths >= 16) & (exon_depths <= 20)).sum(),
                        "Depth of Coverage (11-15x)": ((exon_depths >= 11) & (exon_depths <= 15)).sum(),
                        "Depth of Coverage (2-10x)": ((exon_depths >= 2) & (exon_depths <= 10)).sum(),
                        "Depth of Coverage (0-1x)": (exon_depths <= 1).sum(),
                    }

                    exon_metrics.update(depth_intervals_exon)

                    # Store the metrics under the specific gene
                    exon_data_for_gene[exon_name] = exon_metrics

                exons_data[gene] = exon_data_for_gene  # Exons for the specific gene    

            results[file_name]['Genes'] = genes_data
            results[file_name]['Exons'] = exons_data

    return results
