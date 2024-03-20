# Importando bibliotecas
import streamlit as st
import pandas as pd
from pathlib import Path
from components import streamlit_page_config
from components import logo

# Configurando página do Streamlit
streamlit_page_config.set_page_configuration()

logo.add_logo()

# Função para adicionar novos painéis ao DataFrame
def add_panel_to_csv(panel_name, genes_lst):
    # Criando um DataFrame com os novos dados
    new_row = pd.DataFrame({'Panel_Name_EN_EMEDGENE': [panel_name], 'Genes': [genes_lst]})
    
    # Verificando se o arquivo CSV já existe
    csv_path = 'data/regions/gene_panels/BED_Files_Emedgene_2.csv'
    if Path(csv_path).is_file():
        # Se existir, carregue o CSV e adicione a nova linha
        data = pd.read_csv(csv_path)
        data = pd.concat([data, new_row])
    else:
        # Se não existir, crie um novo DataFrame com a nova linha
        data = new_row
    
    # Salvando o DataFrame atualizado de volta ao CSV
    data.to_csv(csv_path)
    
    return data


def set_name(panel_name, genes_lst):
    st.session_state.panel_name = panel_name
    st.session_state.genes_lst = genes_lst
    
# Step 1 - Criando novo painel de genes
st.markdown("# Gene panel builder\n#")
with st.container(border = True):
    st.markdown("## :red[Step 1.] Create new Gene Panel\n")
    panel_name = st.text_input(label='Panel Name', placeholder='Insert a name for the Panel', key='panel_name')
    genes_lst = st.text_area(label='Genes', placeholder='Insert the genes for the panel', key='genes_lst')

    if st.button('Create Gene Panel', on_click=set_name, args=[panel_name, genes_lst], type="primary"):
        if panel_name and genes_lst:
            # Adicionando novo painel ao DataFrame
            add_panel_to_csv(panel_name, genes_lst)
            st.success(f'Gene Panel {panel_name} created successfully!')
        else:
            st.warning('Please fill in all the fields!')
    
    if panel_name or genes_lst:
        if st.button('Reset', on_click=set_name, args=['',''], type="secondary"):
            st.warning('Gene Panel reset successfully!')

# Step 2 - Exibindo lista de painéis de genes
with st.container(border = True):
    st.markdown("## :red[Step 2.] Gene Panel list\n")
    # Carregando o DataFrame do CSV
    data = pd.read_csv('data/regions/gene_panels/BED_Files_Emedgene_2.csv')
    # Selecionando apenas as colunas desejadas
    data = data[['Panel_Name_EN_EMEDGENE', 'Genes']]
    st.data_editor(data, use_container_width=True, num_rows="dynamic")
