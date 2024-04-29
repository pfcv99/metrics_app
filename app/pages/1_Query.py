# metrics_app/app/pages/1_Analyser.py

# Import necessary libraries
import streamlit as st
import pandas as pd
from pathlib import Path
import subprocess
import os
from components import streamlit_page_config
from components import samtools_depth as sd 
from components import logo
from components import genome_regions
from components import gene_panel_creator as pc
from time import sleep
from stqdm import stqdm

# Set Streamlit page configuration
streamlit_page_config.set_page_configuration()

logo.add_logo()

def step1_analysis_type():
    analysis_type = st.radio(
                "Select an option",
                ["Single Gene", "Gene Panel", "Exome"],
                key="analysis",
                label_visibility="visible",
                disabled=False,
                horizontal=True
                )
    return analysis_type

def step2_genome_assembly():
    assembly = st.radio(
                "Select an option",
                ["GRCh37/hg19", "GRCh38/hg38"],
                key="assembly",
                label_visibility="visible",
                disabled=False,
                horizontal=True, index=1
                )
    if assembly == "GRCh38/hg38":
        assembly_file = genome_regions.mane()
    elif assembly == "GRCh37/hg19":
        assembly_file = genome_regions.ucsc() 
    return assembly_file

 
def step3_region_of_interest(analysis, df_assembly):
    # IF ANALYSIS TYPE IS 'SINGLE GENE'
    exon_selection = []
    if analysis == "Single Gene":
        region = st.selectbox('Select a Gene of Interest', sorted(df_assembly[3].unique().tolist()), key="gene", index=None, label_visibility="collapsed",placeholder="Select a Gene of Interest")
        if region:  # Verifica se um gene foi selecionado
            all_exons = st.checkbox("All Exons", value=True)
            if all_exons == True:
                exon_selection = df_assembly[df_assembly[3] == region][4].tolist()
            else:
                exon_selection = st.multiselect('Select Exons', df_assembly[df_assembly[3] == region][4], key="exon", label_visibility="collapsed",placeholder="Select Exons")
        else:
            region = None  # Define region como None se nenhum gene for selecionado
#VER MELHOR AQUI: 
    # - SELEÇÃO DOS EXÕES, VER NO GENOME_REGIONS.PY
    
    # IF ANALYSIS TYPE == GENE PANEL
    elif analysis == "Gene Panel":
        data = pd.read_csv('data/regions/gene_panels/BED_Files_Emedgene_2.csv', sep=',', header=0)
        df = pd.DataFrame(data)
        panel_lst = df['Panel_Name_EN_EMEDGENE'].unique().tolist()
        panel = st.selectbox('Select a Gene Panel', panel_lst, index=None, key="region", label_visibility="collapsed",placeholder="Select a Gene Panel")
        if panel:
            hide_streamlit_style = """
            <style>
            tbody th {display:none}
            .blank{
            display: none;
            }
            </style>
            """
            st.markdown(hide_streamlit_style, unsafe_allow_html=True)
            st.table(df[df['Panel_Name_EN_EMEDGENE'] == panel]["Genes"])
        
        genes_lst = df[df['Panel_Name_EN_EMEDGENE'] == panel]['Genes'].tolist()
        region = genes_lst
        pc.panel_creator()
        
    # IF ANALYSIS TYPE == EXOME          
    elif analysis == "Exome":
        region = st.selectbox('Select an Exome', assembly, index=None, key="region", label_visibility="collapsed",placeholder="Select an Exome")
    
    # If no BED file is selected show error
    if region is None: 
        if analysis == "Single Gene":
            st.info("No Gene of Interest selected. Please select a Gene of Interest.")
            if region is not None and ((exon is False) and (not exon_selection)):
                st.info("No Exon selected. Please select an Exon.")
        elif analysis == "Gene Panel":
            st.info("No Gene Panel selected. Please select a Gene Panel.")
        elif analysis == "Exome":
            st.info("No Exome selected. Please select an Exome.")

    
            
    return region, exon_selection



