import streamlit as st
import pandas as pd
from components import metrics, plot, session_state
import numpy as np
from weasyprint import HTML
import base64
import datetime
import time

# Load logos
sidebar_logo = "data/img/unilabs_logo.png"
main_body_logo = "data/img/thumbnail_image001.png"
st.logo(sidebar_logo, icon_image=main_body_logo)

st.title("Results")

# Desired order of metrics
desired_order = [
    'Size Coding', 'Size Covered', 'Breadth of Coverage %', 'Average Read Depth', 'Min Read Depth', 'Max Read Depth',
    'Depth of Coverage (0-1x)', 'Depth of Coverage (2-10x)', 'Depth of Coverage (11-15x)', 'Depth of Coverage (16-20x)',
    'Depth of Coverage (21-30x)', 'Depth of Coverage (31-50x)', 'Depth of Coverage (51-100x)',
    'Depth of Coverage (101-500x)', 'Depth of Coverage (>500x)', 'Depth of Coverage % (1x)',
    'Depth of Coverage % (10x)', 'Depth of Coverage % (15x)', 'Depth of Coverage % (20x)',
    'Depth of Coverage % (30x)', 'Depth of Coverage % (50x)', 'Depth of Coverage % (100x)',
    'Depth of Coverage % (500x)'
]

# Function to select or deselect all metrics
def select_all_metrics(select_all, metrics_dict, key_prefix):
    """Function to select or deselect all metrics."""
    for section, metrics_list in metrics_dict.items():
        for metric in metrics_list:
            st.session_state[f"{key_prefix}_metric_{metric}"] = select_all

# Function to render metric filters
@st.fragment
def render_metric_filters(tab_name, metrics_dict):
    with st.popover("Filters"):
        st.subheader("Select Metrics to Display")

        # Check if all metrics are selected
        all_selected = all(
            st.session_state.get(f"{tab_name}_metric_{metric}", False)
            for metrics_list in metrics_dict.values()
            for metric in metrics_list
        )

        # Button to select/deselect all metrics
        if st.button("Select All" if not all_selected else "Deselect All", key=f"{tab_name}_select_all"):
            select_all_metrics(not all_selected, metrics_dict, tab_name)
            st.rerun(scope="fragment")

        # Divide the UI into 3 columns
        col1, col2, col3 = st.columns(3)
        metrics_keys = list(metrics_dict.keys())

        # Display metrics within columns
        for i, section in enumerate(metrics_keys):
            with [col1, col2, col3][i % 3]:
                st.write(f"**{section}**")
                for metric in metrics_dict[section]:
                    st.checkbox(metric, key=f"{tab_name}_metric_{metric}")

