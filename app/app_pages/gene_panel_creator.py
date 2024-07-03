import streamlit as st
import pandas as pd

def panel_creator(panel_df):
    df = pd.DataFrame(panel_df)
    panel_name = st.text_input("Panel Name", placeholder="Enter Panel Name")
    genes = st.text_area("Add Genes", placeholder="Enter gene symbols separated by commas")
    if st.button("Create Panel"):
        # Add the new panel to the DataFrame and save to CSV
        new_panel = {'Panel Name PT (Klims)': panel_name, 'Genes': genes}
        df = pd.concat([df, pd.DataFrame([new_panel])], ignore_index=True)
        df.to_csv('data/regions/gene_panels/BED_Files_Emedgene_2.csv', sep=';', index=False, encoding="latin1")  # Save updated DataFrame to CSV
        st.success("Panel created successfully!", icon=":material/check:")
        st.rerun() #TO IMPROVE: not the ideal way to rerun the page
        


def download_panel(panel_df, universal_bed_df):
    # Converter o DataFrame do painel para uma lista de nomes de painéis únicos
    panel_lst = panel_df['Panel Name PT (Klims)'].unique().tolist()
    
    # Criar uma caixa de seleção no Streamlit para selecionar o painel
    panel = st.selectbox('Select a gene panel', panel_lst, index=None, key="region", label_visibility="collapsed", placeholder="Select a gene panel")
    
    if panel:
        # Esconder o índice e linhas em branco na tabela
        hide_streamlit_style = """
        <style>
        tbody th {display:none}
        .blank{
        display: none;
        }
        </style>
        """
        st.markdown(hide_streamlit_style, unsafe_allow_html=True)
        
        # Mostrar os genes do painel selecionado
        genes_str = panel_df[panel_df['Panel Name PT (Klims)'] == panel]["Genes"].values[0]
        genes_lst = [gene.strip() for gene in genes_str.split(',')]
        st.data_editor(panel_df[panel_df['Panel Name PT (Klims)'] == panel]["Genes"], hide_index=True, use_container_width=True)
        
        # Filtrar o arquivo BED universal para incluir apenas as linhas correspondentes aos genes selecionados
        filtered_bed = universal_bed_df[universal_bed_df[3].isin(genes_lst)]
        
        # Encontrar genes que não estão na BED universal
        not_found_genes = [gene for gene in genes_lst if gene not in universal_bed_df[3].values]
        count = len(not_found_genes)
        if not_found_genes:
            st.warning(f"{count} genes not found in the universal BED file: {', '.join(not_found_genes)}")
        
        # Fornecer um botão para download do arquivo BED filtrado
        st.download_button(
            label="Download BED",
            data=filtered_bed.to_csv(sep='\t', header=False, index=False).encode("utf-8"),
            file_name=f"{panel}.bed",
            mime="text/bed"
        )
        

# Ler os dados dos painéis e do BED universal dos arquivos CSV
panel_df = pd.read_csv('data/regions/gene_panels/BED_Files_Emedgene_2.csv', sep=';', header=0, encoding='latin1')
universal_bed_df = pd.read_csv('data/regions/genome_exons/hg38_Twist_ILMN_Exome_2.0_Plus_Panel_annotated_modif.BED', sep='\t', header=None)

st.title("Gene Panel Creator")
panel_creator(panel_df)
# Executar o aplicativo Streamlit
st.title("Download BED Panel")
download_panel(panel_df, universal_bed_df)







#@st.cache_data
#def convert_df(df):
#    # IMPORTANT: Cache the conversion to prevent computation on every rerun
#    return df.to_csv().encode("utf-8")
#
#csv = convert_df(my_large_df)
#
#st.download_button(
#    label="Download data as CSV",
#    data=csv,
#    file_name="large_df.csv",
#    mime="text/csv",
#)