import streamlit as st
from st_files_connection import FilesConnection

def bam_cram():
    conn = st.connection('s3', type=FilesConnection)
    df2 = conn.read("unilabs/bam_bed_map.csv", input_format="csv", ttl=600)
    st.dataframe(df2)

#def list_bam_files(directory='unilabs/'):
#    # Conectar ao bucket S3
#    conn = st.connection('s3', type=FilesConnection)
#    
#    # Listar todos os ficheiros no diretório `directory` e subdiretórios
#    files = conn.fs.ls(directory)
#    
#    # Filtrar os ficheiros .bam
#    bam_files = [file for file in files if file.endswith('.bam')]
#    
#    return bam_files
#
#def bam_cram():
#    st.title("BAM File Manager")
#    
#    bam_files = list_bam_files()
#    
#    if not bam_files:
#        st.write("No BAM files found in the 'unilabs' directory.")
#        return
#    
#    st.write(f"Found {len(bam_files)} BAM files:")
#    for file in bam_files:
#        st.write(file)
#    
#    selected_files = st.multiselect("Select BAM files to manage:", bam_files)
#    
#    if selected_files:
#        conn = st.connection('s3', type=FilesConnection)
#        for file in selected_files:
#            st.write(f"Managing file: {file}")
#            # Exemplo de leitura de um ficheiro BAM
#            bam_content = conn.read(file, input_format="bam", ttl=600)
#            st.write(f"File Content: {bam_content[:100]}...")  # Mostrar apenas os primeiros 100 caracteres
#
#            # Exemplo de escrita (substitua com a operação desejada)
#            # conn.write(file, data_to_write, output_format="bam")
#            
#            # Exemplo de manipulação (substitua com a operação desejada)
#            # manipulate_file(bam_content)
    
if __name__ == "__main__":
    bam_cram()