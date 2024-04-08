import pandas as pd

def mane():
    path_mane = 'data/regions/genome_exons/MANE_hg38_exons_modif_MANE.bed'
    data_mane = pd.read_csv(path_mane, sep='\t', header=None)
    df_mane = pd.DataFrame(data_mane)
    gene_lst = sorted(df_mane[3].unique().tolist())
    return path_mane, gene_lst

def ucsc():
    path_ucsc = 'data/regions/genome_exons/UCSC_hg19_exons_modif_canonical.bed'
    data_ucsc = pd.read_csv(path_ucsc, sep='\t', header=None)
    df_ucsc = pd.DataFrame(data_ucsc)
    gene_lst = sorted(df_ucsc[3].unique().tolist())
    return path_ucsc, gene_lst