# Function to select BAM files based on the selected BED
def step4_bam_file(bam_files, region):
    # Allow the user to select BAM files in a multi-selection dropdown
    container = st.container()
    all_bam_files = [Path(f).name for f in bam_files]
    
    if region is not None:
        all = st.checkbox("Select all ")
    else:
        all = False
    
    if all != False:
        bam = container.multiselect('Select BAM file(s)', all_bam_files, all_bam_files, key="bam", label_visibility="collapsed",placeholder="Select a BAM file(s)")
    else:
        bam = container.multiselect('Select BAM file(s)', all_bam_files, key="bam", label_visibility="collapsed",placeholder="Select a BAM file(s)")

    # If no BAM filread_depthes are selected, allow the user to upload BAM file(s)
    if not bam:
        st.info("No BAM file(s) selected. Please select BAM file(s).")

    return bam


# Function to calculate average read depth
def compute_read_depth(bam_path, assembly_file, depth_path, region, analysis, exon_selection):
    if analysis == "Single Gene":
        sd.run_samtools_depth_v2_exon(bam_path, assembly_file, depth_path, region, exon_selection)
        average_read_depth, min_read_depth, max_read_depth = sd.calculate_depth_statistics(depth_path)
        coverage_stats = sd.count_coverage_singlegene(depth_path)
        date_utc = pd.Timestamp.utcnow()
        
        return {
            'Date': date_utc,
            'Average_Read_Depth': average_read_depth,
            **coverage_stats,
            
        }
    elif analysis == "Gene Panel":
        max_gene_size, per_gene_size, normalization_factors, global_size = sd.normalization_factor(assembly_file, region)
        per_gene_size_output = {gene: size for gene, size in per_gene_size.items()}
        normalization_factors_output = {gene: factor for gene, factor in normalization_factors.items()}
        
        average_read_depth, min_read_depth, max_read_depth = sd.calculate_depth_statistics(depth_path)
        coverage_stats = sd.count_coverage_genepanel(depth_path, normalization_factors_output)
        date_utc = pd.Timestamp.utcnow()


        return {
            'Date': date_utc,
            'Average_Read_Depth': average_read_depth,
            'Size_Coding': global_size,
            'Per_Gene_Size': per_gene_size_output,
            'Normalization_Factors': normalization_factors_output,
            'Min_Read_Depth': min_read_depth,
            'Max_Read_Depth': max_read_depth,
            **coverage_stats
        }
            


def single_gene(bam, region, bam_folder, depth_folder, analysis, assembly_file, exon_selection):
    results = []
    
    for bam_file in bam:
        bam_path = bam_folder / bam_file
        depth_file = depth_folder / f"{os.path.basename(bam_file)[:-4]}.depth"
        result = compute_read_depth(bam_path, assembly_file, depth_file, region, analysis, exon_selection)
        result.update({'BAM_File': bam_file, 'Region': region})
        results.append(result)
    return results

def gene_panel(bam, region, bam_folder, depth_folder, analysis, assembly_file, exon_selection):
    results = []
    
    for bam_file in bam:
        bam_path = os.path.join(bam_folder, bam_file)
        depth_file = os.path.join(depth_folder, f"{os.path.basename(bam_file)[:-4]}.depth")
        
        for gene in region:
            result = compute_read_depth(bam_path, assembly_file, depth_file, gene, analysis, exon_selection)
            result.update({'BAM_File': bam_file, 'Depth_File': depth_file, 'Region': gene})
            results.append(result)
    
    return results

def exome(bam, region, bam_folder, depth_folder, analysis, assembly_file, exon_selection):
    results = []
    
    for bam_file in bam:
        bam_path = os.path.join(bam_folder, bam_file)
        depth_files = [f for f in os.listdir(depth_folder) if f.startswith(os.path.basename(bam_file)[:-4])]
        
        for depth_file in depth_files:
            depth_path = os.path.join(depth_folder, depth_file)
            result = compute_read_depth(bam_path, assembly_file, depth_path, region, analysis, exon_selection)
            result.update({'BAM_File': bam_file, 'Depth_File': depth_file, 'Region': region})
            results.append(result)
    
    return results
    
