import streamlit as st
import pandas as pd
from components import dataframe, metrics

sidebar_logo = "data/img/unilabs_logo.png"
main_body_logo = "data/img/thumbnail_image001.png"
st.logo(sidebar_logo, icon_image=main_body_logo)

st.title("Results")
tab1, tab2, tab3 = st.tabs(["Overview", "Gene Detail", "Exon Detail"])

def select_all_columns(select_all, columns):
    """Função para selecionar ou desmarcar todas as colunas."""
    for section, cols in columns.items():
        for col in cols:
            st.session_state[f"col_{col}"] = select_all
            
with tab1:
    columns = {
    "Basic Information": ["Date", "BAM", "Region", "Average Read Depth", "Size Coding"],
    "Coverage": ["Coverage (0-1x)", "Coverage (2-10x)", "Coverage (11-15x)", "Coverage (16-20x)", 
                 "Coverage (21-30x)", "Coverage (31-50x)", "Coverage (51-100x)", "Coverage (101-500x)"],
    "Coverage Percentage": ["Coverage % (1x)", "Coverage % (10x)", "Coverage % (15x)", "Coverage % (20x)", 
                            "Coverage % (30x)", "Coverage % (50x)", "Coverage % (100x)", "Coverage % (500x)"]
}

# Inicializa as checkboxes de "Basic Information" como selecionadas por padrão
for col in columns["Basic Information"]:
    if f"col_{col}" not in st.session_state:
        st.session_state[f"col_{col}"] = True
        
with st.popover("Filters"):
    st.subheader("Select Columns to Display")
    
    # Verifica se todas as colunas estão selecionadas
    all_selected = all(st.session_state.get(f"col_{col}", False) for section in columns.values() for col in section)
    
    # Alterna entre selecionar e desmarcar todas as colunas
    if st.button("Select All" if not all_selected else "Deselect All"):
        select_all_columns(not all_selected, columns)
        st.rerun()

    # Organizando checkboxes em três colunas
    col1, col2, col3 = st.columns(3)
    columns_keys = list(columns.keys())
    
    for i, section in enumerate(columns_keys):
        with [col1, col2, col3][i % 3]:
            st.write(f"**{section}**")
            for col in columns[section]:
                st.checkbox(col, key=f"col_{col}")
            
    # Cria o DataFrame com base nas colunas selecionadas
selected_columns = [col for section in columns.values() for col in section if st.session_state.get(f"col_{col}", False)]

# Exemplo de dados para preencher o DataFrame
data = {
    "Date": ["2023-01-01", "2023-01-02"],
    "BAM": ["file1.bam", "file2.bam"],
    "Region": ["Region1", "Region2"],
    "Average Read Depth": [30, 40],
    "Size Coding": [1000, 2000],
    "Coverage (0-1x)": [0, 0],
    "Coverage (2-10x)": [5, 10],
    "Coverage (11-15x)": [15, 20],
    "Coverage (16-20x)": [20, 25],
    "Coverage (21-30x)": [30, 35],
    "Coverage (31-50x)": [50, 55],
    "Coverage (51-100x)": [75, 80],
    "Coverage (101-500x)": [100, 150],
    "Coverage % (1x)": [95, 96],
    "Coverage % (10x)": [90, 92],
    "Coverage % (15x)": [85, 88],
    "Coverage % (20x)": [80, 85],
    "Coverage % (30x)": [75, 80],
    "Coverage % (50x)": [70, 75],
    "Coverage % (100x)": [65, 70],
    "Coverage % (500x)": [60, 65],
}

# Filtrando apenas as colunas selecionadas
filtered_data = {col: data[col] for col in selected_columns}
df = pd.DataFrame(filtered_data)

st.dataframe(df)
    #df = pd.DataFrame(
    #[
    #    {"command": "st.selectbox", "rating": 4, "is_widget": True},
    #    {"command": "st.balloons", "rating": 5, "is_widget": False},
    #    {"command": "st.time_input", "rating": 3, "is_widget": True},
    #]
    #)
    #edited_df = st.data_editor(
    #    df,
    #    column_config={
    #        "command": "Streamlit Command",
    #        "rating": st.column_config.NumberColumn(
    #            "Your rating",
    #            help="How much do you like this command (1-5)?",
    #            min_value=1,
    #            max_value=5,
    #            step=1,
    #            format="%d ⭐",
    #        ),
    #        "is_widget": "Widget ?",
    #    },
    #    disabled=["command", "is_widget"],
    #    hide_index=True,
    #)

    #favorite_command = edited_df.loc[edited_df["rating"].idxmax()]["command"]
    #st.markdown(f"Your favorite command is **{favorite_command}** 🎈")

with tab2:
    st.write("Gene Detail")
    
    df = dataframe.dataframe()
    st.dataframe(df)
    
with tab3:
    st.write("Exon Detail")