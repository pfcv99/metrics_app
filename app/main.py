# metrics_app/app/main.py

# Import necessary libraries
import streamlit as st
import pandas as pd
from pathlib import Path
import subprocess
import os
import time
from components import streamlit_page_config
from components import settings
from streamlit_option_menu import option_menu





# Set Streamlit page configuration
streamlit_page_config.set_page_configuration()


# Define constants for file extensions
BAM_EXTENSION = ".bam"
BED_EXTENSION = ".bed"
OUTPUT_EXTENSION = ".depth"


# Function to create necessary folders
def folders():
    output_folder = Path("./data/depth")
    bed_folder = Path("/mnt/DADOS/Biologia Molecular/15-NGS/PCRMultiplex/3-Analise/2024/Casos Somático/BED")
    bam_folder = Path("/mnt/DADOS/Biologia Molecular/15-NGS/PCRMultiplex/3-Analise/2024/Casos Somático/BAM")
    return output_folder, bed_folder, bam_folder

# Function to select BED file
def select_bed(bed_files):
    # Allow the user to select a BED file from a dropdown
    option_bed = st.selectbox('Select a BED file', bed_files, index=None, label_visibility="collapsed",placeholder="Select a BED file")
    
    # If no BED file is selected, allow the user to upload a BED file
    if not option_bed:
        st.info("No BED file selected. Please select a BED file.")
    return option_bed

# Function to select BAM files based on the selected BED
def select_bam(bam_files, option_bed, mapping_file):
    # Read the mapping file
    mapping_df = pd.read_csv(mapping_file)

    # Filter BAM files that correspond to the selected BED
    valid_bam_files = mapping_df[mapping_df['BED_File'] == option_bed]['BAM_File'].tolist()

    # Allow the user to select BAM files in a multi-selection dropdown
    container = st.container()
    all_bam_files = [Path(f).name for f in bam_files if Path(f).name in valid_bam_files]
    
    if option_bed:
        all = st.checkbox("Select all ")
    else:
        all = False
    
    if all != False:
        option_bam = container.multiselect('Select BAM file(s)', all_bam_files, all_bam_files, label_visibility="collapsed",placeholder="Select a BAM file(s)")
    else:
        option_bam = container.multiselect('Select BAM file(s)', all_bam_files, label_visibility="collapsed",placeholder="Select a BAM file(s)")

    # If no BAM files are selected, allow the user to upload BAM file(s)
    if not option_bam:
        st.info("No BAM file(s) selected. Please select BAM file(s).")

    return option_bam

# Function to calculate average read depth
def calculate_average_read_depth(bam_path, bed_path, output_path):
    run_samtools_depth(bam_path, bed_path, output_path)
    average_read_depth = calculate_average_depth(output_path)
    coverage_stats = count_coverage(output_path)
    date_utc = pd.Timestamp.utcnow()

    return {
        'Date': date_utc,
        'Average_Read_Depth': average_read_depth,
        **coverage_stats
    }

# Function to execute samtools depth
def run_samtools_depth(bam_path, bed_path, output_path):
    command = f"samtools depth -b '{bed_path}' '{bam_path}' > '{output_path}'"
    subprocess.run(command, shell=True)

# Function to calculate average depth
def calculate_average_depth(output_path):
    awk_command = f"awk '{{sum += $3}} END {{print sum/NR}}' {output_path}"
    result = subprocess.run(awk_command, shell=True, capture_output=True, text=True)
    return float(result.stdout.strip()) if result.stdout.strip() else None

# Function to count coverage at different levels
def count_coverage(output_path):
    bases_with_coverage = {1: 0, 10: 0, 15: 0, 20: 0, 30: 0, 50: 0, 100: 0, 500: 0}

    with open(output_path) as file:
        lines = file.readlines()
        total_bases = len(lines)

        if total_bases == 0:
            return {'Coverage_1x(%)': None, 'Coverage_10x(%)': None, 'Coverage_15x(%)': None ,'Coverage_20x(%)': None,
                    'Coverage_30x(%)': None, 'Coverage_50x(%)': None, 'Coverage_100x(%)': None, 'Coverage_500x(%)': None}

        for line in lines:
            fields = line.strip().split()
            depth = float(fields[2])

            for coverage, count in bases_with_coverage.items():
                if depth >= coverage:
                    bases_with_coverage[coverage] += 1

    percentage_with_coverage = {cov: (count / total_bases) * 100.0 for cov, count in bases_with_coverage.items()}
    return {f'Coverage_{cov}x(%)': percentage for cov, percentage in percentage_with_coverage.items()}

# Modified function to process files
def process_files(option_bam, option_bed, bed_folder, bam_folder, output_folder, mapping_file):
    # Read the mapping file
    mapping_df = pd.read_csv(mapping_file)

    results = []

    for bam_file in option_bam:
        bam_path = bam_folder / bam_file
        bed_path = bed_folder / option_bed
        output_file = output_folder / f"output_{os.path.basename(bam_file)[:-4]}.depth"

        result = calculate_average_read_depth(bam_path, bed_path, output_file)
        result.update({'BAM_File': bam_file, 'BED_File': option_bed})

        # Add 'OMNOMICS_Average_Read_Depth' column using mapping information
        mapping_info = mapping_df[mapping_df['BAM_File'] == bam_file]['OMNOMICS_Average_Read_Depth'].values
        result['OMNOMICS_Average_Read_Depth'] = mapping_info[0] if len(mapping_info) > 0 else None

        results.append(result)

    return results