# Function to display results in a DataFrame
def display_results(results, analysis):
    if analysis == "Single Gene":
        st.header("Results - Single Gene")
        tab1, tab2 = st.tabs(["Overview", "Details"])
        with tab1:
            df = pd.DataFrame(results)
            df.set_index('Date', inplace=True)
            # Replace the line that sets ordered_columns with the following
            ordered_columns = ['Region','BAM_File'] + [col for col in df.columns if col not in ['BAM_File', 'Region']]

            df = df[ordered_columns]

            column_configs = {}
            for column in df.columns[df.columns.str.startswith('Coverage')]:
                column_configs[column] = st.column_config.ProgressColumn(
                    help="Coverage percentage",
                    format="%.2f",
                    min_value=0,
                    max_value=100
                )

            df.progress_apply(lambda x: sleep(0.15), axis=1)
            if df['Average_Read_Depth'].isnull().all():
                st.warning("No results found. Please check Genome Assembly or the selected BAM File(s) and try again.")
            else:
                # Display the DataFrame with column configurations
                st.dataframe(df, column_config=column_configs)
        with tab2:
            st.write("Details")
            
    elif analysis == "Gene Panel":
        st.header("Results - Gene Panel")

        
        df = pd.DataFrame(results)
        df.set_index('Date', inplace=True)
        # Replace the line that sets ordered_columns with the following
        ordered_columns = ['Region','BAM_File'] + [col for col in df.columns if col not in ['BAM_File', 'Region']]

        df = df[ordered_columns]

        column_configs = {}
        for column in df.columns[df.columns.str.startswith('Coverage')]:
            column_configs[column] = st.column_config.ProgressColumn(
                help="Coverage percentage",
                format="%.2f",
                min_value=0,
                max_value=100
            )

        df.progress_apply(lambda x: sleep(0.15), axis=1)

        if df['Average_Read_Depth'].isnull().all():
            st.warning("No results found. Please check the selected files and try again.")
        else:
            # Display the DataFrame with column configurations
            st.dataframe(df, column_config=column_configs)
            
    elif analysis == "Exome":
        st.header("Results - Exome")



        df = pd.DataFrame(results)
        df.set_index('Date', inplace=True)
        # Replace the line that sets ordered_columns with the following
        ordered_columns = ['Region','BAM_File'] + [col for col in df.columns if col not in ['BAM_File', 'Region']]

        df = df[ordered_columns]

        column_configs = {}
        for column in df.columns[df.columns.str.startswith('Coverage')]:
            column_configs[column] = st.column_config.ProgressColumn(
                help="Coverage percentage",
                format="%.2f",
                min_value=0,
                max_value=100
            )

        df.progress_apply(lambda x: sleep(0.15), axis=1)

        if df['Average_Read_Depth'].isnull().all():
            st.warning("No results found. Please check the selected files and try again.")
        else:
            # Display the DataFrame with column configurations
            st.dataframe(df, column_config=column_configs)


def working_directory(analysis):
    while True:
        try:
            if analysis == "Single Gene":
                bam_folder = Path("./data/mapped")
                depth_folder = Path("./data/depth")
                
            elif analysis == "Gene Panel":
                bam_folder = Path("./data/mapped")
                depth_folder = Path("./data/depth")
            
            elif analysis == "Exome":
                bam_folder = Path("./data/mapped")
                depth_folder = Path("./data/depth")
            
            # If everything is successful, break out of the loop
            break

        except OSError as e:
            st.error(f"Error: {e}")
            st.warning("Please resolve the error before continuing.")
            # Continue the loop if there is an error

    return bam_folder, depth_folder

def example():
    with st.popover("Query Examples"):
        example = st.selectbox(
            'Select an example:',
            ('Single Gene > GRCh38/hg38 > PKD1 > 1110366_PKD1.bam',
             'Gene Panel > GRCh38/hg38 > OncoRisk Expanded (NGS panel for 96 genes)_Wes_transição > 1101542.bam',
             'Exome > GRCh38/hg38 > Exome > 1101542.bam'),
            index=None,)
        #VER MELHOR
        if example == "Single Gene > GRCh38/hg38 > PKD1 > 1110366_PKD1.bam":
            analysis = "Single Gene"
            assembly = "GRCh38/hg38"
            region = "PKD1"
            bam = ["1110366_PKD1.bam"]
        elif example == "Gene Panel > GRCh38/hg38 > OncoRisk Expanded (NGS panel for 96 genes)_Wes_transição > 1101542.bam":
            analysis = "Gene Panel"
            assembly = "GRCh38/hg38"
            region = ["OncoRisk Expanded (NGS panel for 96 genes)_Wes_transição"]
        elif example == "Exome > GRCh38/hg38 > Exome > 1101542.bam":
            analysis = "Exome"
            assembly = "GRCh38/hg38"
            region = "Exome"
            bam = ["1101542.bam"]

