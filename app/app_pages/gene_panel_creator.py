import streamlit as st
import pandas as pd
import time

if 'panel_name' not in st.session_state:
    st.session_state.panel_name = None
if 'genes' not in st.session_state:
    st.session_state.genes = None
if 'panel' not in st.session_state:
    st.session_state.panel = None

def panel_creator(panel_df):
    df = pd.DataFrame(panel_df)
    if st.button("Create Panel"):
        # Add the new panel to the DataFrame and save to CSV
        new_panel = {'Panel Name PT (Klims)': st.session_state.panel_name, 'Genes': st.session_state.genes}
        df = pd.concat([df, pd.DataFrame([new_panel])], ignore_index=True)
        df.to_excel('data/regions/gene_panels/BED_Files_Emedgene_2.xlsx', index=False)  # Save updated DataFrame to CSV
        progress_text = "Operation in progress. Please wait."
        my_bar = st.progress(0, text=progress_text)
        for percent_complete in range(100):
            time.sleep(0.01)
            my_bar.progress(percent_complete + 1, text=progress_text)
        time.sleep(1)
        my_bar.empty()
        st.success("Panel created successfully!", icon=":material/check:")
        time.sleep(2)
        st.rerun() #TO IMPROVE: not the ideal way to rerun the page
        


def download_panel(panel_df, universal_bed_df):
    
    if st.session_state.panel:
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
        genes_str = panel_df[panel_df['Panel Name PT (Klims)'] == st.session_state.panel]["Genes"].values[0]
        genes_lst = [gene.strip() for gene in genes_str.split(',')]
        st.data_editor(panel_df[panel_df['Panel Name PT (Klims)'] == st.session_state.panel]["Genes"], hide_index=True, use_container_width=True)
        with st.status("Getting BED file ready...", expanded=True) as status:
            status.update(label="Searching for genes...", state="running", expanded=False)
            # Filter the universal BED file to include only the rows corresponding to the selected genes using pattern matching
            pattern = '|'.join(r'\b' + gene + r'\b' for gene in genes_lst)
            filtered_bed = universal_bed_df[universal_bed_df[3].str.contains(pattern, regex=True, na=False)]
            # Find genes not in the universal BED file
            not_found_genes = [gene for gene in genes_lst if not universal_bed_df[3].str.contains(r'\b' + gene + r'\b', regex=True, na=False).any()]
            count = len(not_found_genes)
            if not_found_genes:
                status.update(label="Gene symbols don't match!", state="error", expanded=True)
                st.warning(f"{count} gene(s) not found in the universal BED file: {', '.join(not_found_genes)}.\n\nPlease check the gene symbols and try again.")
            else:
                status.update(label="All genes found! Ready for download", state="complete", expanded=True)
                # Fornecer um botão para download do arquivo BED filtrado
                st.download_button(
                    label="Download BED",
                    data=filtered_bed.to_csv(sep='\t', header=False, index=False).encode("utf-8"),
                    file_name=f"{st.session_state.panel}.bed",
                    mime="text/bed"
                )
        

# Ler os dados dos painéis e do BED universal dos arquivos CSV
panel_df = pd.read_excel('data/regions/gene_panels/BED_Files_Emedgene_2.xlsx', header=0)
universal_bed_df = pd.read_csv('data/regions/genome_exons/hg38_Twist_ILMN_Exome_2.0_Plus_Panel_annotated.BED', sep='\t', header=None)

st.title("Gene Panel Creator")
st.text_input("Panel Name", placeholder="Enter Panel Name", key="panel_name")
st.text_area("Add Genes", placeholder="Enter gene symbols separated by commas", key="genes")
panel_creator(panel_df)
# Executar o aplicativo Streamlit
st.title("Download BED Panel")
# Criar uma caixa de seleção no Streamlit para selecionar o painel
st.selectbox('Select a gene panel', panel_df['Panel Name PT (Klims)'].unique().tolist(), index=None, key="panel", label_visibility="collapsed", placeholder="Select a gene panel")
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