# Function to display progress bar
def progress_bar():
    progress_text = "Operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)

    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1, text=progress_text)
    time.sleep(1)
    my_bar.empty()
    
    success = st.success('Successfully completed!', icon="✅")
    time.sleep(1)
    success.empty()

# Function to display results in a DataFrame
def display_results(results):
    st.header("Results")
    df = pd.DataFrame(results)
    df.set_index('Date', inplace=True)
    # Replace the line that sets ordered_columns with the following
    ordered_columns = ['BED_File','BAM_File', 'OMNOMICS_Average_Read_Depth'] + [col for col in df.columns if col not in ['BAM_File', 'BED_File', 'OMNOMICS_Average_Read_Depth']]

    df = df[ordered_columns]

    column_configs = {}
    for column in df.columns[df.columns.str.startswith('Coverage')]:
        column_configs[column] = st.column_config.ProgressColumn(
            help="Coverage percentage",
            format="%.2f",
            min_value=0,
            max_value=100
        )
    # Display the DataFrame with column configurations
    st.dataframe(df, column_config=column_configs)

# Function to define Streamlit app
def streamlit_app(bam_files, bed_files, bed_folder, bam_folder, output_folder, mapping_file):
    # Set the title for the sidebar
    st.sidebar.title(":red[Unilabs] analysis tools")

    with st.sidebar:
        # Create an option menu in the sidebar
        selected = option_menu(None, ["Average read depth calculator", "About", 'Settings'],
                               icons=['calculator', 'info-circle', 'gear'], menu_icon="menu-app", default_index=0)

    if selected == "Average read depth calculator":
        # Set the title for the main section
        st.markdown(
            "# Average read depth calculator\n#"
        )
        with st.container(height=300, border = True):
            # Create two columns for layout
            col1, col2 = st.columns(2)
            with col1:
                # Column for BED file selection
                st.markdown(
                    "## :red[Step 1.] BED file",
                    help=(
                        "**Please select a BED file.**\n"
                        "- The selection of a :red[BED file] is crucial for calculating the :red[average read depth].\n"
                        "- A :red[BED file] defines the genomic regions of interest.\n"
                        "- The :red[read depth] will be calculated specifically for these regions.\n"
                        "- Ensure that the selected :red[BED file] corresponds to the genomic regions you want to analyze."
                    )
                )
                option_bed = select_bed(bed_files)
            with col2:
                # Column for BAM file selection
                st.markdown(
                    "## :red[Step 2.] BAM file",
                    help=(
                        "**Please select a BAM file.**\n"
                        "- The selection of a :red[BAM file] is essential for analyzing the sequencing data.\n"
                        "- A :red[BAM file] contains aligned sequencing reads on the reference genome.\n"
                        "- Ensure that the selected :red[BAM file] corresponds to the sequencing data you want to analyze."
                    )
                )
                option_bam = select_bam(bam_files, option_bed, mapping_file)
            
            
        if option_bam and option_bed:
            # Display progress bar during file processing
            progress_bar()
            # Process selected files and display results
            results = process_files(option_bam, option_bed, bed_folder, bam_folder, output_folder, mapping_file)
            display_results(results)

    elif selected == "About":
        # Display information about the tool
        st.title("About")
        st.divider()
        st.subheader("Base code for average read depth calculator")
        st.code("samtools depth -b file.bed file.bam > output.  depth\n\nawk '{{sum += $3}} END {{print sum/NR}}' output.depth",
                language="bash")

    elif selected == "Settings":
        # Column for BED file selection
        st.markdown(
                "## :red[Step 1.] BED Working Directory",
                help=(
                    ":red[**Please select a BED Working Directory.**]"
                )
            )
        settings.bed_working_directory()
        # Column for BAM file selection
        st.markdown(
                "## :red[Step 2.] BAM Working Directory",
                help=(
                    ":red[**Please select a BAM Working Directory.**]"
                )
            )
        settings.bam_working_directory()
        # Column for BED_BAM_Map csv file
        st.markdown(
                "## :red[Step 3.] BED_BAM_Map file",
                help=(
                    ":red[**Please select a BED_BAM_Map file.**]"
                )
            )
        settings.bed_bam_map_file()
            
        

# Main function
def main():
    # Create necessary folders
    output_folder, bed_folder, bam_folder = folders()

    bam_files = [f.name for f in bam_folder.iterdir() if f.suffix == BAM_EXTENSION]
    bed_files = [f.name for f in bed_folder.iterdir() if f.suffix == BED_EXTENSION]

    # Provide the path to the mapping file
    mapping_file = Path("/mnt/DADOS/Biologia Molecular/15-NGS/PCRMultiplex/3-Analise/2024/Casos Somático/Casos2.csv")

    # Run the Streamlit app
    streamlit_app(bam_files, bed_files, bed_folder, bam_folder, output_folder, mapping_file)

# Run the main function if the script is executed directly
if __name__ == "__main__":
    main()
