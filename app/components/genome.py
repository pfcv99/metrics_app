import pandas as pd

#def mane(analysis):
#    path_mane = 'data/regions/genome_exons/MANE_hg38_exons_modif_MANE_with_difference.bed'
#    path_mane_chr = 'data/regions/genome_exons/MANE_hg38_exons_modif_MANE_with_difference_chr.bed'
#    if analysis == "Single Gene":
#        path = path_mane
#    elif analysis == "Gene Panel":
#        path = path_mane_chr
#        
#    data_mane = pd.read_csv(path, sep='\t', header=None)
#    df_mane = pd.DataFrame(data_mane)
#    return path, df_mane

#def ucsc(analysis):
#    path_ucsc = 'data/regions/genome_exons/UCSC_hg19_exons_modif_canonical_with_difference.bed'
#    path_ucsc_chr = 'data/regions/genome_exons/UCSC_hg19_exons_modif_canonical_with_difference_chr.bed'
#    if analysis == "Single Gene":
#        path = path_ucsc
#    elif analysis == "Gene Panel":
#        path = path_ucsc_chr
#
#    data_ucsc = pd.read_csv(path, sep='\t', header=None)
#    df_ucsc = pd.DataFrame(data_ucsc)
#    return path, df_ucsc

def assembly(assembly, analysis):
    paths = {
        "GRCh38/hg38": {
            "Single Gene": 'data/regions/genome_exons/hg38_Twist_ILMN_Exome_2.0_Plus_Panel_annotated_modif_nochr.bed',
            "Gene Panel": 'data/regions/genome_exons/hg38_Twist_ILMN_Exome_2.0_Plus_Panel_annotated_modif.bed',
            "Exome": 'data/regions/genome_exons/hg38_Twist_ILMN_Exome_2.0_Plus_Panel_annotated_modif.bed'
        },
        "GRCh37/hg19": {
            "Single Gene": 'data/regions/genome_exons/hg19_Twist_ILMN_Exome_2.0_Plus_Panel_annotated_modif_nochr.BED',
            "Gene Panel": 'data/regions/genome_exons/hg19_Twist_ILMN_Exome_2.0_Plus_Panel_annotated_modif.BED',
            "Exome": 'data/regions/genome_exons/hg19_Twist_ILMN_Exome_2.0_Plus_Panel_annotated_modif.BED'
        }
    }

    path = paths.get(assembly, {}).get(analysis)
    if path:
        return path, pd.read_csv(path, sep='\t', header=None)
    else:
        raise ValueError("Invalid assembly or analysis type")
    
  
def panel():
    paths = {
        "Gene Panel" : 'data/regions/gene_panels/BED_Files_Emedgene_2.xlsx'
        }
    path = paths.get("Gene Panel")
    if path:
        return pd.read_excel(path, header=0)