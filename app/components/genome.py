import pandas as pd
import streamlit as st

@st.cache_data
def assembly(assembly, analysis):
    paths = {
        "GRCh38/hg38": {
            "Single Gene": 'data/regions/genome_exons/hg38_Twist_ILMN_Exome_2.0_Plus_Panel_annotated_modif_nochr.BED',
            "Gene Panel": 'data/regions/genome_exons/hg38_Twist_ILMN_Exome_2.0_Plus_Panel_annotated_modif.BED',
            "Exome": 'data/regions/genome_exons/hg38_Twist_ILMN_Exome_2.0_Plus_Panel_annotated_modif_nochr.BED'
        },
        "GRCh37/hg19": {
            "Single Gene": 'data/regions/genome_exons/hg19_Twist_ILMN_Exome_2.0_Plus_Panel_annotated_modif_nochr.BED',
            "Gene Panel": 'data/regions/genome_exons/hg19_Twist_ILMN_Exome_2.0_Plus_Panel_annotated_modif.BED',
            "Exome": 'data/regions/genome_exons/hg19_Twist_ILMN_Exome_2.0_Plus_Panel_annotated_modif_nochr.BED'
        }
    }

    path = paths.get(assembly, {}).get(analysis)
    if path:
        return path, pd.read_csv(path, sep='\t', header=None)
    else:
        raise ValueError("Invalid assembly or analysis type")
    
@st.cache_data
def panel():
    paths = {
        "Gene Panel" : 'data/regions/gene_panels/BED_Files_Emedgene_2.xlsx'
        }
    path = paths.get("Gene Panel")
    if path:
        return pd.read_excel(path, header=0)