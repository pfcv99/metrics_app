import streamlit as st
import pandas as pd
from components import metrics
import numpy as np
import plotly.figure_factory as ff

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

# Call the calculate_metrics function and store results
all_genes, genes_data, exons_data = metrics.calculate_metrics()

# Desired order of metrics
desired_order = [
    'Size Coding', 'Size Covered', 'Average Read Depth', 'Min Read Depth', 'Max Read Depth',
    'Coverage (0-1x)', 'Coverage (2-10x)', 'Coverage (11-15x)', 'Coverage (16-20x)',
    'Coverage (21-30x)', 'Coverage (31-50x)', 'Coverage (51-100x)', 'Coverage (101-500x)', 'Coverage (>500x)',
    'Coverage % (1x)', 'Coverage % (10x)', 'Coverage % (15x)', 'Coverage % (20x)',
    'Coverage % (30x)', 'Coverage % (50x)', 'Coverage % (100x)', 'Coverage % (500x)'
]

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

            mandatory_columns = ["Date", "BAM", "Region"]

            # Selecting checked columns
            selected_columns = [col for section in columns.values() for col in section if st.session_state.get(f"tab1_col_{col}", False)]
            final_columns = mandatory_columns + selected_columns

            # Ensure the ordering of columns according to desired order
            final_columns = [col for col in desired_order if col in final_columns]

            # Filtering data based on selected columns
            filtered_data = {col: all_genes.iloc[0].get(col, None) for col in final_columns}
            df = pd.DataFrame([filtered_data]).melt(var_name='Metric', value_name='Value')

            # Display the DataFrame
            st.dataframe(df, hide_index=True, height=738, width=205)
    elif st.session_state.analysis == 'Single Gene':
        st.write('Test')

with tab2:
    with st.container():
        gene = st.selectbox("Select Gene", genes_data.index, key="gene_selectbox")

        # Filter metrics for selected gene
        df = genes_data.loc[gene].reset_index().rename(columns={'index': 'Metric', gene: 'Value'})

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
        df = df[df['Metric'].isin(selected_columns)].reset_index(drop=True)

        # Display the DataFrame
        st.dataframe(df, hide_index=True, height=738, width=205)

with tab3:
    with st.container():
        st.write("Exon Detail")

    with st.container():
        gene = st.selectbox("Select Gene", exons_data.index.get_level_values(0).unique(), key="exon_gene_selectbox")
        exon = st.selectbox("Select Exon", exons_data.loc[gene].index, key="exon_selectbox")

        # Show metrics for the selected exon
        df = exons_data.loc[(gene, exon)].reset_index().rename(columns={'index': 'Metric', (gene, exon): 'Value'})

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
        df = df[df['Metric'].isin(selected_columns)].reset_index(drop=True)

        # Display the DataFrame
        st.dataframe(df, hide_index=True, height=772, width=205)
