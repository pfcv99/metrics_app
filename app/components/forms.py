import streamlit as st
import threading
import time
import psutil
from components import genome, analysis, bam_cram

def update_progress_bar():
    progress_text = "Operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)
    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1, text=progress_text)
    time.sleep(1)
    my_bar.empty()


def session_state_initialize():
    file_dict = bam_cram.files()
    # Initialize session state variables with valid default values
    defaults = {
        'analysis': 'Single Gene',
        'assembly': "GRCh38/hg38",
        'region': None,
        'bam_cram': bam_cram.files(),
        'bam_cram_keys': file_dict.keys(),
        'bam_cram_panel': file_dict.keys(),
        'bam_cram_selected': None,
        'success': None,
        'exon': [],
        'all_exons': True,
        'panel_name': None, 
        'results': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
def single_gene():
    
    if 'depth_output' in st.session_state and 'filtered_bed' in st.session_state:
        st.session_state.pop('depth_output')
        st.session_state.pop('filtered_bed')
    if 'results' in st.session_state:
        st.session_state.pop('results')
    session_state_initialize()
    with st.container(border=True):
                
        st.markdown(
                    "#### Genome Assembly",
                    help=(
                        "**Please select the genome assembly.**\n"
                        "- The selection of a :red[genome assembly] is crucial for analyzing the sequencing data.\n"
                        "- A :red[genome assembly] defines the reference genome used for aligning the sequencing reads.\n"
                        "- Ensure that the selected :red[genome assembly] corresponds to the reference genome used for aligning the sequencing reads."
                    )
                )
        st.radio(
                "Select an option",
                ["GRCh37/hg19", "GRCh38/hg38"],
                key="assembly_value",
                label_visibility="visible",
                disabled=False,
                horizontal=True
                )
        
        st.session_state.assembly = st.session_state.assembly_value
        
        # Dynamically update the genes list when assembly changes
        genes_list = sorted([str(gene) for gene in genome.assembly(st.session_state.assembly, st.session_state.analysis)[1][3].unique().tolist()]) 
        # Now use the sorted list in the selectbox
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                        "#### Gene of Interest",
                        help=(
                            "**Please select a Gene of Interest.**\n"
                            "- The selection of a :red[Gene of Interest] is     crucial for calculating the :red[metrics].   \n"
                            "- A :red[Gene of Interest] defines the genomic     region of interest.\n"
                            "- The :red[key metrics] will be calculated  specifically for these region.\n"
                            "- Ensure that the selected :red[Gene of Interest]  corresponds to the genomic region you want to analyze.   "
                        )
                    )
            st.selectbox('Select a Gene of Interest', genes_list, key="region_value", index=None,  label_visibility="collapsed", placeholder="Select a Gene of Interest")
            st.session_state.region = st.session_state.region_value
        with col2:
            st.markdown(
                    "#### Exons",
                    help=(
                        "**Please select a one, multiple or all exons**\n"
                        "- The selection of a :red[exons] is essential for   analyzing the sequencing data.\n"
                    )
                )
            df = genome.assembly(st.session_state.assembly, st.session_state.analysis)[1][:]
            filtered_exon = df[df[3]==st.session_state.region][4]
            st.multiselect("Select exons",filtered_exon, key="exon_value", label_visibility="collapsed", placeholder="Select #exons", disabled=st.session_state.all_exons)
            st.checkbox("All exons", key="all_exons")
            
            if st.session_state.all_exons:
                st.session_state.exon = filtered_exon.tolist()
            else:
                st.session_state.exon = st.session_state.exon_value
        st.markdown(
                    "#### BAM/CRAM file(s)",
                    help=(
                        "**Please select a BAM/CRAM file(s).**\n"
                        "- The selection of a :red[BAM/CRAM file(s)] is essential for   analyzing the sequencing data.\n"
                        "- A :red[BAM/CRAM file(s)] contains aligned sequencing reads on    the reference genome.\n"
                        "- Ensure that the selected :red[BAM/CRAM file(s)] corresponds to   the sequencing data you want to analyze."
                    )
                )
        bam_cram_files = st.session_state.bam_cram_keys
        st.multiselect('Select a BAM/CRAM file(s)', bam_cram_files, key="bam_cram_single_gene", label_visibility="collapsed",placeholder="Select a BAM/CRAM file(s)")
        
        st.session_state.bam_cram_selected = st.session_state.bam_cram_single_gene
        
        # Every form must have a submit button.
        submitted_single_gene = st.button("Submit", key="submit_single_gene")
        st.session_state.submit = submitted_single_gene
        if submitted_single_gene:
            if st.session_state.analysis and st.session_state.assembly and st.session_state.region and st.session_state.bam_cram:
                # Atualizar a barra de progresso enquanto o cálculo está a decorrer
                with st.spinner('Submitting Form...'):              
                    samtools_start_time = time.time()
                    # Monitoriza o uso da CPU e memória antes de iniciar a função
                    samtools_cpu_percent_start = psutil.cpu_percent(interval=None)
                    samtools_memory_info_start = psutil.virtual_memory().used
                    # Call the samtools.depth function to calculate the depth of coverage

                    depth_thread = threading.Thread(target=analysis.run_single_gene())
                    depth_thread.start()


                    # Esperar o término do thread de cálculo
                    depth_thread.join()

                    st.success("Form submitted")
                    st.session_state.sucess = True
                    st.session_state.results = True
                    samtools_end_time = time.time()
                    samtools_execution_time = samtools_end_time - samtools_start_time
                    print(f"Samtools | Execution time: {samtools_execution_time} seconds")
                    # Monitoriza novamente após a execução
                    samtools_cpu_percent_end = psutil.cpu_percent(interval=None)
                    samtools_memory_info_end = psutil.virtual_memory().used

                    # Calcula a diferença
                    samtools_cpu_usage = samtools_cpu_percent_end - samtools_cpu_percent_start
                    samtools_memory_usage = (samtools_memory_info_end - samtools_memory_info_start) / (1024 * 1024)  # Convertido para MB

                    print(f"Samtools | CPU Usage: {samtools_cpu_usage}%")
                    print(f"Samtools | Memory Usage: {samtools_memory_usage} MB")
                    time.sleep(1)

                    if st.session_state.depth_output:
                        st.switch_page("app_pages/results.py")
                        
                    else:
                        st.warning('No depth content found!')
            else:
                st.warning("Form not submitted. Please fill in all fields.")
            
