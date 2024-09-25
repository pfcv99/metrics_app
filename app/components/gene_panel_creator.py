import streamlit as st
import pandas as pd

@st.cache_data
def panel_creator():
    data = pd.read_excel('data/regions/gene_panels/BED_Files_Emedgene_2.xlsx', header=0)
    df = pd.DataFrame(data)

    with st.popover("Add new"):
                panel_name = st.text_input("Panel Name", placeholder="Enter Panel Name")
                genes = st.text_area("Add Genes", placeholder="Enter gene symbols separated by commas")
                if st.button("Create Panel"):
                    # Add the new panel to the DataFrame and save to CSV
                    new_panel = {'Panel_Name_EN_EMEDGENE': panel_name, 'Genes': genes}
                    df = pd.concat([df, pd.DataFrame([new_panel])], ignore_index=True)
                    df.to_excel('data/regions/gene_panels/BED_Files_Emedgene_2.xlsx', index=False)  # Save updated DataFrame to CSV
                    st.rerun() #TO IMPROVE: not the ideal way to rerun the page