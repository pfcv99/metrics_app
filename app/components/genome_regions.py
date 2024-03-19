import pandas as pd

def mane():
    data_mane = pd.read_csv('data/regions/MANE_genomic/MANE_hg38_exons_modif_MANE.bed', sep='\t', header=None)
    df_mane = pd.DataFrame(data_mane)
    gene_lst = df_mane[3].unique().tolist()
    return sorted(gene_lst)

def ucsc():
    data_ucsc = pd.read_csv('data/regions/MANE_genomic/UCSC_hg19_exons_modif_canonical.bed', sep='\t', header=None)
    df_ucsc = pd.DataFrame(data_ucsc)
    gene_lst = df_ucsc[3].unique().tolist()
    return sorted(gene_lst)