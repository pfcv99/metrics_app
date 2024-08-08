import streamlit as st
import io
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

import boto3
import streamlit as st

def cram():
    s3 = boto3.client('s3')
    bucket_name = 'unilabs'
    s3_object = st.session_state.cram[0]
    print(s3_object)
    obj = s3.get_object(Bucket=bucket_name, Key=s3_object)
    
    streaming_body = obj["Body"]
    
    chunk_size = 1024 * 1024  # 1 MB
    content = b''  # Inicializar um contêiner para o conteúdo
    
    try:
        for chunk in iter(lambda: streaming_body.read(chunk_size), b''):
            # Processar cada pedaço aqui
            # Exemplo: simplesmente imprimir o tamanho do pedaço
            print(f'Chunk size: {len(chunk)} bytes')

            # Adicione aqui o código para processar cada pedaço do conteúdo binário
            # Aqui estamos apenas acumulando os pedaços em `content`
            content += chunk

    finally:
        # Certifique-se de fechar o StreamingBody quando terminar
        streaming_body.close()
    
    return content
