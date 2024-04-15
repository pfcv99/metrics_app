import pandas as pd

def mane():
    path_mane = 'data/regions/genome_exons/MANE_hg38_exons_modif_MANE_with_difference.bed'
    data_mane = pd.read_csv(path_mane, sep='\t', header=None)
    df_mane = pd.DataFrame(data_mane)
    return path_mane, df_mane

def ucsc():
    path_ucsc = 'data/regions/genome_exons/UCSC_hg19_exons_modif_canonical_with_difference.bed'
    data_ucsc = pd.read_csv(path_ucsc, sep='\t', header=None)
    df_ucsc = pd.DataFrame(data_ucsc)
    return path_ucsc, df_ucsc

