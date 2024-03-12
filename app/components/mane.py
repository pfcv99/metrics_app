import pandas as pd

input = pd.read_csv('data/regions/MANE_genomic/MANE_exons_modif_MANE.bed', sep='\t', header=None)
df = pd.DataFrame(input)

def genes(df):

    gene_lst = df[3].unique().tolist()
    
    return sorted(gene_lst)

def data(df, gene):
    
    data_gene = df[df[3] == gene]
    
    return data_gene