import pandas as pd

def dataframe(*args):
    """
    Cria um DataFrame a partir de múltiplos dicionários fornecidos como argumentos.
    
    Parâmetros:
        *args: Múltiplos dicionários a serem combinados em um DataFrame.
        
    Retorna:
        df: Um DataFrame contendo os dados combinados.
    """
    # Inicializa uma lista para armazenar os dicionários
    lista_de_dicionarios = []
    
    # Itera sobre os argumentos fornecidos
    for dicionario in args:
        if isinstance(dicionario, dict):
            lista_de_dicionarios.append(dicionario)
        else:
            raise ValueError("Todos os argumentos devem ser dicionários.")
    
    # Cria o DataFrame a partir da lista de dicionários
    df = pd.DataFrame(lista_de_dicionarios)
    
    return df
