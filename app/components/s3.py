import streamlit as st
import boto3

# Configura o recurso S3 e o cliente S3
@st.cache_resource
def get_s3_client():
    return boto3.client('s3')

@st.cache_resource
def get_s3_resource():
    return boto3.resource('s3')

def list_cram_files(bucket_name='unilabs'):
    
    # Inicializa a paginação
    paginator = st.session_state.s3_client.get_paginator('list_objects_v2')

    # Configura o paginator para listar todos os objetos no bucket
    operation_parameters = {'Bucket': bucket_name}
    
    # Lista para armazenar os ficheiros .cram encontrados
    if 'cram_files' not in st.session_state:
        st.session_state.cram_files = []

    # Pagina sobre os resultados
    for page in paginator.paginate(**operation_parameters):
        for obj in page.get('Contents', []):
            if obj['Key'].endswith('.cram'):
                st.session_state.cram_files.append(obj['Key'])

    return st.session_state.cram_files

def cram():
    st.title("CRAM File Manager")

    # Recupera a lista de arquivos CRAM, utilizando cache para melhorar a eficiência
    cram_files = list_cram_files()
    if not cram_files:
        st.write("No CRAM files found in the 'unilabs' bucket.")
        return
    
    # Mostra os arquivos encontrados
    st.write(f"Found {len(cram_files)} CRAM files: {cram_files}")
    selected_files = st.session_state.get('selected_files', [])
    
    # Permite ao usuário selecionar arquivos
    selected_files = st.multiselect("Select CRAM files to manage:", cram_files, default=selected_files)
    
    # Armazena os arquivos selecionados no estado da sessão
    st.session_state['selected_files'] = selected_files
    
    if selected_files:
        for file in selected_files:
            st.write(f"Managing file: {file}")
            # Exemplo de leitura de um ficheiro CRAM
            # Aqui você pode implementar a leitura e exibição do conteúdo do ficheiro CRAM
            obj = st.session_state.s3_client.get_object(Bucket='unilabs', Key=file)
            cram_content = obj['Body'].read()
            st.write(f"File Content: {cram_content[:100]}...")  # Mostrar apenas os primeiros 100 caracteres

# Execute a função cram se o script for executado
if __name__ == '__main__':
    cram()
