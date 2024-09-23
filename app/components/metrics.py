import pandas as pd
import streamlit as st
import io

# Reusable structure for metrics
def initialize_metrics():
    return {
        'Size Coding': 0,
        'Size Covered': 0,
        'Average Read Depth': 0,
        'Min Read Depth': 0,
        'Max Read Depth': 0,
        'Coverage % (1x)': 0,
        'Coverage % (10x)': 0,
        'Coverage % (15x)': 0,
        'Coverage % (20x)': 0,
        'Coverage % (30x)': 0,
        'Coverage % (50x)': 0,
        'Coverage % (100x)': 0,
        'Coverage % (500x)': 0,
        'Coverage (>500x)': 0,
        'Coverage (0-1x)': 0,
        'Coverage (2-10x)': 0,
        'Coverage (11-15x)': 0,
        'Coverage (16-20x)': 0,
        'Coverage (21-30x)': 0,
        'Coverage (31-50x)': 0,
        'Coverage (51-100x)': 0,
        'Coverage (101-500x)': 0
    }

def calculate_metrics():
    # Access the filtered BED content from session_state
    bed_content = st.session_state.get('filtered_bed', '')
    depth_content = st.session_state.get('depth_output', '')

    if not bed_content:
        raise ValueError("No filtered BED content found in session state.")
    
    if not depth_content:
        raise ValueError("No DEPTH content found in session state.")

    # Read the filtered .bed file
    bed_df = pd.read_csv(io.StringIO(bed_content), sep='\t', header=None, names=['CHROM', 'START', 'END', 'GENE', 'EXON', 'SIZE'])

    # Read the .depth file
    depth_df = pd.read_csv(io.StringIO(depth_content), sep='\t', header=None, names=['CHROM', 'POS', 'DEPTH'])

    # Initialize the results dictionary
    results = {}

    # All Genes metrics
    all_genes_metrics = initialize_metrics()

    # Size Coding for All Genes
    all_genes_metrics['Size Coding'] = bed_df['SIZE'].sum()

    # Depth values for All Genes
    all_depths = depth_df['DEPTH']

    total_positions = all_genes_metrics['Size Coding']

    # In case size coding is zero, use the number of depth entries
    if total_positions == 0:
        total_positions = len(all_depths)

    # Average Read Depth
    all_genes_metrics['Average Read Depth'] = all_depths.mean() if len(all_depths) > 0 else 0

    # Min Read Depth
    all_genes_metrics['Min Read Depth'] = all_depths.min() if len(all_depths) > 0 else 0

    # Max Read Depth
    all_genes_metrics['Max Read Depth'] = all_depths.max() if len(all_depths) > 0 else 0

    # Size Covered
    if not depth_df.empty:
        all_genes_metrics['Size Covered'] = depth_df['POS'].max() - depth_df['POS'].min() + 1
    else:
        all_genes_metrics['Size Covered'] = 0

    # Initialize counts for coverage percentages and depth intervals
    coverage_thresholds = [1, 10, 15, 20, 30, 50, 100, 500]
    coverage_counts = {threshold: 0 for threshold in coverage_thresholds}

    depth_intervals = {
        "Coverage (>500x)": 0,
        "Coverage (101-500x)": 0,
        "Coverage (51-100x)": 0,
        "Coverage (31-50x)": 0,
        "Coverage (21-30x)": 0,
        "Coverage (16-20x)": 0,
        "Coverage (11-15x)": 0,
        "Coverage (2-10x)": 0,
        "Coverage (0-1x)": 0
    }

    # Classify depth values into intervals and count positions meeting each coverage threshold
    for depth in all_depths:
        # Count positions meeting each coverage threshold
        for threshold in coverage_thresholds:
            if depth >= threshold:
                coverage_counts[threshold] += 1

        # Classify depth into intervals
        if depth > 500:
            depth_intervals["Coverage (>500x)"] += 1
        elif 101 < depth <= 500:
            depth_intervals["Coverage (101-500x)"] += 1
        elif 51 <= depth < 101:
            depth_intervals["Coverage (51-100x)"] += 1
        elif 31 <= depth < 51:
            depth_intervals["Coverage (31-50x)"] += 1
        elif 21 <= depth < 31:
            depth_intervals["Coverage (21-30x)"] += 1
        elif 16 <= depth < 21:
            depth_intervals["Coverage (16-20x)"] += 1
        elif 11 <= depth < 16:
            depth_intervals["Coverage (11-15x)"] += 1
        elif 2 <= depth < 11:
            depth_intervals["Coverage (2-10x)"] += 1
        else:
            depth_intervals["Coverage (0-1x)"] += 1

    # Compute coverage percentages
    for threshold in coverage_thresholds:
        percentage = (coverage_counts[threshold] / total_positions) * 100 if total_positions > 0 else 0
        all_genes_metrics[f"Coverage % ({threshold}x)"] = percentage

    # Add depth intervals to the metrics
    all_genes_metrics.update(depth_intervals)

    # Store All Genes metrics
    results['All Genes'] = all_genes_metrics

    # Now compute metrics for each gene
    genes = bed_df['GENE'].unique()

    genes_data = {}
    exons_data = {}

    for gene in genes:
        gene_metrics = initialize_metrics()

        # Size Coding for the gene
        gene_bed_df = bed_df[bed_df['GENE'] == gene]
        gene_metrics['Size Coding'] = gene_bed_df['SIZE'].sum()

        # Get depth data for this gene
        gene_positions = []

        for idx, row in gene_bed_df.iterrows():
            start = row['START']
            end = row['END']
            gene_positions.append((start, end))

        # Filter depth_df for positions within gene_positions
        gene_depths = pd.Series(dtype=float)

        for start, end in gene_positions:
            exon_depths = depth_df[(depth_df['POS'] >= start) & (depth_df['POS'] <= end)]['DEPTH']
            gene_depths = pd.concat([gene_depths, exon_depths], ignore_index=True)

        total_positions_gene = gene_metrics['Size Coding']

        if total_positions_gene == 0:
            total_positions_gene = len(gene_depths)

        gene_metrics['Average Read Depth'] = gene_depths.mean() if len(gene_depths) > 0 else 0
        gene_metrics['Min Read Depth'] = gene_depths.min() if len(gene_depths) > 0 else 0
        gene_metrics['Max Read Depth'] = gene_depths.max() if len(gene_depths) > 0 else 0

        if not gene_depths.empty:
            gene_metrics['Size Covered'] = gene_depths.index[-1] - gene_depths.index[0] + 1
        else:
            gene_metrics['Size Covered'] = 0

        # Initialize counts for coverage percentages and depth intervals for the gene
        coverage_counts_gene = {threshold: 0 for threshold in coverage_thresholds}
        depth_intervals_gene = {
            "Coverage (>500x)": 0,
            "Coverage (101-500x)": 0,
            "Coverage (51-100x)": 0,
            "Coverage (31-50x)": 0,
            "Coverage (21-30x)": 0,
            "Coverage (16-20x)": 0,
            "Coverage (11-15x)": 0,
            "Coverage (2-10x)": 0,
            "Coverage (0-1x)": 0
        }

        # Count positions meeting each coverage threshold for the gene
        for depth in gene_depths:
            # Count positions meeting each coverage threshold
            for threshold in coverage_thresholds:
                if depth >= threshold:
                    coverage_counts_gene[threshold] += 1

            # Classify depth into intervals for the gene
            if depth > 500:
                depth_intervals_gene["Coverage (>500x)"] += 1
            elif 101 < depth <= 500:
                depth_intervals_gene["Coverage (101-500x)"] += 1
            elif 51 <= depth < 101:
                depth_intervals_gene["Coverage (51-100x)"] += 1
            elif 31 <= depth < 51:
                depth_intervals_gene["Coverage (31-50x)"] += 1
            elif 21 <= depth < 31:
                depth_intervals_gene["Coverage (21-30x)"] += 1
            elif 16 <= depth < 21:
                depth_intervals_gene["Coverage (16-20x)"] += 1
            elif 11 <= depth < 16:
                depth_intervals_gene["Coverage (11-15x)"] += 1
            elif 2 <= depth < 11:
                depth_intervals_gene["Coverage (2-10x)"] += 1
            else:
                depth_intervals_gene["Coverage (0-1x)"] += 1

        # Compute coverage percentages for the gene
        for threshold in coverage_thresholds:
            percentage = (coverage_counts_gene[threshold] / total_positions_gene) * 100 if total_positions_gene > 0 else 0
            gene_metrics[f"Coverage % ({threshold}x)"] = percentage

        # Add depth intervals to the gene metrics
        gene_metrics.update(depth_intervals_gene)

        # Store gene metrics
        genes_data[gene] = gene_metrics

        # Now compute metrics for each exon of the gene
        exons = gene_bed_df['EXON'].unique()
        for exon in exons:
            exon_metrics = initialize_metrics()
            exon_bed_df = gene_bed_df[gene_bed_df['EXON'] == exon]
            exon_size_coding = exon_bed_df['SIZE'].sum()
            exon_metrics['Size Coding'] = exon_size_coding

            # Get depth data for this exon
            exon_positions = []
            for idx, row in exon_bed_df.iterrows():
                start = row['START']
                end = row['END']
                exon_positions.append((start, end))

            exon_depths = pd.Series(dtype=float)

            for start, end in exon_positions:
                depth_values = depth_df[(depth_df['POS'] >= start) & (depth_df['POS'] <= end)]['DEPTH']
                exon_depths = pd.concat([exon_depths, depth_values], ignore_index=True)

            total_positions_exon = exon_metrics['Size Coding']
            if total_positions_exon == 0:
                total_positions_exon = len(exon_depths)

            exon_metrics['Average Read Depth'] = exon_depths.mean() if len(exon_depths) > 0 else 0
            exon_metrics['Min Read Depth'] = exon_depths.min() if len(exon_depths) > 0 else 0
            exon_metrics['Max Read Depth'] = exon_depths.max() if len(exon_depths) > 0 else 0

            if not exon_depths.empty:
                exon_metrics['Size Covered'] = exon_depths.index[-1] - exon_depths.index[0] + 1
            else:
                exon_metrics['Size Covered'] = 0

            # Initialize counts for coverage percentages and depth intervals for the exon
            coverage_counts_exon = {threshold: 0 for threshold in coverage_thresholds}
            depth_intervals_exon = {
                "Coverage (>500x)": 0,
                "Coverage (101-500x)": 0,
                "Coverage (51-100x)": 0,
                "Coverage (31-50x)": 0,
                "Coverage (21-30x)": 0,
                "Coverage (16-20x)": 0,
                "Coverage (11-15x)": 0,
                "Coverage (2-10x)": 0,
                "Coverage (0-1x)": 0
            }

            # Count positions meeting each coverage threshold for the exon
            for depth in exon_depths:
                # Count positions meeting each coverage threshold
                for threshold in coverage_thresholds:
                    if depth >= threshold:
                        coverage_counts_exon[threshold] += 1

                # Classify depth into intervals for the exon
                if depth > 500:
                    depth_intervals_exon["Coverage (>500x)"] += 1
                elif 101 < depth <= 500:
                    depth_intervals_exon["Coverage (101-500x)"] += 1
                elif 51 <= depth < 101:
                    depth_intervals_exon["Coverage (51-100x)"] += 1
                elif 31 <= depth < 51:
                    depth_intervals_exon["Coverage (31-50x)"] += 1
                elif 21 <= depth < 31:
                    depth_intervals_exon["Coverage (21-30x)"] += 1
                elif 16 <= depth < 21:
                    depth_intervals_exon["Coverage (16-20x)"] += 1
                elif 11 <= depth < 16:
                    depth_intervals_exon["Coverage (11-15x)"] += 1
                elif 2 <= depth < 11:
                    depth_intervals_exon["Coverage (2-10x)"] += 1
                else:
                    depth_intervals_exon["Coverage (0-1x)"] += 1

            # Compute coverage percentages for the exon
            for threshold in coverage_thresholds:
                percentage = (coverage_counts_exon[threshold] / total_positions_exon) * 100 if total_positions_exon > 0 else 0
                exon_metrics[f"Coverage % ({threshold}x)"] = percentage

            # Add depth intervals to the exon metrics
            exon_metrics.update(depth_intervals_exon)

            # Store exon metrics
            exons_data[(gene, exon)] = exon_metrics

    # Create DataFrames for All Genes, Genes, and Exons
    all_genes_df = pd.DataFrame([results['All Genes']])
    genes_data_df = pd.DataFrame.from_dict(genes_data, orient='index')
    exons_data_df = pd.DataFrame.from_dict(exons_data, orient='index')
    exons_data_df.index.names = ['GENE', 'EXON']

    # Reorder columns as per desired order
    desired_order = [
        'Size Coding', 'Size Covered', 'Average Read Depth', 'Min Read Depth', 'Max Read Depth',
        'Coverage % (1x)', 'Coverage % (10x)', 'Coverage % (15x)', 'Coverage % (20x)',
        'Coverage % (30x)', 'Coverage % (50x)', 'Coverage % (100x)', 'Coverage % (500x)',
        'Coverage (>500x)'
    ]

    all_genes_df = all_genes_df[desired_order]
    genes_data_df = genes_data_df[desired_order]
    exons_data_df = exons_data_df[desired_order]

    return all_genes_df, genes_data_df, exons_data_df
