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

def select_all_columns(select_all, columns, key_prefix):
    """Function to select or deselect all columns."""
    for section, cols in columns.items():
        for col in cols:
            st.session_state[f"{key_prefix}_col_{col}"] = select_all

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
            columns = {
                "Basic Information": ["Average Read Depth", "Size Coding", "Size Covered"],
                "Coverage": ["Coverage (0-1x)", "Coverage (2-10x)", "Coverage (11-15x)", "Coverage (16-20x)",
                             "Coverage (21-30x)", "Coverage (31-50x)", "Coverage (51-100x)", "Coverage (101-500x)", 'Coverage (>500x)'],
                "Coverage Percentage": ["Coverage % (1x)", "Coverage % (10x)", "Coverage % (15x)", "Coverage % (20x)",
                                        "Coverage % (30x)", "Coverage % (50x)", "Coverage % (100x)", "Coverage % (500x)"]
            }

            # Initialize checkboxes as selected by default if not in session state
            for category in columns:
                for col in columns[category]:
                    if f"tab1_col_{col}" not in st.session_state:
                        st.session_state[f"tab1_col_{col}"] = True
            
            with st.popover("Filters"):
                st.subheader("Select Columns to Display")

                all_selected = all(st.session_state.get(f"tab1_col_{col}", False) for section in columns.values() for col in section)

                if st.button("Select All" if not all_selected else "Deselect All", key="tab1_select_all"):
                    select_all_columns(not all_selected, columns, "tab1")
                    st.rerun()

                col1, col2, col3 = st.columns(3)
                columns_keys = list(columns.keys())

                for i, section in enumerate(columns_keys):
                    with [col1, col2, col3][i % 3]:
                        st.write(f"**{section}**")
                        for col in columns[section]:
                            st.checkbox(col, key=f"tab1_col_{col}")

            # Selecting checked columns
            selected_columns = [col for section in columns.values() for col in section if st.session_state.get(f"tab1_col_{col}", False)]
            final_columns = selected_columns

            # Filter the DataFrame
            metrics_df = all_genes_df[all_genes_df['Metric'].isin(final_columns)].reset_index(drop=True)

            # Display the DataFrame
            st.dataframe(metrics_df, hide_index=True, height=738, width=800)

    elif st.session_state.analysis == 'Single Gene':
        st.write('Test')

with tab2:
    with st.container():
        gene = st.selectbox("Select Gene", genes_list, key="gene_selectbox")
        gene_metrics_df = genes_dfs[gene]

        # Filters for tab2
        columns = {
            "Basic Information": ["Average Read Depth", "Size Coding", "Size Covered"],
            "Coverage": ["Coverage (0-1x)", "Coverage (2-10x)", "Coverage (11-15x)", "Coverage (16-20x)",
                         "Coverage (21-30x)", "Coverage (31-50x)", "Coverage (51-100x)", "Coverage (101-500x)", 'Coverage (>500x)'],
            "Coverage Percentage": ["Coverage % (1x)", "Coverage % (10x)", "Coverage % (15x)", "Coverage % (20x)",
                                    "Coverage % (30x)", "Coverage % (50x)", "Coverage % (100x)", "Coverage % (500x)"]
        }

        for category in columns:
            for col in columns[category]:
                if f"tab2_col_{col}" not in st.session_state:
                    st.session_state[f"tab2_col_{col}"] = True
        
        with st.popover("Filters"):
            st.subheader("Select Columns to Display")

            all_selected = all(st.session_state.get(f"tab2_col_{col}", False) for section in columns.values() for col in section)

            if st.button("Select All" if not all_selected else "Deselect All", key="tab2_select_all"):
                select_all_columns(not all_selected, columns, "tab2")
                st.rerun()

            col1, col2, col3 = st.columns(3)
            columns_keys = list(columns.keys())

            for i, section in enumerate(columns_keys):
                with [col1, col2, col3][i % 3]:
                    st.write(f"**{section}**")
                    for col in columns[section]:
                        st.checkbox(col, key=f"tab2_col_{col}")

        # Filter the DataFrame based on selected columns
        selected_columns = [col for section in columns.values() for col in section if st.session_state.get(f"tab2_col_{col}", False)]
        df = gene_metrics_df[gene_metrics_df['Metric'].isin(selected_columns)].reset_index(drop=True)

        # Display the DataFrame
        st.dataframe(df, hide_index=True, height=738, width=800)

with tab3:
    with st.container():
        gene = st.selectbox("Select Gene", genes_list, key="exon_gene_selectbox")
        exons_list = sorted(exons_dfs[gene].keys())
        exon = st.selectbox("Select Exon", exons_list, key="exon_selectbox")
        exon_metrics_df = exons_dfs[gene][exon]

        # Filters for tab3
        columns = {
            "Basic Information": ["Average Read Depth", "Size Coding", "Size Covered"],
            "Coverage": ["Coverage (0-1x)", "Coverage (2-10x)", "Coverage (11-15x)", "Coverage (16-20x)",
                         "Coverage (21-30x)", "Coverage (31-50x)", "Coverage (51-100x)", "Coverage (101-500x)", 'Coverage (>500x)'],
            "Coverage Percentage": ["Coverage % (1x)", "Coverage % (10x)", "Coverage % (15x)", "Coverage % (20x)",
                                    "Coverage % (30x)", "Coverage % (50x)", "Coverage % (100x)", "Coverage % (500x)"]
        }

        for category in columns:
            for col in columns[category]:
                if f"tab3_col_{col}" not in st.session_state:
                    st.session_state[f"tab3_col_{col}"] = True
        
        with st.popover("Filters"):
            st.subheader("Select Columns to Display")

            all_selected = all(st.session_state.get(f"tab3_col_{col}", False) for section in columns.values() for col in section)

            if st.button("Select All" if not all_selected else "Deselect All", key="tab3_select_all"):
                select_all_columns(not all_selected, columns, "tab3")
                st.rerun()

            col1, col2, col3 = st.columns(3)
            columns_keys = list(columns.keys())

            for i, section in enumerate(columns_keys):
                with [col1, col2, col3][i % 3]:
                    st.write(f"**{section}**")
                    for col in columns[section]:
                        st.checkbox(col, key=f"tab3_col_{col}")

        # Filter the DataFrame based on selected columns
        selected_columns = [col for section in columns.values() for col in section if st.session_state.get(f"tab3_col_{col}", False)]
        df = exon_metrics_df[exon_metrics_df['Metric'].isin(selected_columns)].reset_index(drop=True)

        # Display the DataFrame
        st.dataframe(df, hide_index=True, height=738, width=800)
