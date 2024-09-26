import streamlit as st
import pandas as pd
from components import metrics, plot, session_state
import numpy as np
import io
from weasyprint import HTML
import base64
import datetime

sidebar_logo = "data/img/unilabs_logo.png"
main_body_logo = "data/img/thumbnail_image001.png"
st.logo(sidebar_logo)
st.logo(main_body_logo)

st.title("Results")

@st.fragment
def render_metric_filters(tab_name, metrics_dict):
    with st.popover("Filters"):
        st.subheader("Select Metrics to Display")

        # Verifica se todas as métricas estão selecionadas
        all_selected = all(
            st.session_state.get(f"{tab_name}_metric_{metric}", False)
            for metrics_list in metrics_dict.values()
            for metric in metrics_list
        )

        # Botão para selecionar/deselecionar todas as métricas
        if st.button("Select All" if not all_selected else "Deselect All", key=f"{tab_name}_select_all"):
            select_all_metrics(not all_selected, metrics_dict, tab_name)
            st.rerun()

        # Divide a UI em 3 colunas
        col1, col2, col3 = st.columns(3)
        metrics_keys = list(metrics_dict.keys())

        # Exibe as métricas dentro das colunas
        for i, section in enumerate(metrics_keys):
            with [col1, col2, col3][i % 3]:
                st.write(f"**{section}**")
                for metric in metrics_dict[section]:
                    st.checkbox(metric, key=f"{tab_name}_metric_{metric}")


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
all_metrics.insert(3, 'Average Read Depth (Gene Weighted)')
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

# Download Report section
with st.status("Building the report...")as status:
    if len(file_names) > 1:
        # If there are multiple samples, allow the user to select one
        selected_sample = st.selectbox("Select Sample", file_names)
    else:
        # If there's only one sample, select it by default
        selected_sample = file_names[0]
        
        st.write(f'Download {selected_sample} report file (.pdf)')
    # Generate PDF report for the selected sample
    # Get the current date and time
    report_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Build an HTML string
    html_content = """
    <html>
    <head>
    <style>
    body {
        font-family: Arial, sans-serif;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        font-size: 10pt;
    }
    th, td {
        text-align: left;
        padding: 8px;
        border: 1px solid #dddddd;
    }
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    h2, h3 {
        color: #2F5496;
    }
    </style>
    </head>
    <body>
    """
    # Add Unilabs logo
    # Encode the logo image to base64
    with open(sidebar_logo, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    html_content += f'<img src="data:image/png;base64,{encoded_string}" alt="Unilabs Logo" style="width:200px;"><br><br>'
    # Add report generation date
    html_content += f'<p>Report generated on: {report_date}</p>'
    # Add Overview DataFrame for the selected sample
    html_content += f'<h2>Overview - Sample: {selected_sample}</h2>'
    if st.session_state.analysis in ['Gene Panel']:
        html_content += f'<p>Gene Panel: {st.session_state.panel_name}</p>'
        overview_df = all_genes_df[['Metric', selected_sample]]
        html_content += overview_df.to_html(index=False)
    if st.session_state.analysis in ['Exome']:
        html_content += f'<p>Exome</p>'
        overview_df = all_genes_df[['Metric', selected_sample]]
        html_content += overview_df.to_html(index=False)
    elif st.session_state.analysis in ['Single Gene']:
        # Add Gene DataFrames for the selected sample
        for gene_name, gene_df in genes_dfs.items():
            gene_sample_df = gene_df[['Metric', selected_sample]]
            if gene_sample_df[selected_sample].notna().any():
                html_content += f'<h2>Gene: {gene_name}</h2>'
                html_content += gene_sample_df.to_html(index=False)
        # Add Exon DataFrames for the selected sample
        for gene_name, exons_dict in exons_dfs.items():
            for exon_name, exon_df in exons_dict.items():
                exon_sample_df = exon_df[['Metric', selected_sample]]
                if exon_sample_df[selected_sample].notna().any():
                    html_content += f'<h3>Exon: {exon_name} (Gene: {gene_name})</h3>'
                    html_content += exon_sample_df.to_html(index=False)
    html_content += '</body></html>'
    # Convert HTML to PDF using WeasyPrint
    html_obj = HTML(string=html_content)
    pdf_bytes = html_obj.write_pdf()
    status.update(label="Generating PDF...")
    # Provide download button
    st.download_button(
        label="Download",
        data=pdf_bytes,
        file_name=f'report_{selected_sample}.pdf',
        mime='application/pdf'
    )
    status.update(label="Report ready for download", expanded=True)

# Determine which tabs to display based on st.session_state.analysis
if st.session_state.analysis == 'Gene Panel':
    tab_names = ["Overview", "Gene Detail", "Exon Detail"]
elif st.session_state.analysis in ['Single Gene', 'Exome']:
    tab_names = ["Gene Detail", "Exon Detail"]
else:
    st.warning("Unsupported analysis type.")
    tab_names = []

# Create the tabs
tabs = st.tabs(tab_names)

# Map tab names to tab objects for easy reference
tab_dict = dict(zip(tab_names, tabs))

@st.fragment
def select_all_metrics(select_all, metrics_dict, key_prefix):
    """Function to select or deselect all metrics."""
    for section, metrics_list in metrics_dict.items():
        for metric in metrics_list:
            st.session_state[f"{key_prefix}_metric_{metric}"] = select_all

if "Overview" in tab_dict:
    with tab_dict["Overview"]:
        st.write(f"Date: {report_date}")
        st.write(f"Analyzing file(s): {file_names}")
        st.write(f"Gene Panel: {st.session_state.panel_name}")

        if st.session_state.analysis in ['Gene Panel', 'Exome']:
            
            with st.container():
                # Use 'metrics_dict' instead of 'columns' to represent the metrics
                metrics_dict = {
                    "Basic Information": ["Average Read Depth",'Average Read Depth (Gene Weighted)', "Size Coding", "Size Covered"],
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

                render_metric_filters("tab1", metrics_dict)


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
                if st.session_state.analysis in ['Gene Panel', 'Exome']:
                    plot.display_graphs()

if "Gene Detail" in tab_dict:
    with tab_dict["Gene Detail"]:
        st.write(f"Date: {report_date}")
        st.write(f"Analyzing file(s): {file_names}")
        
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

                render_metric_filters("tab2", metrics_dict)


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
                if st.session_state.analysis in ['Single Gene']:
                    plot.display_graphs()
if "Exon Detail" in tab_dict:
    with tab_dict["Exon Detail"]:
        st.write(f"Date: {report_date}")
        st.write(f"Analyzing file(s): {file_names}")
        
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

                    render_metric_filters("tab3", metrics_dict)


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