# Function to define Streamlit app
def app_ARDC():    
    # TITLE
    st.markdown(
        "# Average read depth and coverage calculator\n#"
    )

    # Create two columns for layout
    col1, col2 = st.columns(2)
    
    # STEP 1. Analysis Type
    with col1:
        with st.container(border = True):
            st.markdown(
                "## :red[Step 1.] Analysis Type",
                help=(
                    "**Please select the type of analysis.**\n"
                    "- This will be mandatory to know where your data is located.\n"
                    "- The analysis will be performed on data within this selected analysis.\n"
                    "- Make sure the necessary files for analysis are in the respective directory."
                )
            )
            analysis = step1_analysis_type()

            bam_folder, depth_folder = working_directory(analysis)
            
    # STEP 2. Genome Assembly  
    with col2:
        with st.container(border = True):
            st.markdown(
                "## :red[Step 2.] Genome Assembly",
                help=(
                    "**Please select the genome assembly.**\n"
                    "- The selection of a :red[genome assembly] is crucial for analyzing the sequencing data.\n"
                    "- A :red[genome assembly] defines the reference genome used for aligning the sequencing reads.\n"
                    "- Ensure that the selected :red[genome assembly] corresponds to the reference genome used for aligning the sequencing reads."
                )
            )
            assembly_file, df_assembly = step2_genome_assembly()
            
    # STEP 3. Region of Interest
    with col1:
        with st.container(border = True):
            if analysis == "Single Gene":
                st.markdown(
                    "## :red[Step 3.] Gene of Interest",
                    help=(
                        "**Please select a Gene of Interest.**\n"
                        "- The selection of a :red[Gene of Interest] is crucial for calculating the :red[average read depth].\n"
                        "- A :red[Gene of Interest] defines the genomic region of interest.\n"
                        "- The :red[read depth] will be calculated specifically for these region.\n"
                        "- Ensure that the selected :red[Gene of Interest] corresponds to the genomic region you want to analyze."
                    )
                )
            elif analysis == "Gene Panel":
                st.markdown(
                    "## :red[Step 3.] Gene Panel",
                    help=(
                        "**Please select a Gene Panel.**\n"
                        "- The selection of a :red[Gene Panel] is crucial for calculating the :red[average read depth].\n"
                        "- A :red[Gene Panel] defines the genomic region of interest.\n"
                        "- The :red[read depth] will be calculated specifically for these region.\n"
                        "- Ensure that the selected :red[Gene Panel] corresponds to the genomic region you want to analyze."
                    )
                )
            elif analysis == "Exome":
                st.markdown(
                    "## :red[Step 3.] Exome",
                    help=(
                        "**Please select an Exome.**\n"
                        "- The selection of an :red[Exome] is crucial for calculating the :red[average read depth].\n"
                        "- An :red[Exome] defines the genomic region of interest.\n"
                        "- The :red[read depth] will be calculated specifically for these region.\n"
                        "- Ensure that the selected :red[Exome] corresponds to the genomic region you want to analyze."
                    )
                )

            region, exon_selection = step3_region_of_interest(analysis, df_assembly)
            
    # STEP 4. BAM file
    with col2:
        with st.container(border = True):
            # Column for BAM file selection
            st.markdown(
                "## :red[Step 4.] BAM file",
                help=(
                    "**Please select a BAM file.**\n"
                    "- The selection of a :red[BAM file] is essential for analyzing the sequencing data.\n"
                    "- A :red[BAM file] contains aligned sequencing reads on the reference genome.\n"
                    "- Ensure that the selected :red[BAM file] corresponds to the sequencing data you want to analyze."
                )
            )
            
            bam_files = [f.name for f in bam_folder.iterdir() if f.suffix == ".bam" or f.suffix == ".cram"]
            bam = step4_bam_file(bam_files, region)
            
    with st.container(border = False):
        if region is None:
            example()
        
    if bam and region is not None:
        #Progress Bar
        stqdm.pandas(desc="Calculating Results")
        # Process selected files and display results
        if analysis == "Single Gene":
            results = single_gene(bam, region, bam_folder, depth_folder, analysis, assembly_file, exon_selection)
        elif analysis == "Gene Panel":
            results = gene_panel(bam, region, bam_folder, depth_folder, analysis, assembly_file, exon_selection)
        elif analysis == "Exome":
            results = exome(bam, region, bam_folder, depth_folder, analysis, assembly_file, exon_selection)
      
        display_results(results, analysis)
        
        


# Main function
def main():
    
    # Run the Streamlit app
    app_ARDC()
    

# Run the main function if the script is executed directly
if __name__ == "__main__":
    main()