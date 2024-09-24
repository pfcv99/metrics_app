import streamlit as st
import pandas as pd
from components import metrics
import numpy as np

sidebar_logo = "data/img/unilabs_logo.png"
main_body_logo = "data/img/thumbnail_image001.png"
st.logo(sidebar_logo)
st.logo(main_body_logo)

st.title("Results")
tab1, tab2, tab3 = st.tabs(["Overview", "Gene Detail", "Exon Detail"])

def select_all_metrics(select_all, metrics_dict, key_prefix):
    """Function to select or deselect all metrics."""
    for section, metrics_list in metrics_dict.items():
        for metric in metrics_list:
            st.session_state[f"{key_prefix}_metric_{metric}"] = select_all

# Desired order of metrics
desired_order = [
    'Size Coding', 'Size Covered', 'Average Read Depth', 'Min Read Depth', 'Max Read Depth',
    'Coverage (0-1x)', 'Coverage (2-10x)', 'Coverage (11-15x)', 'Coverage (16-20x)',
    'Coverage (21-30x)', 'Coverage (31-50x)', 'Coverage (51-100x)', 'Coverage (101-500x)', 'Coverage (>500x)',
    'Coverage % (1x)', 'Coverage % (10x)', 'Coverage % (15x)', 'Coverage % (20x)',
    'Coverage % (30x)', 'Coverage % (50x)', 'Coverage % (100x)', 'Coverage % (500x)'
]

# Call the calculate_metrics function and store results for multiple depth files
results = metrics.calculate_metrics()
file_names = list(results.keys())

# Prepare All Genes DataFrame
all_metrics = desired_order
all_genes_df = pd.DataFrame({'Metric': all_metrics})

for file_key in results:
    all_genes_metrics = results[file_key].get('All Genes', {})
    metrics_values = [all_genes_metrics.get(metric, np.nan) for metric in all_metrics]
    all_genes_df[file_key] = metrics_values

# Prepare Genes DataFrames
all_genes_set = set()
for file_key in results:
    genes = results[file_key].get('Genes', {}).keys()
    all_genes_set.update(genes)
genes_list = sorted(all_genes_set)

genes_dfs = {}
for gene in genes_list:
    gene_metrics_df = pd.DataFrame({'Metric': desired_order})
    for file_key in results:
        gene_metrics = results[file_key].get('Genes', {}).get(gene, {})
        metrics_values = [gene_metrics.get(metric, np.nan) for metric in desired_order]
        gene_metrics_df[file_key] = metrics_values
    genes_dfs[gene] = gene_metrics_df

# Prepare Exons DataFrames
exons_dfs = {}
for gene in genes_list:
    exons_dfs[gene] = {}
    exons_set = set()
    for file_key in results:
        exons = results[file_key].get('Exons', {}).get(gene, {}).keys()
        exons_set.update(exons)
    exons_list = sorted(exons_set)

    for exon in exons_list:
        exon_metrics_df = pd.DataFrame({'Metric': desired_order})
        for file_key in results:
            exon_metrics = results[file_key].get('Exons', {}).get(gene, {}).get(exon, {})
            metrics_values = [exon_metrics.get(metric, np.nan) for metric in desired_order]
            exon_metrics_df[file_key] = metrics_values
        exons_dfs[gene][exon] = exon_metrics_df

with tab1:
    st.write(f"Analyzing BAM file: {st.session_state.bam_cram_selected}")

    if st.session_state.analysis in ['Gene Panel', 'Exome']:
        with st.container():
            st.write("Overview")

        with st.container():
            # Use 'metrics_dict' instead of 'columns' to represent the metrics
            metrics_dict = {
                "Basic Information": ["Average Read Depth", "Size Coding", "Size Covered"],
                "Coverage": ["Coverage (0-1x)", "Coverage (2-10x)", "Coverage (11-15x)", "Coverage (16-20x)",
                             "Coverage (21-30x)", "Coverage (31-50x)", "Coverage (51-100x)", "Coverage (101-500x)", 'Coverage (>500x)'],
                "Coverage Percentage": ["Coverage % (1x)", "Coverage % (10x)", "Coverage % (15x)", "Coverage % (20x)",
                                        "Coverage % (30x)", "Coverage % (50x)", "Coverage % (100x)", "Coverage % (500x)"]
            }

            # Initialize checkboxes as selected by default if not in session state
            for category in metrics_dict:
                for metric in metrics_dict[category]:
                    if f"tab1_metric_{metric}" not in st.session_state:
                        st.session_state[f"tab1_metric_{metric}"] = True

            with st.popover("Filters"):
                st.subheader("Select Metrics to Display")

                all_selected = all(
                    st.session_state.get(f"tab1_metric_{metric}", False)
                    for metrics_list in metrics_dict.values()
                    for metric in metrics_list
                )

                if st.button("Select All" if not all_selected else "Deselect All", key="tab1_select_all"):
                    select_all_metrics(not all_selected, metrics_dict, "tab1")
                    st.rerun()

                col1, col2, col3 = st.columns(3)
                metrics_keys = list(metrics_dict.keys())

                for i, section in enumerate(metrics_keys):
                    with [col1, col2, col3][i % 3]:
                        st.write(f"**{section}**")
                        for metric in metrics_dict[section]:
                            st.checkbox(metric, key=f"tab1_metric_{metric}")

            # Selecting checked metrics
            selected_metrics = [
                metric
                for metrics_list in metrics_dict.values()
                for metric in metrics_list
                if st.session_state.get(f"tab1_metric_{metric}", False)
            ]
            final_metrics = ['Metric'] + [col for col in all_genes_df.columns if col != 'Metric']
            metrics_df = all_genes_df[all_genes_df['Metric'].isin(selected_metrics)].reset_index(drop=True)

            # Display the DataFrame
            st.dataframe(metrics_df[final_metrics], hide_index=True, height=738, width=800)

    elif st.session_state.analysis == 'Single Gene':
        st.write('Test')

