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

def select_all_columns(select_all, columns):
    """Função para selecionar ou desmarcar todas as colunas."""
    for section, cols in columns.items():
        for col in cols:
            st.session_state[f"col_{col}"] = select_all


# Call the calculate_metrics function and store results
all_genes, genes_data, exons_data = metrics.calculate_metrics()

# Ordem desejada das métricas
desired_order = [
    'Size Coding', 'Size Covered', 'Average Read Depth', 'Min Read Depth', 'Max Read Depth',
    'Coverage (0-1x)', 'Coverage (2-10x)', 'Coverage (11-15x)', 'Coverage (16-20x)',
    'Coverage (21-30x)', 'Coverage (31-50x)', 'Coverage (51-100x)', 'Coverage (101-500x)',
    'Coverage % (1x)', 'Coverage % (10x)', 'Coverage % (15x)', 'Coverage % (20x)',
    'Coverage % (30x)', 'Coverage % (50x)', 'Coverage % (100x)', 'Coverage % (500x)'
]

with tab1:
    # Mostrar o nome do arquivo BAM e a data de análise
    st.write(f"Analyzing BAM file: {st.session_state.bam_cram_selected}")
    if st.session_state.analysis == 'Gene Panel' or 'Exome':
        with st.container():
            st.write("Overview")

        with st.container():
            # Definir a estrutura de colunas e categorias
            columns = {
                "Basic Information": ["Average Read Depth", "Size Coding", "Size Covered"],
                "Coverage": ["Coverage (0-1x)", "Coverage (2-10x)", "Coverage (11-15x)", "Coverage (16-20x)",
                             "Coverage (21-30x)", "Coverage (31-50x)", "Coverage (51-100x)", "Coverage (101-500x)"],
                "Coverage Percentage": ["Coverage % (1x)", "Coverage % (10x)", "Coverage % (15x)", "Coverage % (20x)",
                                        "Coverage % (30x)", "Coverage % (50x)", "Coverage % (100x)", "Coverage % (500x)"]
            }
            
            # Inicializar checkboxes como selecionadas por padrão se não estiverem no estado da sessão
            for category in columns:
                for col in columns[category]:
                    if f"col_{col}" not in st.session_state:
                        st.session_state[f"col_{col}"] = True
            
            with st.container():
                # Seção de filtros com popover
                with st.popover("Filters"):
                    st.subheader("Select Columns to Display")
            
                    # Verificar se todas as colunas estão selecionadas
                    all_selected = all(st.session_state.get(f"col_{col}", False) for section in columns.values() for col in section)
            
                    # Botão para selecionar/desmarcar todas as colunas
                    if st.button("Select All" if not all_selected else "Deselect All"):
                        select_all_columns(not all_selected, columns)
                        st.experimental_rerun()
            
                    # Organizar as checkboxes em três colunas
                    col1, col2, col3 = st.columns(3)
                    columns_keys = list(columns.keys())
            
                    for i, section in enumerate(columns_keys):
                        with [col1, col2, col3][i % 3]:
                            st.write(f"**{section}**")
                            for col in columns[section]:
                                st.checkbox(col, key=f"col_{col}")
            
                # Seção de exibição de dados
                # Colunas obrigatórias
                mandatory_columns = ["Date", "BAM", "Region"]
            
                # Selecionar colunas marcadas nas checkboxes
                selected_columns = [col for section in columns.values() for col in section if st.session_state.get(f"col_{col}", False)]
                final_columns = mandatory_columns + selected_columns
            
                # Garantir a ordenação das colunas conforme a ordem desejada
                desired_order = mandatory_columns + [col for section in columns.values() for col in section]
                final_columns = [col for col in desired_order if col in final_columns]
            
                # Filtrar os dados baseando-se nas colunas selecionadas
                filtered_data = {col: all_genes.iloc[0].get(col, None) for col in final_columns}
                df = pd.DataFrame([filtered_data])
            
                # Exibir o DataFrame com as colunas filtradas
                st.dataframe(df, hide_index=True, height=492, width=205)
    elif st.session_state.analysis == 'Single Gene':
        st.write('Test')
with tab2:
        
    with st.container():
        # Selecionar o gene para exibir detalhes
        gene = st.selectbox("Select Gene", genes_data.index, key="gene_selectbox")

        # Mostrar as métricas do gene selecionado
        df = genes_data.loc[gene].reset_index().rename(columns={'index': 'Metric', gene: 'Value'})
        st.dataframe(df, hide_index=True, height=492, width=205)

with tab3:
    with st.container():
        st.write("Exon Detail")

    with st.container():
        # Selecionar o gene e exão para exibir detalhes
        gene = st.selectbox("Select Gene", exons_data.index.get_level_values(0).unique(), key="exon_gene_selectbox")
        exon = st.selectbox("Select Exon", exons_data.loc[gene].index, key="exon_selectbox")

        # Mostrar as métricas do exão selecionado
        df = exons_data.loc[(gene, exon)].reset_index().rename(columns={'index': 'Metric', (gene, exon): 'Value'})
        st.dataframe(df, hide_index=True, height=528, width=205)