def gene_panel():
    if 'depth_output' in st.session_state and 'filtered_bed' in st.session_state:
        st.session_state.pop('depth_output')
        st.session_state.pop('filtered_bed')
    if 'results' in st.session_state:
        st.session_state.pop('results')
    session_state_initialize()
    with st.container(border=True):
        st.markdown(
            "#### Genome Assembly",
            help=(
                "**Please select the genome assembly.**\n"
                "- The selection of a :red[genome assembly] is crucial for analyzing the sequencing data.\n"
                "- A :red[genome assembly] defines the reference genome used for aligning the sequencing reads.\n"
                "- Ensure that the selected :red[genome assembly] corresponds to the reference genome used for aligning the sequencing reads."
            )
        )
        st.radio(
            "Select an option",
            ["GRCh37/hg19", "GRCh38/hg38"],
            key="panel_assembly_value",
            label_visibility="visible",
            disabled=False,
            horizontal=True,
        )
        
        st.session_state.assembly = st.session_state.panel_assembly_value
        
        st.markdown(
            "#### Gene Panel of Interest",
            help=(
                "**Please select a Gene Panel of Interest.**\n"
                "- The selection of a :red[Gene Panel of Interest] is crucial for calculating the :red[metrics].\n"
                "- A :red[Gene Panel of Interest] defines the genomic region of interest.\n"
                "- The :red[metrics] will be calculated specifically for this region.\n"
                "- Ensure that the selected :red[Gene Panel of Interest] corresponds to the genomic region you want to analyze."
            )
        )
        
        # Get the panel list and sort it
        panels_df = genome.panel()  # Assuming this is your DataFrame
        panels = panels_df['Panel Name PT (Klims)'].unique().tolist()
        panel_list = sorted([str(panel) for panel in panels])
        
        # Panel selectbox
        selected_panel = st.selectbox(
            'Select a Gene Panel of Interest', 
            panel_list, 
            key="panel_region_value", 
            index=None, 
            label_visibility="collapsed", 
            placeholder="Select a Gene Panel of Interest"
        )
        
        # Filter the DataFrame for the selected panel
        filtered_panel = panels_df[panels_df['Panel Name PT (Klims)'] == selected_panel]
        st.session_state.panel_name = selected_panel
        # Check if any rows match the selected panel
        if not filtered_panel.empty:
            # Get the 'Genes' column, split the string into a list of genes
            selected_genes_string = filtered_panel['Genes'].values[0]  # Get the first matching string
            selected_genes = selected_genes_string.split(',')  # Split the string by commas to create a list of genes
        else:
            # If no matching rows, return an empty list
            selected_genes = []

        # Store the list of genes (or empty list) in session state
        st.session_state.region = selected_genes
        
        st.markdown(
            "#### BAM/CRAM file(s)",
            help=(
                "**Please select a BAM/CRAM file(s).**\n"
                "- The selection of a :red[BAM/CRAM file(s)] is essential for analyzing the sequencing data.\n"
                "- A :red[BAM/CRAM file(s)] contains aligned sequencing reads on the reference genome.\n"
                "- Ensure that the selected :red[BAM/CRAM file(s)] corresponds to the sequencing data you want to analyze."
            )
        )
        
        # Cram file selection
        bam_cram_files = st.session_state.bam_cram_keys
        st.multiselect(
            'Select a BAM/CRAM file(s)', 
            bam_cram_files, 
            key="panel_bam_cram_value", 
            label_visibility="collapsed", 
            placeholder="Select a BAM/CRAM file(s)"
        )
        
        st.session_state.bam_cram_panel = st.session_state.panel_bam_cram_value
        st.session_state.bam_cram_selected = st.session_state.panel_bam_cram_value
        
        # Submit button
        submitted_gene_panel = st.button("Submit", key="panel_submit")
        st.session_state.submit = submitted_gene_panel
        if submitted_gene_panel:
            if st.session_state.analysis and st.session_state.assembly and st.session_state.bam_cram_panel:
                # Update the progress bar while calculation is ongoing
                with st.spinner('Submitting Form...'):
                    
                    # Call the samtools.depth function to calculate the depth of coverage
                    depth_thread = threading.Thread(target=analysis.run_gene_panel())
                    depth_thread.start()



                    # Wait for the calculation thread to finish
                    depth_thread.join()

                    st.success("Form submitted")
                    st.session_state.success = True
                    st.session_state.results = True
                    time.sleep(0.5)
                    if st.session_state.depth_output:
                        st.switch_page("app_pages/results.py")
                    else:
                        st.warning('No depth content found!')
            else:
                st.warning("Form not submitted. Please fill in all fields.")
               