with tab2:
    with st.container():
        if not genes_list:
            st.warning("No genes found in the results.")
        else:
            gene = st.selectbox("Select Gene", genes_list, key="gene_selectbox")
            gene_metrics_df = genes_dfs[gene]

            # Filters for tab2
            metrics_dict = {
                "Basic Information": ["Average Read Depth", "Size Coding", "Size Covered"],
                "Coverage": ["Coverage (0-1x)", "Coverage (2-10x)", "Coverage (11-15x)", "Coverage (16-20x)",
                             "Coverage (21-30x)", "Coverage (31-50x)", "Coverage (51-100x)", "Coverage (101-500x)", 'Coverage (>500x)'],
                "Coverage Percentage": ["Coverage % (1x)", "Coverage % (10x)", "Coverage % (15x)", "Coverage % (20x)",
                                        "Coverage % (30x)", "Coverage % (50x)", "Coverage % (100x)", "Coverage % (500x)"]
            }

            for category in metrics_dict:
                for metric in metrics_dict[category]:
                    if f"tab2_metric_{metric}" not in st.session_state:
                        st.session_state[f"tab2_metric_{metric}"] = True

            with st.popover("Filters"):
                st.subheader("Select Metrics to Display")

                all_selected = all(
                    st.session_state.get(f"tab2_metric_{metric}", False)
                    for metrics_list in metrics_dict.values()
                    for metric in metrics_list
                )

                if st.button("Select All" if not all_selected else "Deselect All", key="tab2_select_all"):
                    select_all_metrics(not all_selected, metrics_dict, "tab2")
                    st.rerun()

                col1, col2, col3 = st.columns(3)
                metrics_keys = list(metrics_dict.keys())

                for i, section in enumerate(metrics_keys):
                    with [col1, col2, col3][i % 3]:
                        st.write(f"**{section}**")
                        for metric in metrics_dict[section]:
                            st.checkbox(metric, key=f"tab2_metric_{metric}")

            # Filter the DataFrame based on selected metrics
            selected_metrics = [
                metric
                for metrics_list in metrics_dict.values()
                for metric in metrics_list
                if st.session_state.get(f"tab2_metric_{metric}", False)
            ]
            df = gene_metrics_df[gene_metrics_df['Metric'].isin(selected_metrics)].reset_index(drop=True)
            final_metrics = ['Metric'] + [col for col in df.columns if col != 'Metric']

            # Display the DataFrame
            st.dataframe(df[final_metrics], hide_index=True, height=738, width=800)

with tab3:
    with st.container():
        if not genes_list:
            st.warning("No genes found in the results.")
        else:
            gene = st.selectbox("Select Gene", genes_list, key="exon_gene_selectbox")
            exons_list = sorted(exons_dfs[gene].keys())
            if not exons_list:
                st.warning(f"No exons found for gene {gene}.")
            else:
                exon = st.selectbox("Select Exon", exons_list, key="exon_selectbox")
                exon_metrics_df = exons_dfs[gene][exon]

                # Filters for tab3
                metrics_dict = {
                    "Basic Information": ["Average Read Depth", "Size Coding", "Size Covered"],
                    "Coverage": ["Coverage (0-1x)", "Coverage (2-10x)", "Coverage (11-15x)", "Coverage (16-20x)",
                                 "Coverage (21-30x)", "Coverage (31-50x)", "Coverage (51-100x)", "Coverage (101-500x)", 'Coverage (>500x)'],
                    "Coverage Percentage": ["Coverage % (1x)", "Coverage % (10x)", "Coverage % (15x)", "Coverage % (20x)",
                                            "Coverage % (30x)", "Coverage % (50x)", "Coverage % (100x)", "Coverage % (500x)"]
                }

                for category in metrics_dict:
                    for metric in metrics_dict[category]:
                        if f"tab3_metric_{metric}" not in st.session_state:
                            st.session_state[f"tab3_metric_{metric}"] = True

                with st.popover("Filters"):
                    st.subheader("Select Metrics to Display")

                    all_selected = all(
                        st.session_state.get(f"tab3_metric_{metric}", False)
                        for metrics_list in metrics_dict.values()
                        for metric in metrics_list
                    )

                    if st.button("Select All" if not all_selected else "Deselect All", key="tab3_select_all"):
                        select_all_metrics(not all_selected, metrics_dict, "tab3")
                        st.rerun()

                    col1, col2, col3 = st.columns(3)
                    metrics_keys = list(metrics_dict.keys())

                    for i, section in enumerate(metrics_keys):
                        with [col1, col2, col3][i % 3]:
                            st.write(f"**{section}**")
                            for metric in metrics_dict[section]:
                                st.checkbox(metric, key=f"tab3_metric_{metric}")

                # Filter the DataFrame based on selected metrics
                selected_metrics = [
                    metric
                    for metrics_list in metrics_dict.values()
                    for metric in metrics_list
                    if st.session_state.get(f"tab3_metric_{metric}", False)
                ]
                df = exon_metrics_df[exon_metrics_df['Metric'].isin(selected_metrics)].reset_index(drop=True)
                final_metrics = ['Metric'] + [col for col in df.columns if col != 'Metric']

                # Display the DataFrame
                st.dataframe(df[final_metrics], hide_index=True, height=738, width=800)
