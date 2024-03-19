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
from time import sleep
from stqdm import stqdm

# Set Streamlit page configuration
streamlit_page_config.set_page_configuration()

logo.add_logo()


# Function to select BED file
def region_of_interest(opt, assembly):
    
    if assembly == "GRCh38/hg38":
        bed_files = genome_regions.mane()
    elif assembly == "GRCh37/hg19":
        bed_files = genome_regions.ucsc() 
    
    # Allow the user to select a region of interest in a dropdown
    if opt == "Single Gene":
        region = st.selectbox('Select a Gene of Interest', bed_files, index=None, label_visibility="collapsed",placeholder="Select a Gene of Interest")
    elif opt == "Gene Panel":
        panel = st.radio('Select a Gene Panel', ["Unilabs Panel", "Custom Panel"], index=0, label_visibility="visible", horizontal=True)
        if panel == "Unilabs Panel":
            data = pd.read_csv('data/regions/gene_panels/BED_Files_Emedgene_2.csv', sep=',', header=0)
            df = pd.DataFrame(data)
            panel_lst = df['Panel_Name_EN_EMEDGENE'].unique().tolist()
            panel = st.selectbox('Select a Gene Panel', panel_lst, index=None, label_visibility="collapsed",placeholder="Select a Gene Panel")
            genes_lst = df[df['Panel_Name_EN_EMEDGENE'] == panel]['Genes'].tolist()
            region = genes_lst 
        elif panel == "Custom Panel":
            region = st.multiselect('Select some Genes', bed_files, label_visibility="collapsed",placeholder="Select some Genes")
    elif opt == "Exome":
        region = st.selectbox('Select an Exome', bed_files, index=None, label_visibility="collapsed",placeholder="Select an Exome")
    
    # If no BED file is selected show error
    if not region:
        if opt == "Single Gene":
            st.info("No Gene of Interest selected. Please select a Gene of Interest.")
        elif opt == "Gene Panel":
            st.info("No Gene Panel selected. Please select a Gene Panel.")
        elif opt == "Exome":
            st.info("No Exome selected. Please select an Exome.")
            
    return region

# Function to select BAM files based on the selected BED
def select_bam(bam_files, region, map_file):
    ## Read the mapping file
    #mapping_df = pd.read_csv(map_file)
#
    ## Filter BAM files that correspond to the selected BED
    #valid_bam_files = mapping_df[mapping_df['BED_File'] == region]['BAM_File'].tolist()

    # Allow the user to select BAM files in a multi-selection dropdown
    container = st.container()
    all_bam_files = [Path(f).name for f in bam_files]
    
    if region:
        all = st.checkbox("Select all ")
    else:
        all = False
    
    if all != False:
        option_bam = container.multiselect('Select BAM file(s)', all_bam_files, all_bam_files, label_visibility="collapsed",placeholder="Select a BAM file(s)")
    else:
        option_bam = container.multiselect('Select BAM file(s)', all_bam_files, label_visibility="collapsed",placeholder="Select a BAM file(s)")

    # If no BAM filread_depthes are selected, allow the user to upload BAM file(s)
    if not option_bam:
        st.info("No BAM file(s) selected. Please select BAM file(s).")

    return option_bam

# Function to calculate average read depth
def compute_read_depth(bam_path, bed_path, depth_path, region):
    
    sd.run_samtools_depth_v2(bam_path, bed_path, depth_path, region)
    average_read_depth = calculate_average_read_depth(depth_path)
    coverage_stats = count_coverage(depth_path)
    date_utc = pd.Timestamp.utcnow()

    return {
        'Date': date_utc,
        'Average_Read_Depth': average_read_depth,
        **coverage_stats
    }


## Function to calculate average depth
#def calculate_average_read_depth(depth_path):
#    awk_command = f"awk '{{sum += $3}} END {{print sum/NR}}' {depth_path}"
#    result = subprocess.run(awk_command, shell=True, capture_output=True, text=True)
#    return float(result.stdout.strip()) if result.stdout.strip() else None

def calculate_average_read_depth(depth_path):
    depths = []

    with open(depth_path, 'r') as file:
        for line in file:
            depth = line.strip().split()[2]
            depths.append(float(depth))

    if depths:
        average_depth = sum(depths) / len(depths)
        return round(average_depth, 2)
    else:
        return None






# Function to count coverage at different levels
def count_coverage(depth_path):
    #bases_with_coverage = {1: 0, 10: 0, 15: 0, 20: 0, 30: 0, 50: 0, 100: 0, 500: 0} # Original
    bases_with_coverage = {500: 0, 100: 0, 50: 0, 30: 0, 20: 0, 15: 0, 10: 0, 1: 0} # Reverse

    with open(depth_path) as file:
        lines = file.readlines()
        total_bases = len(lines)

        #if total_bases == 0:
        #    return {'Coverage_1x(%)': None, 'Coverage_10x(%)': None, 'Coverage_15x(%)': None ,'Coverage_20x(%)': None,
        #            'Coverage_30x(%)': None, 'Coverage_50x(%)': None, 'Coverage_100x(%)': None, 'Coverage_500x(%)': None}
        
        if total_bases == 0:
            return {'Coverage_500x(%)': None, 'Coverage_100x(%)': None, 'Coverage_50x(%)': None ,'Coverage_30x(%)': None,
                    'Coverage_20x(%)': None, 'Coverage_15x(%)': None, 'Coverage_10x(%)': None, 'Coverage_1x(%)': None}

        for line in lines:
            fields = line.strip().split()
            depth = float(fields[2])

            for coverage, count in bases_with_coverage.items():
                if depth >= coverage:
                    bases_with_coverage[coverage] += 1

    percentage_with_coverage = {cov: (count / total_bases) * 100.0 for cov, count in bases_with_coverage.items()}
    return {f'Coverage_{cov}x(%)': percentage for cov, percentage in percentage_with_coverage.items()}

