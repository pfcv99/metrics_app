from pathlib import Path

def files():
    # Usando Path().iterdir() para iterar pelos arquivos do diretório
    bam_cram_files = [f.name for f in Path("./data/mapped").iterdir() if f.suffix in [".bam", ".cram"]]
    
    return bam_cram_files

    
#def step4_bam_file(bam_files, region):
#    # Allow the user to select BAM files in a multi-selection dropdown
#    container = st.container()
#    all_bam_files = [Path(f).name for f in bam_files]
#    
#    if region is not None:
#        all = st.checkbox("Select all ")
#    else:
#        all = False
#    
#    if all != False:
#        bam = container.multiselect('Select BAM file(s)', all_bam_files, all_bam_files, key="bam", label_visibility="collapsed",placeholder="Select a BAM file(s)")
#    else:
#        bam = container.multiselect('Select BAM file(s)', all_bam_files, key="bam", label_visibility="collapsed",placeholder="Select a BAM file(s)")
#
#    return bam
#
#bam_files = [f.name for f in bam_folder.iterdir() if f.suffix == ".bam" or f.suffix == ".cram"]