# Main code
if st.session_state.get('results', False):
    with st.spinner('Generating Results...'):
        results = metrics.calculate_metrics()
        file_names = list(results.keys())

        # Prepare All Genes DataFrame
        all_metrics = desired_order.copy()
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
        with st.status("Building the report...") as status:
            if len(file_names) > 1:
                selected_sample = st.selectbox("Select Sample", file_names)
            else:
                selected_sample = file_names[0]
                st.write(f'Download {selected_sample} report file (.pdf)')

            report_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Build an HTML string
            html_content = "<html><head><style>"
            html_content += """
            body { font-family: Arial, sans-serif; }
            table { border-collapse: collapse; width: 100%; font-size: 10pt; }
            th, td { text-align: left; padding: 8px; border: 1px solid #dddddd; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            h2, h3 { color: #2F5496; }
            </style></head><body>
            """

            # Add Unilabs logo
            with open(sidebar_logo, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
            html_content += f'<img src="data:image/png;base64,{encoded_string}" alt="Unilabs Logo" style="width:200px;"><br><br>'
            html_content += f'<p>Report generated on: {report_date}</p>'

            # Add Overview DataFrame for the selected sample
            html_content += f'<h2>Overview - Sample: {selected_sample}</h2>'
            if st.session_state.analysis in ['Gene Panel']:
                html_content += f'<p>Gene Panel: {st.session_state.panel_name}</p>'
            elif st.session_state.analysis in ['Exome']:
                html_content += f'<p>Exome</p>'
            overview_df = all_genes_df[['Metric', selected_sample]]
            html_content += overview_df.to_html(index=False)

            # Additional sections for Single Gene analysis
            if st.session_state.analysis in ['Single Gene']:
                for gene_name, gene_df in genes_dfs.items():
                    gene_sample_df = gene_df[['Metric', selected_sample]]
                    if gene_sample_df[selected_sample].notna().any():
                        html_content += f'<h2>Gene: {gene_name}</h2>'
                        html_content += gene_sample_df.to_html(index=False)
                for gene_name, exons_dict in exons_dfs.items():
                    for exon_name, exon_df in exons_dict.items():
                        exon_sample_df = exon_df[['Metric', selected_sample]]
                        if exon_sample_df[selected_sample].notna().any():
                            html_content += f'<h3>Exon: {exon_name} (Gene: {gene_name})</h3>'
                            html_content += exon_sample_df.to_html(index=False)

            html_content += '</body></html>'

            # Convert HTML to PDF
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

        # Functions for each tab
        @st.fragment
        def overview_tab():
            st.write(f"Date: {report_date}")
            st.write(f"Analyzing file(s): {file_names}")
            st.write(f"Gene Panel: {st.session_state.panel_name}")

            metrics_dict = {
                "Basic Information": ["Average Read Depth", "Size Coding", "Size Covered", 'Breadth of Coverage %',
                                      'Min Read Depth', 'Max Read Depth'],
                "Depth of Coverage": ["Depth of Coverage (0-1x)", "Depth of Coverage (2-10x)", "Depth of Coverage (11-15x)",
                                      "Depth of Coverage (16-20x)", "Depth of Coverage (21-30x)", "Depth of Coverage (31-50x)",
                                      "Depth of Coverage (51-100x)", "Depth of Coverage (101-500x)", 'Depth of Coverage (>500x)'],
                "Depth of Coverage Percentage": ["Depth of Coverage % (1x)", "Depth of Coverage % (10x)",
                                                 "Depth of Coverage % (15x)", "Depth of Coverage % (20x)",
                                                 "Depth of Coverage % (30x)", "Depth of Coverage % (50x)",
                                                 "Depth of Coverage % (100x)", "Depth of Coverage % (500x)"]
            }

            # Initialize checkboxes
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
            st.dataframe(metrics_df[final_metrics], hide_index=True, height=842, width=800)
            if st.session_state.analysis in ['Gene Panel', 'Exome']:
                if len(st.session_state.get('region', [])) < 3:
                    plot.display_graphs()
                else:
                    st.info("The plot was not generated due to the large volume of data")

        @st.fragment
        def gene_detail_tab():
            if not genes_list:
                st.warning("No genes found in the results.")
            else:
                gene = st.selectbox("Select Gene", genes_list, key="gene_selectbox")
                gene_metrics_df = genes_dfs[gene]

                metrics_dict = {
                    "Basic Information": ["Average Read Depth", "Size Coding", "Size Covered", 'Breadth of Coverage %',
                                          'Min Read Depth', 'Max Read Depth'],
                    "Depth of Coverage": ["Depth of Coverage (0-1x)", "Depth of Coverage (2-10x)", "Depth of Coverage (11-15x)",
                                          "Depth of Coverage (16-20x)", "Depth of Coverage (21-30x)", "Depth of Coverage (31-50x)",
                                          "Depth of Coverage (51-100x)", "Depth of Coverage (101-500x)", 'Depth of Coverage (>500x)'],
                    "Depth of Coverage Percentage": ["Depth of Coverage % (1x)", "Depth of Coverage % (10x)",
                                                     "Depth of Coverage % (15x)", "Depth of Coverage % (20x)",
                                                     "Depth of Coverage % (30x)", "Depth of Coverage % (50x)",
                                                     "Depth of Coverage % (100x)", "Depth of Coverage % (500x)"]
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
                st.dataframe(df[final_metrics], hide_index=True, height=842, width=800)
                if st.session_state.analysis in ['Single Gene']:
                    plot.display_graphs()

        @st.fragment
        def exon_detail_tab():
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

                    metrics_dict = {
                        "Basic Information": ["Average Read Depth", "Size Coding", "Size Covered", 'Breadth of Coverage %',
                                              'Min Read Depth', 'Max Read Depth'],
                        "Depth of Coverage": ["Depth of Coverage (0-1x)", "Depth of Coverage (2-10x)", "Depth of Coverage (11-15x)",
                                              "Depth of Coverage (16-20x)", "Depth of Coverage (21-30x)", "Depth of Coverage (31-50x)",
                                              "Depth of Coverage (51-100x)", "Depth of Coverage (101-500x)", 'Depth of Coverage (>500x)'],
                        "Depth of Coverage Percentage": ["Depth of Coverage % (1x)", "Depth of Coverage % (10x)",
                                                         "Depth of Coverage % (15x)", "Depth of Coverage % (20x)",
                                                         "Depth of Coverage % (30x)", "Depth of Coverage % (50x)",
                                                         "Depth of Coverage % (100x)", "Depth of Coverage % (500x)"]
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
                    st.dataframe(df[final_metrics], hide_index=True, height=842, width=800)

        # Render the tabs
        if "Overview" in tab_dict:
            with tab_dict["Overview"]:
                overview_tab()
        if "Gene Detail" in tab_dict:
            with tab_dict["Gene Detail"]:
                gene_detail_tab()
        if "Exon Detail" in tab_dict:
            with tab_dict["Exon Detail"]:
                exon_detail_tab()

else:
    st.info("No results to show!")
    time.sleep(2)
    st.switch_page("app_pages/query.py")
