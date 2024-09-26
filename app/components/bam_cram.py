from pathlib import Path
import streamlit as st

@st.cache_data
def files():
    # Usando Path().iterdir() para iterar pelos arquivos do diretório
    file_dict = {f.name: str(f) for f in Path("./data/mapped").iterdir() if f.suffix in [".bam", ".cram"]}
    
    return file_dict
