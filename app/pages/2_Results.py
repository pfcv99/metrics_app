import streamlit as st
import pandas as pd
from components import logo

sidebar_logo = "data/img/unilabs_logo.svg"
main_body_logo = "data/img/thumbnail_image001.png"
st.logo(sidebar_logo, icon_image=main_body_logo)



# Function to display results in a DataFrame
def display_results(results):
    
    st.header("Results")
    
    
    
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
    
    # Display the DataFrame with column configurations
    st.dataframe(df, column_config=column_configs)

#results = query.process_files(option_bam, option_bed, bed_folder, bam_folder, depth_folder, map_file)
#display_results(results)