# Modified function to process files
def process_files(option_bam, region, bam_folder, depth_folder, opt):
    if opt == "Single Gene":

        results = []

        for bam_file in option_bam:
            bam_path = bam_folder / bam_file
            bed_path = "data/regions/MANE_genomic/UCSC_hg19_exons_modif_canonical.bed"
            depth_file = depth_folder / f"{os.path.basename(bam_file)[:-4]}.depth"

            result = compute_read_depth(bam_path, bed_path, depth_file, region)
            result.update({'BAM_File': bam_file, 'BED_File': region})

            ## Add 'OMNOMICS_Average_Read_Depth' column using mapping information
            #mapping_info = mapping_df[mapping_df['BAM_File'] == bam_file]['OMNOMICS_Average_Read_Depth'].values
            #result['OMNOMICS_Average_Read_Depth'] = mapping_info[0] if len(mapping_info) > 0 else None

            results.append(result)

        return results
    
    elif opt == "Gene Panel":
        # Gene Panel
        print("Gene Panel")

    
    elif opt == "Exome":
        # Exome
        print("Exome")

# Function to display results in a DataFrame
def display_results(results, opt):
    if opt == "Single Gene":
        st.header("Results - Single Gene")


        df = pd.DataFrame(results)
        df.set_index('Date', inplace=True)
        # Replace the line that sets ordered_columns with the following
        ordered_columns = ['BED_File','BAM_File'] + [col for col in df.columns if col not in ['BAM_File', 'BED_File']]

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
    elif opt == "Gene Panel":
        st.header("Results - Gene Panel")


        df = pd.DataFrame(results)
        df.set_index('Date', inplace=True)
        # Replace the line that sets ordered_columns with the following
        ordered_columns = ['BED_File','BAM_File'] + [col for col in df.columns if col not in ['BAM_File', 'BED_File']]

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
            
    elif opt == "Exome":
        st.header("Results - Exome")



        df = pd.DataFrame(results)
        df.set_index('Date', inplace=True)
        # Replace the line that sets ordered_columns with the following
        ordered_columns = ['BED_File','BAM_File'] + [col for col in df.columns if col not in ['BAM_File', 'BED_File']]

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


def working_directory(opt):
    while True:
        try:
            if opt == "Single Gene":
                bam_folder = Path("./data/mapped")
                map_file = Path("./data/bam_bed_map/bam_bed_map.csv")
                depth_folder = Path("./data/depth")
                
            elif opt == "Gene Panel":
                bam_folder = Path("./data/mapped")
                map_file = Path("./data/bam_bed_map/gene_panels_bam_bed_map.csv")
                depth_folder = Path("./data/depth")
            
            elif opt == "Exome":
                bam_folder = Path("./data/mapped")
                map_file = Path("./data/bam_bed_map/bam_bed_map.csv")
                depth_folder = Path("./data/depth")
            
            # If everything is successful, break out of the loop
            break

        except OSError as e:
            st.error(f"Error: {e}")
            st.warning("Please resolve the error before continuing.")
            # Continue the loop if there is an error

    return bam_folder, map_file, depth_folder



# Function to define Streamlit app
def app_ARDC():    
    # Set the title for the main section
    st.markdown(
        "# Average read depth and coverage calculator\n#"
    )
    with st.container(border = True):
        # Create two columns for layout
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                "## :red[Step 1.] Analysis Type",
                help=(
                    "**Please select the type of analysis.**\n"
                    "- This will be mandatory to know where your data is located.\n"
                    "- The analysis will be performed on data within this selected analysis.\n"
                    "- Make sure the necessary files for analysis are in the respective directory."
                )
            )
            opt = st.radio(
                "Select an option",
                ["Single Gene", "Gene Panel", "Exome"],
                key="visibility",
                label_visibility="visible",
                disabled=False,
                horizontal=True
                )

            bam_folder, map_file, depth_folder = working_directory(opt)
            
        with col2:
            st.markdown(
                "## :red[Step 2.] Genome Assembly",
                help=(
                    "**Please select the genome assembly.**\n"
                    "- The selection of a :red[genome assembly] is crucial for analyzing the sequencing data.\n"
                    "- A :red[genome assembly] defines the reference genome used for aligning the sequencing reads.\n"
                    "- Ensure that the selected :red[genome assembly] corresponds to the reference genome used for aligning the sequencing reads."
                )
            )
            assembly = st.radio(
                "Select an option",
                ["GRCh37/hg19", "GRCh38/hg38"],
                label_visibility="visible",
                disabled=False,
                horizontal=True, index=1
                )

            
    
    with st.container(border = True):
        # Create two columns for layout
        col1, col2 = st.columns(2)
        with col1:
            if opt == "Single Gene":
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
            elif opt == "Gene Panel":
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
            elif opt == "Exome":
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

            region = region_of_interest(opt, assembly)
            
        with col2:
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
            
            bam_files = [f.name for f in bam_folder.iterdir() if f.suffix == ".bam"]
            option_bam = select_bam(bam_files, region, map_file)
        
        
    if option_bam and region:
        #Progress Bar
        stqdm.pandas(desc="Calculating Results")
        # Process selected files and display results
        results = process_files(option_bam, region, bam_folder, depth_folder, opt)
      
        display_results(results, opt)
        
        


# Main function
def main():
    
    # Run the Streamlit app
    app_ARDC()
    

# Run the main function if the script is executed directly
if __name__ == "__main__":
    main()