def exome():
    if 'depth_output' in st.session_state and 'filtered_bed' in st.session_state:
        st.session_state.pop('depth_output')
        st.session_state.pop('filtered_bed')
    if 'results' in st.session_state:
        st.session_state.pop('results')
    session_state_initialize()
    with st.container(border=True):
                
        st.markdown(
                    "#### Genome Assembly",
                    help=(
                        "**Please select the genome assembly.**\n"
                        "- The selection of a :red[genome assembly] is crucial for analyzing the sequencing data.\n"
                        "- A :red[genome assembly] defines the reference genome used for aligning the sequencing reads.\n"
                        "- Ensure that the selected :red[genome assembly] corresponds to the reference genome used for aligning the sequencing reads."
                    )
                )
        st.radio(
                "Select an option",
                ["GRCh37/hg19", "GRCh38/hg38"],
                key="assembly_value_exome",
                label_visibility="visible",
                disabled=False,
                horizontal=True
                )
        
        st.session_state.assembly_exome = st.session_state.assembly_value_exome
        
        # Now use the sorted list in the selectbox
        col1, col2, col3 = st.columns(3)
        with col1:
            
            st.markdown(
                        "#### BAM/CRAM file(s)",
                        help=(
                            "**Please select a BAM/CRAM file(s).**\n"
                            "- The selection of a :red[BAM/CRAM file(s)] is essential for   analyzing the sequencing data.\n"
                            "- A :red[BAM/CRAM file(s)] contains aligned sequencing reads on    the reference genome.\n"
                            "- Ensure that the selected :red[BAM/CRAM file(s)] corresponds to   the sequencing data you want to analyze."
                        )
                    )
            bam_cram_files = st.session_state.bam_cram_keys
            st.multiselect('Select a BAM/CRAM file(s)', bam_cram_files, key="bam_cram_value_exome", label_visibility="collapsed",placeholder="Select a BAM/CRAM file(s)")
        
        st.session_state.bam_cram_selected = st.session_state.bam_cram_value_exome
        st.session_state.bam_cram_exome = st.session_state.bam_cram_value_exome
        
        # Every form must have a submit button.
        submitted_exome = st.button("Submit", key="submit_exome")
        st.session_state.submit = submitted_exome
        if submitted_exome:
            if st.session_state.analysis and st.session_state.assembly_exome and st.session_state.bam_cram_value_exome:
                # Atualizar a barra de progresso enquanto o cálculo está a decorrer
                with st.spinner('Submitting Form...'):               
                    
                    # Call the samtools.depth function to calculate the depth of coverage
                    
                    depth_thread = threading.Thread(target=analysis.run_exome())
                    depth_thread.start()
    
    
                    # Esperar o término do thread de cálculo
                    depth_thread.join()
                    
                    st.success("Form submitted")
                    st.session_state.sucess = True
                    st.session_state.results = True
                    time.sleep(2)
                    if st.session_state.depth_output:
                        st.switch_page("app_pages/results.py")
                    else:
                        st.warning('No depth content found!')
            else:
                st.warning("Form not submitted. Please fill in all fields.")